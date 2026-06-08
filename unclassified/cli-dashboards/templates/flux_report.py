#!/usr/bin/env python3
"""
Starter terminal dashboard — rich + sqlite + sparklines + CSV export.
Copy and modify for any domain.

Usage:
    python3 flux_report.py --seed          # populate with simulated data
    python3 flux_report.py                 # full matrix
    python3 flux_report.py --format csv    # pipe to file or tool
"""

import argparse
import csv
import sqlite3
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich import box

DB_PATH = Path(__file__).parent / "data" / "dashboard.db"
BLOCKS = "▁▂▃▄▅▆▇█"


def sparkline(values, width=10):
    if not values:
        return ""
    mn, mx = min(values), max(values)
    if mx == mn:
        return "▁" * min(width, len(values))
    scaled = [(v - mn) / (mx - mn) for v in values]
    step = max(1, len(scaled) // width)
    sampled = [scaled[i] for i in range(0, len(scaled), step)][:width]
    return "".join(BLOCKS[int(s * (len(BLOCKS) - 1))] for s in sampled)


def bar_blocks(value, max_value, width=10):
    if max_value == 0:
        return ""
    filled = int((value / max_value) * width)
    return "█" * filled + "░" * (width - filled)


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_schema():
    conn = get_conn()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS events (
            id      TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            label   TEXT NOT NULL,
            value   REAL,
            date    TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_cat ON events(category);
        CREATE INDEX IF NOT EXISTS idx_date ON events(date);
        """
    )
    conn.commit()
    conn.close()


def seed():
    import random, datetime
    random.seed(42)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM events")
    if cur.fetchone()[0] > 0:
        conn.close()
        return 0
    start = datetime.date(2024, 1, 1)
    cats = [("alpha", "foo"), ("alpha", "bar"), ("beta", "baz")]
    for i in range(200):
        cat, label = random.choice(cats)
        d = start + datetime.timedelta(days=random.randint(0, 500))
        val = random.gauss(5 if cat == "alpha" else 2, 4)
        cur.execute("INSERT INTO events VALUES (?, ?, ?, ?, ?)",
                    (f"E-{i:04d}", cat, label, round(val, 2), d.isoformat()))
    conn.commit()
    conn.close()
    return 200


def fetch_matrix():
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT category, label,
               COUNT(*), SUM(CASE WHEN value > 0 THEN 1 ELSE 0 END),
               ROUND(AVG(value), 2), ROUND(MIN(value), 2)
        FROM events
        GROUP BY category, label
        ORDER BY AVG(value) DESC
        """
    ).fetchall()
    conn.close()
    return rows


def fetch_series():
    conn = get_conn()
    rows = conn.execute(
        "SELECT strftime('%Y-%m', date) as m, SUM(value) FROM events GROUP BY m ORDER BY m"
    ).fetchall()
    conn.close()
    return rows


def render(rows, console):
    if not rows:
        console.print("[dim]No data.[/dim]")
        return
    max_n = max(r[2] for r in rows)
    table = Table(
        title="Dashboard",
        box=box.MINIMAL_DOUBLE_HEAD,
        header_style="bold #B4B4B4",
        border_style="#333333",
        collapse_padding=True,
    )
    table.add_column("Category", style="bold")
    table.add_column("Label")
    table.add_column("N", justify="right")
    table.add_column("Win%", justify="right")
    table.add_column("Avg", justify="right")
    table.add_column("Min", justify="right")
    table.add_column("Activity", justify="left")
    for cat, label, n, wins, avg, mn in rows:
        win_pct = (wins / n * 100) if n else 0
        color = "#00E5FF" if (avg or 0) > 0 else "#FF6B6B"
        dd_color = "#FF6B6B" if (mn or 0) < -5 else "#B4B4B4"
        table.add_row(
            cat, label, str(n), f"{win_pct:.0f}%",
            f"[{color}]{avg:+.1f}[/{color}]",
            f"[{dd_color}]{mn:.1f}[/{dd_color}]",
            f"[#555555]{bar_blocks(n, max_n, 8)}[/#555555]",
        )
    console.print(table)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", action="store_true")
    parser.add_argument("--format", choices=["terminal", "csv"], default="terminal")
    args = parser.parse_args()

    init_schema()
    if args.seed:
        n = seed()
        print(f"Seeded {n} rows.")
        return

    conn = get_conn()
    n = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    conn.close()
    if n == 0:
        seed()

    rows = fetch_matrix()
    if args.format == "csv":
        w = csv.writer(sys.stdout)
        w.writerow(["category", "label", "count", "wins", "win_pct", "avg", "min"])
        for r in rows:
            cat, label, count, wins, avg, mn = r
            w.writerow([cat, label, count, wins, f"{wins/count*100:.1f}" if count else 0, avg, mn])
        return

    console = Console()
    render(rows, console)
    series = fetch_series()
    if series:
        months = [r[0] for r in series]
        vals = [r[1] for r in series]
        total = sum(vals)
        color = "#00E5FF" if total > 0 else "#FF6B6B"
        console.print(
            f"\n[bold]Series[/bold]  [dim]{months[0]} → {months[-1]}[/dim]  "
            f"[{color}]${total:,.0f}[/{color}]  {sparkline(vals, 24)}"
        )


if __name__ == "__main__":
    main()
