#!/bin/bash
# Start automated trading system
# TradingView webhooks → Execution → Risk → Discord

cd "$(dirname "$0")/.."
python3 -m automation.integration "$@"
