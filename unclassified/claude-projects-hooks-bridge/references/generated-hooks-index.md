## Hooks

| Name | Path | Summary | Notes |
| --- | --- | --- | --- |
| damage-control.py | .claude/hooks/damage-control.py |  | events=PreToolUse,PreToolUse,PreToolUse,PreToolUse; matchers=Bash,Write,Edit,Read |
| inbox-auto-claim.py | .claude/hooks/inbox-auto-claim.py |  | events=UserPromptSubmit; matchers=* |
| loop-stop-hook.py | .claude/hooks/loop-stop-hook.py |  | events=Stop; matchers=* |
| post-tool-tracker.py | .claude/hooks/post-tool-tracker.py |  | events=PostToolUse; matchers=* |
| pre-compact.py | .claude/hooks/pre-compact.py |  | events=PreCompact; matchers=* |
| sandbox-observer.py | .claude/hooks/sandbox-observer.py |  | events=PostToolUse; matchers=* |
| session-end.py | .claude/hooks/session-end.py |  | events=Stop; matchers=* |
| session-start.py | .claude/hooks/session-start.py |  |  |
| skill-activation.py | .claude/hooks/skill-activation.py |  | events=UserPromptSubmit; matchers=* |
| trading-observer.py | .claude/hooks/trading-observer.py |  | events=PostToolUse; matchers=* |
| verify-completion.py | .claude/hooks/verify-completion.py |  |  |
| webfetch-archive.py | .claude/hooks/webfetch-archive.py |  | events=PostToolUse; matchers=* |
