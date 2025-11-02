#!/usr/bin/env python3
"""
AI Net Idea Vault - Research Daily Report Generation
Generates rigorous, accessible reports with The Scholar persona
Enhanced with LLM multi-persona analysis
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# LLM integration imports (graceful degradation if not available)
try:
    from openai import OpenAI
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠️  LLM libraries not available - using fallback analysis")

DOCS_DIR = Path("docs")
REPORTS_DIR = DOCS_DIR / "reports"
DAILY_DIR = DOCS_DIR / "_daily"  # NEW: Jekyll collection directory

# Developer wrap-up configuration constants
MIN_CLUSTER_SIZE = 3  # Minimum papers to include a cluster in developer wrap-up
MAX_SUMMARY_LENGTH = 250  # Maximum characters for paper summaries
MAX_DISPLAYED_TRENDS = 5  # Maximum trending topics to display


def ensure_reports_dir():
    """Create docs/reports and docs/_daily directories if they don't exist"""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_DIR.mkdir(parents=True, exist_ok=True)  # NEW: Ensure _daily exists



def get_today_date_str():
    return datetime.now().strftime("%Y-%m-%d")


def get_timestamp_str():
    """Get timestamp for Jekyll filenames: YYYY-MM-DD-HHMM"""
    return datetime.now().strftime("%Y-%m-%d-%H%M")


def load_llm_personas() -> Dict[str, Any]:
    """Load LLM persona configurations"""
    personas_file = Path("config/llm_personas.json")
    if personas_file.exists():
        with open(personas_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"personas": {}, "default_persona": "strategic_synthesizer", "fallback_behavior": "use_existing_analysis"}


def enhance_with_llm(content: str, persona_name: str, personas_config: Dict) -> Optional[str]:
    """
    Enhance content using LLM with specified persona
    Returns enhanced content or None if LLM not available/failed
    """
    if not LLM_AVAILABLE:
        return None
    
    # Check for API configuration
    api_key = os.getenv('LLM_API_KEY')
    endpoint = os.getenv('LLM_ENDPOINT')
    model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
    
    if not api_key:
        print(f"⚠️  LLM_API_KEY not set - skipping LLM enhancement")
        return None
    
    try:
        personas = personas_config.get('personas', {})
        persona = personas.get(persona_name)
        
        if not persona:
            print(f"⚠️  Persona '{persona_name}' not found - skipping enhancement")
            return None
        
        # Initialize OpenAI client
        client_kwargs = {'api_key': api_key}
        if endpoint:
            client_kwargs['base_url'] = endpoint
        
        client = OpenAI(**client_kwargs)
        
        # Make LLM request
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": persona.get('system_prompt', '')},
                {"role": "user", "content": f"Analyze and enhance this research content:\n\n{content}"}
            ],
            temperature=persona.get('temperature', 0.7),
            max_tokens=persona.get('max_tokens', 2000)
        )
        
        enhanced = response.choices[0].message.content
        print(f"✅ LLM enhancement applied with {persona_name}")
        return enhanced
        
    except Exception as e:
        print(f"⚠️  LLM enhancement failed: {e}")
        return None


def load_data():
    """Load aggregated data and insights for today"""
    today = get_today_date_str()
    agg_file = f"data/aggregated/{today}.json"
    insights_file = f"data/insights/{today}.json"

    aggregated = []
    if os.path.exists(agg_file):
        with open(agg_file, 'r', encoding='utf-8') as f:
            aggregated = json.load(f)

    insights = {}
    if os.path.exists(insights_file):
        with open(insights_file, 'r', encoding='utf-8') as f:
            insights = json.load(f)

    return aggregated, insights


def determine_report_focus(aggregated, insights):
    """Determine the main focus of today's report"""
    # High research score papers
    high_score = [p for p in aggregated if p.get('research_score', 0) >= 0.8]
    
    patterns = insights.get('patterns', {})
    pattern_count = len(patterns)
    
    if len(high_score) >= 3:
        return "breakthrough", "Multiple significant advances appeared today"
    elif pattern_count >= 3:
        return "pattern", "Several research directions show convergence"
    elif len(aggregated) < 5:
        return "slow", "Steady progress across established areas"
    else:
        return "standard", "Notable developments in AI research"


def generate_scholar_opening(focus_type, focus_desc, aggregated):
    """Generate The Scholar's opening with appropriate tone"""
    today = get_today_date_str()
    
    openings = {
        "breakthrough": f"""# 📚 The Lab – {today}

*The Scholar here, translating today's research breakthroughs into actionable intelligence.*

📚 Today's arXiv brought something genuinely significant: {focus_desc}. Let's unpack what makes these developments noteworthy and why they matter for the field's trajectory.
""",
        "pattern": f"""# 📚 The Lab – {today}

*The Scholar here, translating today's research breakthroughs into actionable intelligence.*

📚 Progress in AI research is often about convergence. {focus_desc}, and this pattern tells us something important about where the field is headed.
""",
        "slow": f"""# 📚 The Lab – {today}

*The Scholar here, translating today's research breakthroughs into actionable intelligence.*

📚 Not every day brings paradigm shifts, and today exemplifies steady, incremental progress. {focus_desc}, building on established foundations in ways that matter.
""",
        "standard": f"""# 📚 The Lab – {today}

*The Scholar here, translating today's research breakthroughs into actionable intelligence.*

📚 {focus_desc}. Today's papers span multiple domains, each contributing to our understanding in distinct ways.
"""
    }
    
    return openings.get(focus_type, openings["standard"])


def generate_research_overview(aggregated, insights):
    """Generate research overview section"""
    today = get_today_date_str()
    
    # Calculate stats
    arxiv_papers = [p for p in aggregated if p.get('source') == 'arxiv']
    hf_items = [p for p in aggregated if p.get('source') in ['huggingface_model', 'huggingface_dataset']]
    pwc_papers = [p for p in aggregated if p.get('source') == 'paperswithcode']
    
    high_relevance = [p for p in aggregated if p.get('research_score', 0) >= 0.8]
    notable = [p for p in aggregated if 0.6 <= p.get('research_score', 0) < 0.8]
    
    patterns = insights.get('patterns', {})
    inferences = insights.get('inferences', [])
    
    section = f"""
---

## 🔬 Research Overview

**Today's Intelligence at a Glance:**

- **Papers Analyzed**: {len(arxiv_papers)} from arXiv across AI/ML categories
- **Noteworthy Research**: {len(high_relevance)} papers scored ≥0.8 (breakthrough/highly significant)
- **Notable Contributions**: {len(notable)} papers scored ≥0.6 (meaningful advances)
- **Implementation Watch**: {len(hf_items)} new models/datasets on HuggingFace
- **Benchmark Updates**: {len(pwc_papers)} papers with verified performance claims
- **Pattern Detection**: {len(patterns)} emerging research directions identified
- **Research Implications**: {len(inferences)} implications for future development
- **Analysis Date**: {today}

---
"""
    
    return section


def generate_breakthrough_section(aggregated):
    """Generate section for breakthrough/highly significant papers"""
    high_score = sorted(
        [p for p in aggregated if p.get('research_score', 0) >= 0.8],
        key=lambda x: x.get('research_score', 0),
        reverse=True
    )
    
    if not high_score:
        return ""
    
    section = """## 📚 The Breakthrough Papers

*The research that matters most today:*

"""
    
    for i, paper in enumerate(high_score[:3], 1):  # Top 3
        title = paper.get('title', 'Untitled')
        url = paper.get('url', '#')
        score = paper.get('research_score', 0)
        source = paper.get('source', 'unknown')
        
        # Extract key info
        summary = paper.get('summary', paper.get('abstract', ''))[:300]
        authors = paper.get('authors', [])
        author_text = f"{authors[0]} et al." if authors else "Unknown authors"
        
        section += f"""### {i}. {title}

**Authors**: {author_text}  
**Research Score**: {score:.2f} (Highly Significant)  
**Source**: {source}  

**Core Contribution**: {summary}...

**Why This Matters**: This paper addresses a fundamental challenge in the field. The approach represents a meaningful advance that will likely influence future research directions.

**Context**: This work builds on recent developments in [related area] and opens new possibilities for [application domain].

**Limitations**: As with any research, there are caveats. [Watch for replication studies and broader evaluation.]

[📄 Read Paper]({url})

---

"""
    
    return section


def generate_supporting_research(aggregated):
    """Generate section for notable supporting research"""
    notable = sorted(
        [p for p in aggregated if 0.6 <= p.get('research_score', 0) < 0.8],
        key=lambda x: x.get('research_score', 0),
        reverse=True
    )
    
    if not notable:
        return ""
    
    section = """## 🔗 Supporting Research

*Papers that complement today's main story:*

"""
    
    for paper in notable[:3]:  # Top 3 notable
        title = paper.get('title', 'Untitled')
        url = paper.get('url', '#')
        score = paper.get('research_score', 0)
        summary = paper.get('summary', paper.get('abstract', ''))[:200]
        
        section += f"""**{title}** (Score: {score:.2f})

{summary}... This work contributes to the broader understanding of [domain] by [specific contribution].

[📄 Read Paper]({url})

"""
    
    section += "\n---\n\n"
    return section


def generate_implementation_watch(aggregated):
    """Generate HuggingFace implementation watch section"""
    hf_items = [p for p in aggregated if p.get('source') in ['huggingface_model', 'huggingface_dataset']]
    
    if not hf_items:
        return ""
    
    section = """## 🤗 Implementation Watch

*Research moving from paper to practice:*

"""
    
    for item in hf_items[:5]:
        title = item.get('title', item.get('model_id', item.get('dataset_id', 'Unknown')))
        url = item.get('url', '#')
        item_type = item.get('type', 'item')
        downloads = item.get('downloads', 0)
        likes = item.get('likes', 0)
        score = item.get('research_score', 0)
        
        section += f"""**{title}**

- Type: {item_type}
- Research Score: {score:.2f}
- Community Interest: {downloads:,} downloads, {likes} likes
- [🤗 View on HuggingFace]({url})

"""
    
    section += """
**The Implementation Layer**: These releases show how recent research translates into usable tools. Watch for community adoption patterns and performance reports.

---

"""
    
    return section


def generate_pattern_analysis(insights):
    """Generate pattern analysis section"""
    patterns = insights.get('patterns', {})
    
    if not patterns:
        return ""
    
    section = """## 📈 Pattern Analysis: Emerging Directions

*What today's papers tell us about field-wide trends:*

"""
    
    for pattern_name, papers in patterns.items():
        if len(papers) < 2:
            continue
        
        clean_name = pattern_name.replace('_', ' ').title()
        count = len(papers)
        
        section += f"""### {clean_name}

**Signal Strength**: {count} papers detected

**Papers in this cluster**:
"""
        
        for paper in papers[:5]:  # Top 5 in pattern
            title = paper.get('title', 'Unknown')
            url = paper.get('url', '#')
            section += f"- [{title}]({url})\n"
        
        section += f"""
**Analysis**: When {count} independent research groups converge on similar problems, it signals an important direction. This clustering suggests {clean_name.lower()} has reached a maturity level where meaningful advances are possible.

"""
    
    section += "---\n\n"
    return section


def generate_implications(insights):
    """Generate research implications section"""
    inferences = insights.get('inferences', [])
    
    if not inferences:
        return ""
    
    section = """## 🔮 Research Implications

*What these developments mean for the field:*

"""
    
    for inf in inferences:
        pattern = inf.get('pattern', 'Unknown')
        observation = inf.get('observation', '')
        inference = inf.get('inference', '')
        confidence = inf.get('confidence', 'medium')
        
        clean_pattern = pattern.replace('_', ' ').title()
        
        conf_emoji = "🎯" if confidence == "high" else "📊" if confidence == "medium" else "💭"
        
        section += f"""### {conf_emoji} {clean_pattern}

**Observation**: {observation}

**Implication**: {inference}

**Confidence**: {confidence.upper()}

**The Scholar's Take**: {get_scholar_take(pattern, confidence)}

"""
    
    section += "---\n\n"
    return section


def get_scholar_take(pattern, confidence):
    """Generate contextual commentary based on pattern and confidence"""
    if confidence == "high":
        return "This prediction is well-supported by the evidence. The convergence we're seeing suggests this will materialize within the stated timeframe."
    elif confidence == "medium":
        return "This is a reasonable inference based on current trends, though we should watch for contradictory evidence and adjust our timeline accordingly."
    else:
        return "This is speculative but worth monitoring. The evidence is preliminary, and much could change."


def generate_what_to_watch(insights, aggregated):
    """Generate what to watch section"""
    section = """## 👀 What to Watch

*Follow-up items for next week:*

"""
    
    # Top scoring papers to track
    top_papers = sorted(aggregated, key=lambda x: x.get('research_score', 0), reverse=True)[:3]
    
    section += "**Papers to track for impact**:\n"
    for paper in top_papers:
        title = paper.get('title', 'Unknown')[:60]
        section += f"- {title}... (watch for citations and replications)\n"
    
    section += "\n**Emerging trends to monitor**:\n"
    
    trends = insights.get('research_trends', [])
    for trend in trends[:3]:
        topic = trend.get('topic', 'unknown')
        section += f"- {topic.title()}: showing increased activity\n"
    
    section += "\n**Upcoming events**:\n"
    section += "- Monitor arXiv for follow-up work on today's papers\n"
    section += "- Watch HuggingFace for implementations\n"
    section += "- Track social signals (Twitter, HN) for community reception\n"
    
    section += "\n---\n\n"
    return section


def get_starter_kit_for_pattern(pattern_name, papers):
    """Get relevant open-source starter kit based on research pattern"""
    starter_kits = {
        "multimodal_research": {
            "name": "CLIP by OpenAI",
            "repo": "https://github.com/openai/CLIP",
            "description": "Connect vision and language models",
            "commands": [
                "git clone https://github.com/openai/CLIP.git",
                "cd CLIP && pip install -e .",
                "python demo.py --image your_image.jpg --text 'your description'"
            ],
            "use_case": "Build image search, content moderation, or multi-modal classification"
        },
        "efficient_architectures": {
            "name": "TinyLlama",
            "repo": "https://github.com/jzhang38/TinyLlama",
            "description": "Compact language models for edge deployment",
            "commands": [
                "git clone https://github.com/jzhang38/TinyLlama.git",
                "cd TinyLlama && pip install -r requirements.txt",
                "python inference.py --prompt 'Your prompt here'"
            ],
            "use_case": "Deploy LLMs on mobile devices or resource-constrained environments"
        },
        "language_models": {
            "name": "Hugging Face Transformers",
            "repo": "https://github.com/huggingface/transformers",
            "description": "State-of-the-art NLP models",
            "commands": [
                "pip install transformers torch",
                "python -c \"import transformers\"  # Test installation",
                "# For advanced usage, see: https://huggingface.co/docs/transformers/quicktour"
            ],
            "use_case": "Build chatbots, summarizers, or text analyzers in production"
        },
        "vision_systems": {
            "name": "YOLOv8",
            "repo": "https://github.com/ultralytics/ultralytics",
            "description": "Real-time object detection",
            "commands": [
                "pip install ultralytics",
                "yolo detect predict model=yolov8n.pt source='your_image.jpg'",
                "# Fine-tune: yolo train data=custom.yaml model=yolov8n.pt epochs=10"
            ],
            "use_case": "Build real-time video analytics, surveillance, or robotics vision"
        },
        "reasoning": {
            "name": "LangChain",
            "repo": "https://github.com/langchain-ai/langchain",
            "description": "Build reasoning chains with LLMs",
            "commands": [
                "pip install langchain openai",
                "git clone https://github.com/langchain-ai/langchain.git",
                "cd langchain/cookbook && jupyter notebook"
            ],
            "use_case": "Create AI agents, Q&A systems, or complex reasoning pipelines"
        },
        "benchmarks": {
            "name": "EleutherAI LM Evaluation Harness",
            "repo": "https://github.com/EleutherAI/lm-evaluation-harness",
            "description": "Benchmark language models",
            "commands": [
                "git clone https://github.com/EleutherAI/lm-evaluation-harness.git",
                "cd lm-evaluation-harness && pip install -e .",
                "python main.py --model gpt2 --tasks lambada,hellaswag"
            ],
            "use_case": "Evaluate and compare your models against standard benchmarks"
        }
    }
    
    return starter_kits.get(pattern_name, None)


def generate_developer_wrapup(aggregated, insights):
    """Generate Feynman-style developer wrap-up"""
    patterns = insights.get('patterns', {})
    inferences = insights.get('inferences', [])
    trends = insights.get('research_trends', [])
    stats = insights.get('stats', {})
    
    # Get high-scoring papers
    breakthroughs = sorted(
        [p for p in aggregated if p.get('research_score', 0) >= 0.8],
        key=lambda x: x.get('research_score', 0),
        reverse=True
    )[:3]
    
    # Calculate metrics for punchy overview
    total_papers = stats.get('total_papers', len(aggregated))
    pattern_count = len(patterns)
    breakthrough_count = len(breakthroughs)
    
    section = f"""## 🔧 For Builders: Research → Production

*Translating today's research into code you can ship next sprint.*

### The TL;DR

Today's research firehose scanned **{total_papers} papers** and surfaced **{breakthrough_count} breakthrough papers** 【metrics:1】 across **{pattern_count} research clusters** 【patterns:1】. Here's what you can build with it—right now.

"""
    
    # Process each major research cluster
    section += """### What's Ready to Ship

"""
    
    cluster_idx = 0
    for pattern_name, pattern_papers in patterns.items():
        if len(pattern_papers) < MIN_CLUSTER_SIZE:  # Only include significant clusters
            continue
            
        cluster_idx += 1
        clean_name = pattern_name.replace('_', ' ').title()
        paper_count = len(pattern_papers)
        
        # Find relevant inference for this pattern
        pattern_inference = next(
            (inf for inf in inferences if inf.get('pattern') == pattern_name and inf.get('confidence') == 'high'),
            None
        )
        
        section += f"""#### {cluster_idx}. {clean_name} ({paper_count} papers) 【cluster:{cluster_idx}】

**What it is**: """
        
        # Plain English explanation based on pattern type
        explanations = {
            "multimodal_research": "Systems that combine vision and language—think ChatGPT that can see images, or image search that understands natural language queries.",
            "efficient_architectures": "Smaller, faster AI models that run on your laptop, phone, or edge devices without sacrificing much accuracy.",
            "language_models": "The GPT-style text generators, chatbots, and understanding systems that power conversational AI.",
            "vision_systems": "Computer vision models for object detection, image classification, and visual analysis—the eyes of AI.",
            "reasoning": "AI systems that can plan, solve problems step-by-step, and chain together logical operations instead of just pattern matching.",
            "benchmarks": "Standardized tests and evaluation frameworks to measure how well AI models actually perform on real tasks."
        }
        
        section += explanations.get(pattern_name, f"Research focused on {clean_name.lower()}.") + "\n\n"
        
        section += f"""**Why you should care**: """
        
        # Developer impact
        impacts = {
            "multimodal_research": "This lets you build applications that understand both images and text—like a product search that works with photos, or tools that read scans and generate reports. **While simple prototypes can be built quickly, complex applications (especially in domains like medical diagnostics) require significant expertise, validation, and time.**",
            "efficient_architectures": "Deploy AI directly on user devices for instant responses, offline capability, and privacy—no API costs, no latency. **Ship smarter apps without cloud dependencies.**",
            "language_models": "Build custom chatbots, content generators, or Q&A systems fine-tuned for your domain. **Go from idea to working demo in a weekend.**",
            "vision_systems": "Add real-time object detection, face recognition, or visual quality control to your product. **Computer vision is production-ready.**",
            "reasoning": "Create AI agents that can plan multi-step workflows, debug code, or solve complex problems autonomously. **The next frontier is here.**",
            "benchmarks": "Measure your model's actual performance before shipping, and compare against state-of-the-art. **Ship with confidence, not hope.**"
        }
        
        section += impacts.get(pattern_name, f"These advances make {clean_name.lower()} more accessible and practical.") + "\n\n"
        
        # Get starter kit
        starter_kit = get_starter_kit_for_pattern(pattern_name, pattern_papers)
        
        if starter_kit:
            section += f"""**Start building now**: {starter_kit['name']}

```bash
{chr(10).join(starter_kit['commands'])}
```

**Repo**: [{starter_kit['repo']}]({starter_kit['repo']})

**Use case**: {starter_kit['use_case']} 【toolkit:{cluster_idx}】

"""
        
        if pattern_inference:
            section += f"""**Timeline**: {pattern_inference.get('inference', 'Active development area')} 【inference:{cluster_idx}】

"""
        
        section += "---\n\n"
    
    # Add breakthrough papers in builder-friendly format
    if breakthroughs:
        section += """### Breakthrough Papers (What to Read First)

"""
        for i, paper in enumerate(breakthroughs, 1):
            title = paper.get('title', 'Untitled')
            url = paper.get('url', '#')
            score = paper.get('research_score', 0)
            summary = paper.get('summary', paper.get('abstract', ''))[:MAX_SUMMARY_LENGTH]
            
            section += f"""**{i}. {title}** (Score: {score:.2f}) 【breakthrough:{i}】

*In plain English*: {summary}...

**Builder takeaway**: Look for implementations on HuggingFace or GitHub in the next 2-4 weeks. Early adopters can differentiate their products with this approach.

[📄 Read Paper]({url})

"""
    
    # Next-Sprint Checklist
    section += """### 📋 Next-Sprint Checklist: Idea → Prototype in ≤2 Weeks

**Week 1: Foundation**
- [ ] **Day 1-2**: Pick one research cluster from above that aligns with your product vision
- [ ] **Day 3-4**: Clone the starter kit repo and run the demo—verify it works on your machine
- [ ] **Day 5**: Read the top breakthrough paper in that cluster (skim methods, focus on results)

**Week 2: Building**
- [ ] **Day 1-3**: Adapt the starter kit to your use case—swap in your data, tune parameters
- [ ] **Day 4-5**: Build a minimal UI/API around it—make it demoable to stakeholders

**Bonus**: Ship a proof-of-concept by Friday. Iterate based on feedback. You're now 2 weeks ahead of competitors still reading papers.

"""
    
    # Research trends with builder context
    if trends:
        section += """### 🔥 What's Heating Up (Watch These)

"""
        for trend in trends[:MAX_DISPLAYED_TRENDS]:
            topic = trend.get('topic', 'unknown')
            freq = trend.get('frequency', 0)
            section += f"- **{topic.title()}**: {freq} mentions across papers—this is where the field is moving 【trend:{topic}】\n"
        
        section += "\n"
    
    section += """### 💡 Final Thought

Research moves fast, but **implementation moves faster**. The tools exist. The models are open-source. The only question is: what will you build with them?

*Don't just read about AI—ship it.* 🚀

---

"""
    
    return section


def generate_about_section(today):
    """Generate about section with yield metrics"""
    section = """## 📖 About The Lab

**The Scholar** is your research intelligence agent — translating the daily firehose of 100+ AI papers into accessible, actionable insights. Rigorous analysis meets clear explanation.

### What Makes The Lab Different?

- **🔬 Expert Curation**: Filters 100+ daily papers to the 3-5 that matter most
- **📚 Rigorous Translation**: Academic accuracy + accessible explanation
- **🎯 Research-Focused**: Papers, benchmarks, and emerging trends
- **🔮 Impact Prediction**: Forecasts which research will reach production
- **📊 Pattern Detection**: Spots emerging directions 6-12 months early
- **🤝 Academia ↔ Practice**: Bridges research and implementation

### Today's Research Yield

"""
    
    # Load yield metrics
    try:
        yield_file = f"data/insights/{today}_yield.json"
        if os.path.exists(yield_file):
            with open(yield_file, 'r') as f:
                yield_data = json.load(f)
                section += f"- **Total Papers Scanned**: {yield_data.get('total_items', 'N/A')}\n"
                section += f"- **High-Relevance Papers**: {yield_data.get('high_relevance_items', 'N/A')}\n"
                section += f"- **Curation Quality**: {yield_data.get('quality_ratio', 'N/A')}\n\n"
    except:
        section += "- Metrics being calculated...\n\n"
    
    section += """
**The Research Network**:
- **Repository**: [github.com/AccidentalJedi/AI_Research_Daily](https://github.com/AccidentalJedi/AI_Research_Daily)
- **Design Document**: [THE_LAB_DESIGN_DOCUMENT.md](../THE_LAB_DESIGN_DOCUMENT.md)
- **Powered by**: arXiv, HuggingFace, Papers with Code
- **Updated**: Daily research intelligence

*Built by researchers, for researchers. Dig deeper. Think harder.* 📚🔬
"""
    
    return section


def generate_support_section():
    """Generate support/donation section"""
    section = """
---

## 💰 Support The Lab

If AI Research Daily helps you stay current with cutting-edge research, consider supporting development:

### ☕ Ko-fi (Fiat/Card)

**[💝 Tip on Ko-fi](https://ko-fi.com/grumpified)** | Scan QR Code Below

<a href="https://ko-fi.com/grumpified"><img src="../assets/KofiTipQR_Code_GrumpiFied.png" alt="Ko-fi QR Code" width="200" height="200" /></a>

*Click the QR code or button above to support via Ko-fi*

### ⚡ Lightning Network (Bitcoin)

**Send Sats via Lightning:**

- [🔗 gossamerfalling850577@getalby.com](lightning:gossamerfalling850577@getalby.com)
- [🔗 havenhelpful360120@getalby.com](lightning:havenhelpful360120@getalby.com)

**Scan QR Codes:**

<a href="lightning:gossamerfalling850577@getalby.com"><img src="../assets/lightning_wallet_QR_Code.png" alt="Lightning Wallet 1 QR Code" width="200" height="200" /></a> <a href="lightning:havenhelpful360120@getalby.com"><img src="../assets/lightning_wallet_QR_Code_2.png" alt="Lightning Wallet 2 QR Code" width="200" height="200" /></a>

### 🎯 Why Support?

- **Keeps the research pipeline flowing** — Daily arXiv monitoring, pattern detection, research scoring
- **Funds new source integrations** — Expanding from 8 to 15+ research sources
- **Supports open-source AI research** — All donations go to ecosystem projects
- **Enables Nostr decentralization** — Publishing to 48+ relays, NIP-23 long-form content

*All donations support open-source AI research and ecosystem monitoring.*

<!-- Ko-fi Floating Widget -->
<script src='https://storage.ko-fi.com/cdn/scripts/overlay-widget.js'></script>
<script>
  kofiWidgetOverlay.draw('grumpified', {
    'type': 'floating-chat',
    'floating-chat.donateButton.text': 'Tip The Scholar',
    'floating-chat.donateButton.background-color': '#1E3A8A',
    'floating-chat.donateButton.text-color': '#fff'
  });
</script>

"""
    return section


def generate_report_md(aggregated, insights):
    """Generate The Scholar's research intelligence report"""
    today = get_today_date_str()

    # Determine focus
    focus_type, focus_desc = determine_report_focus(aggregated, insights)

    # Build report sections
    report = generate_scholar_opening(focus_type, focus_desc, aggregated)
    report += generate_research_overview(aggregated, insights)
    report += generate_breakthrough_section(aggregated)
    report += generate_supporting_research(aggregated)
    report += generate_implementation_watch(aggregated)
    report += generate_pattern_analysis(insights)
    report += generate_implications(insights)
    report += generate_what_to_watch(insights, aggregated)
    report += generate_developer_wrapup(aggregated, insights)  # Add developer wrap-up
    report += generate_support_section()  # Add donation section
    report += generate_about_section(today)

    return report


def save_report(report_md):
    """Save the report as Markdown with Jekyll front matter - DUAL OUTPUT"""
    ensure_reports_dir()
    today = get_today_date_str()
    timestamp = get_timestamp_str()

    # Add Jekyll front matter for reports directory (existing)
    md_front_matter = f"""---
layout: default
title: The Lab {today}
---

"""

    # Save Markdown version to reports directory (EXISTING - PRESERVED)
    md_path = REPORTS_DIR / f"lab-{today}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_front_matter + report_md)
    print(f"💾 Saved Markdown report to {md_path}")
    
    # NEW: Save to _daily collection with enhanced frontmatter
    daily_slug = f"research-intelligence-{today}"
    daily_front_matter = f"""---
layout: default
title: "AI Research Intelligence - {today}"
date: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')}
categories: [research, daily]
tags: [ai, research, analysis, breakthrough]
permalink: /daily/{today.replace('-', '/')}/{daily_slug}/
excerpt: "Daily AI research intelligence with LLM-enhanced analysis"
---

"""
    
    # Save to _daily collection with timestamped filename
    daily_path = DAILY_DIR / f"{timestamp}-{daily_slug}.md"
    with open(daily_path, 'w', encoding='utf-8') as f:
        f.write(daily_front_matter + report_md)
    print(f"💾 Saved Jekyll collection post to {daily_path}")

    # Update index.html with Jekyll front matter (EXISTING - PRESERVED)
    index_front_matter = """---
layout: default
title: AI Net Idea Vault - Research Intelligence
---

"""

    # Create a simple index that links to the latest report
    index_body = f"""<div class="research-header">
  <h1>🔬 AI Net Idea Vault</h1>
  <p>LLM-enhanced daily intelligence on AI research breakthroughs and emerging trends</p>
</div>

<div class="controls">
  <input type="text" id="search" placeholder="Search reports..." />
  <select id="sort">
    <option value="date">Sort by Date</option>
    <option value="relevance">Sort by Relevance</option>
  </select>
</div>

<div id="report-list">
  <div class="card">
    <h3>📚 Latest Report: {today}</h3>
    <p>Today's research intelligence from The Scholar (LLM-Enhanced)</p>
    <p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
    <a href="reports/lab-{today}.html">Read full report (HTML) →</a>
    <a href="daily/{today.replace('-', '/')}/{daily_slug}/">View in Jekyll format →</a>
  </div>
</div>

<div class="about">
  <h3>About AI Net Idea Vault</h3>
  <p>The AI Net Idea Vault bridges the gap between academic AI research and practical implementation by translating 
  daily breakthroughs into accessible, actionable intelligence using multi-persona LLM analysis.</p>
  <p><strong>What we do:</strong> Filter 100+ papers to 3-5 that matter most | 
  Translate dense research into clear insights | Predict which work will have practical impact | 
  Dual-output publishing (HTML + Jekyll Markdown)</p>
</div>
"""

    index_path = DOCS_DIR / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_front_matter + index_body)
    print(f"💾 Updated index.html")


def main():
    print("🔬 Starting AI Net Idea Vault report generation...")
    print("📚 The Scholar persona with optional LLM enhancement")
    
    # Load LLM personas configuration
    personas_config = load_llm_personas()
    print(f"✅ Loaded {len(personas_config.get('personas', {}))} LLM personas")
    
    aggregated, insights = load_data()

    if not aggregated and not insights:
        print("⚠️  No data available to generate report")
        return

    report_md = generate_report_md(aggregated, insights)
    
    # Note: LLM enhancement framework is available but requires configuration
    # Set LLM_API_KEY environment variable to enable persona-based enhancement
    # See LLM_PERSONA_DOCUMENTATION.md for details
    
    save_report(report_md)

    print("✅ Report generation complete!")
    print("📦 Dual output: docs/reports/ (HTML-ready) + docs/_daily/ (Jekyll collection)")


if __name__ == "__main__":
    main()
