# Reference: RUNE flux_report.py instance

Date: 2026-05-21
Context: RUNE paper-trading platform (formerly ETCC)
File: `/Users/djm/claude-projects/claude-vault/16-Projects/RUNE/06-FLUX/flux_report.py`

## What this instance does

P&L attribution dashboard for a multi-agent paper trading system.
Two agents (kilo, pamela) share one Alpaca account via virtual partition.
Dashboard separates P&L by `agent_id` so kilo's PMCC drawdowns never mix with pamela's theta trades.

## Schema specifics

`flux_trades` table: 22 columns including trade metadata, P&L, Greeks contribution (theta/vega/delta), execution slippage, IV at entry/exit, and `agent_id`.

`flux_regime_matrix` materialized view: GROUP BY agent_id, regime, strategy. Computes trade_count, win_count, avg_pnl_pct, sharpe, max_drawdown, avg_days_held.

## Simulated backfill

120 trades seeded across 2024-01 → 2025-05 with realistic distributions per strategy:
- PMCC: μ=+3.8%, σ=4.2
- EBCP: μ=+2.4%, σ=2.8
- 0DTE: μ=+1.2%, σ=2.5
- theta: μ=+0.9%, σ=1.8

## CLI surface

```
python3 flux_report.py                  # full attribution matrix
python3 flux_report.py --agent kilo     # kilo only
python3 flux_report.py --month 2025-03 # monthly filter
python3 flux_report.py --format csv     # CSV export
python3 flux_report.py --live           # open positions (mocked until ECHO live)
python3 flux_report.py --seed           # (re)seed simulated data
python3 flux_report.py --rebuild        # rebuild regime matrix
```

## Live wiring path

When ECHO starts producing real paper fills:
1. ECHO writes to `flux_trades` with `agent_id` tag (same schema)
2. Run `python3 flux_report.py --rebuild` to refresh the matrix
3. No code changes to `flux_report.py` needed — it is schema-native

## Key user constraint captured

User said: "i don't want new polling until we lock in the dashboard"
→ Phase 1 = static terminal report with simulated data. No polling, no web server, no live refresh.
Phase 2 (after ECHO operational) = lightweight Node WebSocket. Phase 3 (after 10 clean loops) = SENTRY Discord automation.

## Files

- `flux_report.py` — 300 lines, rich + sqlite3 (stdlib) + csv (stdlib)
- `data/flux.db` — SQLite, 61KB after 120 simulated trades
- `06-FLUX/README.md` — docs with CLI usage examples
