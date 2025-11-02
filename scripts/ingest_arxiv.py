#!/usr/bin/env python3
"""
The Lab - arXiv Paper Ingestion
Fetches and filters papers from arXiv API for relevant AI/ML categories
"""
import glob
import json
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
import requests
from xml.etree import ElementTree as ET

# arXiv categories to monitor
ARXIV_CATEGORIES = [
    'cs.AI',  # Artificial Intelligence
    'cs.LG',  # Machine Learning
    'cs.CL',  # Computation and Language (NLP)
    'cs.CV',  # Computer Vision
    'cs.NE',  # Neural and Evolutionary Computing
    'stat.ML'  # Machine Learning (Statistics)
]

# Known research labs/organizations (for author reputation)
KNOWN_LABS = [
    'deepmind', 'google', 'openai', 'meta', 'facebook', 'microsoft',
    'anthropic', 'apple', 'nvidia', 'stanford', 'mit', 'berkeley',
    'cmu', 'oxford', 'cambridge', 'eth', 'toronto', 'montreal',
    'huggingface', 'cohere', 'inflection', 'adept'
]


def ensure_data_dir():
    """Create data/arxiv directory if it doesn't exist"""
    Path("data/arxiv").mkdir(parents=True, exist_ok=True)


def get_today_filename():
    """Get filename for today's data"""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"data/arxiv/{today}.json"


def build_arxiv_query(categories, max_results=200):
    """Build arXiv API query for recent papers"""
    # Get papers from last 2 days to ensure we don't miss any
    start_date = (datetime.now() - timedelta(days=2)).strftime("%Y%m%d")
    
    # Build category query (OR across all categories)
    cat_query = ' OR '.join([f'cat:{cat}' for cat in categories])
    
    query = f'({cat_query}) AND submittedDate:[{start_date}0000 TO {datetime.now().strftime("%Y%m%d")}2359]'
    
    return {
        'search_query': query,
        'start': 0,
        'max_results': max_results,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }


def fetch_arxiv_papers():
    """Fetch recent papers from arXiv API"""
    print("📚 Fetching papers from arXiv...")
    
    query_params = build_arxiv_query(ARXIV_CATEGORIES)
    base_url = 'https://export.arxiv.org/api/query'
    
    try:
        response = requests.get(base_url, params=query_params, timeout=30)
        response.raise_for_status()
        
        # Parse XML response
        root = ET.fromstring(response.content)
        
        # Extract namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom',
              'arxiv': 'http://arxiv.org/schemas/atom'}
        
        papers = []
        entries = root.findall('atom:entry', ns)
        
        print(f"📄 Found {len(entries)} papers")
        
        for entry in entries:
            paper = extract_paper_info(entry, ns)
            if paper:
                papers.append(paper)
        
        return papers
        
    except Exception as e:
        print(f"❌ Error fetching arXiv papers: {e}")
        return []


def extract_paper_info(entry, ns):
    """Extract relevant information from arXiv entry"""
    try:
        # Basic information
        arxiv_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
        title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
        summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
        
        # Published date
        published = entry.find('atom:published', ns).text[:10]
        
        # Authors
        authors = []
        for author in entry.findall('atom:author', ns):
            name = author.find('atom:name', ns)
            if name is not None:
                authors.append(name.text)
        
        # Categories
        categories = []
        for category in entry.findall('atom:category', ns):
            term = category.get('term')
            if term:
                categories.append(term)
        
        # PDF link
        pdf_link = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        abs_link = f"https://arxiv.org/abs/{arxiv_id}"
        
        return {
            'arxiv_id': arxiv_id,
            'title': title,
            'summary': summary,
            'authors': authors,
            'categories': categories,
            'published': published,
            'url': abs_link,
            'pdf_url': pdf_link,
            'date': datetime.now().strftime("%Y-%m-%d"),
            'source': 'arxiv'
        }
        
    except Exception as e:
        print(f"⚠️  Error parsing entry: {e}")
        return None


def calculate_author_reputation(authors):
    """Calculate author reputation score based on known labs"""
    score = 0.0
    
    for author in authors:
        author_lower = author.lower()
        
        # Check if author is from a known lab (based on email/affiliation)
        for lab in KNOWN_LABS:
            if lab in author_lower:
                score = max(score, 0.8)
                break
    
    return score


def calculate_novelty_score(title, summary):
    """Estimate novelty based on keywords and phrasing"""
    text = (title + ' ' + summary).lower()
    
    # Breakthrough indicators
    breakthrough_terms = [
        'novel', 'new', 'first', 'breakthrough', 'state-of-the-art', 'sota',
        'outperforms', 'improves', 'achieves', 'surpasses', 'efficient',
        'scalable', 'surprising', 'unexpected'
    ]
    
    # Methodological terms
    method_terms = [
        'architecture', 'mechanism', 'framework', 'approach', 'method',
        'algorithm', 'technique', 'strategy', 'model'
    ]
    
    # Application terms
    application_terms = [
        'vision', 'language', 'multimodal', 'reasoning', 'generation',
        'understanding', 'translation', 'classification', 'detection'
    ]
    
    score = 0.0
    
    # Breakthrough terms add more
    for term in breakthrough_terms:
        if term in text:
            score += 0.15
    
    # Method terms
    for term in method_terms:
        if term in text:
            score += 0.05
    
    # Application terms
    for term in application_terms:
        if term in text:
            score += 0.03
    
    # Cap at 1.0
    return min(score, 1.0)


def score_paper_relevance(paper):
    """Score paper relevance for The Lab"""
    # Base score
    score = 0.3
    
    # Author reputation (up to +0.3)
    author_rep = calculate_author_reputation(paper.get('authors', []))
    score += author_rep * 0.3
    
    # Novelty indicators (up to +0.3)
    novelty = calculate_novelty_score(paper.get('title', ''), paper.get('summary', ''))
    score += novelty * 0.3
    
    # Category relevance (up to +0.2)
    categories = paper.get('categories', [])
    priority_cats = ['cs.AI', 'cs.LG', 'cs.CL']
    if any(cat in priority_cats for cat in categories):
        score += 0.2
    elif any(cat in ARXIV_CATEGORIES for cat in categories):
        score += 0.1
    
    # Recency boost (papers from today get slight boost)
    if paper.get('published') == datetime.now().strftime("%Y-%m-%d"):
        score += 0.1
    
    return min(score, 1.0)


def filter_and_score_papers(papers):
    """Filter and score papers for relevance"""
    print("🔍 Scoring papers for relevance...")
    
    scored_papers = []
    
    for paper in papers:
        relevance_score = score_paper_relevance(paper)
        paper['research_score'] = round(relevance_score, 2)
        
        # Only keep papers with score >= 0.4
        if paper['research_score'] >= 0.4:
            scored_papers.append(paper)
    
    # Sort by score (highest first)
    scored_papers.sort(key=lambda x: x['research_score'], reverse=True)
    
    print(f"✅ Kept {len(scored_papers)} relevant papers (score ≥ 0.4)")
    print(f"   High relevance (≥0.8): {len([p for p in scored_papers if p['research_score'] >= 0.8])}")
    print(f"   Notable (≥0.6): {len([p for p in scored_papers if p['research_score'] >= 0.6])}")
    
    return scored_papers


def save_papers(papers):
    """Save papers to JSON file"""
    ensure_data_dir()
    filename = get_today_filename()
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved {len(papers)} papers to {filename}")


def load_recent_papers_as_fallback():
    """
    Load papers from the most recent successful ingestion as fallback
    
    When the arXiv API is unavailable (e.g., due to GitHub Actions firewall),
    this function provides graceful degradation by using cached papers from
    the last 1-3 days. Research papers don't change daily, so recent papers
    remain relevant and valuable for analysis.
    
    Returns:
        list: Papers from most recent successful ingestion, or empty list
    """
    arxiv_dir = Path("data/arxiv")
    
    # Look for recent files (last 3 days)
    for days_ago in range(1, 4):
        past_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        past_file = arxiv_dir / f"{past_date}.json"
        if past_file.exists():
            with open(past_file, 'r', encoding='utf-8') as f:
                papers = json.load(f)
            print(f"📦 Using fallback data from {past_date} ({len(papers)} papers)")
            return papers
    return []


def main():
    print("🔬 Starting arXiv paper ingestion...")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📚 Categories: {', '.join(ARXIV_CATEGORIES)}")
    
    # Fetch papers
    papers = fetch_arxiv_papers()
    
    if not papers:
        print("⚠️  No papers fetched from arXiv API")
        print("🔄 Attempting to use recent data as fallback...")
        papers = load_recent_papers_as_fallback()
        
        if not papers:
            print("❌ No fallback data available")
            # Create empty file so aggregation doesn't fail
            save_papers([])
            return
    
    # Filter and score
    relevant_papers = filter_and_score_papers(papers)
    
    # Save
    save_papers(relevant_papers)
    
    print("✅ arXiv ingestion complete!")
    
    # Rate limiting - be nice to arXiv
    time.sleep(3)


if __name__ == "__main__":
    main()
