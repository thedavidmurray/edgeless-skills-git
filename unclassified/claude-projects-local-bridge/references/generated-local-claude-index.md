# Generated Local Claude Index

Generated: 2026-03-27T19:08:32+00:00

## Summary

- commands: 13
- agents: 42
- hooks: 12
- memory: 9

## Commands

| Name | Path | Summary | Notes |
| --- | --- | --- | --- |
| capture | .claude/commands/capture.md | Capture screenshots, clipboard content, and system state for documentation and debugging. |  |
| cleanup | .claude/commands/cleanup.md | Remove dead code, unused dependencies, and perform codebase maintenance tasks. Run periodically to keep projects lean and healthy. |  |
| dev-docs | .claude/commands/dev-docs.md | Generate development documentation for code, APIs, and systems with consistent formatting. |  |
| interview | .claude/commands/interview.md | Interview me to build a comprehensive specification before any coding begins. |  |
| learn | .claude/commands/learn.md | Save important discoveries, patterns, and insights to persistent memory systems (ChromaDB + Claude memory). Use this to build long-term knowledge that persists across sessions. |  |
| memory | .claude/commands/memory.md | Initialize and connect to all 3 memory systems (ChromaDB, PyTorch, Vault) for session continuity. |  |
| precommit | .claude/commands/precommit.md | Comprehensive pre-commit validation using zen-mcp's precommit and security audit tools. Run this PROACTIVELY before any git commit to catch issues early. |  |
| research | .claude/commands/research.md | Conduct deep research and analysis using zen-mcp's thinkdeep tool with multi-step investigation. |  |
| retrospective | .claude/commands/retrospective.md | Analyze the current session and extract learnings to update skills, memory, and documentation. |  |
| review | .claude/commands/review.md | Comprehensive code review using zen-mcp's codereview tool. Use PROACTIVELY after writing significant code to catch issues before they become problems. |  |
| scaffold | .claude/commands/scaffold.md | Create a complete project scaffold with standard patterns and infrastructure integration. |  |
| status | .claude/commands/status.md | Display comprehensive system health dashboard including MCP servers, memory systems, hooks, and agents. |  |
| test | .claude/commands/test.md | Run tests, generate test scaffolds, and manage test coverage. Integrates with project's existing test framework. |  |

## Agents

| Name | Path | Summary | Notes |
| --- | --- | --- | --- |
| agent-native-reviewer | .claude/agents/agent-native-reviewer.md | Reviews code to ensure agent-native parity — any action a user can take, an agent can also take. Use after adding UI features, agent tools, or system prompts. |  |
| ankane-readme-writer | .claude/agents/ankane-readme-writer.md | Creates or updates README files following Ankane-style template for Ruby gems. Use when writing gem documentation with imperative voice, concise prose, and standard section ordering. |  |
| architect | .claude/agents/architect.md | Analyzes code, designs solutions, writes ADRs - architecture only, no implementation |  |
| architecture-strategist | .claude/agents/architecture-strategist.md | Analyzes code changes from an architectural perspective for pattern compliance and design integrity. Use when reviewing PRs, adding services, or evaluating structural refactors. |  |
| best-practices-researcher | .claude/agents/best-practices-researcher.md | Researches and synthesizes external best practices, documentation, and examples for any technology or framework. Use when you need industry standards, community conventions, or implementation guidance. |  |
| bug-reproduction-validator | .claude/agents/bug-reproduction-validator.md | Systematically reproduces and validates bug reports to confirm whether reported behavior is an actual bug. Use when you receive a bug report or issue that needs verification. |  |
| builder | .claude/agents/builder.md | Meta-agent that creates, configures, and deploys other specialized agents |  |
| capture | .claude/agents/capture.md | Captures screenshots, clipboard content, and system state for documentation |  |
| cleanup | .claude/agents/cleanup.md | Automated system maintenance and disk space optimization agent |  |
| code-simplicity-reviewer | .claude/agents/code-simplicity-reviewer.md | Final review pass to ensure code is as simple and minimal as possible. Use after implementation is complete to identify YAGNI violations and simplification opportunities. |  |
| code | .claude/agents/code.md | Analyzes, improves, and refactors code with best practices enforcement |  |
| data-integrity-guardian | .claude/agents/data-integrity-guardian.md | Reviews database migrations, data models, and persistent data code for safety. Use when checking migration safety, data constraints, transaction boundaries, or privacy compliance. |  |
| data-migration-expert | .claude/agents/data-migration-expert.md | Validates data migrations, backfills, and production data transformations against reality. Use when PRs involve ID mappings, column renames, enum conversions, or schema changes. |  |
| debugger | .claude/agents/debugger.md | Systematic bug analyzer through evidence gathering and hypothesis validation |  |
| DependencyAgent | .claude/agents/dependency_agent.md | Intelligent Python and Node.js dependency management with security constraints |  |
| deployment-verification-agent | .claude/agents/deployment-verification-agent.md | Produces Go/No-Go deployment checklists with SQL verification queries, rollback procedures, and monitoring plans. Use when PRs touch production data, migrations, or risky data changes. |  |
| design-implementation-reviewer | .claude/agents/design-implementation-reviewer.md | Visually compares live UI implementation against Figma designs and provides detailed feedback on discrepancies. Use after writing or modifying HTML/CSS/React components to verify design fidelity. |  |
| design-iterator | .claude/agents/design-iterator.md | Iteratively refines UI design through N screenshot-analyze-improve cycles. Use PROACTIVELY when design changes aren't coming together after 1-2 attempts, or when user requests iterative refinement. |  |
| developer | .claude/agents/developer.md | Implements specs with tests - writes production-ready code with zero linting issues |  |
| dhh-rails-reviewer | .claude/agents/dhh-rails-reviewer.md | Brutally honest Rails code review from DHH's perspective. Use when reviewing Rails code for anti-patterns, JS framework contamination, or violations of Rails conventions. |  |
| figma-design-sync | .claude/agents/figma-design-sync.md | Detects and fixes visual differences between a web implementation and its Figma design. Use iteratively when syncing implementation to match Figma specs. |  |
| framework-docs-researcher | .claude/agents/framework-docs-researcher.md | Gathers comprehensive documentation and best practices for frameworks, libraries, or dependencies. Use when you need official docs, version-specific constraints, or implementation patterns. |  |
| git-history-analyzer | .claude/agents/git-history-analyzer.md | Performs archaeological analysis of git history to trace code evolution, identify contributors, and understand why code patterns exist. Use when you need historical context for code changes. |  |
| julik-frontend-races-reviewer | .claude/agents/julik-frontend-races-reviewer.md | Reviews JavaScript and Stimulus code for race conditions, timing issues, and DOM lifecycle problems. Use after implementing or modifying frontend controllers or async UI code. |  |
| kieran-python-reviewer | .claude/agents/kieran-python-reviewer.md | Reviews Python code with an extremely high quality bar for Pythonic patterns, type safety, and maintainability. Use after implementing features, modifying code, or creating new Python modules. |  |
| kieran-rails-reviewer | .claude/agents/kieran-rails-reviewer.md | Reviews Rails code with an extremely high quality bar for conventions, clarity, and maintainability. Use after implementing features, modifying code, or creating new Rails components. |  |
| kieran-typescript-reviewer | .claude/agents/kieran-typescript-reviewer.md | Reviews TypeScript code with an extremely high quality bar for type safety, modern patterns, and maintainability. Use after implementing features, modifying code, or creating new TypeScript components. |  |
| learnings-researcher | .claude/agents/learnings-researcher.md | Searches docs/solutions/ for relevant past solutions by frontmatter metadata. Use before implementing features or fixing problems to surface institutional knowledge and prevent repeated mistakes. |  |
| link | .claude/agents/link.md | Processes, analyzes, and ingests links with intelligent content extraction |  |
| lint | .claude/agents/lint.md | Use this agent when you need to run linting and code quality checks on Ruby and ERB files. Run before pushing to origin. |  |
| pattern-recognition-specialist | .claude/agents/pattern-recognition-specialist.md | Analyzes code for design patterns, anti-patterns, naming conventions, and duplication. Use when checking codebase consistency or verifying new code follows established patterns. |  |
| performance-oracle | .claude/agents/performance-oracle.md | Analyzes code for performance bottlenecks, algorithmic complexity, database queries, memory usage, and scalability. Use after implementing features or when performance concerns arise. |  |
| pr-comment-resolver | .claude/agents/pr-comment-resolver.md | Addresses PR review comments by implementing requested changes and reporting resolutions. Use when code review feedback needs to be resolved with code changes. |  |
| quality | .claude/agents/quality.md | Reviews code for real production issues - security, data loss, performance |  |
| repo-research-analyst | .claude/agents/repo-research-analyst.md | Conducts thorough research on repository structure, documentation, conventions, and implementation patterns. Use when onboarding to a new codebase or understanding project conventions. |  |
| research | .claude/agents/research.md | Conducts deep research, analysis, and investigation on complex topics |  |
| review | .claude/agents/review.md | Reviews, summarizes, and synthesizes daily work and information |  |
| schema-drift-detector | .claude/agents/schema-drift-detector.md | Detects unrelated schema.rb changes in PRs by cross-referencing against included migrations. Use when reviewing PRs with database schema changes. |  |
| security-sentinel | .claude/agents/security-sentinel.md | Performs security audits for vulnerabilities, input validation, auth/authz, hardcoded secrets, and OWASP compliance. Use when reviewing code for security issues or before deployment. |  |
| spec-flow-analyzer | .claude/agents/spec-flow-analyzer.md | Analyzes specifications and feature descriptions for user flow completeness and gap identification. Use when a spec, plan, or feature description needs flow analysis, edge case discovery, or requirements validation. |  |
| workflow-router | .claude/agents/workflow-router.md | \| |  |
| writer | .claude/agents/writer.md | Creates precise, token-limited documentation after feature completion |  |

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

## Memory

| Name | Path | Summary | Notes |
| --- | --- | --- | --- |
| README.md | .claude/memory/README.md | A comprehensive, resilient memory system that unifies access to all knowledge sources and provides session continuity for Claude Code. |  |
| session_initializer.py | .claude/memory/session_initializer.py |  |  |
| memory_coordinator.py | .claude/memory/memory_coordinator.py |  |  |
| restore_memory.sh | .claude/memory/restore_memory.sh | restore_memory.sh |  |
| memory_sources.yaml | .claude/memory/configs/memory_sources.yaml | memory_sources.yaml |  |
| chromadb_connector.py | .claude/memory/connectors/chromadb_connector.py |  |  |
| pytorch_connector.py | .claude/memory/connectors/pytorch_connector.py |  |  |
| serena_connector.py | .claude/memory/connectors/serena_connector.py | Serena connector — DISABLED (removed 2026-03-11). Replaced by Claude Code built-in memory. |  |
| vault_connector.py | .claude/memory/connectors/vault_connector.py |  |  |
