# Idea Vault - GitHub Copilot Instructions

## Project Vision

The Idea Vault is a personal knowledge garden that automatically curates, processes, and publishes daily insights from the web. It transforms raw content into beautifully formatted, easily digestible reports that are published through GitHub Pages. Think of it as your automated research assistant that never sleeps—continuously gathering interesting content, processing it with intelligence, and presenting it in a clean, dark-themed Jekyll site.

This project embodies the philosophy that knowledge should be both accessible and aesthetically pleasing. By automating the collection and formatting process, it allows you to focus on what matters: consuming and acting on insights rather than spending time on manual curation.

## Required Artifacts

When working on this project, keep these core components in focus:

1. **Jekyll Site** (`docs/`): A dark-themed static site with a `_daily` collection for timestamped reports
2. **Daily Report Workflow** (`.github/workflows/daily-report.yml`): Automated scraping and publishing that runs twice daily (08:00 and 20:00 UTC)
3. **Markdown Collection** (`docs/_daily/`): Auto-generated markdown files containing processed daily insights
4. **Python Scraper** (`scripts/scrape_and_clean.py`): Fetches content, strips HTML, and processes with LLM prompts
5. **Author Prompt** (`scripts/author_prompt.txt`): System prompt that guides the LLM to create engaging, witty daily reports

## Guidance for Copilot Suggestions

When providing code suggestions, completions, or assistance:

- **Focus on simplicity**: Prefer straightforward solutions that work reliably in GitHub Actions
- **Maintain the dark theme**: All UI/UX suggestions should respect the dark color palette
- **Preserve automation**: Don't suggest manual steps for things that should be automated
- **Think in markdown**: Remember this is a Jekyll-powered static site—content is king
- **Keep it minimal**: Avoid adding unnecessary dependencies or complexity
- **Respect the structure**: The `docs/` folder is the Jekyll site source, `scripts/` contains automation
- **GitHub Actions first**: Solutions should work in the GitHub Actions environment without local setup

When I'm working on the scraper, help me make it robust and handle errors gracefully. When I'm working on the Jekyll theme, help me maintain visual consistency. When I'm working on workflows, help me ensure they're efficient and reliable.

This is a personal project meant to be elegant, automated, and maintenance-free. Keep suggestions aligned with that vision.
