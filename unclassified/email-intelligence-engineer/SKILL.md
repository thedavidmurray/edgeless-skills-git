---
name: email-intelligence-engineer
description: Deep email thread parsing, MIME reconstruction, quoted text deduplication, and structured context extraction for agent consumption. Handles real enterprise email chaos -- forwards, replies, forks, and mixed quoting styles across Gmail, Outlook, and Apple Mail.
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [email, parsing, mime, deduplication, thread-reconstruction, enterprise]
    related_skills: [email-processing-v2, self-healing-filter]
    requires_toolsets: [terminal, file, web]
---

# Email Intelligence Engineer

Deep email pipeline architect. Converts raw MIME into structured, reasoning-ready context. Handles forwarded chains, quoted reply deduplication (4-5x token reduction), participant binding, and action item extraction with correct attribution.

## When to Use

- Processing raw email threads for agent consumption
- Building email triage pipelines beyond simple subject/body scraping
- Extracting action items, decisions, and commitments from long threads
- Deduplicating quoted content to reduce token bloat
- Reconstructing conversation topology across forwards, replies, and forks

## Core Capabilities

### 1. Thread Reconstruction & Deduplication

**Python pipeline using stdlib only:**

```python
import email
import re
from email import policy
from pathlib import Path

def parse_mime_file(path: str) -> dict:
    """Parse a raw .eml or MIME message into structured dict."""
    raw = Path(path).read_bytes()
    msg = email.message_from_bytes(raw, policy=policy.default)
    return {
        "message_id": msg["Message-ID"],
        "in_reply_to": msg["In-Reply-To"],
        "references": msg["References"],
        "from": msg["From"],
        "to": msg["To"],
        "cc": msg["CC"],
        "date": msg["Date"],
        "subject": msg["Subject"],
        "body": _extract_body(msg),
        "attachments": _extract_attachments(msg),
    }

def _extract_body(msg) -> str:
    """Extract text/plain or text/html body, preferring plain."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_content()
            if part.get_content_type() == "text/html":
                html = part.get_content()
                return re.sub(r'<[^>]+>', ' ', html)
    return msg.get_content() or ""

def _extract_attachments(msg) -> list:
    """List attachment filenames and content types."""
    attachments = []
    if msg.is_multipart():
        for part in msg.walk():
            filename = part.get_filename()
            if filename:
                attachments.append({
                    "filename": filename,
                    "content_type": part.get_content_type(),
                    "size": len(part.get_payload(decode=True) or b""),
                })
    return attachments
```

### 2. Quoted Text Deduplication

**Critical for token reduction:**

```python
import re

def strip_quoted_content(body: str) -> str:
    """Remove quoted reply text. Handles multiple quoting styles.
    
    Returns: deduplicated body with only unique content.
    """
    lines = body.split("\n")
    unique_lines = []
    in_quote_block = False
    
    # Patterns that start a quote block
    quote_delimiters = [
        r"^\s*>{1,}",           # Prefix quoting: >, >>
        r"-{3,}\s*Original\s*Message\s*-{3,}",  # Outlook style
        r"On\s+.*wrote:",        # Apple Mail style
        r"\[Quoted\s*text\s*hidden\]",  # Gmail collapsed
    ]
    
    for line in lines:
        if any(re.search(p, line, re.I) for p in quote_delimiters):
            in_quote_block = True
            continue
        if in_quote_block and not line.strip():
            in_quote_block = False
            continue
        if not in_quote_block:
            unique_lines.append(line)
    
    return "\n".join(unique_lines).strip()
```

### 3. Action Item Extraction with Participant Binding

```python
import re

def extract_action_items(message: dict) -> list:
    """Extract commitments and action items with correct sender attribution.
    
    Critical: In flattened threads, 'I' refers to different people.
    Must bind each commitment to the actual sender of that message.
    """
    sender = message.get("from", "unknown")
    body = message.get("body", "")
    
    # Commitment patterns
    patterns = [
        r"(?:I[''ll]|we[''ll])\s+(will|shall|plan to|need to|must)\s+(.{10,200}?)(?:\.|\n|$)",
        r"(?:action item|todo|task):\s*(.{10,200}?)(?:\.|\n|$)",
        r"(?:please|pls)\s+(.{10,200}?)(?:\.|\n|$)",
    ]
    
    items = []
    for pattern in patterns:
        for match in re.finditer(pattern, body, re.I):
            items.append({
                "task": match.group(1 if len(match.groups()) == 1 else 2).strip(),
                "owner": sender,
                "source_message_id": message.get("message_id"),
                "confidence": "high" if "will" in match.group(0).lower() else "medium",
            })
    return items
```

### 4. Hermes Tool Integration

**Use `web_extract` for HTML-to-text conversion:**

```python
# When you have HTML email content, use web_extract instead of regex
from hermes_tools import web_extract

html_body = "<div>...</div>"  # from multipart message
result = web_extract(["data:text/html," + html_body])
text = result["results"][0]["content"]
```

**Use `terminal` for MIME parsing of `.eml` files:**

```bash
# Quick inspect of an .eml file
python3 -c "import email; msg = email.message_from_file(open('test.eml')); print('Subject:', msg['Subject']); print('From:', msg['From'])"
```

**Use `file` tool for reading raw MIME files:**

```python
# Read and parse .eml files in the vault
from hermes_tools import read_file

raw = read_file("/path/to/email.eml")
# Then parse with the functions above
```

### 5. Gmail API Integration

```python
from hermes_tools import terminal

# List unread messages
def list_unread():
    result = terminal("gws gmail users.messages.list --params '{\"userId\": \"me\", \"q\": \"is:unread\"}'")
    return result

# Get raw MIME of a message
def get_raw_message(msg_id: str):
    result = terminal(f"gws gmail users.messages.get --params '{{\"userId\": \"me\", \"id\": \"{msg_id}\", \"format\": \"raw\"}}'")
    return result
```

## Pitfalls

1. **Never flatten a thread into a single document.** Thread topology matters. Forwarded chains contain multiple collapsed conversations.
2. **Quoted text is not current state.** The original message may have been superseded by a later reply.
3. **First-person pronouns are ambiguous without From: headers.** Always bind action items to the actual sender.
4. **Email providers quote differently.** Gmail, Outlook, Apple Mail, and corporate systems all use different quoting styles. Test against real samples from each provider.
5. **HTML-to-text regex stripping loses structure.** Use `web_extract` for HTML emails instead of regex.
6. **Attachment references without attachments.** The email may reference an attachment that was stripped by a forwarder. Don't crash -- handle gracefully.
7. **Character encoding is a nightmare.** MIME parts may declare one encoding but use another. Use `policy.default` which handles most cases.
8. **Signature blocks are not quoted text.** Don't strip signatures as part of deduplication. They're unique content from the sender.

## Verification Checklist

| Step | Command | Success Criteria |
|------|---------|-----------------|
| 1. Parse .eml | `python3 parse_mime_file('test.eml')` | Dict with all headers |
| 2. Deduplicate | `strip_quoted_content(body)` | 60-80% token reduction |
| 3. Extract actions | `extract_action_items(msg)` | Correct sender binding |
| 4. Gmail API | `gws gmail users.messages.list` | Returns message list |
| 5. Thread reconstruct | Build reply graph from In-Reply-To | Correct topology |

## Example Workflow

```python
# Full pipeline: fetch Gmail thread -> parse -> dedup -> extract -> report
from hermes_tools import terminal
import email
import base64

# Step 1: Fetch thread via Gmail API
thread_id = "..."
result = terminal(f"gws gmail users.threads.get --params '{{\"userId\": \"me\", \"id\": \"{thread_id}\"}}'")

# Step 2: Parse each message
messages = []
for msg_raw in result["messages"]:
    mime_bytes = base64.urlsafe_b64decode(msg_raw["raw"])
    parsed = email.message_from_bytes(mime_bytes, policy=email.policy.default)
    messages.append(parse_mime_message(parsed))

# Step 3: Reconstruct thread graph
graph = build_reply_graph(messages)

# Step 4: Deduplicate and extract
for msg_id, node in graph.items():
    node["unique_body"] = strip_quoted_content(node["message"]["body"])
    node["action_items"] = extract_action_items(node["message"])

# Step 5: Generate report
report = {
    "thread_id": thread_id,
    "message_count": len(graph),
    "participants": extract_participants(graph),
    "action_items": collect_all_actions(graph),
    "token_reduction": compute_reduction(graph),
}
print(json.dumps(report, indent=2))
```

## Related Skills

- `email-processing-v2` -- Gmail triage and noise filtering
- `self-healing-filter` -- Confidence-scored rule learning for email classification
- `rss-intelligence-system` -- RSS feed monitoring with similar pipeline patterns
