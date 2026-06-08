# API Resilience for Batch Vault Enrichment

Session: 2026-05-27  
Context: YouTube vault enrichment (`03-Knowledge/YouTube/`) using LLM APIs for metadata backfill (context, enrichment_tier, vault_connections).  
Script: `~/claude-projects/scripts/yt_enrich_deepseek_runner.py`

## Provider Test Results (May 2026)

| Provider | Model | Status | Notes |
|----------|-------|--------|-------|
| Nous Research | `deepseek/deepseek-v4-flash:free` | **DEGRADED** | Single requests succeed; batch requests return 401/timeout. Effectively unusable for batch enrichment. |
| Nous Research | `qwen/qwen3.6-flash` | **DEGRADED** | Same API infra; timeouts on chat completions. |
| Google AI Studio | `gemini-2.0-flash` | **QUOTA EXHAUSTED** | 429 `generative_content_free_tier_requests` limit: 0. |
| Cerebras | `qwen-3-235b-a22b-instruct-2507` | **WORKING** | Fast, reliable JSON output. Available via `CEREBRAS_API_KEY`. |
| Cerebras | `gpt-oss-120b` | Available | Not tested this session. |

## Reasoning-Model JSON Null-Content Bug

DeepSeek V4 Flash (and similar reasoning-first models) may return:

```json
{
  "choices": [{
    "message": {
      "content": null,
      "reasoning": "Okay, the user wants JSON with keys..."
    }
  }]
}
```

The `content` field is `null` because the model consumed all output tokens in reasoning.  
**Fix**: Fall back to `msg.get('reasoning', '')` when `content` is `None`, then attempt JSON parse from the reasoning text. The reasoning text often still contains the final JSON block.

```python
raw = msg.get('content')
if raw is None:
    raw = msg.get('reasoning', '')
    if not raw:
        return False, "model returned None content and no reasoning"
parsed = json.loads(raw)  # may still succeed
```

## Retry Logic for Flaky Inference APIs

Added to `yt_enrich_deepseek_runner.py` (2026-05-27):

- **3 attempts** with exponential backoff (`sleep(2 ** attempt)`)
- **Retry on HTTP codes**: 401, 429, 502, 503, 504 (transient auth/rate-limit/server errors)
- **Retry on null content + no reasoning**: model failed to produce output
- **Retry on non-dict parse result**: likely garbled output
- **Do NOT retry** on other 4xx errors (e.g., 400 bad request)

```python
for attempt in range(1, 4):
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        resp.raise_for_status()
        # ... parse content / reasoning ...
    except requests.exceptions.HTTPError as e:
        if e.response.status_code in (401, 429, 502, 503, 504):
            time.sleep(2 ** attempt)
            continue
        return False, str(e)
    except Exception as e:
        time.sleep(2 ** attempt)
        continue
return False, last_err
```

## Script Path Discrepancy

Cron job referenced:
- `~/.hermes/profiles/beau/scripts/yt_enrich_deepseek_runner.sh` — **does not exist**
- Actual runner: `~/claude-projects/scripts/yt_enrich_deepseek_runner.py`

If a cron wrapper shell script is needed, create it at the expected path or update the cron command to invoke the Python script directly.

## Canonical Log File

Enrichment runs append to:
`~/claude-projects/claude-vault/10-Meta/yt-enrichment-deepseek-run.jsonl`

Each line is JSON:
```json
{"timestamp": "2026-05-27T01:00:00", "path": "...", "ok": true|false, "msg": "...", "missing": ["context"]}
```

## Model Substitution Reference

When the primary model fails, switch the `model` and `API_URL` in the runner:

```python
# Nous (flaky)
API_URL = 'https://inference-api.nousresearch.com/v1/chat/completions'
MODEL = 'deepseek/deepseek-v4-flash:free'

# Cerebras (working fallback)
API_URL = 'https://api.cerebras.ai/v1/chat/completions'
MODEL = 'qwen-3-235b-a22b-instruct-2507'
```

Cerebras uses the same OpenAI-compatible response shape, so the parsing code requires no changes.
