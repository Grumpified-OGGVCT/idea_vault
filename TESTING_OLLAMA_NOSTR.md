# Testing Guide: Ollama Turbo/Cloud and NOSTR Integration

This guide covers testing the restored Ollama Turbo/Cloud services and NOSTR publishing functionality.

## Prerequisites

- Repository cloned locally
- Python 3.11+ installed
- Required dependencies installed: `pip install -r requirements.txt`
- (Optional) Ollama Cloud API key
- (Optional) NOSTR private key in hex format

## Test 1: Ollama Data Ingestion

### Test Ollama Official Sources

```bash
# Test blog RSS and /cloud page ingestion
python scripts/ingest_official.py
```

**Expected Output**:
```
🚀 Starting official sources ingestion...
📡 Fetching Ollama blog RSS...
✅ Found X blog posts
📡 Fetching Ollama /cloud page...
✅ Found X cloud models
💾 Saved X entries to data/official/YYYY-MM-DD.json
✅ Official sources ingestion complete!
```

**Verify**:
```bash
ls -la data/official/
cat data/official/$(date +%Y-%m-%d).json | jq '.[0]'
```

### Test Ollama Cloud Models

```bash
python scripts/ingest_cloud.py
```

**Expected Output**:
```
🚀 Starting Ollama Cloud ingestion...
📡 Fetching Ollama tags...
✅ Found X cloud models
💾 Saved X entries to data/cloud/YYYY-MM-DD.json
✅ Ollama Cloud ingestion complete!
```

### Test Community Sources

```bash
python scripts/ingest_community.py
```

**Expected Output**:
```
🚀 Starting community ingestion...
📡 Fetching Reddit r/ollama...
✅ Found X Reddit posts
📡 Fetching YouTube...
...
✅ Community ingestion complete!
```

### Test Tools & GitHub

```bash
python scripts/ingest_tools.py
```

**Expected Output**:
```
🚀 Starting tools & integrations ingestion...
📡 Fetching GitHub repos with 'ollama' topic...
✅ Found X GitHub repos
💾 Saved X entries to data/tools/YYYY-MM-DD.json
✅ Tools & integrations ingestion complete!
```

### Test GitHub Issues

```bash
python scripts/ingest_issues.py
```

**Expected Output**:
```
🚀 Starting GitHub issues/PRs ingestion...
📡 Searching GitHub issues: 'ollama turbo cloud'...
✅ Found X GitHub issues/PRs
💾 Saved X entries to data/community/YYYY-MM-DD.json
✅ GitHub issues/PRs ingestion complete!
```

## Test 2: Data Aggregation with Ollama Sources

```bash
# First run all ingestors (or at least the research ones)
python scripts/ingest_arxiv.py
python scripts/ingest_huggingface.py
python scripts/ingest_paperswithcode.py

# Then aggregate
python scripts/aggregate.py
```

**Expected Output**:
```
🚀 Starting data aggregation...
🔄 Aggregating data from research sources...
  📚 arXiv: X entries
  🤗 HuggingFace: X entries
  📊 Papers with Code: X entries
  📡 Ollama Official: X entries
  ☁️  Ollama Cloud: X entries
  👥 Community: X entries
  🔧 Tools: X entries
🎯 Applying research relevance filtering...
✅ Aggregated X high-relevance entries (from X total)
💾 Saved aggregated data to data/aggregated/YYYY-MM-DD.json
📊 Saved yield metrics to data/insights/YYYY-MM-DD_yield.json
✅ Data aggregation complete!
```

**Verify**:
```bash
# Check that Ollama sources are included
cat data/aggregated/$(date +%Y-%m-%d).json | jq '[.[] | select(.source | contains("ollama") or contains("official") or contains("cloud"))] | length'
```

## Test 3: Ollama Turbo Client

### Test Standalone Client

```bash
python3 << 'EOF'
import asyncio
import os
from scripts.ollama_turbo_client import OllamaTurboClient, MODELS

async def test_ollama():
    # Note: This requires OLLAMA_API_KEY environment variable
    api_key = os.getenv('OLLAMA_API_KEY', 'test-key')
    
    async with OllamaTurboClient(api_key=api_key) as client:
        try:
            response = await client.generate(
                model=MODELS['reasoning'],
                prompt="What is AI research?",
                max_tokens=100,
                temperature=0.7
            )
            print(f"✅ Ollama Turbo Client working!")
            print(f"Response: {response[:200]}...")
        except Exception as e:
            print(f"⚠️  Ollama API call failed (expected without valid key): {e}")

asyncio.run(test_ollama())
EOF
```

**Expected Output** (without API key):
```
⚠️  Ollama API call failed (expected without valid key): ...
```

**Expected Output** (with valid API key):
```
✅ Ollama Turbo Client working!
Response: AI research is the scientific study of...
```

## Test 4: LLM-Enhanced Report Generation

### Test with Ollama (requires OLLAMA_API_KEY)

```bash
export OLLAMA_API_KEY="your-ollama-api-key"
export OLLAMA_ENDPOINT="https://api.ollama.ai"
python scripts/generate_report.py
```

**Expected Output**:
```
🔬 Starting AI Net Idea Vault report generation...
📚 The Scholar persona with optional LLM enhancement
✅ Loaded 3 LLM personas
...
✅ Ollama enhancement applied with strategic_synthesizer using deepseek-v3.1:671b-cloud
...
💾 Saved Markdown report to docs/reports/lab-YYYY-MM-DD.md
💾 Saved Jekyll collection post to docs/_daily/...
💾 Updated index.html
✅ Report generation complete!
```

### Test with Fallback (no Ollama key)

```bash
unset OLLAMA_API_KEY
export LLM_API_KEY="sk-test"  # Or leave unset for no LLM
python scripts/generate_report.py
```

**Expected Output**:
```
⚠️  OLLAMA_API_KEY not set - skipping Ollama enhancement
⚠️  LLM_API_KEY not set - skipping LLM enhancement
...
✅ Report generation complete!
```

### Verify Report Generation

```bash
# Check that report was created
ls -la docs/reports/lab-$(date +%Y-%m-%d).md
ls -la docs/_daily/*.md | tail -1

# View report
head -50 docs/reports/lab-$(date +%Y-%m-%d).md
```

## Test 5: NOSTR Publishing

### Generate Test NOSTR Keys

```bash
python3 << 'EOF'
from pynostr.key import PrivateKey

private_key = PrivateKey()
print(f"Private key (hex): {private_key.hex()}")
print(f"Public key (hex): {private_key.public_key.hex()}")
print(f"\nSave the private key as NOSTR_PRIVATE_KEY secret")
EOF
```

### Test NOSTR Publishing

```bash
# Set your NOSTR private key (hex format)
export NOSTR_PRIVATE_KEY="your-private-key-hex"

# Run publisher
python scripts/publish_nostr.py
```

**Expected Output**:
```
🚀 Starting NOSTR publishing...
📄 Loading report: lab-YYYY-MM-DD.md
📡 NOSTR Publisher initialized
   Public Key: abcdef123456...
   Relays: 48
🔗 Connecting to 48 NOSTR relays...
✅ Connected to X relays
📝 Publishing report: 📚 The Lab – YYYY-MM-DD
✅ Report published to NOSTR network
   Event ID: 1234567890abcdef...
   Kind: 30023 (NIP-23 long-form)
   Relays: 48
💾 Publication record saved to data/nostr_publications/YYYY-MM-DD.json
🔌 Closed NOSTR relay connections
✅ NOSTR publishing complete!
```

### Verify NOSTR Publication

```bash
# Check publication record
cat data/nostr_publications/$(date +%Y-%m-%d).json | jq '.'
```

**Expected Output**:
```json
{
  "event_id": "abc123...",
  "public_key": "def456...",
  "kind": 30023,
  "title": "📚 The Lab – 2025-11-02",
  "relays": 48,
  "published_at": "2025-11-02T20:30:00.123456"
}
```

### Verify on NOSTR Network

1. Copy your public key from the output
2. Visit NOSTR clients:
   - https://snort.social
   - https://iris.to
   - https://damus.io (iOS)
3. Search for your public key
4. Look for your published report (kind 30023)

## Test 6: Complete Workflow

### Test Full Pipeline Locally

```bash
# Set environment variables (optional)
export OLLAMA_API_KEY="your-key"
export NOSTR_PRIVATE_KEY="your-hex-key"

# Run complete pipeline
python scripts/ingest_arxiv.py
python scripts/ingest_huggingface.py
python scripts/ingest_paperswithcode.py
python scripts/ingest_official.py
python scripts/ingest_cloud.py
python scripts/ingest_community.py
python scripts/ingest_tools.py
python scripts/ingest_issues.py
python scripts/aggregate.py
python scripts/mine_insights.py
python scripts/generate_report.py
python scripts/generate_report_index.py
python scripts/publish_nostr.py
```

### Verify Complete Output

```bash
# Check all data directories
echo "=== Data Files ==="
find data -name "$(date +%Y-%m-%d)*" -type f

# Check reports
echo "=== Reports ==="
ls -la docs/reports/lab-$(date +%Y-%m-%d).md
ls -la docs/_daily/*$(date +%Y-%m-%d)*.md

# Check NOSTR publication
echo "=== NOSTR Publication ==="
cat data/nostr_publications/$(date +%Y-%m-%d).json | jq '.'
```

## Test 7: GitHub Actions Integration

### Manual Workflow Trigger

1. Go to repository → Actions
2. Select "The Lab Research Ingestion"
3. Click "Run workflow"
4. Wait for completion
5. Check workflow logs:
   - ✅ Ollama ingestion scripts ran
   - ✅ Data aggregated with Ollama sources
   - ✅ Counts shown for each source

### Daily Report Workflow

1. Go to repository → Actions
2. Select "AI Net Idea Vault - Daily Research Report"
3. Click "Run workflow"
4. Wait for completion
5. Check workflow logs:
   - ✅ Report generated
   - ✅ NOSTR publishing attempted
   - ✅ Reports committed and pushed

### Verify Secrets

1. Go to Settings → Secrets and variables → Actions
2. Verify these secrets exist:
   - `OLLAMA_API_KEY` ✅
   - `NOSTR_PRIVATE_KEY` ✅
   - `LLM_API_KEY` (optional)
   - `LLM_ENDPOINT` (optional)

## Troubleshooting

### Ollama Ingestion Issues

**Problem**: No Ollama data in aggregated files

**Solution**:
```bash
# Check individual source files
ls -la data/official/
ls -la data/cloud/
ls -la data/community/
ls -la data/tools/

# Run ingestion scripts manually with debug
python -u scripts/ingest_official.py 2>&1 | tee /tmp/ingest_official.log
cat /tmp/ingest_official.log
```

### NOSTR Publishing Issues

**Problem**: Publishing fails or times out

**Solution**:
```bash
# Test with fewer relays first
python3 << 'EOF'
import os
os.environ['NOSTR_PRIVATE_KEY'] = 'your-key-hex'

# Modify scripts/publish_nostr.py temporarily to use only 3 relays
# DEFAULT_RELAYS = [
#     "wss://relay.damus.io",
#     "wss://relay.nostr.band",
#     "wss://nostr.wine",
# ]

import asyncio
import sys
sys.path.insert(0, 'scripts')
from publish_nostr import main
main()
EOF
```

### LLM Enhancement Not Working

**Problem**: No LLM enhancement in reports

**Solution**:
```bash
# Check which LLM backend is being used
python3 << 'EOF'
import os
print(f"OLLAMA_API_KEY: {'SET' if os.getenv('OLLAMA_API_KEY') else 'NOT SET'}")
print(f"LLM_API_KEY: {'SET' if os.getenv('LLM_API_KEY') else 'NOT SET'}")
EOF

# Test LLM connectivity
export OLLAMA_API_KEY="your-key"
python3 -c "from scripts.ollama_turbo_client import OllamaTurboClient; print('✅ Ollama client imported')"
```

## Success Criteria

All tests pass when:
- ✅ Ollama ingestion scripts run without errors
- ✅ Data from all 5 Ollama sources appears in aggregated data
- ✅ Ollama Turbo Client can be initialized
- ✅ Reports are generated with/without LLM enhancement
- ✅ NOSTR publishing creates event and publication record
- ✅ GitHub Actions workflows complete successfully
- ✅ Reports visible on GitHub Pages
- ✅ NOSTR events visible on NOSTR network

## Next Steps

After successful testing:
1. Set production secrets in GitHub repository
2. Enable scheduled workflows
3. Monitor first automated runs
4. Verify NOSTR events appear on network
5. Check report quality with Ollama enhancement
