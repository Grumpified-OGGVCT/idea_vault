# Repository Inventory & Structure

## 1. Top-Level Folder & File Inventory

### Purpose of Each Component

#### Core Directories

**`.github/`**
- **Purpose**: GitHub-specific configurations and automations
- **Contents**: 
  - `workflows/` - GitHub Actions workflow definitions
  - `copilot-instructions.md` - Instructions for GitHub Copilot
  - `copilot-setup-steps.yaml` - Development environment setup
- **Reusable**: Yes, the workflow patterns and Copilot configurations are reusable

**`docs/`**
- **Purpose**: Jekyll-powered static site source files (GitHub Pages)
- **Contents**:
  - `_config.yml` - Jekyll site configuration
  - `_daily/` - Collection of daily report markdown files
  - `_sass/` - Custom stylesheets (dark theme)
  - `assets/` - Images, CSS, JavaScript
  - `reports/` - Legacy report files (to be migrated)
  - `index.html` - Site homepage
- **Reusable**: Yes, the Jekyll structure and dark theme are fully reusable

**`scripts/`**
- **Purpose**: Automation scripts for content generation
- **Contents**:
  - `scrape_and_clean.py` - Web scraper and content processor
  - `author_prompt.txt` - LLM system prompt for content generation
- **Reusable**: Yes, the scraper pattern is adaptable to any URL

**`data/`**
- **Purpose**: Legacy data storage from previous AI research system
- **Contents**: Various research data from arXiv, HuggingFace, etc.
- **Reusable**: Structure is reusable, but content is project-specific

**`reports/`**
- **Purpose**: Legacy reports directory (being phased out)
- **Contents**: Old report files
- **Reusable**: No, this is legacy and will be removed

#### Documentation Files

**`README.md`**
- **Purpose**: Project overview and quick start guide
- **Reusable**: Template structure is reusable

**`LICENSE`**
- **Purpose**: MIT License for the project
- **Reusable**: Yes, standard MIT license

**`DEPLOYMENT_GUIDE.md`**
- **Purpose**: Deployment instructions for the previous system
- **Reusable**: Partially, GitHub Pages setup steps apply

**`THE_LAB_DESIGN_DOCUMENT.md`**
- **Purpose**: Original design document for copyright and content moderation
- **Reusable**: Partially, as guidelines for ethical content handling

**`TESTING_COMPLETE.md`**
- **Purpose**: Testing documentation for previous system
- **Reusable**: No, specific to old system

**`TRANSFORMATION_SUMMARY.md`**
- **Purpose**: Documentation of previous transformations
- **Reusable**: No, historical record

**`WORKFLOW_SCHEDULE_CHANGES.md`**
- **Purpose**: Documentation of workflow schedule changes
- **Reusable**: No, historical record

#### Configuration Files

**`requirements.txt`**
- **Purpose**: Python dependencies (legacy)
- **Reusable**: No, replaced by direct installation in workflow

**`.gitignore`**
- **Purpose**: Git ignore patterns
- **Reusable**: Yes, comprehensive Python/Node/Jekyll patterns

---

## 2. New Target Layout

```
idea_vault/
├── .github/
│   ├── workflows/
│   │   └── daily-report.yml          # Runs 2x daily (08:00 & 20:00 UTC)
│   ├── copilot-instructions.md       # Copilot project context
│   └── copilot-setup-steps.yaml      # Dev environment setup
│
├── docs/                              # Jekyll site source (GitHub Pages)
│   ├── _config.yml                    # Jekyll config with dark theme
│   ├── _daily/                        # Daily reports collection
│   │   ├── .gitkeep
│   │   └── YYYY-MM-DD-HHMM-daily-report.md
│   ├── _sass/
│   │   └── custom.scss                # Dark mode stylesheet
│   ├── assets/
│   │   └── (images, css, js)
│   └── index.html                     # Homepage
│
├── scripts/
│   ├── scrape_and_clean.py            # Single scraper script
│   └── author_prompt.txt              # LLM system prompt
│
├── .gitignore                         # Git ignore patterns
├── LICENSE                            # MIT License
└── README.md                          # Project documentation
```

### Component Descriptions

#### `.github/workflows/daily-report.yml`
- **Trigger**: Scheduled at 08:00 UTC and 20:00 UTC daily, plus manual dispatch
- **Actions**:
  1. Checkout repository
  2. Set up Node.js 20 and Python
  3. Install dependencies (httpx, beautifulsoup4)
  4. Run `scrape_and_clean.py` with SOURCE_URL environment variable
  5. Commit new files in `docs/_daily/`
  6. Trigger GitHub Pages deployment
- **Permissions**: Requires `contents: write` and `pages: write`

#### `docs/_config.yml`
- **Theme**: Minima with dark skin
- **Collections**: Defines `_daily` collection with post layout
- **Output**: Generates URLs like `/daily/YYYY/MM/DD/title/`
- **Plugins**: Jekyll-feed and Jekyll-SEO-tag

#### `docs/_sass/custom.scss`
- **Purpose**: Override Minima theme defaults
- **Color Scheme**: GitHub-inspired dark palette
  - Background: `#0d1117` (primary), `#161b22` (secondary)
  - Text: `#c9d1d9` (primary), `#8b949e` (secondary)
  - Accent: `#58a6ff` (primary), `#1f6feb` (secondary)
- **Scope**: Global styles, headers, links, code blocks, tables

#### `docs/_daily/`
- **Purpose**: Collection directory for daily reports
- **Files**: Timestamped markdown files with YAML frontmatter
- **Naming**: `YYYY-MM-DD-HHMM-daily-report.md`
- **Layout**: Uses `post` layout from Jekyll

#### `scripts/scrape_and_clean.py`
- **Input**: SOURCE_URL environment variable
- **Process**:
  1. Fetch content from URL using httpx
  2. Parse HTML with BeautifulSoup
  3. Strip navigation, scripts, styles
  4. Extract main content
  5. Process with LLM using author prompt
  6. Write timestamped markdown to `docs/_daily/`
- **Output**: Success message with file path

#### `scripts/author_prompt.txt`
- **Purpose**: System prompt for LLM
- **Content**: Instructions to create witty, structured daily reports
- **Style**: Conversational yet professional, with emojis
- **Format**: Markdown with sections, bullets, emphasis

#### `.github/copilot-instructions.md`
- **Purpose**: Provide project context to GitHub Copilot
- **Content**: 
  - Vision: Personal knowledge garden with automated curation
  - Required artifacts: Jekyll site, workflow, scraper
  - Guidance: Focus on simplicity, dark theme, automation

#### `.github/copilot-setup-steps.yaml`
- **Purpose**: Configure development environment
- **Steps**:
  1. Install Node.js 20
  2. Install Ruby + Jekyll
  3. Install Python dependencies (httpx, beautifulsoup4)
  4. Verify installation
  5. Test Jekyll build
  6. Test scraper script

---

## 3. What's Reusable for Public Idea Vault

### Fully Reusable Components ✅

1. **Jekyll Structure** (`docs/` directory)
   - Dark theme configuration
   - `_daily` collection setup
   - Custom SCSS for consistent branding

2. **Scraper Architecture** (`scripts/scrape_and_clean.py`)
   - URL fetching and HTML cleaning
   - LLM integration pattern
   - Timestamped file generation

3. **Automation Workflow** (`.github/workflows/daily-report.yml`)
   - Scheduled execution (2x daily)
   - Dependency installation
   - Automatic commits and deployments

4. **Copilot Integration** (`.github/copilot-*.md/yaml`)
   - Project context system
   - Development environment setup

### Partially Reusable Components ⚠️

1. **Author Prompt** (`scripts/author_prompt.txt`)
   - Reusable structure, customizable content
   - Adapt tone and style for different use cases

2. **Configuration Files** (`.gitignore`, `_config.yml`)
   - Base structure is reusable
   - Customize titles, descriptions, URLs

### Not Reusable (Legacy) ❌

1. **Data Directory** - Project-specific research data
2. **Old Reports** - Historical content
3. **Legacy Documentation** - Specific to previous system

---

## Summary

The new Idea Vault structure is **lean, automated, and elegant**:
- Single workflow running twice daily
- Single scraper script with LLM integration
- Jekyll-powered dark theme site
- Fully automated commits and deployments
- Zero maintenance required

This architecture is **highly reusable** for anyone wanting to:
- Create a personal knowledge garden
- Automate content curation from web sources
- Publish beautiful daily insights via GitHub Pages
- Integrate LLM-powered content processing
