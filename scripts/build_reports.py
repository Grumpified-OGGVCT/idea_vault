#!/usr/bin/env python3
"""
Build HTML reports from markdown source files using Jinja2 templates
Implements SEO optimization, TL;DR generation, and responsive design
"""
import re
import math
import json
from pathlib import Path
from datetime import datetime
import frontmatter
import markdown
from jinja2 import Environment, FileSystemLoader
from collections import Counter

# Try to import sumy for TL;DR generation (graceful degradation)
try:
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lex_rank import LexRankSummarizer
    SUMY_AVAILABLE = True
    
    # Download required NLTK data
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
    except:
        pass
except ImportError:
    SUMY_AVAILABLE = False
    print("⚠️  sumy not available - TL;DR will use first paragraphs")

# Paths
BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
REPORTS_DIR = BASE_DIR / "docs" / "reports"
OUTPUT_DIR = BASE_DIR / "docs" / "reports"

# Configuration
TABLE_COLLAPSE_THRESHOLD = 10  # Rows count threshold for collapsible tables

# Emoji mapping for sections
EMOJI_MAP = {
    'research overview': '🔬',
    'breakthrough papers': '📚',
    'the breakthrough papers': '📚',
    'supporting research': '🔗',
    'implementation watch': '🤗',
    'pattern analysis': '📈',
    'emerging directions': '📈',
    'research implications': '🔮',
    'what to watch': '👀',
    'for builders': '🔧',
    'buildable solutions': '🚀',
    'support': '💰',
    'about': '📖',
    'tldr': '🔍',
    'summary': '📊',
}


def slugify(text):
    """Convert text to URL-safe slug"""
    # Remove emojis and special chars, keep alphanumeric, spaces, hyphens, and underscores
    text = re.sub(r'[^\w\s-]', '', text.lower())
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[-_\s]+', '-', text)
    return text.strip('-')


def wordcount(text):
    """Count words in text"""
    return len(re.findall(r'\w+', text))


def read_time(words):
    """Calculate reading time (200 words per minute)"""
    return max(1, math.ceil(words / 200))


def extract_emoji(title):
    """Extract emoji from section title or use mapping"""
    emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]|[\u2600-\u26FF\u2700-\u27BF]')
    emojis = emoji_pattern.findall(title)
    if emojis:
        return emojis[0]
    
    # Try to find from mapping
    clean_title = re.sub(emoji_pattern, '', title).strip().lower()
    for key, emoji in EMOJI_MAP.items():
        if key in clean_title:
            return emoji
    
    return '📄'  # Default emoji


def generate_tldr(content, max_sentences=3):
    """Generate TL;DR summary from content"""
    if SUMY_AVAILABLE:
        try:
            # Use NLTK tokenization for better sentence splitting
            parser = PlaintextParser.from_string(content, Tokenizer('english'))
            summarizer = LexRankSummarizer()
            summary_sentences = summarizer(parser.document, max_sentences)
            return ' '.join([str(sentence) for sentence in summary_sentences])
        except Exception as e:
            print(f"⚠️  LexRank summarization failed: {e}")
    
    # Fallback: use NLTK sentence tokenizer if available
    try:
        import nltk
        sentences = nltk.sent_tokenize(content)
        clean_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        return ' '.join(clean_sentences[:max_sentences])
    except:
        # Last resort: simple regex split
        sentences = re.split(r'[.!?]+', content)
        clean_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        return '. '.join(clean_sentences[:max_sentences]) + '.'


def parse_markdown_sections(md_content):
    """Parse markdown content into sections with IDs"""
    sections = []
    
    # Remove "Back to Top" links as per SEO requirements
    # These are replaced by sticky navigation
    md_content = re.sub(r'<p class="back-to-home"><a href="#top">⬆️ Back to Top</a></p>\s*', '', md_content)
    md_content = re.sub(r'\[⬆️ Back to Top\]\(#top\)\s*', '', md_content)
    
    # Split by h2 headings (##)
    parts = re.split(r'\n##\s+', md_content)
    
    for i, part in enumerate(parts[1:], 1):  # Skip first part (before first h2)
        lines = part.split('\n', 1)
        if len(lines) < 2:
            continue
        
        title = lines[0].strip()
        content = lines[1] if len(lines) > 1 else ''
        
        # Extract emoji and clean title
        emoji = extract_emoji(title)
        clean_title = re.sub(r'[\U00010000-\U0010ffff]|[\u2600-\u26FF\u2700-\u27BF]', '', title).strip()
        
        # Generate section ID
        section_id = slugify(clean_title)
        
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])
        html_content = md.convert(content)
        
        # Count table rows
        table_count = html_content.count('<tr>')
        
        # Extract table if present
        table_data = None
        if table_count > 0:
            table_data = {
                'html': html_content,
                'row_count': table_count,
                'caption': clean_title
            }
        
        sections.append({
            'id': section_id,
            'title': clean_title,
            'emoji': emoji,
            'content': html_content,
            'table': table_data  # Always include table data; let template handle threshold logic
        })
    
    return sections


def build_toc(sections):
    """Build table of contents from sections"""
    toc = []
    for sec in sections:
        toc.append({
            'id': sec['id'],
            'title': sec['title'],
            'emoji': sec['emoji']
        })
    return toc


def extract_keywords(content, max_keywords=10):
    """Extract keywords from content"""
    # Simple keyword extraction based on frequency
    words = re.findall(r'\b[a-z]{4,}\b', content.lower())
    
    # Use NLTK stopwords if available, otherwise use basic set
    try:
        import nltk
        try:
            from nltk.corpus import stopwords
            stop_words = set(stopwords.words('english'))
        except:
            nltk.download('stopwords', quiet=True)
            from nltk.corpus import stopwords
            stop_words = set(stopwords.words('english'))
    except:
        # Fallback to basic stopwords
        stop_words = {'that', 'this', 'with', 'from', 'have', 'been', 'were', 
                     'will', 'their', 'there', 'these', 'those', 'what', 'when',
                     'where', 'which', 'while', 'about', 'after', 'before', 'being'}
    
    words = [w for w in words if w not in stop_words]
    
    # Count frequencies
    word_counts = Counter(words)
    return [word for word, count in word_counts.most_common(max_keywords)]


def build_html_report(md_path, template):
    """Build HTML report from markdown file"""
    print(f"📄 Processing: {md_path.name}")
    
    # Load markdown with frontmatter
    try:
        post = frontmatter.load(md_path)
        content = post.content
        metadata = post.metadata
    except Exception as e:
        print(f"⚠️  No frontmatter found, using plain markdown: {e}")
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        metadata = {}
    
    # Extract date from filename if not in metadata
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', md_path.name)
    date_str = metadata.get('date', date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d'))
    
    # Generate metadata
    title = metadata.get('title', f"AI Net Idea Vault – {date_str}")
    description = metadata.get('description', 
        "Daily AI research digest – breakthrough papers, implementation watch, pattern radar & ready-to-code playbook.")
    
    # Extract or generate keywords
    if 'keywords' in metadata:
        keywords = metadata['keywords'] if isinstance(metadata['keywords'], list) else [metadata['keywords']]
    else:
        keywords = extract_keywords(content)
    
    # Calculate metrics
    word_count = wordcount(content)
    reading_time = read_time(word_count)
    slug = slugify(title)
    
    # Parse sections
    sections = parse_markdown_sections(content)
    
    # Build TOC
    toc = build_toc(sections)
    
    # Generate TL;DR
    # Remove markdown formatting for better summary
    clean_content = re.sub(r'[#*_`\[\]()]', '', content)
    clean_content = re.sub(r'http\S+', '', clean_content)
    summary = generate_tldr(clean_content, max_sentences=3)
    
    # Prepare template data
    meta = {
        'title': title,
        'date': date_str,
        'description': description,
        'keywords': keywords,
        'author': metadata.get('author', 'Grumpified-OGGVCT'),
        'slug': slug,
        'filename': md_path.name.replace('.md', '.html'),  # Use actual filename for canonical URL
        'wordcount': word_count,
        'read_time': reading_time,
        'table_threshold': TABLE_COLLAPSE_THRESHOLD  # Pass threshold to template
    }
    
    # Render template
    html = template.render(
        meta=meta,
        toc=toc,
        sections=sections,
        summary=summary
    )
    
    return html, slug


def main():
    """Main build process"""
    print("🔨 Starting HTML report build...")
    
    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template('report.html')
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process all markdown reports
    md_files = list(REPORTS_DIR.glob('*.md'))
    
    if not md_files:
        print("⚠️  No markdown files found in reports directory")
        return
    
    print(f"📚 Found {len(md_files)} markdown report(s)")
    
    built_count = 0
    for md_path in md_files:
        # Skip index files
        if 'index' in md_path.name.lower():
            continue
        
        try:
            html_content, slug = build_html_report(md_path, template)
            
            # Write HTML file
            output_path = OUTPUT_DIR / f"{md_path.stem}.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ Built: {output_path.name}")
            built_count += 1
            
        except Exception as e:
            print(f"❌ Failed to process {md_path.name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎉 Build complete! Generated {built_count} HTML report(s)")
    print(f"📂 Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
