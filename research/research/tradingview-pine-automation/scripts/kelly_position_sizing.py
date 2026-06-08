#!/usr/bin/env python3
"""
Kelly Criterion Position Sizing Calculator
For automated trading systems with quarter-Kelly safety factor.
"""

def calculate_kelly_size(win_rate: float, avg_win: float, avg_loss: float, 
                         portfolio_value: float, kelly_divisor: int = 4,
                         max_position_pct: float = 0.05) -> float:
    """
    Calculate Kelly-optimal position size.
    
    Args:
        win_rate: Probability of winning (0.0 to 1.0)
        avg_win: Average win amount (% as decimal, e.g., 0.015 for 1.5%)
        avg_loss: Average loss amount (% as decimal, positive)
        portfolio_value: Current portfolio value
        kelly_divisor: Divisor for fractional Kelly (default 4 = quarter-Kelly)
        max_position_pct: Maximum position size as % of portfolio (default 5%)
    
    Returns:
        Position size in dollars
    """
    if avg_loss == 0 or win_rate <= 0:
        return 0.0
    
    # Kelly formula: f* = (bp - q) / b
    b = avg_win / avg_loss  # Odds
    p = win_rate
    q = 1 - p
    
    kelly = (b * p - q) / b
    fractional_kelly = max(0, kelly / kelly_divisor)
    
    # Cap at maximum position size
    position_pct = min(fractional_kelly, max_position_pct)
    
    return portfolio_value * position_pct


def main():
    # Example: 0DTE theta strategy
    win_rate = 0.72
    avg_win = 0.015  # 1.5%
    avg_loss = 0.030  # 3%
    portfolio = 100000
    
    position_size = calculate_kelly_size(win_rate, avg_win, avg_loss, portfolio)
    print(f"Kelly position size: ${position_size:,.2f} ({position_size/portfolio:.2%})")
    
    # Example: Factor rotation
    win_rate = 0.60
    avg_win = 0.025
    avg_loss = 0.015
    
    position_size = calculate_kelly_size(win_rate, avg_win, avg_loss, portfolio)
    print(f"Factor position size: ${position_size:,.2f} ({position_size/portfolio:.2%})")


if __name__ == "__main__":
    main()
