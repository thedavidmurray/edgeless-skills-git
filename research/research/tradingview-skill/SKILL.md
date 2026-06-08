---
name: tradingview-mcp
description: >
  TradingView market data and Pine Script automation via MCP progressive disclosure.
  78 on-demand tools for chart manipulation, indicator authoring, strategy backtesting,
  alerts, and UI automation. Loads only when invoked, saving ~15,600 tokens per session.
  Pair with tradingview-pine-automation for Pine Script authoring workflows.
version: 1.1.1
author: Critic (Paperclip Agent)
license: MIT
metadata:
  hermes:
    tags: [mcp, tradingview, progressive-disclosure, charting, pine-script, backtesting]
    tier: task-specific
    domain: research
    lazy_load: true
    mcp_source: tradingview
    related_skills: [tradingview-pine-automation]
prerequisites:
  commands: [python3, node]
  files: [~/.hermes/skills/research/tradingview-skill/proxy.py]
---

# TradingView MCP Tools

TradingView market data and Pine Script automation via progressive-disclosure MCP proxy.

## Overview

This skill wraps the TradingView MCP server (78 tools) into a lazy-loaded Hermes skill
interface. Tools are fetched on-demand when `skill_view('tradingview-mcp')` is called,
never at session startup. The underlying MCP server controls TradingView Desktop via
Chrome DevTools Protocol (CDP).

**Token efficiency:** 0 tokens until loaded; ~15,600 tokens saved per session vs native
MCP integration.

**Skill pairing:** For Pine Script authoring, syntax help, and strategy templates, use
tradingview-pine-automation. This skill provides the runtime execution layer;
tradingview-pine-automation provides the authoring layer.

## When to Use

- User needs to interact with a TradingView chart (change symbol, timeframe, indicators)
- User wants to automate Pine Script compilation, testing, or injection
- User needs strategy backtest results or equity curves from TradingView
- User wants to create alerts, manage watchlists, or take screenshots
- User needs real-time OHLCV data, quotes, or DOM depth from TradingView
- User wants to draw shapes, set price levels, or annotate charts programmatically
- User needs to replay bars or test strategies in replay mode
- User wants to run batch operations across multiple symbols/timeframes

## When NOT to Use

- TradingView Desktop is not installed or not running
- User only wants Pine Script syntax help (use tradingview-pine-automation instead)
- User wants financial data without chart interaction (use Alpaca, yfinance, or Polygon)
- User is on a headless server without GUI (TradingView Desktop requires display)
- One-off quick quote check (use web search or a data API instead)

## Prerequisites

### 1. TradingView Desktop

Install TradingView Desktop app (Mac/Windows/Linux). The MCP server auto-detects
install location.

### 2. TradingView MCP Server

The proxy expects the MCP server at:
```
/Users/djm/claude-projects/mcp-servers/tradingview-mcp/src/server.js
```

Ensure dependencies are installed:
```bash
cd /Users/djm/claude-projects/mcp-servers/tradingview-mcp
npm install
```

### 3. Node.js

Node.js must be available in PATH for the proxy to spawn the MCP server.

## Common Workflows

### Workflow: Analyze Current Chart

1. `tv_health_check` — verify CDP connection and chart state
2. `chart_get_state` — get symbol, timeframe, indicators
3. `data_get_ohlcv` (summary=true) — compact bar stats
4. `data_get_study_values` — read current indicator values
5. `quote_get` — real-time price data

### Workflow: Build and Test a Pine Strategy

1. `pine_new` — create blank script
2. `pine_set_source` — inject Pine code
3. `pine_analyze` — offline static analysis (catches array errors, loop bounds)
4. `pine_compile` — compile to chart
5. `pine_get_errors` — check Monaco markers
6. `data_get_strategy_results` — read performance metrics
7. `data_get_trades` — inspect trade list
8. `data_get_equity` — equity curve

### Workflow: Set Alerts and Backtest

1. `chart_set_symbol` + `chart_set_timeframe` — set target market
2. `alert_create` — create price or indicator alert
3. `alert_list` — verify alert exists
4. `replay_start` — begin bar replay at a specific date
5. `replay_step` / `replay_autoplay` — advance through history
6. `data_get_strategy_results` — evaluate strategy performance

### Workflow: Multi-Symbol Batch Scan

1. `batch_run` — run an action across multiple symbols/timeframes
2. `watchlist_add` — collect symbols into a watchlist
3. `watchlist_get` — scan prices, change, change%
4. `capture_screenshot` — save chart images for review

## Tool Categories

| Category | Tools | Purpose |
|----------|-------|---------|
| Connection | tv_health_check, tv_discover, tv_launch | CDP lifecycle |
| Chart | chart_get_state, chart_set_symbol, chart_set_timeframe, chart_set_type, chart_set_visible_range, chart_scroll_to_date | Chart configuration |
| Pine Script | pine_get_source, pine_set_source, pine_compile, pine_get_errors, pine_save, pine_new, pine_open, pine_list_scripts, pine_analyze, pine_check, pine_smart_compile | Strategy authoring |
| Data | data_get_ohlcv, data_get_indicator, data_get_strategy_results, data_get_trades, data_get_equity, quote_get, depth_get, data_get_study_values | Market data extraction |
| Pine Drawings | data_get_pine_lines, data_get_pine_labels, data_get_pine_tables, data_get_pine_boxes | Read indicator outputs |
| UI | ui_click, ui_open_panel, ui_fullscreen, ui_keyboard, ui_type_text, ui_hover, ui_scroll, ui_mouse_click, ui_find_element, ui_evaluate | DOM automation |
| Drawings | draw_shape, draw_list, draw_clear, draw_remove_one, draw_get_properties | Manual annotations |
| Alerts | alert_create, alert_list, alert_delete | Price alerts |
| Replay | replay_start, replay_step, replay_autoplay, replay_stop, replay_trade, replay_status | Bar replay testing |
| Layout | layout_list, layout_switch, pane_list, pane_set_layout, pane_focus, pane_set_symbol, tab_list, tab_new, tab_close, tab_switch | Multi-pane management |
| Watchlist | watchlist_get, watchlist_add | Symbol tracking |
| Batch | batch_run | Cross-symbol automation |
| Indicator | indicator_set_inputs, indicator_toggle_visibility, chart_manage_indicator | Study management |

## One-Shot Recipes

### Recipe: Screenshot a Chart at a Specific Timeframe

```python
# 1. Set chart
chart_set_symbol(symbol="AAPL")
chart_set_timeframe(timeframe="1D")

# 2. Wait for chart to load (ui_click or brief pause)
ui_click(selector=".chart-gui-wrapper")

# 3. Capture
capture_screenshot()
```

### Recipe: Validate Pine Script Without Chart Open

```python
# Use pine_check to compile via TradingView server API without chart
pine_check(source="""//@version=5\nindicator(\"Test\")\nplot(close)\n""")
# Returns errors/warnings if any
```

### Recipe: Read All Active Indicator Values

```python
# Get data window values for all visible studies
values = data_get_study_values()
# Returns: [{study_name, values: {plot_name: current_value}}]
```

## Common Pitfalls

1. **MCP server not running** — `tv_health_check` must return healthy before any chart
   or data tool works. If it fails, ensure TradingView Desktop is open and the MCP
   server `npm install` is complete.

2. **Pine compile without analysis** — Always run `pine_analyze` before `pine_compile`.
   It catches array out-of-bounds and loop errors offline without needing a chart.

3. **OHLCV data overload** — `data_get_ohlcv` returns all bars by default. Use
   `summary=true` for compact stats (open, high, low, close, volume, bar_count)
   unless you need individual bar data.

4. **UI selectors are brittle** — `ui_click` by CSS class can break on TradingView
   updates. Prefer `aria-label`, `data-name`, or text content selectors.

5. **Alert creation requires dialog** — `alert_create` opens the TradingView alert
   dialog. If it fails, the dialog may already be open or the symbol may not support
   alerts.

6. **Replay trades are simulated** — `replay_trade` executes in replay mode only.
   It does not place real orders.

7. **Batch run scope** — `batch_run` runs an action across symbols/timeframes but
   returns aggregated results. For per-symbol deep analysis, loop explicitly with
   `chart_set_symbol` + `data_get_ohlcv`.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `tv_health_check` returns unhealthy | TradingView Desktop not running | Launch TradingView Desktop first |
| `pine_compile` times out | Pine Script has infinite loop | Run `pine_analyze` first; check loop bounds |
| `chart_set_symbol` fails | Invalid symbol or no exchange specified | Use `symbol_search` to validate symbol |
| `ui_click` fails | Selector changed or element not visible | Use `ui_find_element` to locate current selector |
| `data_get_ohlcv` returns empty | Chart not loaded for symbol | Call `chart_get_state` to verify; wait for chart load |
| `capture_screenshot` is blank | Chart not focused or window minimized | Call `ui_fullscreen` or `ui_click` on chart first |

## Cross-Skill Reference

- **tradingview-pine-automation** — Pine Script v5 syntax, templates, webhook alerts,
  backtesting patterns. Use this skill for writing Pine code; use tradingview-mcp for
  executing it on the chart.

- **mcp-to-skill-proxy** — For converting other MCP servers into Hermes skills using
  the same progressive-disclosure pattern.

## Verification Checklist

- [ ] `tv_health_check` returns healthy before starting work
- [ ] `chart_get_state` returns expected symbol and timeframe
- [ ] `pine_analyze` runs without errors before `pine_compile`
- [ ] `data_get_ohlcv` (summary=true) returns non-empty stats
- [ ] `capture_screenshot` produces non-empty image file
- [ ] Token count before skill load: ~15,600; after load: 0 saved until invocation

## Implementation Notes

This skill uses the MCP-to-Skill proxy pattern:
1. `proxy.py` spawns the TradingView MCP server subprocess
2. Tool schemas are fetched on first `skill_view()` call
3. Tool calls route through the bridge back to the MCP server
4. Session persists across multiple tool calls within the same agent turn

Original MCP server: `tradingview` (stdio transport, Node.js)
Proxy location: `~/.hermes/skills/research/tradingview-skill/proxy.py`
