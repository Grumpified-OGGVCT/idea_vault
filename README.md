# 🔬 AI Net Idea Vault

**LLM-Enhanced Research Intelligence with Dual-Output Publishing**

AI Net Idea Vault is a GitHub-native research aggregator that continuously monitors cutting-edge AI research, analyzes discoveries with scholarly depth using optional LLM enhancement, and publishes comprehensive reports twice daily through dual-output channels (HTML + Jekyll Markdown)—all automated on GitHub's free tier.

## 🎯 What It Does

- **Ingests Research**: Daily scraping of AI research from arXiv, HuggingFace, Papers with Code
- **Ollama Ecosystem Tracking**: Monitors Ollama blog, Cloud models, community discussions, tools, and GitHub integrations
- **Deep Analysis**: Three-layer scholarly examination (Deep Dive, Cross-Project Analysis, Practical Implications)
- **LLM Enhancement**: Optional multi-persona LLM analysis using Ollama Turbo Cloud or OpenAI-compatible endpoints
- **The Scholar Persona**: Academic voice with technical rigor and contextual depth
- **NOSTR Publishing**: Publishes reports to 48+ NOSTR relays using NIP-23 (long-form content)
- **Dual-Output Publishing**: 
  - Markdown to `docs/_daily/` (Jekyll collection with frontmatter)
  - HTML to `docs/reports/` (existing crimson-themed format)
  - NOSTR network (decentralized social protocol)
- **Auto-Publishes**: GitHub Pages deployment with searchable archive
- **Twice-Daily Execution**: Runs at 08:00 UTC and 20:00 UTC
- **Zero Maintenance**: Fully automated on GitHub Actions

## 🏗️ Architecture

```
AI_Net_Idea_Vault/
├── .github/workflows/
│   └── daily_report.yml         # Twice-daily report generation (08:00 & 20:00 UTC)
├── scripts/
│   ├── generate_report.py       # Enhanced with Ollama Turbo + OpenAI LLM integration
│   ├── generate_report_index.py # Report index generation
│   ├── ingest_*.py              # Multiple data source ingesters
│   ├── ingest_official.py       # Ollama blog and official sources
│   ├── ingest_cloud.py          # Ollama Cloud models
│   ├── ingest_community.py      # Reddit, HN, YouTube, newsletters
│   ├── ingest_tools.py          # GitHub Ollama integrations
│   ├── ingest_issues.py         # GitHub issues/PRs about Ollama
│   ├── ollama_turbo_client.py   # Ollama Cloud API client
│   ├── publish_nostr.py         # NOSTR publishing (48+ relays)
│   ├── aggregate.py             # Data aggregation
│   └── mine_insights.py         # Pattern detection & insights
├── config/
│   └── llm_personas.json        # Multi-persona LLM configurations
├── data/
│   ├── arxiv/                   # arXiv research papers
│   ├── huggingface/             # HF models & datasets
│   ├── paperswithcode/          # SOTA benchmarks
│   ├── official/                # Ollama blog & official sources
│   ├── cloud/                   # Ollama Cloud models
│   ├── community/               # Community discussions & content
│   ├── tools/                   # Ollama tools & integrations
│   ├── aggregated/              # Aggregated daily data
│   ├── insights/                # Mined insights & patterns
│   └── nostr_publications/      # NOSTR publication records
├── docs/
│   ├── _daily/                  # 🆕 Jekyll collection (timestamped posts)
│   ├── reports/                 # HTML/Markdown reports
│   ├── assets/css/              # Enhanced dark theme with crimson accents
│   ├── _config.yml              # Jekyll configuration
│   └── index.html               # Dual-content navigation
├── requirements.txt             # Python deps (including LLM libraries)
└── package.json                 # Frontend dependencies
```

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/Grumpified-OGGVCT/idea_vault.git
cd idea_vault
pip install -r requirements.txt
```

### 2. Enable GitHub Actions
- Go to Settings → Actions → General
- Enable "Read and write permissions"

### 3. Configure Secrets (Optional - For LLM Enhancement)
Add these secrets in Settings → Secrets and variables → Actions:
- `LLM_API_KEY`: Your OpenAI-compatible API key
- `LLM_ENDPOINT`: (Optional) Custom LLM endpoint URL
- `LLM_MODEL`: (Optional) Model name (default: gpt-3.5-turbo)
- `OLLAMA_API_KEY`: Your Ollama Cloud API key
- `OLLAMA_ENDPOINT`: (Optional) Ollama API endpoint (default: https://api.ollama.ai)
- `NOSTR_PRIVATE_KEY`: Your NOSTR private key (hex format) for publishing to relays
- `SOURCE_URL`: (Optional) Custom source URL

**Note**: The system works without LLM secrets using fallback analysis. NOSTR publishing is optional and gracefully skipped if not configured.

### 4. Enable GitHub Pages
- Go to Settings → Pages
- Source: main branch, Folder: /docs

### 5. Test Locally
```bash
python scripts/generate_report.py
```

## 📊 Report Structure

Each daily report includes:

### 🔬 Deep Dive
Technical explanations of how technologies work:
- Architecture and algorithms
- Design decisions and trade-offs
- Implementation details

### 🔗 Cross-Project Analysis
Identifying synergies between research:
- Related projects and models
- Integration opportunities
- Comparative approaches

### 💡 Practical Implications
Real-world applications:
- Use cases and ecosystem fit
- Who should care and why
- Future possibilities

### 🤖 LLM Enhancement (When Enabled)
Multi-persona analysis using configured personas:
- **Technical Analyst**: Deep technical dissection (temperature: 0.3)
- **Strategic Synthesizer**: Cross-project synthesis (temperature: 0.7)
- **Practical Applicator**: Real-world application mapping (temperature: 0.5)

## 🎨 Design Features

- **Crimson Accents** (#DC143C) - Scholarly sophistication
- **Dark Theme** - Comfortable reading
- **Dual Output**:
  - Jekyll collection in `docs/_daily/` with timestamped filenames
  - HTML reports in `docs/reports/` (backward compatible)
- **Reports Archive** - Searchable with list/calendar views
- **Responsive Layout** - Mobile-friendly
- **Calendar Navigation** - Visual date-based browsing

### 🤖 LLM Persona System

The system supports multiple LLM personas with **dual backend support**:

#### Ollama Turbo Cloud (Priority)
- **Models**: deepseek-v3.1:671b-cloud, qwen3-vl:235b-cloud, qwen3-coder:30b-cloud
- **Features**: Deep reasoning, vision capabilities, web search fallback
- **Usage**: Set `OLLAMA_API_KEY` secret
- **Endpoint**: https://api.ollama.ai (default)

#### OpenAI-Compatible Fallback
- **Models**: Any OpenAI-compatible model
- **Usage**: Set `LLM_API_KEY` and optionally `LLM_ENDPOINT`, `LLM_MODEL`
- **Fallback**: Automatically used if Ollama is unavailable

### Technical Analyst
- **Focus**: Algorithms, architectures, implementation details
- **Temperature**: 0.3 (precise, methodical)
- **Use Case**: Deep technical paper analysis

### Strategic Synthesizer (Default)
- **Focus**: Research connections, trend prediction, synthesis
- **Temperature**: 0.7 (creative, connective)
- **Use Case**: Identifying emerging patterns and opportunities

### Practical Applicator
- **Focus**: Use cases, implementation roadmaps, ecosystem fit
- **Temperature**: 0.5 (balanced, pragmatic)
- **Use Case**: Translating research to production systems

### Graceful Degradation
If LLM APIs are unavailable or not configured:
- System falls back to existing Scholar analysis
- No functionality loss
- Clear console messaging

### NOSTR Publishing
- **Protocol**: NIP-23 (long-form content)
- **Relays**: 48+ default relays (configurable)
- **Event Kind**: 30023 (long-form content with metadata)
- **Tags**: AI, research, daily, llm, machinelearning
- **Authentication**: NOSTR private key (nsec format)
- **Graceful Failure**: Publishing skipped if key not configured

### Personas Defined

## 🔗 Integration with GrumpiBlogged

AI Net Idea Vault is part of the GrumpiBlogged ecosystem:
- **Ollama Pulse** (various times) - EchoVein's vein-tapping reports
- **AI Net Idea Vault** (08:00 & 20:00 UTC) - The Scholar's LLM-enhanced analysis
- **GitHub Trending** (09:00 CT) - Persona-driven project reviews

Access via: `http://127.0.0.1:8081/admin/grumpiblogged`

## 📅 Execution Schedule

- **Morning Report**: 08:00 UTC daily
- **Evening Report**: 20:00 UTC daily
- **Manual Trigger**: Available via workflow_dispatch

## 🔧 Technical Stack

- **Python 3.11+**: Core scripting
- **GitHub Actions**: Automation
- **Jekyll**: Static site generation
- **OpenAI-compatible LLMs**: Optional enhancement
- **Libraries**:
  - `httpx`: Async HTTP for LLM calls
  - `aiohttp`: Async HTTP for Ollama Turbo Client
  - `openai`: OpenAI-compatible LLM integration
  - `nostr`: NOSTR protocol implementation
  - `pydantic`: Configuration validation
  - `sentence-transformers`: Embeddings
  - `scikit-learn`: Pattern detection
  - `beautifulsoup4`: Web scraping
  - `feedparser`: RSS/Atom parsing

## 📝 Output Formats

### Markdown (Jekyll Collection)
- **Location**: `docs/_daily/`
- **Filename**: `YYYY-MM-DD-HHMM-research-intelligence-YYYY-MM-DD.md`
- **Frontmatter**: Full Jekyll metadata (layout, title, date, categories, tags, permalink, excerpt)
- **Use Case**: Jekyll site integration, canonical markdown archive

### HTML (Reports Directory)
- **Location**: `docs/reports/`
- **Filename**: `lab-YYYY-MM-DD.md`
- **Format**: Markdown with minimal Jekyll frontmatter
- **Use Case**: Backward compatibility, direct HTML rendering

## 🔒 Security & Privacy

- No secrets committed to repository
- LLM API keys stored as GitHub secrets
- Graceful failure handling
- All data processing on GitHub infrastructure
- No external data transmission except to configured LLM endpoint

## 🧪 Testing

```bash
# Test report generation (with or without LLM)
python scripts/generate_report.py

# Verify dual output
ls docs/reports/lab-*.md
ls docs/_daily/*.md

# Check Jekyll frontmatter
head -15 docs/_daily/*.md
```

## 📄 License

MIT License

---

**Live Dashboard**: https://grumpified-oggvct.github.io/idea_vault
**Repository**: https://github.com/Grumpified-OGGVCT/idea_vault
**Design Philosophy**: Preserve all existing functionality while adding LLM enhancement and dual-output publishing
