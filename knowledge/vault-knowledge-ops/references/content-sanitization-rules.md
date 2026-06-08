# Content Sanitization Rules for Public-Facing Posts

Scrub internal identifiers from all blog posts, X threads, newsletters, and any public-facing content before publication. User explicitly stated: "exposing bot names is a bad idea."

## ALWAYS SCRUB

| Category | Examples | Replacement |
|----------|----------|-------------|
| **Swarm bot names** | Hive, Kilo, Beau, Scribe, Edgeless CC, Pamela, Atlas, Ombudsman | "the agent," "the system," "autonomous agents," "the operator" |
| **Internal project codes** | EDGA-XXX, task-NNN, EDGA-147 | Generic description or omit |
| **Agent IDs / Paperclip IDs** | 7f8aa3c8-73db-465e-9f25-e2de8cf10802 | Omit entirely |
| **Internal channel names** | #bot-backroom, #audit-log | Generic reference or omit |
| **Infrastructure details** | Hetzner IP, VPS paths, cron schedules | Omit or generalize |
| **Discord handles** | Hive#2662, Kilo#3551 | Omit |

## ALWAYS KEEP

| Category | Examples |
|----------|----------|
| **Product names** | Claude, ChatGPT, OpenAI, Notion, Airtable |
| **Generic terminology** | "autonomous agents," "LLMs," "AI," "wetware" |
| **Public frameworks** | "dream cycles" (user-endorsed), "maintenance architecture" |
| **Personal voice** | "I," "we," "your" — first-person is David's voice |

## Platform-Specific Exposure Levels

| Platform | Exposure Rule |
|----------|---------------|
| **X thread** | Most restrictive. Scrub everything internal. Only generic concepts and public product names. |
| **Beehiiv / Edgeless blog** | Medium restriction. Can reference internal concepts abstractly ("autonomous agents run maintenance cycles") but never name specific bots or infrastructure. |
| **LinkedIn** | User preference: skip entirely for technical content. If used, same level as Beehiiv. |

## Pre-Publication Checklist

Add to Stage 5 (Prepped) of the blog pipeline:
- [ ] Search document for every swarm bot name
- [ ] Search for "EDGA-" or "task-" prefixes
- [ ] Search for Discord handles or channel references
- [ ] Verify "wetware" usage is present if applicable (user-endorsed)
- [ ] Confirm product names (Claude, etc.) are correctly capitalized
- [ ] Read footer/credit line — scrub agent names from "Council-verified by X, Y, Z"

## Scrubbing Pattern

```python
SWARM_NAMES = {"Hive", "Kilo", "Beau", "Scribe", "Edgeless CC", 
               "Pamela", "Atlas", "Ombudsman", "Edgeless"}

def scrub_public_content(text: str) -> str:
    for name in SWARM_NAMES:
        text = text.replace(name, "the agent")
    # Deduplicate adjacent replacements
    text = text.replace("the agent, the agent", "the agent")
    return text
```

## User Preferences (Session 2026-05-21)

- "Wetware is good though" — keep this term, it is explicitly endorsed
- LinkedIn posts "don't make a lot of sense" for technical blog content
- X threads and Beehiiv (Edgeless) posts are preferred platforms
- Approval style: apply requested changes without pushing back
