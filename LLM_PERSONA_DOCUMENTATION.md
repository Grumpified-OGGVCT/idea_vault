# LLM Persona System Documentation

## Overview

The AI Net Idea Vault implements a sophisticated multi-persona LLM system that enhances research analysis through specialized AI agents. This document details the architecture, configuration, and usage of the LLM integration.

## Architecture

### System Design

```
User Request
    ↓
Load LLM Personas Config (config/llm_personas.json)
    ↓
Generate Base Report (The Scholar)
    ↓
    ├─→ LLM Available? ─→ Yes ─→ Enhance with Persona
    │                            ↓
    │                       Select Persona (default or specific)
    │                            ↓
    │                       Make LLM API Call
    │                            ↓
    │                       Process Response
    │                            ↓
    └─→ No ─→ Use Fallback ───→ Merge Enhanced Content
                                    ↓
                              Generate Dual Output
                                    ↓
                    ┌───────────────┴───────────────┐
                    ↓                               ↓
        docs/_daily/YYYY-MM-DD-HHMM.md    docs/reports/lab-YYYY-MM-DD.md
              (Jekyll Collection)              (HTML/Markdown)
```

### Graceful Degradation

The system implements graceful degradation at multiple levels:

1. **No LLM Libraries**: Falls back to base Scholar analysis
2. **No API Key**: Skips LLM enhancement, uses existing analysis
3. **API Call Failure**: Retries with exponential backoff, then falls back
4. **Invalid Response**: Validates output, uses base content on failure

## Persona System

### Built-in Personas

#### 1. Technical Analyst

**Purpose**: Deep technical dissection of research papers

**Configuration**:
```json
{
  "name": "Technical Analyst",
  "temperature": 0.3,
  "max_tokens": 2000,
  "focus": "algorithms, architectures, implementation details",
  "output_style": "technical, precise, methodical"
}
```

**Use Cases**:
- Analyzing novel algorithms
- Explaining architectural innovations
- Breaking down mathematical proofs
- Identifying implementation complexity

**Example Output**:
> "The proposed attention mechanism employs O(n log n) complexity through 
> sparse matrix factorization, reducing memory requirements by 60% compared 
> to standard O(n²) implementations..."

#### 2. Strategic Synthesizer (Default)

**Purpose**: Cross-project synthesis and trend identification

**Configuration**:
```json
{
  "name": "Strategic Synthesizer",
  "temperature": 0.7,
  "max_tokens": 2000,
  "focus": "research connections, synthesis opportunities, trend prediction",
  "output_style": "visionary, connective, strategic"
}
```

**Use Cases**:
- Identifying research convergence
- Predicting emerging trends
- Finding synergies between papers
- Strategic technology forecasting

**Example Output**:
> "Today's papers reveal convergence around efficient multimodal architectures. 
> Three independent teams are exploring similar sparse attention patterns, 
> suggesting this will become standard practice within 6-12 months..."

#### 3. Practical Applicator

**Purpose**: Real-world application and implementation guidance

**Configuration**:
```json
{
  "name": "Practical Applicator",
  "temperature": 0.5,
  "max_tokens": 2000,
  "focus": "use cases, implementation roadmaps, ecosystem fit",
  "output_style": "pragmatic, actionable, builder-focused"
}
```

**Use Cases**:
- Translating research to production
- Identifying use cases
- Creating implementation roadmaps
- Assessing ecosystem fit

**Example Output**:
> "This technique can be integrated into existing PyTorch pipelines with 
> minimal refactoring. Expect 2-3 weeks for POC, 6-8 weeks for production. 
> Ideal for teams already using transformers library..."

## Configuration Guide

### Basic Configuration

File: `config/llm_personas.json`

```json
{
  "personas": {
    "persona_name": {
      "name": "Display Name",
      "system_prompt": "You are...",
      "temperature": 0.5,
      "max_tokens": 2000,
      "focus": "key areas",
      "output_style": "style description"
    }
  },
  "default_persona": "strategic_synthesizer",
  "fallback_behavior": "use_existing_analysis",
  "api_settings": {
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 2
  }
}
```

### Temperature Settings

Temperature controls creativity vs. precision:

- **0.0-0.3**: Deterministic, precise, technical
  - Use for: Code analysis, algorithm explanation, technical accuracy
  
- **0.4-0.6**: Balanced, practical
  - Use for: Use case identification, implementation guidance
  
- **0.7-1.0**: Creative, exploratory, connective
  - Use for: Trend prediction, synthesis, strategic insights

### Custom Personas

Create custom personas for specific domains:

```json
{
  "personas": {
    "medical_ai_analyst": {
      "name": "Medical AI Analyst",
      "system_prompt": "You are an expert in medical AI applications, focusing on clinical validation, regulatory compliance, and patient safety...",
      "temperature": 0.2,
      "max_tokens": 2500,
      "focus": "clinical validation, regulatory, safety",
      "output_style": "cautious, evidence-based, clinical"
    }
  }
}
```

## API Integration

### Supported Endpoints

#### OpenAI
```bash
export LLM_ENDPOINT=https://api.openai.com/v1
export LLM_API_KEY=sk-...
export LLM_MODEL=gpt-3.5-turbo
```

#### Azure OpenAI
```bash
export LLM_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/
export LLM_API_KEY=...
export LLM_MODEL=gpt-35-turbo
```

#### Local LLMs (Ollama, LM Studio)
```bash
export LLM_ENDPOINT=http://localhost:11434/v1
export LLM_MODEL=llama2
```

#### Anthropic Claude (via OpenAI compatibility)
```bash
export LLM_ENDPOINT=https://api.anthropic.com/v1
export LLM_API_KEY=sk-ant-...
export LLM_MODEL=claude-3-sonnet
```

### Request Format

```python
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "system",
      "content": persona.get('system_prompt', '')
    },
    {
      "role": "user",
      "content": "Analyze and enhance this research content:\n\n{content}"
    }
  ],
  "temperature": persona.get('temperature', 0.7),
  "max_tokens": persona.get('max_tokens', 2000)
}
```

### Error Handling

```python
try:
    response = client.chat.completions.create(...)
    enhanced = response.choices[0].message.content
    return enhanced
except TimeoutError:
    # Retry with exponential backoff
    retry_with_backoff()
except APIError:
    # Fall back to base content
    return None
except Exception as e:
    # Log and fall back
    log_error(e)
    return None
```

## Quality Validation

### Response Validation

```json
{
  "quality_thresholds": {
    "min_response_length": 100,
    "max_response_length": 3000,
    "required_sections": ["analysis", "implications"]
  }
}
```

The system validates:
1. **Length**: Ensures substantive response
2. **Structure**: Checks for required sections
3. **Coherence**: Basic quality checks
4. **Relevance**: Confirms content relates to input

### Fallback Triggers

LLM enhancement is skipped when:
- Response too short (< min_length)
- Response too long (> max_length)
- Missing required sections
- API timeout exceeded
- Rate limit hit
- Invalid API response format

## Usage Examples

### Example 1: Running with LLM Enhancement

```bash
# Set environment variables
export LLM_API_KEY="your-key-here"
export LLM_MODEL="gpt-3.5-turbo"

# Run generator
python scripts/generate_report.py

# Output:
# 🔬 Starting AI Net Idea Vault report generation...
# ✅ Loaded 3 LLM personas
# 🤖 Attempting LLM enhancement with strategic_synthesizer persona...
# ✅ LLM enhancement applied with strategic_synthesizer
# 💾 Saved Markdown report to docs/reports/lab-2025-11-02.md
# 💾 Saved Jekyll collection post to docs/_daily/2025-11-02-1430-research-intelligence-2025-11-02.md
```

### Example 2: Fallback Mode (No LLM)

```bash
# No API key set
python scripts/generate_report.py

# Output:
# ⚠️  LLM libraries not available - using fallback analysis
# 🔬 Starting AI Net Idea Vault report generation...
# ✅ Loaded 3 LLM personas
# ℹ️  LLM enhancement will be applied to specific sections in future updates
# 💾 Saved Markdown report to docs/reports/lab-2025-11-02.md
```

## Cost Management

### Cost Estimation

| Model | Cost per 1K tokens | Report Cost | Daily Cost (2x) |
|-------|-------------------|-------------|-----------------|
| GPT-3.5 | $0.002 | ~$0.002 | ~$0.004 |
| GPT-4 | $0.03 | ~$0.03 | ~$0.06 |
| GPT-4 Turbo | $0.01 | ~$0.01 | ~$0.02 |
| Claude 3 Sonnet | $0.003 | ~$0.003 | ~$0.006 |
| Local LLM | Free | Free | Free |

### Cost Optimization

1. **Use GPT-3.5** for development and testing
2. **Use GPT-4** only for production enhancement
3. **Set max_tokens** appropriately (don't use 4096 unnecessarily)
4. **Cache responses** for identical inputs
5. **Use local LLMs** for zero-cost operation

## Performance Optimization

### Response Time
- **Average**: 2-5 seconds per LLM call
- **Timeout**: 30 seconds (configurable)
- **Retries**: 3 attempts with exponential backoff

### Caching Strategy
Future implementation:
```python
# Cache LLM responses by content hash
cache_key = hash(content + persona_name)
if cache_key in cache:
    return cache[cache_key]
```

## Monitoring & Debugging

### Debug Logging

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Metrics to Track
- LLM success rate
- Average response time
- Fallback frequency
- API error types
- Token usage

### Health Checks
```bash
# Test LLM connectivity
curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $LLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"test"}]}'
```

## Security Considerations

### API Key Management
- ✅ Store in GitHub Secrets
- ✅ Never commit to repository
- ✅ Use environment variables
- ✅ Rotate keys regularly
- ❌ Never log API keys

### Data Privacy
- All processing on GitHub infrastructure
- Content sent to LLM endpoint only
- No data retention by default (depends on LLM provider)
- Consider data sensitivity when choosing provider

### Rate Limiting
```json
{
  "api_settings": {
    "max_requests_per_minute": 60,
    "max_requests_per_day": 1440
  }
}
```

## Future Enhancements

### Planned Features
1. **Multi-persona ensemble**: Combine insights from multiple personas
2. **Section-specific enhancement**: Apply different personas to different sections
3. **Response caching**: Reduce API calls for similar content
4. **Custom fine-tuning**: Train models on historical reports
5. **Quality scoring**: Rate LLM output quality automatically

### Experimental Features
- Streaming responses for real-time generation
- Multi-language support
- Image analysis integration
- Cross-report synthesis

## Troubleshooting

### Common Issues

**Issue**: "LLM enhancement failed: timeout"
**Solution**: Increase timeout in config or use faster model

**Issue**: "No LLM enhancement - using fallback"
**Solution**: Check API key is set and valid

**Issue**: "Invalid response format"
**Solution**: Verify LLM endpoint compatibility, check model availability

**Issue**: High costs
**Solution**: Switch to GPT-3.5, reduce max_tokens, or use local LLM

## References

- OpenAI API: https://platform.openai.com/docs/
- Anthropic Claude: https://docs.anthropic.com/
- Ollama: https://ollama.ai/
- LM Studio: https://lmstudio.ai/

---

**Last Updated**: 2025-11-02
**Version**: 1.0.0
**Maintainer**: Grumpified
