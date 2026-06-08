---
name: tradingview-pine-automation
title: TradingView Pine Script Automation
description: >
  Pine Script v5 automation for TradingView — build indicators, strategies, alerts,
  and backtests. Covers syntax, built-in functions, common patterns, and alert
  webhook integration.
version: 1.1.0
author: Builder Agent
metadata:
  tags: [tradingview, pine-script, trading, automation, alerts, backtesting, indicators]
  tier: task-specific
  domain: research
---

# TradingView Pine Script Automation

Build trading indicators, strategies, alerts, and backtests using Pine Script v5 on TradingView.

## When to Use

- User asks for trading indicator (RSI, MACD, moving averages, custom oscillators)
- User wants a trading strategy with entry/exit rules
- User needs TradingView alerts with webhook integration
- User wants to backtest a strategy on historical data
- User asks about Pine Script syntax or built-in functions
- User needs to convert a trading idea into executable Pine code

## Templates (Copy/Paste Starters)

These are ready-to-use Pine v5 starters under:
`templates/`

- `templates/ma_crossover_strategy.pine` — minimal MA crossover strategy + alerts
- `templates/rsi_indicator.pine` — RSI indicator with multi-level coloring + alertconditions
- `templates/webhook_alerts.pine` — multi-signal webhook-style alert system (uses TradingView `{{...}}` placeholders)
- `templates/risk-management.pine` — ATR-based stops, position sizing, daily loss limits, trailing stops
- `templates/factor-rotation-automated.pine` — multi-factor ETF regime rotation with monthly rebalancing
- `templates/zerodte-theta-automated.pine` — same-day options theta capture with IV rank filtering

## Pine Script v5 Basics

### Script Structure

```pinescript
//@version=5
indicator("My Indicator", shorttitle="MI", overlay=true)
// OR
strategy("My Strategy", shorttitle="MS", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10)

// Inputs
length = input.int(14, "Length", minval=1)
src = input.source(close, "Source")

// Calculations
ma = ta.sma(src, length)

// Plotting
plot(ma, "MA", color=color.blue)
// OR for strategies
if ta.crossover(close, ma)
    strategy.entry("Long", strategy.long)
if ta.crossunder(close, ma)
    strategy.close("Long")
```

### Key Directives

| Directive | Purpose |
|-----------|---------|
| `//@version=5` | Required - specifies Pine Script version |
| `indicator()` | For studies/indicators (no trading) |
| `strategy()` | For backtestable trading strategies |
| `library()` | For reusable function libraries |

### Common Built-in Functions

Moving Averages:
- `ta.sma(source, length)` - Simple Moving Average
- `ta.ema(source, length)` - Exponential Moving Average
- `ta.wma(source, length)` - Weighted Moving Average
- `ta.vwma(source, length)` - Volume Weighted Moving Average
- `ta.hma(source, length)` - Hull Moving Average

Oscillators:
- `ta.rsi(source, length)` - Relative Strength Index
- `ta.macd(source, fastlen, slowlen, siglen)` - MACD
- `ta.stoch(source, high, low, length)` - Stochastic
- `ta.cci(source, length)` - Commodity Channel Index
- `ta.atr(length)` - Average True Range

Trend/Momentum:
- `ta.adx(high, low, close, length)` - ADX
- `ta.obv(close, volume)` - On Balance Volume
- `ta.mfi(high, low, close, volume, length)` - Money Flow Index
- `ta.cmo(source, length)` - Chande Momentum Oscillator

Pattern Recognition:
- `ta.crossover(x, y)` - True when x crosses above y
- `ta.crossunder(x, y)` - True when x crosses below y
- `ta.pivothigh(source, leftbars, rightbars)` - Pivot high
- `ta.pivotlow(source, leftbars, rightbars)` - Pivot low

### Variables and Types

```pinescript
// Simple types
myInt = 10
myFloat = 10.5
myBool = true
myColor = color.red
myString = "Hello"

// Series (time-series data)
mySeries = close  // Built-in: open, high, low, close, volume, hl2, hlc3, ohlc4

// Arrays (Pine v5)
myArray = array.new_float(10, 0.0)
array.set(myArray, 0, close)
value = array.get(myArray, 0)

// Matrices (Pine v5)
myMatrix = matrix.new<float>(3, 3, 0.0)
```

### Variable Declaration Modifiers

```pinescript
// var: Initialize once, persist across bars
var line myLine = na
if condition
    line.delete(myLine)
    myLine := line.new(bar_index, high, bar_index, low, color=color.red)

// varip: Initialize once, update on every price change within the bar (intrabar)
varip float lastTickPrice = 0.0
lastTickPrice := close

// Regular: Recalculated on every bar
regularValue = close + 1  // New value every bar
```

### Library Functions

```pinescript
//@version=5
library("MyLibrary", overlay=true)

// Export a function for use in other scripts
export calculate_rsi(length) =>
    ta.rsi(close, length)

// Export with default parameter
export ema_with_color(src, length=20) =>
    ema = ta.ema(src, length)
    col = ema > ema[1] ? color.green : color.red
    [ema, col]
```

Use in another script:
```pinescript
//@version=5
import user/MyLibrary/1 as lib

[myEma, myColor] = lib.ema_with_color(close, 14)
plot(myEma, color=myColor)
```

## Strategy Automation

### Entry and Exit

```pinescript
strategy("My Strategy", overlay=true)

// Entry conditions
longCondition = ta.crossover(ta.sma(close, 10), ta.sma(close, 30))
shortCondition = ta.crossunder(ta.sma(close, 10), ta.sma(close, 30))

// Execute trades
if longCondition
    strategy.entry("Long", strategy.long)

if shortCondition
    strategy.close("Long")  // Close long position
    // OR: strategy.entry("Short", strategy.short) for short selling

// Stop loss and take profit
strategy.exit("Exit Long", "Long", stop=close * 0.95, limit=close * 1.10)
```

### Strategy Parameters

```pinescript
strategy("Optimized Strategy",
     overlay=true,
     initial_capital=10000,
     default_qty_type=strategy.percent_of_equity,
     default_qty_value=10,
     commission_type=strategy.commission.percent,
     commission_value=0.1,
     slippage=1)
```

### Complete Strategy Parameters Reference

| Parameter | Type | Description | Common Values |
|-----------|------|-------------|---------------|
| `title` | string | Strategy name (required) | `"My Strategy"` |
| `shorttitle` | string | Short display name | `"MS"` |
| `overlay` | bool | Overlay on price chart | `true`, `false` |
| `initial_capital` | int | Starting capital | `10000`, `100000` |
| `default_qty_type` | enum | Position sizing method | `strategy.fixed`, `strategy.percent_of_equity`, `strategy.cash`, `strategy.contracts` |
| `default_qty_value` | float | Position size value | `10` (percent), `100` (fixed) |
| `commission_type` | enum | Commission model | `strategy.commission.percent`, `strategy.commission.cash` |
| `commission_value` | float | Commission amount | `0.1` (percent), `1.0` (cash) |
| `slippage` | int | Slippage ticks | `0`, `1`, `2` |
| `max_lines_count` | int | Max lines on chart | `500`, `1000` |
| `max_bars_back` | int | Max bars in history | `5000` |
| `max_lines_back` | int | Max lines history | `100` |
| `precision` | int | Decimal precision | `2`, `4`, `8` |
| `scale` | enum | Panel scale | `scale.left`, `scale.right`, `scale.none` |
| `pyramiding` | int | Max entries in same direction | `0`, `1`, `10` |
| `calc_on_order_fills` | bool | Recalculate on fill | `true`, `false` |
| `calc_on_every_tick` | bool | Recalculate on every tick | `true`, `false` |
| `process_orders_on_close` | bool | Process orders at bar close | `true`, `false` |
| `close_entries_rule` | enum | Close order priority | `"FIFO"`, `"ANY"` |
| `currency` | string | Account currency | `"USD"`, `"EUR"` |
| `use_bar_magnifier` | bool | Use bar magnifier for backtesting | `true`, `false` |

### Risk Management

```pinescript
// Position sizing based on ATR
atr = ta.atr(14)
riskPercent = input.float(1.0, "Risk %")
accountRisk = strategy.equity * riskPercent / 100
stopDistance = atr * 2
positionSize = accountRisk / stopDistance

if longCondition
    strategy.entry("Long", strategy.long, qty=positionSize)
    strategy.exit("SL", "Long", stop=close - stopDistance)
```

## Alert Automation

### Basic Alerts

```pinescript
alertcondition(longCondition, title="Long Signal", message='{"action": "buy", "ticker": "{{ticker}}", "price": {{close}}}')
```

### alert() vs alertcondition()

| Function | Use Case | When It Fires | Can Use `{{ticker}}` Placeholders |
|----------|----------|---------------|-----------------------------------|
| `alertcondition()` | Create reusable alert conditions | Only when user manually sets an alert in UI | Yes |
| `alert()` | Programmatic real-time alerts | Immediately in code (no manual setup) | No (use `str.tostring()` instead) |

```pinescript
// alertcondition: User must manually create an alert in TradingView UI
alertcondition(longCondition, title="Buy Signal", message='{"action": "buy", "ticker": "{{ticker}}"}')

// alert: Fires immediately when condition is met
if longCondition
    alert('{"action": "buy", "symbol": "' + syminfo.ticker + '", "price": ' + str.tostring(close) + '}', alert.freq_once_per_bar_close)
```

### Dynamic Alerts with Webhooks

```pinescript
// Build alert message
alertMsg = '{"action": "' + (longCondition ? "buy" : shortCondition ? "sell" : "hold") + '", "symbol": "' + syminfo.ticker + '", "price": ' + str.tostring(close) + ', "time": "' + str.tostring(time) + '"}'

// Trigger on bar close
if longCondition or shortCondition
    alert(alertMsg, alert.freq_once_per_bar_close)
```

### Webhook Integration

TradingView Pro/Premium users can configure webhook URLs in alert settings:
1. Create alert with the indicator/strategy
2. Set webhook URL (e.g., `https://your-trading-bot.com/webhook`)
3. Use JSON message format in alert
4. Your server receives POST with JSON payload

### Multi-Timeframe Alerts

```pinescript
// Get higher timeframe data
htfClose = request.security(syminfo.tickerid, "D", close)
htfRsi = request.security(syminfo.tickerid, "D", ta.rsi(close, 14))

// Alert only when HTF and current TF align
tfAlignment = close > ta.sma(close, 20) and htfClose > ta.sma(htfClose, 20)
alertcondition(tfAlignment, title="HTF Alignment", message="Multi-TF buy signal")
```

### Critical Pine Script v5 Limitations

**A strategy can ONLY trade the symbol of the chart it is running on.** You cannot pass a ticker symbol to `strategy.entry()` or trade multiple symbols from a single script. To implement multi-symbol strategies (like factor rotation):

1. **Run the strategy on a single symbol** (e.g., SPY as a market proxy)
2. **Use `request.security()` to fetch data** from other symbols for regime detection
3. **Use `alert()` to fire webhook signals** to an external execution engine that handles the actual multi-symbol trades
4. **Or use `input.symbol()` + `request.security()`** to make decisions on the current chart based on external symbol data

```pinescript
// CORRECT: Use request.security for data, trade current chart symbol
spy_data = request.security("SPY", timeframe.period, close)
qqq_data = request.security("QQQ", timeframe.period, close)

// Decision based on QQQ/SPY ratio
is_growth = qqq_data > ta.sma(qqq_data, 20)

// Trade only the current chart's symbol
if is_growth
    strategy.entry("Long", strategy.long)

// INCORRECT: strategy.entry does NOT accept a ticker symbol
// strategy.entry("Long", strategy.long, "QQQ")  // ERROR
```

## Common Patterns

### Moving Average Crossover

```pinescript
//@version=5
strategy("MA Crossover", overlay=true)
fastLength = input.int(10, "Fast MA")
slowLength = input.int(30, "Slow MA")

fastMA = ta.sma(close, fastLength)
slowMA = ta.sma(close, slowLength)

plot(fastMA, color=color.blue)
plot(slowMA, color=color.orange)

longCondition = ta.crossover(fastMA, slowMA)
shortCondition = ta.crossunder(fastMA, slowMA)

if longCondition
    strategy.entry("Long", strategy.long)
if shortCondition
    strategy.close("Long")
```

### RSI Overbought/Oversold

```pinescript
//@version=5
indicator("RSI Strategy", overlay=false)
rsiLength = input.int(14, "RSI Length")
oversold = input.int(30, "Oversold")
overbought = input.int(70, "Overbought")

rsi = ta.rsi(close, rsiLength)
plot(rsi, "RSI", color=color.purple)
hline(overbought, "Overbought", color=color.red)
hline(oversold, "Oversold", color=color.green)

bgcolor(rsi < oversold ? color.green : rsi > overbought ? color.red : na)
```

### Bollinger Bands

```pinescript
//@version=5
indicator("Bollinger Bands", overlay=true)
length = input.int(20, "Length")
mult = input.float(2.0, "Multiplier")

basis = ta.sma(close, length)
dev = mult * ta.stdev(close, length)
upper = basis + dev
lower = basis - dev

plot(basis, "Basis", color=color.orange)
p1 = plot(upper, "Upper", color=color.blue)
p2 = plot(lower, "Lower", color=color.blue)
fill(p1, p2, color=color.new(color.blue, 90))
```

### Supertrend

```pinescript
//@version=5
indicator("Supertrend", overlay=true)
atrPeriod = input.int(10, "ATR Period")
factor = input.float(3.0, "Factor")

atr = ta.atr(atrPeriod)
hl2 = (high + low) / 2

upperBand = hl2 + factor * atr
lowerBand = hl2 - factor * atr

var float prevUpperBand = upperBand
var float prevLowerBand = lowerBand
var int trend = 1

if close[1] > prevUpperBand
    trend := 1
else if close[1] < prevLowerBand
    trend := -1

upperBand := trend == 1 and upperBand < prevUpperBand ? prevUpperBand : upperBand
lowerBand := trend == -1 and lowerBand > prevLowerBand ? prevLowerBand : lowerBand

prevUpperBand := upperBand
prevLowerBand := lowerBand

plot(trend == 1 ? lowerBand : upperBand, "Supertrend", color=trend == 1 ? color.green : color.red)
```

## Advanced Techniques

### Session-Based Trading

```pinescript
// Only trade during specific hours
inSession = hour >= 9 and hour < 16 and dayofweek != dayofweek.saturday and dayofweek != dayofweek.sunday

if longCondition and inSession
    strategy.entry("Long", strategy.long)
```

### Table Output

```pinescript
// Display metrics on chart
var table stats = table.new(position.top_right, 2, 5, bgcolor=color.black)

if barstate.islast
    table.cell(stats, 0, 0, "Win Rate", text_color=color.white)
    table.cell(stats, 1, 0, str.tostring(strategy.closedtrades.winning / strategy.closedtrades * 100, "#.##") + "%", text_color=color.green)
    table.cell(stats, 0, 1, "Profit", text_color=color.white)
    table.cell(stats, 1, 1, "$" + str.tostring(strategy.closedtrades.profit), text_color=color.white)
```

### Drawing Objects

```pinescript
// Draw lines and labels
var line supportLine = na
if ta.pivotlow(low, 5, 5)
    line.delete(supportLine)
    supportLine := line.new(bar_index[5], low[5], bar_index, low, color=color.green, style=line.style_dashed)

// Labels
if longCondition
    label.new(bar_index, low, "BUY", color=color.green, textcolor=color.white, style=label.style_label_up)
```

## Debugging Tips

1. Use `plot()` for variables: `plot(rsi, "Debug RSI")` shows values on chart
2. Use `log.info()`: `log.info("RSI value: {0}", rsi)` outputs to Pine Logs
3. Check compilation errors: Hover over red squiggles for error details
4. Use Data Window: Click the {} icon to see all variable values
5. Plot shapes for signals: `plotshape(longCondition, "Long", shape.triangleup, location.belowbar, color.green)`

## External Resources

- Pine Script v5 Reference: https://www.tradingview.com/pine-script-reference/v5/
- Pine Script Tutorial: https://www.tradingview.com/pine-script-docs/en/v5/primer/
- TradingView Ideas: https://www.tradingview.com/ideas/
- PineCoders: https://www.pinecoders.com/ (community resources)
