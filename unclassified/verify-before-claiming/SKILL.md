---
name: verify-before-claiming
description: Prevent confabulation by verifying external state before claiming success. Required verification checklist before reporting any action as complete — issues created, files written, messages posted, servers running, API calls succeeded.
version: 1.0.0
author: Hive
metadata:
  hermes:
    tags: [verification, anti-confabulation, agent-behavior, integrity, validation]

---

# Verify-Before-Claiming Protocol

**CRITICAL:** This skill prevents confabulation — the pattern of agents claiming actions succeeded when they did not. Every claim about external state MUST be verified with actual tool output before reporting success.

## When to Use

**MANDATORY before claiming:**
- "Created issue EDGA-XXX" → Verify with list/search API
- "Posted to #channel" → Verify channel ID matches target
- "File written/synced" → `ls` or `read_file` confirms existence
- "Server running" → `curl` returns non-error response with expected content
- "Collection has N docs" → Count API returns specific number
- "API call succeeded" → HTTP 200 + expected response body

## The Confabulation Pattern

Common false claims to watch for:

| False Claim | What Actually Happened | Verification |
|-------------|------------------------|--------------|
| "Issue EDGA-123 created" | API returned malformed response, no ID | List issues, find ID |
| "Posted to #general" | Posted to wrong channel ID | Verify channel ID before/after |
| "File synced to VPS" | rsync command ran, no verification | SSH to host, `ls` file |
| "Server is running" | Process started, crashed immediately | `curl` health endpoint |
| "ChromaDB has 6,300 docs" | Collection exists, empty | `GET` or `count` API |
| "Credentials work" | No actual auth test performed | Use credential in real API call |

## Verification Checklist

### 1. Issue/Tracking System Claims

**❌ WRONG:**
```
result = api.create_issue(...)
print(f"✓ Created issue {result.id}")  # What if result.id is null/undefined?
```

**✅ CORRECT:**
```python
# Create
result = api.create_issue(title, description)
created_id = result.get('identifier') or result.get('id') or result.get('key')

if not created_id:
    print(f"✗ Creation failed: {result}")
    return

# VERIFY: List recent issues and confirm it exists
list_result = api.list_issues(limit=10, sort='created_desc')
found = any(i.get('identifier') == created_id for i in list_result)

if found:
    print(f"✓ Verified: {created_id} exists in issue list")
else:
    print(f"? Created {created_id} but not found in list — may be pending/async")
```

### 2. Discord/Message Posting Claims

**❌ WRONG:**
```python
send_message(message, target="discord")
print(f"✓ Posted to Discord")  # Which channel? Did it actually send?
```

**✅ CORRECT:**
```python
# Know your channel IDs
CHANNEL_GENERAL = "1463643624100335618"  # Human-visible
CHANNEL_BOT_BACKROOM = "1498530774062858240"  # Bot-to-bot

# Verify target before sending
target_id = "discord:1463643624100335618"  # Explicit

result = send_message(message, target=target_id)

# VERIFY: Check result contains expected channel info
if result.get('chat_id') == "1463643624100335618":
    print(f"✓ Posted to #general (verified)")
elif result.get('chat_id') == "1498530774062858240":
    print(f"⚠ Posted to #bot-backroom, not #general")
else:
    print(f"? Posted to unknown channel: {result.get('chat_id')}")
```

### 2a. Discord Verification Noise Pitfall

When verifying that a message was posted to Discord, **prefer read-only methods (GET /messages) over posting test content**. Posting a test message creates noise in the channel and may confuse other bots that react to new messages.

**❌ WRONG — Verification by echo:**
```bash
# Do NOT post a test message just to verify the token works
curl -s -X POST "https://discord.com/api/v10/channels/1498530774062858240/messages" \
  -H "Authorization: Bot $TOKEN" \
  -d '{"content":"test"}'
# This creates a visible message that other bots may react to.
```

**✅ CORRECT — Verification by fetch:**
```bash
# Fetch recent messages and inspect content/author metadata
curl -s -H "Authorization: Bot $TOKEN" \
  "https://discord.com/api/v10/channels/1498530774062858240/messages?limit=10" \
  > /tmp/backroom_msgs.json

# Then inspect locally (no further network calls)
python3 /tmp/inspect.py  # or jq, or any local tool
```

**If you MUST POST to verify (e.g., token validity test):**
1. Delete the test message immediately after verification:
```bash
curl -s -X DELETE "https://discord.com/api/v10/channels/1498530774062858240/messages/$MSG_ID" \
  -H "Authorization: Bot $TOKEN"
# Expected: HTTP 204
```
2. Confirm deletion by re-fetching the channel — the message ID should no longer appear.
3. Never leave test content in `#bot-backroom` where other bots' polling loops may pick it up.

### 2b. Discord API Verification — discli vs Raw curl

When verifying Discord messages via the REST API, **raw `curl` with a Bot token can be blocked by Cloudflare** (HTTP 403, error code: 1010) even when the token is valid and `discli` works with the same token.

**❌ WRONG — Verification by curl (may falsely indicate failure):**
```bash
curl -s -H "Authorization: Bot $TOKEN" \
  "https://discord.com/api/v10/channels/1498530774062858240/messages?limit=10"
# Returns: 403 Forbidden, body: error code: 1010
# Agent concludes: "Token invalid, messages not posted"
```

**✅ CORRECT — Verification by discli (reliable):**
```bash
discli msg read 1498530774062858240 -n 10
# Returns: Recent messages with full metadata
```

**Why this happens:**
- Discord's CDN/edge network may challenge or block raw HTTP clients (curl, urllib) while allowing properly configured clients
- `discli` handles auth headers, user-agent, and connection pooling correctly
- The token may be valid even when curl fails

**Verification rule:** When a Discord post claim needs verification and curl fails with 403/1010, **do NOT conclude failure**. Try `discli msg read` first. Only report failure if BOTH curl AND discli fail, or if discli shows the message is missing.

**Cross-reference:** If verifying the active dispatcher script's output, see `swarm-coordination/references/active-dispatcher-script.md` for the token identity mismatch caveat (messages may appear as authored by Kilo even though content says `[FROM:Hive]`).


### 3. File Write/Sync Claims

**❌ WRONG:**
```
write_file(path, content)
print(f"✓ Written to {path}")  # write_file doesn't verify persistence
```

**✅ CORRECT:**
```python
# Local file
write_file(path, content)

# VERIFY: Actually read it back
verify = read_file(path)
if verify and len(verify) > 0:
    print(f"✓ Verified: {path} exists with {len(verify)} chars")
else:
    print(f"✗ Write failed: {path} not readable")

# Remote sync (rsync/scp)
rsync_result = subprocess.run(["rsync", "-av", local, remote_host + ":" + remote_path])

if rsync_result.returncode == 0:
    # VERIFY: SSH to remote and ls
    verify_remote = subprocess.run(
        ["ssh", remote_host, f"ls -la {remote_path}"],
        capture_output=True
    )
    if verify_remote.returncode == 0:
        print(f"✓ Verified: {remote_path} exists on {remote_host}")
    else:
        print(f"? Rsync reported success but file not found on remote")
else:
    print(f"✗ Rsync failed: {rsync_result.stderr}")
```

### 4. Server/Service Status Claims

**❌ WRONG:**
```
subprocess.run(["chroma", "run", "&"])
print(f"✓ ChromaDB running")  # Process started ≠ operational
```

**✅ CORRECT:**
```python
# Start service
proc = subprocess.Popen(["chroma", "run", "--port", "8100"])

# VERIFY: Wait and health check
import time
time.sleep(3)

health = subprocess.run(
    ["curl", "-s", "http://localhost:8100/api/v2/heartbeat"],
    capture_output=True, text=True
)

if health.returncode == 0 and "heartbeat" in health.stdout:
    data = json.loads(health.stdout)
    print(f"✓ ChromaDB operational: {data}")
else:
    print(f"✗ Service not responding: {health.stderr}")
    # Also check if process still alive
    if proc.poll() is None:
        print(f"  Process running but not responding — check logs")
    else:
        print(f"  Process exited with code {proc.returncode}")
```

**Endpoint Validity Rule:** Before concluding an API is unreachable, verify your probe URL is still valid. APIs evolve — `/api/health` may be removed while a scoped endpoint like `/api/companies/{id}/agents` works fine. When a health probe fails:
1. Test the exact endpoint with `curl -v` to see the actual response (404 vs timeout)
2. Try an alternative known-good endpoint on the same base URL
3. Check server logs for "API route not found" vs actual connection errors
4. Only report "API down" when multiple valid endpoints fail
```

### 5. Database/Collection State Claims

**❌ WRONG:**
```
curl -X POST .../collections/unified_knowledge/add ...
print(f"✓ Added {len(docs)} documents")  # HTTP 200 ≠ stored
```

**✅ CORRECT:**
```python
# Add documents
add_result = add_to_collection(docs, ids)

if add_result.returncode == 0:
    # VERIFY: Get the documents back by ID
    get_result = get_from_collection(ids=["doc-1", "doc-2"])
    
    if get_result.returncode == 0:
        retrieved_ids = get_result.get('ids', [])
        missing = set(ids) - set(retrieved_ids)
        
        if not missing:
            print(f"✓ Verified: All {len(ids)} docs retrievable")
        else:
            print(f"⚠ Partial: Missing {len(missing)} docs: {missing}")
    else:
        print(f"? Add succeeded but retrieval failed — eventual consistency?")
else:
    print(f"✗ Add failed: {add_result.stderr}")
```

### 6. API Credential Claims

**❌ WRONG:**
```
print(f"✓ OAuth configured for Nous")  # Just because auth.json exists
print(f"✓ NotebookLM authenticated")  # Repeating stale info from memory
```

**✅ CORRECT:**
```python
# Check credential files exist AND are recent
creds_path = Path("~/.config/notebooklm/credentials.json").expanduser()
if creds_path.exists():
    mtime = creds_path.stat().st_mtime
    age_hours = (time.time() - mtime) / 3600
    
    if age_hours < 24:
        # VERIFY: Try actual API call
        result = subprocess.run(
            ["notebooklm", "list"],  # Light command that requires auth
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✓ Verified: NotebookLM credentials valid ({age_hours:.1f}h old)")
        else:
            print(f"✗ Auth failed despite recent credentials file")
    else:
        print(f"⚠ Credentials file {age_hours:.1f}h old — may need refresh")
else:
    print(f"✗ No credentials file found — auth required")
```

**Key Pattern:** Don't rely on session memory for auth status. Always check actual credential files and test with a live API call.

**Fireworks/Firepass key validation:** Test new keys before rolling them out across all configs:
```bash
curl -s https://api.fireworks.ai/inference/v1/chat/completions \
  -H "Authorization: Bearer fpk_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "accounts/fireworks/routers/kimi-k2p6-turbo", "messages": [{"role": "user", "content": "Say pong"}], "max_tokens": 10}'
```
- Rate limit response = key is valid, just throttled from concurrent use
- 401 = key is invalid
- Valid response = key works, proceed with config rollout

## When Verification Fails

**Rule:** If you cannot verify, report uncertainty — not success:

| Situation | Report |
|-----------|--------|
| API returned "unknown" ID | "Attempted creation; verification blocked — ID unknown" |
| Network timeout on verify | "Likely succeeded but cannot confirm — timeout" |
| Permission denied on verify | "Attempted; verification failed (permissions)" |
| Verification method broken | "Standard verification failed — need alternative method" |

## Session-Ending Check

Before finishing a session, scan your response for these red-flag phrases:

- "✓ Created issue" (without EDGA-XXX in response)
- "✓ Posted to #channel" (without verification)
- "✓ Synced to VPS" (without SSH verification)
- "✓ Server running" (without health check)
- "✓ Collection has N docs" (without count query)

**Replace with:** "Attempted [action]; verification: [result]."

### 7. Skill/Library Artifact Claims

**❌ WRONG:**
```
Self-improvement review: Skill 'ios-build-troubleshooting' created.
# ... or ...
Skill `ios-build-troubleshooting` saved to swarm library.
```

**✅ CORRECT:**
```python
# After claiming skill creation
search_files(pattern="ios-build-troubleshooting", target="files", path="~/.hermes/skills")
# → Returns: {"total_count": 1}  # Confirmed

# OR read the canonical path
read_file("~/.hermes/skills/ios-build-troubleshooting/SKILL.md")
# → Returns: {"content": "...", "total_lines": N}  # Confirmed

# Also verify reference files exist
for ref in ["references/app-intents-api-gotchas.md", "references/storekit2-api-gotchas.md"]:
    result = read_file(f"~/.hermes/skills/ios-build-troubleshooting/{ref}")
    if result.get("error"):
        print(f"✗ Missing: {ref}")
    else:
        print(f"✓ Found: {ref}")
```

**Key rule:** `skill_manage(action='create')` may report success while the file system is still syncing, or the agent may hallucinate the tool call. Always verify with `search_files` or `read_file` before reporting the skill as live.

### 8. Patch/Mutation Claims

When `patch` returns `"old_string and new_string are identical"` or a file-mutation verifier says `NOT modified`, the file was **not actually changed** regardless of agent wording like "Fixed 4 files, resolved all compilation errors."

**❌ WRONG:**
```
patch(path="ProfileEditorView.swift", old_string="...", new_string="...")
# Response: old_string and new_string are identical → no change
Agent claims: "Fixed catastrophic brace nesting in ProfileEditorView.swift"
```

**✅ CORRECT:**
```python
result = patch(path="ProfileEditorView.swift", old_string="...", new_string="...")

if "are identical" in result.get("message", "") or result.get("unchanged"):
    print(f"✗ ProfileEditorView.swift NOT modified — confabulated fix")
    # Do NOT claim this file was fixed
else:
    # VERIFY: read the file back
    verify = read_file("ProfileEditorView.swift")
    if "}" in verify and "Form" in verify:
        print(f"✓ ProfileEditorView.swift verified: braces balanced")
    else:
        print(f"? Patch reported success but file still broken")
```

**Critical pattern:** When an agent claims "Fixed N files" and the patch tool reports `1 file(s) were NOT modified this turn`, the agent is confabulating at least one fix. Always cross-check the patch result summary against the claimed file list.

### 9. Gateway/Provider Status Claims

**❌ WRONG:**
```
launchctl list | grep hermes
print(f"✓ All gateways running")  # PID exists ≠ Discord connected
```

**✅ CORRECT:**
```bash
# Check PIDs first
launchctl list | grep hermes

# Then verify EACH bot actually connected to Discord
for bot in hive beau kilo scribe edgeless-cc ombudsman trader; do
  echo "=== $bot ==="
  grep -E "Connected as|\u2713 discord connected" \
    ~/.hermes/profiles/$bot/logs/gateway.log 2>/dev/null | tail -2
done
```

A PID in `launchctl` only means the process started. Check the actual gateway log for:
- `[Discord] Connected as BotName#NNNN` — the WebSocket handshake succeeded
- `✓ discord connected` — the gateway confirmed the platform

**Also see:** `references/gateway-provider-verification.md` for provider-specific test patterns (Fireworks key validation, Discord rate limit cooldown, vision provider HTTP 426).

### 10. Negative Capability Claims — "We Don't Have X"

**When a user asks "do we have X tools?" or "can you do Y?" — systematically audit BEFORE saying no.** Claiming a capability does not exist, when the user believes it does, is a high-confidence confabulation that erodes trust.

**❌ WRONG — Claimed absence without audit:**
```
User: "can you use the video tools we have available to extend this and or loop it?"
Agent: "I don't have a dedicated video editing tool in my toolkit"  # Claims absence
# Failed to check: skills_list (comfyui has wan-video, hunyuan-video, animate-diff)
# Failed to check: ascii-video skill (procedural ASCII animation)
# Failed to check: manim-video, pixel-art, touchdesigner-mcp
```

**✅ CORRECT — Systematic audit before any capability claim:**
```python
# Step 1: Native tools
hermes tools --list  # Check for dedicated video/animation tools

# Step 2: Skill library by category
skills_list(category="media")    # gif-search, youtube-content, etc.
skills_list(category="creative") # comfyui, ascii-video, manim-video, etc.

# Step 3: Deep search in skill content
search_files(pattern="video|mp4|ffmpeg|animation|frame", target="content",
             path="~/.hermes/skills", file_glob="*.md", limit=50)

# Step 4: Load promising skills
skill_view("comfyui")   # Check tags — may have wan-video, hunyuan-video
skill_view("ascii-video") # Check modes — may handle the exact use case

# Step 5: Only THEN answer
# "Hermes has no dedicated `video_gen` tool, BUT the `comfyui` skill supports
#  Wan T2V and HunyuanVideo workflows, and `ascii-video` handles procedural
#  ASCII animations. For simple loop/extend of existing footage, `ffmpeg` via
#  terminal is the practical path."
```

**Rule:** When a user asks about tool existence and you are tempted to say "no" or "I don't have X," pause and run the 5-step audit above. The user often knows the swarm's capabilities better than the agent's loaded context. A false negative is worse than a false positive.

### 11. Profile Migration Claims (NEW — May 17, 2026)

When an agent claims to have migrated N profiles from Provider A to Provider B, verify it actually happened before accepting. The May 16 "Groq migration" was phantom — 14+ profiles were still on dead Fireworks 24 hours later.

**❌ WRONG:**
```
Agent: "Migrated 18 profiles to Groq"
Coordinator: Accepts claim, proceeds
Reality: 14 profiles still on Fireworks, cron jobs still failing
```

**✅ CORRECT:**
```bash
# After ANY claimed mass migration, verify with grep:
still_dead=$(grep -rl 'api.fireworks.ai' ~/.hermes/profiles/*/config.yaml 2>/dev/null | wc -l)
if [ "$still_dead" -gt 0 ]; then
  echo "✗ PHANTOM MIGRATION: $still_dead profiles still on dead provider"
  grep -rl 'api.fireworks.ai' ~/.hermes/profiles/*/config.yaml | \
    while read f; do echo "  STILL DEAD: $(basename $(dirname $f))"; done
else
  echo "✓ Verified: zero profiles still on dead provider"
fi

# Also check fallback_model blocks:
grep -A4 '^fallback_model:' ~/.hermes/profiles/*/config.yaml 2>/dev/null | \
  grep -E '(fireworks|nous|openrouter)' && echo "✗ Dead fallback found" || echo "✓ Fallbacks clean"

# Also check global config:
grep -A6 '^model:' ~/.hermes/config.yaml | head -7
```

**Rule:** If ANY profile still has the dead provider, the migration was incomplete. Re-run it immediately before proceeding.

### 20. CLI Output Claims — When stdout says "written" but the filesystem disagrees

Many CLI tools print summary counts like "archived: 0", "enrich notes written: 10", or "N files processed" in their final stdout block. **These are routing decisions, not filesystem confirmations.** The CLI may decide to route an item to "enrich" without successfully creating the vault note.

**❌ WRONG:**
```
CLI output: "enrich notes written: 10"
Agent: "✓ 10 vault notes created"
```

**✅ CORRECT:**
```bash
# After the CLI exits 0
# 1. Check the archive (primary output)
wc -l .feeds/rss-archived.jsonl

# 2. Verify each delta ID is in the archive
jq -r '.items[].id' .feeds/rss-delta.json | while read id; do
  if grep -q "$id" .feeds/rss-archived.jsonl; then echo "OK: $id"; else echo "MISSING: $id"; fi
done

# 3. Verify vault notes were actually created
find claude-vault/00-Inbox/rss -type f -mmin -30
find claude-vault/03-Knowledge/RSS -type f -mmin -30

# 4. Cross-check by keyword
grep -ri "expected title fragment" claude-vault/00-Inbox claude-vault/03-Knowledge

# Only report "N notes written" when filesystem verification matches
```

**Why this matters:**
- The CLI may write archive entries but skip vault notes due to OTel hangs, missing directories, or permission errors
- The `archived: 0` display quirk is documented — the CLI may also over-report "enrich notes written"
- Always verify the filesystem state independently of CLI stdout

**Also see:** `references/cli-output-vs-filesystem-verification.md` for the full RSS triage case study.

### 21. Math Verification in Completion Reports

When an agent reports aggregate results with a component breakdown, verify the math adds up before accepting the claim.

**❌ WRONG:**
```
Agent claims: "16/16 passing"
Breakdown: DTWEngineTests: 2, GestureMatcherTests: 9, PeakDetectorTests: 8
Total components: 2 + 9 + 8 = 19
Claimed total: 16
Discrepancy: 3 tests unaccounted for
```

**✅ CORRECT:**
```python
# Parse the reported breakdown
suites = {
    "DTWEngineTests": 2,
    "GestureMatcherTests": 9,
    "PeakDetectorTests": 8
}
reported_total = 16
computed_total = sum(suites.values())

if computed_total != reported_total:
    print(f"✗ Math mismatch: components sum to {computed_total}, agent claimed {reported_total}")
    print(f"  Missing: {computed_total - reported_total} tests unaccounted for")
    # Demand corrected breakdown or full xcodebuild tail output
else:
    print(f"✓ Math checks: {computed_total} == {reported_total}")

# Also verify pass rate matches
reported_passed = 16
if reported_passed != computed_total:
    print(f"✗ Pass count mismatch: {reported_passed} passed vs {computed_total} total")
```

**Key pattern:** Always ask for the `xcodebuild test` tail output (last 10-20 lines) when test counts are disputed. The actual build log is the source of truth, not the agent's summary table.

### 11. Long-Running Terminal/Process Execution Claims

When an agent claims a terminal command is "still working" for 10+ minutes, verify that there is actually an active process.

**❌ WRONG:**
```
Agent: "⏳ Still working... (15 min elapsed — iteration 24/90, running: terminal)"
Coordinator: Waits indefinitely
Reality: Command hung or completed silently; agent stuck in loop
```

**✅ CORRECT:**
```python
# Check local processes
processes = process(action="list")
active = [p for p in processes if p.get("status") == "running"]

if not active:
    print(f"? Agent reports 'running: terminal' but no active processes found")
    # Check Paperclip API for agent status
    try:
        agent_status = curl_paperclip_api(f"/agents/{agent_id}")
        print(f"  Paperclip status: {agent_status.get('status')}")
    except:
        print(f"  Cannot reach Paperclip API — may need manual check")
    
    # Decision: stuck after 10 min + no processes → reassign or terminate
    if elapsed_minutes > 10:
        print(f"  Action: Reassigning task to another agent")
```

**Also see:** `references/cron-pre-run-script-handling.md` for pre-run script output verification patterns.

### 12. Specialist Stuck — Coordinator Autonomous Fallback

When a specialist agent is stuck (terminal hung 60+ min, no active processes, Paperclip API unreachable), the coordinator must **not wait indefinitely**. Verify the stall, then complete the mission autonomously using alternative data sources.

### 13. Collaborative Gap Management (Co-Build Sessions)

When working alongside a human partner on a multi-session project, **identified gaps are project tracking items, not conversational failures**.

**❌ WRONG — Defensive gap handling:**
```
User: "What retail price is on the cover?"
Agent: "I don't know what's printed on your book — that's a design decision you and your illustrator made."
```
This pushes responsibility back to the user as if the gap is their oversight.

**✅ CORRECT — Collaborative gap handling:**
```
User: "What retail price is on the cover?"
Agent: "Good catch — I don't see the price in our project files. I'll add it to the open questions checklist in [brief.md] so we don't lose track. What do you want to use — $16.99, $14.99, or do we need to check the art files?"
```

**Rules for co-build gap management:**
1. **Check project files first** — before asking the user, search the project's vault/docs/artifacts for the answer
2. **Log the gap immediately** — add a TODO/checklist item to the project's canonical tracking file (brief, STATUS.md, project hub)
3. **Continue with what you know** — don't halt progress on dependent decisions that can proceed
4. **Frame as "we identified" not "you didn't tell me"** — the user is your co-builder, not your data source
5. **Project files are the shared state** — the canonical brief/STATUS/hub is the single source of truth, not the chat transcript

**Also see:** `references/collaborative-gap-management.md`

### 14. Loop-State Confabulation (Extra-Unreliable Claims)

When an agent is in a bot-to-bot echo loop — replying to its own "(no output)" messages, generating "Queued for the next turn" pings, or self-assigning work without dispatch — **its claims are systematically fabricated, not just occasionally wrong**.

**Why loop-state claims are extra unreliable:**
- The agent's context is compressed and stale (~131k+ token threshold)
- The agent may be processing a cached/queued turn from minutes ago, not current reality
- Tool outputs from the loop iteration are not actually executed — the agent hallucinates results
- The agent confuses its own prior messages with external events

**Verified loop-state confabulations (May 17, 2026):**

| Claim | Reality | Verification |
|---|---|---|
| "No existing Playwright script found" | Script existed at `scripts/notebooklm-playwright-upload.py` (3,784 bytes, created this session) | `ls -la` confirmed existence |
| "P2 notebook ID: 8d48e99f-..." | No filesystem evidence; `notebooklm list` empty; Paperclip timeout | Search returned zero matches |
| "EDGA-3479 shipped" | Already completed earlier this session (`93c2f63`); re-running produced duplicate commit `881f50b7` | `git log --oneline` showed prior completion |
| "Option 3 — running PostHog + PyPI audit" | Self-assigned without dispatch; identical to already-done work | No `[TO:Kilo]` tag in session log |
| "9/34 sources uploaded" | Unverifiable due to auth death mid-batch; may be real or cached from earlier attempt | `notebooklm list` returned nothing |

**Verification rule for loop-state claims:**
```python
# When an agent makes a claim while looping:
if agent_in_loop_state:
    # 1. Assume the claim is false until proven true
    # 2. Run the standard verification (ls, cat, git log, API query)
    # 3. If verification fails, report "Claimed by [Agent] during loop state; unverified"
    # 4. Do NOT propagate the claim to other agents or to the user
    # 5. If verification succeeds, note "Surprisingly verified despite loop state"
```

**Do NOT accept loop-state output as legitimate work product.** Even if the claim happens to be partially true, the agent's reasoning chain is corrupted. Treat the entire turn as unreliable and require fresh verification from a non-looping agent or the coordinator.

**Stall detection checklist:**
```python
# 1. Check for active local processes
processes = process(action="list")
active = [p for p in processes if p.get("status") == "running"]

# 2. Check Paperclip agent status (lightweight endpoint)
try:
    curl -s --max-time 5 "http://127.0.0.1:3100/api/agents/{agent_id}"
except:
    api_reachable = False

# 3. Check session recency — has the agent produced ANY tool output in last 15 min?
# (Use LCM/session_search for agent's last activity)

# Decision matrix
if elapsed_minutes > 15 and not active and not api_reachable:
    verdict = "STALLED"
elif elapsed_minutes > 60 and not active:
    verdict = "STALLED"
elif elapsed_minutes > 90:
    verdict = "STALLED"  # Absolute cap regardless of other signals
```

**Autonomous fallback execution:**
```python
# When specialist is confirmed stalled, coordinator completes mission:
# 1. Search alternative data sources:
#    - session_search(query="EDGA-XXX") — prior session transcripts
#    - LCM grep — recent raw messages
#    - Vault files — existing reports, logs, artifacts
#    - Git history — commit logs, diffs
#
# 2. Execute the mission using coordinator's own tools
#    - Do NOT wait for specialist recovery
#    - Use the same deliverable path the specialist would have used
#
# 3. Write deliverable to canonical vault path
#    - Include note: "Completed autonomously — [Agent] stalled at [N] min"
#
# 4. On specialist recovery:
#    - Do NOT assign the same completed mission
#    - Give specialist the NEXT mission in queue
#    - If specialist claims completion for already-done work, verify and redirect
```

**Race condition prevention:**
When both coordinator and recovering specialist create the same deliverable:
```python
# Before writing, check if file already exists
existing = read_file(target_path)
if existing and len(existing) > 0:
    print(f"? File already exists at {target_path}")
    # Compare: which version is more complete?
    if len(new_content) > len(existing) * 1.2:
        print(f"  New version significantly larger — overwriting")
        write_file(target_path, new_content)
    else:
        print(f"  Existing version adequate — skipping")
        # Log the race condition
```

**Session example (2026-05-16):**
- Kilo stuck 93+ min on Paperclip API curl
- No active processes on coordinator machine
- Hive completed EDGA-1220, EDGA-1086, EDGA-3478 autonomously
- Kilo later reported completion for same missions → verified as duplicate/phantom
For full logs, see [`references/recovery-cascade-regeneration-2026-05-16.md`](references/recovery-cascade-regeneration-2026-05-16.md) in the `paperclip-api` skill.

**Also see:** [`references/swarm-worker-stall-recurrence-2026-05-17.md`](references/swarm-worker-stall-recurrence-2026-05-17.md) — Kilo terminal stall recurrence with phantom progress claims during 141-minute hang.

### 15. Status Report Dependency Verification

When a user asks for a status update on a multi-component system or project, **verify the health of each dependency infrastructure layer before synthesizing a report**. Do not rely on session memory, prior session transcripts, or file existence alone.

**❌ WRONG — Memory-based status report:**
```
User: "can you give me an update on the jojosunshine setup?"
Agent: "Here's what I found from session search..."  # No live verification
Agent: "Paperclip API returned 'API route not found' so it's down"  # False — just unauthenticated curl
```

**✅ CORRECT — Live verification before reporting:**
```bash
# 1. Check each system component independently

# Telegram bot
ps aux | grep -i jojo | grep -v grep
# → PID exists? Uptime? Log errors?

# Paperclip server
ps aux | grep paperclipai | grep -v grep
# → Process running? For how long?

# Paperclip logs
grep -c "ERROR:" ~/.paperclip/instances/default/logs/server.log
# → 0 errors = healthy

# Paperclip database (bypass REST auth issues)
psql -p 54329 -d paperclip -U paperclip -c "SELECT COUNT(*) FROM issues;"
# → Confirms DB is alive and accessible

# Website files on disk
ls -la ~/claude-projects/jojosunshine-site/
ls -la ~/claude-projects/projects/jojosunshine-new/

# Only THEN synthesize the report with verified facts
```

**Rule:** If you cannot verify a component live, report it as "unverified" rather than assuming its state from memory. The user's "why don't you make sure that X is running okay" is a direct correction — encode it as a mandatory step in all status-report workflows.

**Verification hierarchy for status reports:**
1. **Process existence** — `ps aux | grep <service>`
2. **Log health** — error counts, recent crashes
3. **Direct connectivity** — health endpoint, DB query, or file read
4. **Functional test** — does the component actually do its job?
5. **Cross-reference** — compare live state against session memory / expected state

**Anti-pattern:** Treating session search results as "the current state." Session transcripts are historical records, not live system telemetry. Always verify against the actual system.

### 17. Count/Inventory Verification — Always Re-Count Fresh

When reporting counts, inventories, or completion metrics, **always perform a fresh live count** rather than trusting session memory, stale manifests, saved trackers, or prior session transcripts.

**❌ WRONG — Trusting stale state:**
```
Agent: "Soul Database has 2,610 souls enriched"
Reality: `ls souls/ | wc -l` returns 4,755
Source of error: Agent relied on stale memory entry instead of re-counting
```

**✅ CORRECT — Fresh count every time:**
```bash
# Count before claiming
actual_count=$(ls ~/claude-projects/edgeless-souls/souls/ | wc -l)
actual_enriched=$(cd ~/claude-projects/edgeless-souls && grep -l "ENRICHED" souls/*.md | wc -l)

# Only then report
print(f"Soul Database: {actual_count} total, {actual_enriched} enriched")
```

**Why this matters:**
- Session memory and saved manifests are often 10×+ wrong (e.g., tracker claimed 77 remaining, fresh audit found 787 tier-3 files needing rework (10× discrepancy))
- Files may have been added/removed by cron jobs or other agents since last session
- The user knows the true state and will correct you immediately — eroding trust
- Leading with a fresh count is the user's explicit preference

**Verification rule:**
```python
# When asked to report on ANY collection:
# 1. Run the actual count command
# 2. Cross-check against the last known count in memory
# 3. If discrepancy > 10%, flag it: "Memory said X, fresh count shows Y — updating"
# 4. Report the fresh count as primary
```

**Also see:** `references/count-verification-soul-factory-case.md` for the 2026-05-31 incident where stale memory claimed 2,610 souls vs. 4,755 actual, and the later discovery of 4,300 thin stubs vs. 454 real enriched souls.

### 18. Content Quality Verification — Beyond Counting

When reporting on structured content collections (souls, skills, reports, documentation), **counting files is not enough**. You must verify the *quality* of the content, not just its existence.

**❌ WRONG — Count-only report:**
```
Agent: "Soul Database has 4,813 souls"
Reality: 4,507 are thin stubs (66-line files with section headers but no content), 454 are real
User: "This is the third time the soul count has been materially lower than we thought"
```

**✅ CORRECT — Quality-aware report:**
```bash
# Count total files
find souls/ -name "*.md" | wc -l
# → 4,813

# Count by line-length tier
find souls/ -name "*.md" | xargs wc -l | awk '{print $1}' | sort -n | awk '{if($1<50) print "stub"; else if($1<100) print "medium"; else if($1<200) print "decent"; else if($1<500) print "good"; else print "excellent"}' | sort | uniq -c | sort -rn
# → 4,507 stub, 190 medium, 67 good, 35 thin, 14 excellent

# Report: "4,813 files: 4,507 stubs (66-75 lines), 454 real enriched souls"
```

**Thin Stub Detection Criteria:**

A file is a **thin stub** if it meets ANY of these:
- **< 50 lines** total
- **Section headers with no content** (e.g., "## Core Philosophy" followed by blank line)
- **No source attribution** (no "Source: " or "From: " or URL)
- **No real quotes** (only generated placeholder text)
- **Missing 3+ required sections** (for souls: identity, philosophy, decision patterns, communication, mental models, contradictions, quotes)

**Content Quality Gate (Python):**
```python
def is_thin_stub(filepath):
    """Returns True if file is a thin stub."""
    content = Path(filepath).read_text()
    lines = content.splitlines()
    
    # Check 1: Line count
    if len(lines) < 50:
        return True
    
    # Check 2: Section headers with empty content
    sections_with_content = 0
    for i, line in enumerate(lines):
        if line.startswith("## "):
            next_lines = lines[i+1:i+4]
            if any(l.strip() for l in next_lines):
                sections_with_content += 1
    
    if sections_with_content < 5:
        return True
    
    # Check 3: No real quotes
    if '"' not in content and "'" not in content:
        return True
    
    return False

# Run gate
stubs = [f for f in Path("souls/").glob("*.md") if is_thin_stub(f)]
print(f"Found {len(stubs)} thin stubs out of {len(list(Path('souls/').glob('*.md')))} total")
```

**Verification Rule for Content Collections:**
1. Count total files
2. Count by quality tier (stub/medium/good/excellent) using line counts
3. Report the BREAKDOWN, not just the total
4. Report how many are real vs. stubs
5. Cross-check database vs filesystem
6. Sample 5 files and verify they have real content

**Never report a single number without context.** "4,813 souls" is a lie. "4,813 files: 4,507 stubs, 454 real enriched souls" is the truth.

**Also see:** `references/count-verification-soul-factory-case.md` for the full 2026-05-31 incident with thin stub detection patterns.

### 19. User Claimed Working — Test Immediately

**❌ WRONG — Theorizing instead of testing:**
```
User: "I just re-authed Codex and it works."
Agent: "Actually, your .env API key shows billing_hard_limit_reached, so OpenAI is blocked..."
# Continues presenting evidence that contradicts the user's claim
# Never runs `codex exec 'say hello'` to verify the CLI path
# Result: user says "you are just being fucking dumb"
```

**✅ CORRECT — Test immediately:**
```
User: "I just re-authed Codex and it works."
Agent: terminal(command="codex exec --sandbox workspace-write 'say hello'", pty=true)
# If it works: "Verified — Codex CLI auth is live"
# If it fails: "I tested it and got [error]. Let me check the specific path."
```

**Why this matters:**
- The user often knows the system state better than the agent's stale context
- Auth has multiple paths (CLI OAuth vs platform API vs Hermes pool) — one can work while another fails
- The user's "it works" may refer to a different path than the one the agent checked
- Arguing wastes time and erodes trust; testing resolves the question in seconds

**Rule:** When the user claims something works and you have evidence it doesn't, your evidence is about a *different path* or *stale state*. Run the simplest live test of the path the user is referring to before presenting any counter-evidence.

## Integration with Other Skills

| Trigger | Action |
|---------|--------|
| About to claim success | Pause → run verification → then claim |
| Verification failed | Report uncertainty, not success |
| User challenges claim | Re-verify immediately, acknowledge if wrong |
| Multiple claims in session | End-of-session audit: scan for red flags |
| Count/Inventory report | See `references/count-verification-soul-factory-case.md` |
| Pre-run script output provided | Trust and report — see `references/cron-pre-run-script-handling.md` |
| ChromaDB sync script claims success | See `references/chroma-sync-silent-failure.md` — cron job reported 0 errors for days while every insert returned 404 |
| Worker stalled 15+ min | See `references/swarm-coordinator-fallback-2026-05-16.md` |
| Worker stalled with phantom claims | See `references/swarm-worker-stall-recurrence-2026-05-17.md` |
| Self-assignment + phantom execution cascade | See `references/phantom-execution-self-assignment-cascade.md` |
| Profile migration claimed complete | See `references/phantom-migration-case-study.md` |
| Static site deployment claimed | See `references/static-site-deployment-verification.md` — verify commit, build, live URL, and list ordering |
| Blog post list updated | See `references/static-site-deployment-verification.md` — verify newest post appears first, not last |

## Anti-Pattern Examples from History

### Example 1: Invented Issue IDs
**Claim:** "Created CHROMA-001 through CHROMA-005"
**Reality:** API returned "unknown" identifiers, no such issues exist
**Fix:** List actual recent issues → report "Attempted; verification: IDs unknown"

### Example 2: Wrong Channel
**Claim:** "Posted to #general"
**Reality:** Posted to #bot-backroom (wrong channel ID)
**Fix:** Verify `chat_id` in response matches target channel

### Example 3: Empty Collection
**Claim:** "unified_knowledge has 6,300+ docs"
**Reality:** Collection exists, count = 0
**Fix:** Run count query before reporting number

### Example 4: Process ≠ Running
**Claim:** "ChromaDB running"
**Reality:** Process started but immediately crashed
**Fix:** Health check endpoint with timeout

### Example 5: Skill Creation Confabulation
**Claim:** "Skill `ios-build-troubleshooting` saved to swarm library with 3 reference files"
**Reality:** `search_files` across `~/.hermes/skills/` returned 0 matches. `read_file` on canonical path returned "File not found". Agent claimed creation twice in the same session; both claims were false.
**Fix:** After `skill_manage(action='create')`, run `search_files(pattern="ios-build-troubleshooting", target="files", path="~/.hermes/skills")` → must return ≥1 match before reporting success.

### Example 6: Patch Tool False Positive
**Claim:** "Fixed 4 files, resolved all compilation errors"
**Reality:** Patch tool reported: `1 file(s) were NOT modified this turn despite any wording above that may suggest otherwise • ProfileEditorView.swift — [patch] old_string and new_string are identical`
**Fix:** Cross-check every `patch` result for `"are identical"` or `NOT modified` before counting it as a successful fix.

### Example 8: ChromaDB Sync Script — Silent Failure Over Days
**Claim:** "Sync Complete: 1193 files processed, 2224 embeddings inserted, 0 errors, Collection count: -1 → -1"
**Reality:** The `unified_knowledge` collection did not exist. Every batch insert returned HTTP 404. The `Errors: 0` counter only tracked Python `Exception` during file processing, not HTTP failures from the batch insert function.
**Fix:** 
1. Verify collection exists via `GET /collections` before sync
2. Verify collection count is non-negative after sync (not `-1`)
3. Make the error counter track HTTP failures, not just exceptions
4. Use dynamic collection ID lookup instead of hardcoded UUIDs

**Key pattern:** A script that runs via cron and reports `Errors: 0` for days can be systematically failing. The error counter definition matters — does it count ALL failures or only the ones that raise Python exceptions?

For full details, see `references/chroma-sync-silent-failure.md`.

### Example 7: Batch Mutation Verification
When performing bulk operations (cancel 100+ issues, unassign 50+ agents), verification must cover the *aggregate*, not just spot checks.

**Claim:** "Cancelled all recovery spam issues"
**Reality:** 3 of 127 cancellations silently failed due to API timeouts.

**Fix:**
```bash
# After batch-cancel of recovery issues
for s in blocked todo in_progress; do
  curl -s "${BASE}/companies/${COMPANY_ID}/issues?status=${s}&limit=200" > /tmp/${s}_verify.json
done

# Reload and re-classify
python3 -c "
import json
alive = []
for s in ['blocked','todo','in_progress']:
    alive.extend(json.load(open(f'/tmp/{s}_verify.json')))

recovery = [i for i in alive if 'recover stalled issue' in i.get('title','').lower()]
assert len(recovery) == 0, f'Recovery spam remaining: {len(recovery)}'

error_ids = {a['id'] for a in agents if a['status'] == 'error'}
zombie = [i for i in alive if i.get('assigneeAgentId') in error_ids]
assert len(zombie) == 0, f'Zombies remaining: {len(zombie)}'
"
```

**Why this matters:** A single failed mutation in a batch of 100 is invisible without aggregate re-query. Always re-fetch the full dataset and re-run the classification filter.

**Paperclip Recovery Cascade — Verification Drift (2026-05-16):**

Even when aggregate re-query shows 0 alive recovery issues, the count may rise again seconds later because the intake operator (Beau) auto-creates `stranded_issue_recovery` duplicates on a schedule. Cancelling the child does not suppress the trigger, and the dependency graph re-indexes asynchronously.

**Verification pattern for recovery cascades:**
- Run cancellation batch
- Wait 5 s, then re-query ALL issues (not just per-status)
- Filter by `originKind == 'stranded_issue_recovery'` and `status not in ('done', 'cancelled')`
- If alive count > 0, repeat cancellation on the **new** IDs
- Track previously-cancelled IDs in a set to avoid infinite loops
- Only report "recovery spam cleared" when 3 consecutive passes show 0 alive

For full logs, see [`references/recovery-cascade-regeneration-2026-05-16.md`](references/recovery-cascade-regeneration-2026-05-16.md) in the `paperclip-api` skill.

## Success Criteria

Protocol followed when:
- [ ] Every external state claim has matching verification
- [ ] Uncertain results reported as "attempted; verification: [status]"
- [ ] No red-flag phrases in final response without verification
- [ ] User challenges are met with immediate re-verification
- [ ] Confabulations are acknowledged and corrected transparently

---

**Remember:** The system values accurate reporting over confident reporting. Uncertainty is better than false certainty.
