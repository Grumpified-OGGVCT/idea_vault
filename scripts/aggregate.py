#!/usr/bin/env python3
"""
The Lab - Data Aggregation
Merges daily JSONs from research sources into unified view
"""
import json
import os
from datetime import datetime
from pathlib import Path


def ensure_data_dir():
    """Create data/aggregated directory if it doesn't exist"""
    Path("data/aggregated").mkdir(parents=True, exist_ok=True)


def get_today_filename():
    """Get filename for today's aggregated data"""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"data/aggregated/{today}.json"


def load_source_data(source_dir):
    """Load today's data from a source directory"""
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"data/{source_dir}/{today}.json"
    
    if not os.path.exists(filename):
        return []
    
    with open(filename, 'r') as f:
        return json.load(f)


def score_research_relevance(entry):
    """
    Score entry relevance for AI research (0-1)
    Higher scores = more relevant research contribution
    """
    # Use existing research_score if available (from ingestion)
    if 'research_score' in entry:
        return entry['research_score']
    
    text = (entry.get('title', '') + ' ' + 
            entry.get('summary', '') + ' ' + 
            entry.get('abstract', '')).lower()
    
    score = 0.0
    
    # Breakthrough indicators
    breakthrough_terms = ['novel', 'new', 'first', 'breakthrough', 'sota', 'state-of-the-art']
    if any(term in text for term in breakthrough_terms):
        score += 0.2
    
    # Research quality signals
    research_terms = ['architecture', 'mechanism', 'framework', 'algorithm', 'method']
    if any(term in text for term in research_terms):
        score += 0.15
    
    # Application domains
    domain_terms = ['vision', 'language', 'multimodal', 'reasoning', 'generation']
    if any(term in text for term in domain_terms):
        score += 0.1
    
    # Benchmark/evaluation
    eval_terms = ['benchmark', 'evaluation', 'performance', 'outperform', 'achieves']
    if any(term in text for term in eval_terms):
        score += 0.15
    
    # Implementation availability
    if entry.get('github_url') or entry.get('source') == 'huggingface_model':
        score += 0.1
    
    return min(score, 1.0)


def filter_by_relevance(entries, threshold=0.4):
    """Filter entries by research relevance score"""
    scored_entries = []
    for entry in entries:
        score = score_research_relevance(entry)
        if score >= threshold:
            entry['research_score'] = round(score, 2)
            scored_entries.append(entry)
    
    return scored_entries


def aggregate_data():
    """Aggregate data from research sources with relevance filtering"""
    print("🔄 Aggregating data from research sources...")
    
    # Load from research sources
    arxiv = load_source_data("arxiv")
    huggingface = load_source_data("huggingface")
    paperswithcode = load_source_data("paperswithcode")
    
    # Load from Ollama-specific sources
    official = load_source_data("official")
    cloud = load_source_data("cloud")
    community = load_source_data("community")
    tools = load_source_data("tools")
    
    print(f"  📚 arXiv: {len(arxiv)} entries")
    print(f"  🤗 HuggingFace: {len(huggingface)} entries")
    print(f"  📊 Papers with Code: {len(paperswithcode)} entries")
    print(f"  📡 Ollama Official: {len(official)} entries")
    print(f"  ☁️  Ollama Cloud: {len(cloud)} entries")
    print(f"  👥 Community: {len(community)} entries")
    print(f"  🔧 Tools: {len(tools)} entries")
    
    # Combine all
    all_entries = arxiv + huggingface + paperswithcode + official + cloud + community + tools
    
    # Deduplicate by URL or arxiv_id
    seen_keys = set()
    unique_entries = []
    for entry in all_entries:
        key = entry.get('arxiv_id') or entry.get('url') or entry.get('title')
        if key not in seen_keys:
            seen_keys.add(key)
            unique_entries.append(entry)
    
    # Apply research relevance filtering
    print("🎯 Applying research relevance filtering...")
    filtered_entries = filter_by_relevance(unique_entries, threshold=0.4)
    
    # Sort by relevance score, then date
    sorted_entries = sorted(
        filtered_entries,
        key=lambda x: (x.get('research_score', 0), x.get('date', '')),
        reverse=True
    )
    
    print(f"✅ Aggregated {len(sorted_entries)} high-relevance entries (from {len(unique_entries)} total)")
    return sorted_entries, len(unique_entries)


def save_aggregated(entries):
    """Save aggregated data"""
    if not entries:
        print("⚠️  No data to save")
        return
    
    filename = get_today_filename()
    
    with open(filename, 'w') as f:
        json.dump(entries, f, indent=2)
    
    print(f"💾 Saved aggregated data to {filename}")


def save_yield_metrics(filtered_count, total_count):
    """Save daily yield metrics for monitoring"""
    today = datetime.now().strftime("%Y-%m-%d")
    yield_filename = f"data/insights/{today}_yield.json"
    
    # Ensure directory exists
    Path("data/insights").mkdir(parents=True, exist_ok=True)
    
    yield_data = {
        "date": datetime.now().isoformat(),
        "total_items": total_count,
        "high_relevance_items": filtered_count,
        "research_papers": filtered_count,
        "filter_threshold": 0.4,
        "quality_ratio": round(filtered_count / max(total_count, 1), 2)
    }
    
    with open(yield_filename, 'w') as f:
        json.dump(yield_data, f, indent=2)
    
    print(f"📊 Saved yield metrics to {yield_filename}")


def main():
    """Main aggregation function"""
    print("🚀 Starting data aggregation...")
    ensure_data_dir()
    
    entries, total_count = aggregate_data()
    save_aggregated(entries)
    save_yield_metrics(len(entries), total_count)
    
    print("✅ Data aggregation complete!")


if __name__ == "__main__":
    main()

