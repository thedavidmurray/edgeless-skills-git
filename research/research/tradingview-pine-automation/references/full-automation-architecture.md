# Full Automation Architecture for TradingView

**For zero-manual-step automated trading systems using TradingView + PineScript.**

## Complete End-to-End System

```
TradingView Charts (PineScript v5)
  ↓ Webhook POST
Flask Webhook Server (port 5000)
  ↓ Signal validation
Risk Manager (automated kill switches)
  ↓ Kelly criterion sizing
Execution Engine (Alpaca API)
  ↓ Paper or live trading
Discord Monitor (alerts only, no decisions)
```

**CRITICAL:** No manual approval steps. All decisions pre-programmed.

---

## Why Mock Data Validation Fails

**LESSON LEARNED:** Paper trading with simulated/mock data is worthless for validating strategy edge.

- Mock prices follow random walk (no theta decay, no factor premiums)
- Technical indicators lose money in simulation AND live (as predicted)
- Only mathematical edges (theta, factors, arbitrage) have predictable alpha
- **Real validation requires:** Real market data OR small live deployment

**Session Evidence:**
- Technical strategies (MA crossover, RSI): Sharpe 0.4 to -0.87 in backtest, 0% win rate in simulation
- Quantitative strategies (theta, factors): Backtest validated but simulation corrupts due to random walk
- Result: Mock data cannot distinguish between genuine edge and noise

---

## Kelly Criterion Position Sizing

Automated position sizing using Kelly criterion (quarter-Kelly for safety):

```python
def calculate_kelly_size(win_rate: float, avg_win: float, avg_loss: float) -> float:
    """
    Kelly criterion: f* = (bp - q) / b
    Quarter-Kelly for reduced variance
    """
    if avg_loss == 0 or win_rate <= 0:
        return 0.0
    
    b = avg_win / avg_loss  # Odds
    p = win_rate
    q = 1 - p
    
    kelly = (b * p - q) / b
    quarter_kelly = max(0, kelly / 4)  # Conservative
    
    # Cap at 5% max per position
    return min(quarter_kelly, 0.05)
```

**Use in PineScript for allocation sizing:**
```pinescript
// From thesis: 72% win rate, 1.5% avg win, 3% avg loss
kelly_fraction = 0.04  // 4% quarter-Kelly
position_value = strategy.equity * kelly_fraction
qty = position_value / close
```

---

## Automated Risk Management (No Override)

**Hard-coded limits (NO discretionary exceptions):**

```python
RISK_LIMITS = {
    'max_daily_loss_pct': 5.0,      # Kill after 5% daily loss
    'max_position_pct': 5.0,        # Max 5% per trade
    'max_portfolio_exposure': 70.0,  # Max 70% invested
    'max_trades_per_day': 3,        # Prevent overtrading
    'sleep_hours': (21, 7),          # No trading 9pm-7am ET
    'max_drawdown_kill': 15.0,      # Kill at 15% total DD
    'min_confidence': 60.0,         # Minimum signal confidence
}
```

**Kill Switch Activation:**
- Daily loss ≥ 5% → Immediate halt
- Drawdown ≥ 15% → Immediate halt
- Manual reset only with confirmation code
- Discord alert sent on activation

---

## Quantitative Strategy Templates

### Template 1: Factor Rotation (Monthly)

```pinescript
//@version=5
strategy("Factor Rotation", overlay=true, initial_capital=100000)

// Multi-factor regime detection
growth_value_ratio = request.security("QQQ", timeframe.period, close) / 
                     request.security("VTV", timeframe.period, close)
size_momentum = request.security("IWM", timeframe.period, close) / 
                request.security("SPY", timeframe.period, close)

// Monthly rebalance trigger
new_month = month != month[1]

// Automated rebalancing (no manual approval)
if new_month
    strategy.close_all(comment="Rebalance")
    
    if growth_value_ratio > ta.sma(growth_value_ratio, 20)
        strategy.entry("Growth", strategy.long)
        alert('{"strategy": "factor_rotation", "action": "rotate_growth", "allocation": 0.35}')
    else
        strategy.entry("Value", strategy.long)
        alert('{"strategy": "factor_rotation", "action": "rotate_value", "allocation": 0.35}')
```

### Template 2: 0DTE Theta Capture (Daily)

```pinescript
//@version=5
strategy("0DTE Theta", overlay=false, initial_capital=100000)

// IV rank proxy using VIX or ATR
vix = request.security("VIX", timeframe.period, close)
vix_sma20 = ta.sma(vix, 20)
iv_rank = ((vix - ta.lowest(vix, 52)) / (ta.highest(vix, 52) - ta.lowest(vix, 52))) * 100

// Time window: 10am-3pm ET optimal for 0DTE
in_window = hour >= 10 and hour <= 15

// High IV + uptrend only
high_iv = iv_rank > 50
in_uptrend = close > ta.ema(close, 20)

// Automated entry (no manual approval)
if high_iv and in_uptrend and in_window and strategy.position_size == 0
    // Kelly-sized position (4% quarter-Kelly)
    qty = (strategy.equity * 0.04) / close
    strategy.entry("Theta", strategy.short, qty=qty)
    alert('{"strategy": "0DTE_theta", "action": "sell_put_spread", "iv_rank": ' + str.tostring(iv_rank) + '}')

// Automated exits (mechanical, no emotion)
// 1. Time-based: Close at 3:45pm ET
if hour == 15 and minute >= 45
    strategy.close_all(comment="Time Exit")

// 2. Profit target: 50% of max profit
strategy.exit("Profit", "Theta", limit=strategy.position_avg_price * 0.995)

// 3. Stop loss: 2x credit received
strategy.exit("Stop", "Theta", stop=strategy.position_avg_price * 1.015)
```

---

## Webhook Integration for Automation

### PineScript Webhook (TradingView Pro required)

```pinescript
// Build structured signal
alert_message = '{"strategy": "0DTE_theta", "action": "sell_put_spread", "symbol": "SPY", "confidence": 0.72, "edge_type": "theta_decay", "timestamp": "' + str.tostring(timenow) + '"}'

// Fire webhook automatically on signal
if signal_condition
    alert(alert_message, alert.freq_once_per_bar)
```

### Flask Webhook Receiver

```python
from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/webhook/pinescript', methods=['POST'])
def receive_signal():
    signal = request.json
    
    # Validate signal
    if not validate_signal(signal):
        return {"status": "rejected"}, 400
    
    # Queue for execution
    queue_signal(signal)
    
    return {"status": "accepted"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## Pitfalls from Real Trading Experience

1. **Technical indicators have no alpha** — MA crossovers, RSI signals are visible to all; backtests show Sharpe < 1.0
2. **Factor premiums require long holding** — 1-3 years, not suitable for daily P&L focus
3. **Theta decay IS real** — But requires options trading (0DTE), not proxy positions
4. **Mock data corrupts validation** — Random walk simulation can't capture real market structure
5. **Kill switches must be automatic** — "I'll watch it" means you'll watch it lose money

---

## Session-Specific Files Generated

This architecture was developed during the Edgeless Trading Command Center build:
- `factor_rotation_strategy.pine` - Monthly factor rotation
- `zerodte_theta_strategy.pine` - Daily theta capture
- `webhook_server.py` - Flask signal receiver
- `execution_engine.py` - Alpaca integration with Kelly sizing
- `risk_manager.py` - Automated kill switches
- `discord_monitor.py` - Trade alerts
- `integration.py` - Full system orchestration

**Location:** `claude-vault/06-Projects/Edgeless-Trading-Command-Center/`
