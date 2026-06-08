---
title: Baoyu Comic Pipeline (Visual + Comedy Split)
category: creative
description: Split-workflow for generating multi-page knowledge comics. Image pipeline (FAL/ligne-claire) produces good art. Comedy writing is delegated to specialist models. This skill documents the integration.
author: hive
version: 1.0.0
---

# Baoyu Comic Pipeline — Visual + Comedy Split

## Problem Statement

The baoyu-comic image generation pipeline (FAL via Nous, ligne-claire style) produces **excellent visual results**. The comedy writing pipeline (Kimi, DeepSeek, Gemini) produces **mediocre to bad gags**.

**Solution:** Split the workflow.
- **Visual execution**: Hive (or any agent with `image_generate`) — FAL ligne-claire
- **Comedy writing**: Delegate to Claude/Codex/DeepSeek-Coder with a structured prompt
- **Integration**: Comic assembler merges comedy script + visual prompts

## What Works (Visual)

| Element | Status | Details |
|---------|--------|---------|
| **FAL image gen** | ✅ Active | Via Nous gateway, `image_generate` tool |
| **ligne-claire style** | ✅ Excellent | "clear black outlines, flat cheerful colors, Tintin/Hergé inspired" |
| **Panel layouts** | ✅ Works | 4-panel standard, dramatic, cinematic variants |
| **Character design** | ✅ Good | Anthropomorphic frogs, consistent when bible is enforced |
| **Anti-human guardrails** | ✅ Critical | Must explicitly ban humans in EVERY prompt |

## What Fails (Comedy)

| Model | Comedy Quality | Notes |
|-------|---------------|-------|
| Kimi (Fireworks) | ❌ Poor | Over-reasons, produces long meta-commentary instead of gags |
| DeepSeek V4 Flash | ❌ Bland | Produces logical but unfunny chains; no surprise or absurdity |
| Gemini 2.5 Pro | ❌ Dead | Quota exceeded, not available |
| Codex | ❌ Dead | OAuth token reused by another client |

**Root cause:** The models default to "safe" physical comedy (rainclouds, balloon inflation) or over-explain the joke instead of writing it.

## Character Bible (Wizard Frogs Example)

**MANDATORY in every prompt:** Re-paste this character section to prevent drift.

```
CHARACTERS (anthropomorphic frogs, NO HUMANS):
- Ripple: tiny spring-green tree frog, enormous round golden eyes, crooked leaf wizard hat, clumsy apprentice, willow wand
- Croakus: massive wise bullfrog, emerald green skin, gold freckles, glowing algae beard, cattail staff with firefly lantern
- Azure: tiny bright blue poison dart frog, ice magic specialist, feisty attitude
- Mottle: spotted leopard frog, earth magic, mushroom-cap beret
- Burrow: grumpy brown toad, divination magic, always annoyed
```

## Anti-Human Guardrails (CRITICAL)

FAL defaults to inserting human children when it sees "tiny," "clumsy," or "apprentice." **Every prompt must include:**

```
ALL CHARACTERS ARE ANTHROPOMORPHIC FROG WIZARDS. NO HUMANS. NO BOYS. NO PEOPLE. NO HUMAN CHILDREN.
```

Place this at the TOP of the prompt and repeat after each panel description.

## Comedy Delegation Template

Send this to Claude/Codex/DeepSeek-Coder for the comedy script:

---

**ROLE:** You are a comedy writer for children's comics in the style of **Looney Tunes** and **Asterix**. Physical slapstick. Visual gags. No dialogue.

**CHARACTERS:**
[Paste character bible here]

**TASK:** Write a 4-panel comic page.

**RULES (strict):**
1. The spell/gag must have a **specific, clear intent**
2. The backfire must be the **exact logical opposite** of the intent
3. Each panel shows a **direct physical consequence** of the previous
4. The punchline resolves the chain **logically but absurdly**
5. **NO dialogue. NO text gags.** Pure visual action.
6. Funny to a 10-year-old AND a 35-year-old

**AVOID:** rainclouds, inflation, random objects appearing, generic magic mishaps, characters acting stupid for no reason.

**FORMAT:**
Panel 1: [one sentence, setup with clear intent]
Panel 2: [one sentence, spell fires, immediate wrong effect]
Panel 3: [one sentence, physical consequence spreads]
Panel 4: [one sentence, logical absurd resolution]

**EXAMPLE OF GOOD STRUCTURE:**
Intent: Wile E. Coyote paints a tunnel on a rock wall
Backfire: The tunnel is REAL for Road Runner but SOLID for Coyote
Consequence: Coyote crashes, a truck emerges from the painted tunnel
Resolution: Coyote is flattened, Road Runner zips out the other side

Now write a NEW gag with the frog characters following that same logic chain.

---

## Image Prompt Assembler

Once you receive the comedy script, assemble the FAL prompt:

```
A slapstick comic page in ligne-claire style (clear black outlines, flat cheerful colors, Tintin/Hergé inspired). Standard 4-panel layout.

Panel 1: [comedy script Panel 1, with character descriptions injected]
Panel 2: [comedy script Panel 2, with visual effects added]
Panel 3: [comedy script Panel 3, with scale/motion added]
Panel 4: [comedy script Panel 4, with punchline framing]

Overall style: ligne-claire, clear crisp outlines, flat warm colors. ANTHROPOMORPHIC FROG WIZARDS ONLY. NO HUMANS.
```

## Known Pitfalls

1. **FAL compresses 4 panels into 3** — FAL sometimes merges panels. If this happens, regenerate with "4-panel layout, clearly separated panels, visible panel borders."
2. **Character drift across pages** — Ripple looks different on each page. Solution: keep a visual reference image and mention "consistent with previous page" in the prompt.
3. **Model ignores "no humans"** — Repeat the guardrail 3+ times in the prompt.
4. **Comedy writers over-explain** — The delegation template explicitly bans intros, outros, and reasoning. One sentence per panel only.
5. **DeepSeek/Codex auth issues** — Have fallback comedy writers ready (Claude via web, Gemini if quota resets).

## Tool Integration

| Tool | Role | Status |
|------|------|--------|
| `image_generate` | FAL image gen | ✅ Active |
| `skill_view` | Load baoyu-comic reference | ✅ Active |
| `delegate_task` | Send comedy writing to Claude/Codex | ❌ Codex dead; Claude web possible |
| `web_extract` | Pull Looney Tunes gags for inspiration | ✅ Active (Nous restored) |

## File Structure

```
~/comic/{project}/
├── characters/characters.md        # Character bible
├── source.md                      # Topic/content source
├── storyboard.md                  # Page-by-page outline
├── comedy/                        # Scripts from comedy writers
│   └── 02-page-comedy.md
├── prompts/                       # Final FAL prompts
│   └── 02-page-fal-prompt.md
└── output/                        # Generated PNGs
    └── 02-page.png
```
