# AI Net Idea Vault - Deployment Guide

## Overview

This guide covers deploying the AI Net Idea Vault with optional LLM enhancement and dual-output publishing.

## Prerequisites

- GitHub account with repository access
- GitHub Pages enabled
- (Optional) OpenAI-compatible LLM API access

## Deployment Steps

### 1. Repository Setup

#### Fork or Clone
```bash
git clone https://github.com/Grumpified-OGGVCT/idea_vault.git
cd idea_vault
```

#### Verify Directory Structure
```bash
ls -la config/
ls -la docs/_daily/
ls -la docs/reports/
```

### 2. Configure GitHub Actions

#### Enable Workflows
1. Go to **Settings** → **Actions** → **General**
2. Under **Workflow permissions**, select:
   - ✅ **Read and write permissions**
   - ✅ **Allow GitHub Actions to create and approve pull requests**

#### Configure Secrets (Optional - For LLM Enhancement & NOSTR Publishing)

Go to **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add the following secrets:

| Secret Name | Description | Required |
|------------|-------------|----------|
| `OLLAMA_API_KEY` | Your Ollama Cloud API key (priority LLM backend) | Optional |
| `OLLAMA_ENDPOINT` | Ollama API endpoint (default: `https://api.ollama.ai`) | Optional |
| `LLM_API_KEY` | Your OpenAI or compatible LLM API key (fallback) | Optional |
| `LLM_ENDPOINT` | Custom LLM endpoint (e.g., `https://api.openai.com/v1`) | Optional |
| `LLM_MODEL` | Model name (e.g., `gpt-3.5-turbo`, `gpt-4`) | Optional |
| `NOSTR_PRIVATE_KEY` | Your NOSTR private key in hex format for publishing | Optional |
| `SOURCE_URL` | Custom data source URL if needed | Optional |

**Note**: 
- If secrets are not configured, the system will use fallback analysis without LLM enhancement.
- NOSTR publishing will be gracefully skipped if `NOSTR_PRIVATE_KEY` is not set.
- Ollama Turbo Cloud is prioritized for LLM enhancement; falls back to OpenAI-compatible endpoint if unavailable.

### 3. Enable GitHub Pages

1. Go to **Settings** → **Pages**
2. Under **Source**, select:
   - Branch: `main`
   - Folder: `/docs`
3. Click **Save**
4. Wait for deployment (usually 1-2 minutes)
5. Visit your site at `https://[username].github.io/idea_vault/`

### 4. Verify Jekyll Configuration

The `docs/_config.yml` should include:

```yaml
collections:
  daily:
    output: true
    permalink: /daily/:year/:month/:day/:title/
```

This enables the `_daily` collection for timestamped posts.

### 5. Test Workflow Execution

#### Manual Trigger
1. Go to **Actions** tab
2. Select "AI Net Idea Vault - Daily Research Report"
3. Click **Run workflow** → **Run workflow**
4. Monitor the workflow execution

#### Verify Output
After successful run, check:
```bash
# Markdown in Jekyll collection
ls docs/_daily/YYYY-MM-DD-HHMM-*.md

# HTML reports (backward compatible)
ls docs/reports/lab-YYYY-MM-DD.md

# Index page updated
cat docs/index.html
```

### 6. Schedule Configuration

The workflow runs automatically at:
- **08:00 UTC** (morning report)
- **20:00 UTC** (evening report)

To modify schedule, edit `.github/workflows/daily_report.yml`:

```yaml
on:
  schedule:
    - cron: '0 8 * * *'    # 08:00 UTC
    - cron: '0 20 * * *'   # 20:00 UTC
```

## LLM Configuration

### Persona System

Edit `config/llm_personas.json` to customize LLM behavior:

```json
{
  "personas": {
    "technical_analyst": {
      "temperature": 0.3,
      "max_tokens": 2000,
      "focus": "algorithms, architectures"
    },
    "strategic_synthesizer": {
      "temperature": 0.7,
      "max_tokens": 2000,
      "focus": "patterns, trends"
    }
  },
  "default_persona": "strategic_synthesizer"
}
```

### API Endpoints

#### OpenAI
```bash
LLM_ENDPOINT=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
```

#### Azure OpenAI
```bash
LLM_ENDPOINT=https://[your-resource].openai.azure.com/
LLM_MODEL=gpt-35-turbo
```

#### Local LLMs (Ollama, etc.)
```bash
LLM_ENDPOINT=http://localhost:11434/v1
LLM_MODEL=llama2
```

#### Ollama Turbo Cloud (Recommended)
```bash
OLLAMA_API_KEY=your-ollama-api-key-here
OLLAMA_ENDPOINT=https://api.ollama.ai
```

**Available Models**:
- `deepseek-v3.1:671b-cloud` - Reasoning and analysis (default)
- `qwen3-vl:235b-cloud` - Vision and multimodal tasks
- `qwen3-coder:30b-cloud` - Creative and coding tasks
- `nomic-embed-text` - Text embeddings

### NOSTR Configuration

#### Generate NOSTR Keys

**Option 1: Using `nak` (recommended)**:
```bash
# Install nak
go install github.com/fiatjaf/nak@latest

# Generate new key pair
nak key generate

# Output will show:
# Private key (nsec): nsec1...
# Public key (npub): npub1...

# Convert nsec to hex for GitHub secret
nak key decode nsec1...
```

**Option 2: Using Python**:
```python
from pynostr.key import PrivateKey

# Generate new key
private_key = PrivateKey()
print(f"Private key (hex): {private_key.hex()}")
print(f"Public key (hex): {private_key.public_key.hex()}")
```

#### Configure NOSTR Secret

1. Generate or retrieve your NOSTR private key in **hex format**
2. Add as `NOSTR_PRIVATE_KEY` secret in GitHub repository settings
3. Publishing will automatically occur after each report generation

**Default Relay List** (48+ relays):
- wss://relay.damus.io
- wss://relay.nostr.band
- wss://nostr.wine
- wss://relay.snort.social
- ... and 44 more (see `scripts/publish_nostr.py`)

#### Verify NOSTR Publishing

After a report is generated:
1. Check workflow logs for "NOSTR publishing" step
2. Look for event ID in logs
3. View publication record in `data/nostr_publications/YYYY-MM-DD.json`
4. Search for your public key on NOSTR clients (e.g., Damus, Snort, Iris)

### Ollama Data Sources

The system now ingests from multiple Ollama-related sources:

1. **Official Sources** (`ingest_official.py`):
   - Ollama blog RSS feed
   - /cloud page for model updates

2. **Cloud Models** (`ingest_cloud.py`):
   - Ollama Cloud API tags
   - Turbo-optimized models

3. **Community** (`ingest_community.py`):
   - Reddit r/ollama
   - YouTube Ollama tutorials
   - Community newsletters
   - Hacker News mentions

4. **Tools & Integrations** (`ingest_tools.py`):
   - GitHub repos with 'ollama' topic
   - n8n marketplace integrations

5. **Issues & PRs** (`ingest_issues.py`):
   - GitHub issues mentioning Ollama
   - Pull requests for Ollama integrations

All sources are aggregated and scored for relevance.

## Monitoring & Troubleshooting

### Check Workflow Logs
1. **Actions** tab → Select latest run
2. Expand "Generate research intelligence report"
3. Look for:
   - ✅ LLM enhancement success messages
   - ⚠️ Fallback warnings (if LLM unavailable)
   - 💾 Dual output confirmation

### Common Issues

#### Ollama Enhancement Not Working
**Symptom**: Report generated but no Ollama LLM enhancement
**Solution**:
1. Verify `OLLAMA_API_KEY` secret is set
2. Check Ollama API endpoint is accessible (https://api.ollama.ai)
3. Review workflow logs for error messages
4. System will gracefully fall back to OpenAI-compatible endpoint or non-LLM analysis

#### NOSTR Publishing Fails
**Symptom**: Report generated but not published to NOSTR
**Solution**:
1. Verify `NOSTR_PRIVATE_KEY` is set in hex format (not nsec)
2. Check if `pynostr` library is installed: `pip install pynostr`
3. Review workflow logs for NOSTR connection errors
4. Publishing gracefully skips if key not configured (not a critical error)

#### Ollama Data Sources Not Appearing
**Symptom**: Only arXiv/HuggingFace data in reports
**Solution**:
1. Verify Ollama ingestion scripts ran: check workflow logs
2. Check data directories: `data/official/`, `data/cloud/`, etc.
3. Review aggregate.py logs for source counts
4. Ensure ingest.yml workflow includes all Ollama scripts

#### LLM Enhancement Not Working
**Symptom**: Report generated but no LLM enhancement
**Solution**:
1. Verify `LLM_API_KEY` secret is set
2. Check API endpoint is accessible
3. Review workflow logs for error messages
4. System will gracefully fall back to non-LLM analysis

#### Jekyll Collection Not Rendering
**Symptom**: `_daily` posts not appearing on site
**Solution**:
1. Verify `docs/_config.yml` has collections configuration
2. Check frontmatter format in generated files
3. Ensure GitHub Pages is rebuilding (check Pages deployment)
4. May take 1-2 minutes for Pages to update

#### Dual Output Missing
**Symptom**: Only one output type generated
**Solution**:
1. Check `scripts/generate_report.py` execution
2. Verify both directories exist: `docs/_daily/` and `docs/reports/`
3. Check file permissions
4. Review workflow logs

### Debug Mode

Run locally with debug output:
```bash
# Test without LLM
python scripts/generate_report.py

# Test with LLM (requires env vars)
export LLM_API_KEY="your-key-here"
export LLM_MODEL="gpt-3.5-turbo"
python scripts/generate_report.py
```

## Performance Optimization

### Workflow Efficiency
- Runs complete in ~2-5 minutes
- Uses pip cache for faster dependency installation
- Graceful timeout handling for LLM calls (30 seconds)

### Cost Management
- **Without LLM**: 100% free (GitHub Actions free tier)
- **With LLM**: 
  - OpenAI GPT-3.5: ~$0.002 per report
  - GPT-4: ~$0.03 per report
  - Twice daily = ~$0.004-$0.06 per day

### Rate Limiting
Configure in `config/llm_personas.json`:
```json
{
  "api_settings": {
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 2
  }
}
```

## Backup & Recovery

### Backup Strategy
```bash
# Backup configuration
cp config/llm_personas.json config/llm_personas.json.backup

# Backup Jekyll config
cp docs/_config.yml docs/_config.yml.backup

# Backup workflow
cp .github/workflows/daily_report.yml .github/workflows/daily_report.yml.backup
```

### Recovery
If something breaks:
1. Check git history: `git log --oneline`
2. Revert to last working commit: `git revert <commit-hash>`
3. Restore from backup branch if created
4. System will continue with fallback analysis

## Maintenance

### Update Dependencies
```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Update Node packages (if using)
npm update
```

### Update LLM Models
Edit secrets in GitHub:
1. **Settings** → **Secrets**
2. Update `LLM_MODEL` to newer version
3. Next workflow run will use new model

### Monitor GitHub Pages Build
1. **Settings** → **Pages**
2. Check latest deployment status
3. View deployment logs if issues occur

## Advanced Configuration

### Custom Themes
Edit `docs/assets/css/style.scss`:
```scss
// Change crimson accent color
$crimson: #DC143C;  // Default

// Change to your preferred color
$crimson: #YOUR_COLOR;
```

### Custom Scheduling
Add additional schedules in workflow:
```yaml
on:
  schedule:
    - cron: '0 8 * * *'   # Morning
    - cron: '0 20 * * *'  # Evening
    - cron: '0 14 * * *'  # Add afternoon run
```

## Security Best Practices

1. **Never commit secrets** to repository
2. **Use GitHub Secrets** for all API keys
3. **Review workflow permissions** regularly
4. **Monitor API usage** to prevent abuse
5. **Keep dependencies updated** for security patches
6. **Enable Dependabot** for automated updates

## Support & Resources

- **Repository Issues**: https://github.com/Grumpified-OGGVCT/idea_vault/issues
- **GitHub Actions Docs**: https://docs.github.com/actions
- **Jekyll Docs**: https://jekyllrb.com/docs/
- **OpenAI API**: https://platform.openai.com/docs/

## Rollback Plan

If the refactor causes issues:

1. **Immediate Rollback**:
   ```bash
   git revert HEAD
   git push
   ```

2. **Restore Previous Version**:
   ```bash
   git log --oneline  # Find previous working commit
   git reset --hard <commit-hash>
   git push --force  # Use with caution
   ```

3. **Preserve Data**:
   - Existing reports in `docs/reports/` are preserved
   - New `_daily` collection is additive
   - No data loss in rollback

## Success Criteria

✅ **Deployment Successful When**:
- GitHub Pages site accessible
- Workflow runs without errors
- Dual output generated (both `_daily/` and `reports/`)
- LLM enhancement working (if configured) OR gracefully falling back
- Existing reports still accessible
- Crimson theme preserved
- Mobile responsive

---

**Last Updated**: 2025-11-02
**Version**: 1.0.0
**Status**: Production Ready
