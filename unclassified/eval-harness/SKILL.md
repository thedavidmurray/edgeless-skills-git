---
name: eval-harness
title: Eval Harness
description: Formal evaluation framework for AI agent sessions implementing eval-driven development (EDD) principles. Define pass/fail criteria, measure agent reliability with pass@k metrics, create regression suites, benchmark across model versions.
category: software-development
related_skills:
  - verification-loop
  - test-driven-development
  - agent-introspection-debugging
triggers:
  - "eval driven"
  - "pass@k"
  - "regression test"
  - "agent reliability"
  - "benchmark agent"
  - "eval harness"
  - "EDD"
---

# Eval Harness

A formal evaluation framework for AI agent sessions, implementing eval-driven development (EDD) principles.

## When to Activate

- Setting up eval-driven development (EDD) for AI-assisted workflows
- Defining pass/fail criteria for agent task completion
- Measuring agent reliability with pass@k metrics
- Creating regression test suites for prompt or agent changes
- Benchmarking agent performance across model versions

## Philosophy

Eval-Driven Development treats evals as the "unit tests of AI development":
- Define expected behavior BEFORE implementation
- Run evals continuously during development
- Track regressions with each change
- Use pass@k metrics for reliability measurement

## Eval Types

### Capability Evals
Test if an agent can do something it couldn't before:
```markdown
[CAPABILITY EVAL: feature-name]
Task: Description of what the agent should accomplish
Success Criteria:
  - [ ] Criterion 1
  - [ ] Criterion 2
  - [ ] Criterion 3
Expected Output: Description of expected result
```

### Regression Evals
Ensure changes don't break existing functionality:
```markdown
[REGRESSION EVAL: feature-name]
Baseline: SHA or checkpoint name
Tests:
  - existing-test-1: PASS/FAIL
  - existing-test-2: PASS/FAIL
  - existing-test-3: PASS/FAIL
Result: X/Y passed (previously Y/Y)
```

## Grader Types

### 1. Code-Based Grader
Deterministic checks using code:
```bash
# Check if file contains expected pattern
grep -q "export function handleAuth" src/auth.ts && echo "PASS" || echo "FAIL"

# Check if tests pass
npm test -- --testPathPattern="auth" && echo "PASS" || echo "FAIL"

# Check if build succeeds
npm run build && echo "PASS" || echo "FAIL"
```

### 2. Model-Based Grader
Use an LLM to evaluate open-ended outputs:
```markdown
[MODEL GRADER PROMPT]
Evaluate the following code change:
1. Does it solve the stated problem?
2. Is it well-structured?
3. Are edge cases handled?
4. Is error handling appropriate?

Score: 1-5 (1=poor, 5=excellent)
Reasoning: [explanation]
```

### 3. Human Grader
Flag for manual review:
```markdown
[HUMAN REVIEW REQUIRED]
Change: Description of what changed
Reason: Why human review is needed
Risk Level: LOW/MEDIUM/HIGH
```

## Metrics

### pass@k
"At least one success in k attempts"
- pass@1: First attempt success rate
- pass@3: Success within 3 attempts
- Typical target: pass@3 > 90%

### pass^k
"All k trials succeed"
- Higher bar for reliability
- pass^3: 3 consecutive successes
- Use for critical paths

## Eval Workflow

### 1. Define (Before Coding)
```markdown
## EVAL DEFINITION: feature-xyz

### Capability Evals
1. Can create new user account
2. Can validate email format
3. Can hash password securely

### Regression Evals
1. Existing login still works
2. Session management unchanged
3. Logout flow intact

### Success Metrics
- pass@3 > 90% for capability evals
- pass^3 = 100% for regression evals
```

### 2. Implement
Write code to pass the defined evals.

### 3. Evaluate
```bash
# Run capability evals
[Run each capability eval, record PASS/FAIL]

# Run regression evals
npm test -- --testPathPattern="existing"

# Generate report
```

### 4. Report
```markdown
EVAL REPORT: feature-xyz
========================

Capability Evals:
  create-user:     PASS (pass@1)
  validate-email:  PASS (pass@2)
  hash-password:   PASS (pass@1)
  Overall:         3/3 passed

Regression Evals:
  login-flow:      PASS
  session-mgmt:    PASS
  logout-flow:     PASS
  Overall:         3/3 passed

Metrics:
  pass@1: 67% (2/3)
  pass@3: 100% (3/3)

Status: READY FOR REVIEW
```

## Integration with Hermes

### Pre-Implementation
Use `todo` to define evals before coding:
```
EVAL DEFINITION: feature-name
- Capability evals: [list]
- Regression evals: [list]
- Success metrics: pass@3 > 90%
```

### During Implementation
Run `verification-loop` continuously as evals pass.

### Post-Implementation
Use `delegate_task` to run evals in parallel subagents.

## Eval Storage

Store evals in project:
```
.hermes/
  evals/
    feature-xyz.md      # Eval definition
    feature-xyz.log     # Eval run history
    baseline.json       # Regression baselines
```

## Testing Infrastructure Pipelines

Infrastructure pipelines (sync, ETL, cron jobs) need different eval patterns than application code:

### 1. Create a Test Fixture First

Before evaluating the real pipeline, create a minimal test fixture:

```bash
# Create test vault with realistic file sizes
mkdir -p /tmp/test-vault/test-dir1 /tmp/test-vault/test-dir2
for i in {1..10}; do
  cat > /tmp/test-vault/test-dir1/file${i}.md << 'EOF'
# Test Document

This is a comprehensive test document for the sync pipeline.
It contains multiple paragraphs with varied content to ensure proper chunking.

The pipeline reads markdown files from the vault, splits them into overlapping chunks,
and embeds them into a ChromaDB collection for semantic search and retrieval.

## Technical Details

The sync pipeline performs several key operations:
- Scans the vault directory for markdown files
- Filters out files that are too small or match exclusion patterns
- Splits content into chunks with configurable overlap
- Embeds chunks via ChromaDB HTTP API
- Tracks progress and writes status reports

## Performance Considerations

For large vaults, the pipeline should:
- Apply limits during scan to avoid memory pressure
- Process files in batches for efficient embedding
- Handle errors gracefully without crashing
- Report meaningful metrics at completion

This document is intentionally long enough to produce multiple chunks.
EOF
done

# Check fixture sizes
find /tmp/test-vault -type f -exec ls -l {} \;
```

**Pitfall**: Test files that are too small (e.g., 100 bytes) will be skipped by `MIN_FILE_SIZE` guards, causing false "all files skipped" failures. Ensure fixture files exceed the pipeline's minimum size threshold.

### 2. Verify Infrastructure Before Testing

```bash
# Check if collection exists
curl -s -o /dev/null -w "%{http_code}" \
  http://localhost:8100/api/v2/tenants/default_tenant/databases/default_database/collections/<COLLECTION_ID>/count
# Expected: 200

# If 404, create the collection or update the pipeline's COLLECTION_ID
```

**Pitfall**: Testing against a missing collection produces 404 errors that look like pipeline bugs. Always verify the target infrastructure exists before evaluating the pipeline.

### 3. Apply Limits During Scan, Not After

```python
# ❌ WRONG: Scans entire vault then limits
markdown_files = list(self.VAULT_PATH.rglob("*.md"))
if self.limit:
    markdown_files = markdown_files[:self.limit]

# ✅ CORRECT: Limits during scan
if self.limit:
    markdown_files = []
    for p in self.VAULT_PATH.rglob("*.md"):
        markdown_files.append(p)
        if len(markdown_files) >= self.limit:
            break
else:
    markdown_files = list(self.VAULT_PATH.rglob("*.md"))
```

**Pitfall**: `rglob("*.md")` on a large vault (23K+ files) can hang indefinitely. Applying `--limit` after the full scan is useless — the scan itself is the bottleneck.

### 4. Use Python for Timeout (macOS Compatibility)

macOS does not have the `timeout` command. Use Python instead:

```python
# ❌ WRONG: macOS doesn't have `timeout`
timeout 30 python3 script.py

# ✅ CORRECT: Python subprocess with timeout
python3 -c "
import subprocess
result = subprocess.run(['python3', 'script.py'], timeout=30, capture_output=True)
print(result.stdout.decode())
"
```

### 5. Eval Checklist for Infrastructure

| Test | What to Verify | Common Pitfall |
|------|---------------|----------------|
| Pipeline completes | Status is success or completed_with_errors | Timeout from rglob on large dirs |
| Files scanned | total_files_scanned > 0 | All files skipped due to MIN_FILE_SIZE |
| Files processed | total_files_processed > 0 | Limit applied after scan, not during |
| Chunks created | total_chunks_created > 0 | Test files too small to chunk |
| Limit respected | total_files_scanned <= limit | Full scan ignores limit |
| No 404 errors | Collection exists before test | Hardcoded COLLECTION_ID mismatch |
| Spot-check dry-run | Correctly skipped in dry-run | Attempts queries on non-existent data |
| Empty vault guard | 0 files → status success | Crashes or reports failure |

### 6. Iterative Fix Pattern

When evals fail, fix one issue at a time and re-run:

1. **Fix**: Update `COLLECTION_ID` to existing collection
2. **Re-run**: Verify 404 errors disappear
3. **Fix**: Apply `--limit` during scan
4. **Re-run**: Verify timeout is resolved
5. **Fix**: Make `MIN_FILE_SIZE` configurable
6. **Re-run**: Verify test files are processed

**Target**: pass@1 = 100% for all capability evals before declaring the pipeline production-ready.

## Best Practices

1. **Define evals BEFORE coding** - Forces clear thinking about success criteria
2. **Run evals frequently** - Catch regressions early
3. **Track pass@k over time** - Monitor reliability trends
4. **Use code graders when possible** - Deterministic > probabilistic
5. **Human review for security** - Never fully automate security checks
6. **Keep evals fast** - Slow evals don't get run
7. **Version evals with code** - Evals are first-class artifacts
8. **Real-world examples in `references/`** - See `references/chroma-sync-eval-example.md` for a complete infrastructure pipeline eval
9. **Skill deployment eval pattern** - See `references/skill-deployment-eval.md` for testing newly deployed skills from external repos

## Example: Adding Authentication

```markdown
## EVAL: add-authentication

### Phase 1: Define (10 min)
Capability Evals:
- [ ] User can register with email/password
- [ ] User can login with valid credentials
- [ ] Invalid credentials rejected with proper error
- [ ] Sessions persist across page reloads
- [ ] Logout clears session

Regression Evals:
- [ ] Public routes still accessible
- [ ] API responses unchanged
- [ ] Database schema compatible

### Phase 2: Implement (varies)
[Write code]

### Phase 3: Evaluate
Run: /eval check add-authentication

### Phase 4: Report
EVAL REPORT: add-authentication
==============================
Capability: 5/5 passed (pass@3: 100%)
Regression: 3/3 passed (pass^3: 100%)
Status: SHIP IT
```

## Related

- `verification-loop` - for formal verification after code changes
- `test-driven-development` - for writing tests before code
- `agent-introspection-debugging` - for diagnosing repeated failures
- `proof-of-completion` - for verifying completions report an EFC
