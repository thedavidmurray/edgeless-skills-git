# Cleaning LLM Reasoning Contamination from Generated Content

When using reasoning-capable models (Kimi K2.5, Claude, o3, etc.) to **generate content** — blog posts, code, frameworks — the model's internal chain-of-thought often leaks into the output. This is different from Q&A where the reasoning is the product. In generation tasks, the reasoning is noise.

## The Problem

A prompt like:

> "Rewrite this draft to fix weaknesses. Output ONLY the rewritten text."

Produces output that starts with the draft, then trails into:

```
## 3. How to Build a Dream Cycle
...

---

Wait, I need to check the word count. Original was 1820. My rewrite is probably 
around there or shorter. Let me review against voice rules:
- "direct, decisive, numbered lists, no filler enthusiasm"
- Check for filler...

Actually, the conclusion might not be needed if the draft didn't have one. But 
the draft cuts off. I should provide a complete article. The user wants the draft 
rewritten. I'll provide the full logical flow.
```

The model "thinks out loud" after finishing the draft, and that reasoning text 
contaminates the output file.

## The Fix: `clean_improved_draft()`

Extract just the generated content by finding structural boundaries:

```python
def clean_improved_draft(raw: str, title: str) -> str:
    lines = raw.splitlines()
    
    # Find first line that looks like the title heading
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("# ") and title.split()[0].lower() in line.lower():
            start_idx = i
            break
    
    # Fallback: any # heading near start
    if start_idx is None:
        for i, line in enumerate(lines):
            if line.strip().startswith("# "):
                start_idx = i
                break
    
    if start_idx is None:
        return raw.strip()
    
    draft_lines = lines[start_idx:]
    
    # Strip trailing empty lines and reasoning paragraphs
    end_idx = len(draft_lines)
    for i in range(len(draft_lines) - 1, -1, -1):
        stripped = draft_lines[i].strip()
        if stripped == "" or stripped.startswith("Wait,") or stripped.startswith("Let me ") or stripped.startswith("Actually,"):
            end_idx = i
        elif stripped == "---":
            end_idx = i  # include the ---
            break
        else:
            break
    
    return "\n".join(draft_lines[:end_idx]).strip()
```

## Prevention: Lock the Prompt

Even with a cleaner, prevent contamination at the prompt level:

```
RULES:
- Output ONLY the rewritten draft text. No explanations, no reasoning, no commentary.
- Do not include score discussions or analysis.
- Do not wrap the output in markdown code blocks.
- Start with the title as a # heading.
- End with --- and a sources line.
```

These rules reduce but do not eliminate leakage. **Always pair prompt rules with a 
post-processing cleaner.**

## When This Hits

- Content generation with reasoning models (Kimi K2.5, Claude Sonnet, o3)
- Long-context rewrites where the model reviews its own work
- Multi-step generation tasks ("write, then check, then revise")
- Any prompt that says "improve" or "rewrite" — the model treats it as a reasoning task

## When It Does Not Hit

- Simple completion ("finish this sentence")
- Structured output with strict JSON schema enforcement
- Short responses (< 500 tokens) where the model stops before reasoning
- Non-reasoning models (older GPT-3.5, non-chain-of-thought variants)

## Related: Skip Auto Re-Score

Another autoreason pitfall: after generating an improved draft, automatically 
re-scoring it with the same model produces unreliable results. The model either:
1. Parses its own reasoning text instead of the draft (bogus low scores)
2. Scores its own output leniently (inflated scores)

**Fix:** Skip automatic re-score. Emit the improved draft with a TBD score, and 
let the next stage (human review, council, or a different model) score it.
