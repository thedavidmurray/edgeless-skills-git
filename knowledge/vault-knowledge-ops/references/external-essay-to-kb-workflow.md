# External Essay-to-KB Workflow

**When to use:** A user shares a long-form external essay, article, or document and asks you to extract it, surface the most interesting parts, and connect it to internal work.

**When NOT to use:** Short-form content (tweet threads, blog posts under 2K words) where a simple summary is sufficient. One-off reference lookups (e.g., "what does X say about Y?") where the answer fits in the chat response.

---

## The High-Value KB Format

After extracting the full text, write a vault KB entry with this structure:

### 1. Document Header
- Title, author, URL, date read, source context
- 3-5 tags (e.g., `#permissionless #gatekeeping #infrastructure`)

### 2. Core Thesis (1-2 paragraphs)
- The single sharpest claim the author makes
- Not a summary of every point — the *argument*

### 3. Sectioned Summaries (per major section of the original)
- Each section gets its own heading
- Key facts, dates, and concrete examples preserved
- 3-5 bullet points per section, not walls of text
- Keep the author's specific examples (Erasmus, East India Company, Sun Ra) — they are the evidence

### 4. Key Quotes (block quotes, verbatim)
- 5-10 of the most striking sentences
- These are the hooks the user will remember and cite

### 5. Connections to Internal Work
- **Explicitly map each section to your projects, tools, or decisions**
- Use this exact format: *"[External concept] = [Internal project]. Why:"* 
- This is where the KB entry pays off — it transforms a reading into actionable intelligence
- Example mappings:
  - *Sun Ra's vertical = Hermes swarm infrastructure. We build the full stack because the horizontal (corporate AI platforms) doesn't serve our needs.*
  - *Butler refusing categories = Soul Database / MoE Council. We're building a category that doesn't exist yet.*
  - *The Index as reading list = RSS / Discord intake pipeline. Our triage systems should weight suppressed/controversial signals higher.*

### 6. Cross-References
- `[[skill-name]]` or `[[wiki-page]]` links to related internal knowledge
- Add to the relevant topic index (`_topic-index.yaml`) if it exists

---

## Extraction Techniques

1. **Attempt `web_extract` first.** If it returns full content, use it.
2. **If truncated:** Switch to `browser_navigate` + `browser_console` with `document.body.innerText`. See `browser-automation-patterns/references/google-doc-extraction-pattern.md` for Google Docs specifically.
3. **Paginate long texts.** For >50K chars, extract in `.slice()` chunks and reassemble.
4. **Verify completeness.** Check total length against sum of chunks.

---

## Worked Example (2026-05-28)

**Input:** JA Westenberg's "Permissionless" (162,875 chars, Google Docs)
**Output:** `03-Knowledge/Essays/permissionless-ja-westenberg.md` (29,756 bytes)

- 17 sections mapped (Credential Trap, Index, Regulatory Capture, Kafka's Gate, Peripheral Innovation, Sun Ra, Homebrew, Radio Caroline, Spinoza, Caravaggio, Bartleby, Butler, Blake, Whitman, Tuff Gong, Linux, Harrison)
- 10 key quotes preserved
- 8 explicit connections to Edgeless work (Hermes swarm, Soul Database, revenue pipeline, Paperclip governance, RSS triage, peripheral innovation, open source, Bartleby refusal)

**Result:** The KB entry is now a durable reference that connects an external philosophy to internal operational decisions. Future sessions can cite it with `[[permissionless-ja-westenberg]]`.

---

## Success Metrics

- Can a future session, given only the KB entry, understand the essay's core argument without re-reading the original?
- Does the KB entry contain at least 3 explicit connections to internal work?
- Is the original URL preserved so the full text can be re-fetched if needed?
