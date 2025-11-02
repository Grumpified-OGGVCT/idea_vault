# 💡 Idea Vault

**Your Personal Knowledge Garden, Automated**

Idea Vault is an automated content curation system that transforms web content into beautifully formatted daily insights. It scrapes designated sources, processes content with intelligence, and publishes to a dark-themed Jekyll site—all running on GitHub's free tier with zero maintenance.

## 🎯 What It Does

- **Auto-Scrapes**: Fetches content from configured sources twice daily (08:00 & 20:00 UTC)
- **Smart Processing**: Strips HTML, cleans content, and formats with LLM assistance
- **Beautiful Publishing**: Dark-themed Jekyll site with timestamped daily reports
- **GitHub Pages**: Automatic deployment with every update
- **Zero Maintenance**: Fully automated via GitHub Actions

## 🏗️ Architecture

```
idea_vault/
├── .github/workflows/
│   └── daily-report.yml       # Runs 2x daily (08:00 & 20:00 UTC)
├── scripts/
│   ├── scrape_and_clean.py    # Scraper + LLM processor
│   └── author_prompt.txt      # LLM system prompt
├── docs/                       # Jekyll site
│   ├── _config.yml            # Dark theme config
│   ├── _daily/                # Daily reports collection
│   ├── _sass/
│   │   └── custom.scss        # Dark mode styles
│   └── index.html             # Homepage
└── INVENTORY.md               # Full structure documentation
```

## 🚀 Quick Start

### 1. Fork & Clone
```bash
git clone https://github.com/YOUR-USERNAME/idea_vault.git
cd idea_vault
```

### 2. Configure Source
Edit `.github/workflows/daily-report.yml` and set your `SOURCE_URL`:
```yaml
env:
  SOURCE_URL: https://your-source-website.com
```

### 3. Enable GitHub Actions
- Go to Settings → Actions → General
- Enable "Read and write permissions"

### 4. Enable GitHub Pages
- Go to Settings → Pages
- Source: Deploy from a branch
- Branch: `main`, Folder: `/docs`

### 5. Test Locally (Optional)
```bash
pip install httpx beautifulsoup4
SOURCE_URL="https://example.com" python scripts/scrape_and_clean.py
```

## 📊 How It Works

### Daily Workflow (Automated)

1. **Trigger** (08:00 & 20:00 UTC)
   - GitHub Actions starts the workflow
   - Environment is prepared (Node 20, Python, dependencies)

2. **Scrape & Process**
   - `scrape_and_clean.py` fetches content from SOURCE_URL
   - HTML is stripped, main content extracted
   - Content is processed with LLM using `author_prompt.txt`

3. **Generate Report**
   - Timestamped markdown file created in `docs/_daily/`
   - YAML frontmatter added for Jekyll
   - Report formatted with sections, bullets, emojis

4. **Publish**
   - New report committed to repository
   - GitHub Pages automatically rebuilds site
   - Dark-themed report appears on your site

### LLM Integration

The `author_prompt.txt` instructs the LLM to:
- Create engaging, witty content
- Structure with clear sections and bullets
- Add personality while maintaining clarity
- Format as clean markdown for Jekyll

## 🎨 Design Features

- **Sophisticated Dark Theme** - GitHub-inspired color palette
- **Responsive Layout** - Mobile-friendly reading experience
- **Automatic Collections** - Daily reports organized by date
- **Clean Typography** - Optimized for long-form reading
- **Fast Loading** - Static site, no database required

## 🔧 Customization

### Change the Theme
Edit `docs/_sass/custom.scss` to customize colors:
```scss
$background-dark: #0d1117;      // Main background
$accent-primary: #58a6ff;       // Links and accents
```

### Modify the Schedule
Edit `.github/workflows/daily-report.yml`:
```yaml
schedule:
  - cron: '0 8 * * *'   # 08:00 UTC
  - cron: '0 20 * * *'  # 20:00 UTC
```

### Customize LLM Behavior
Edit `scripts/author_prompt.txt` to change:
- Tone and style
- Report structure
- Content focus

### Add LLM API Integration
Update `call_llm_with_prompt()` in `scrape_and_clean.py` to use:
- OpenAI API
- Anthropic Claude
- Local Ollama
- Any other LLM service

## 📚 Documentation

- **INVENTORY.md** - Complete structure and component documentation
- **.github/copilot-instructions.md** - Project context for AI assistants
- **.github/copilot-setup-steps.yaml** - Development environment setup

## 🤝 Contributing

This is a personal knowledge garden template. Fork it, customize it, make it your own!

## 📄 License

MIT License - See LICENSE file for details

---

**Build your own knowledge garden**: Fork this repository and start curating your daily insights!

**Repository**: https://github.com/Grumpified-OGGVCT/idea_vault
