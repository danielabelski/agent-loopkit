#!/usr/bin/env bash
# Robinhood Safe Growth — Stage 2 launcher (Afternoon Defense)

set -euo pipefail

export RH_SAFE_GROWTH_MODE="${RH_SAFE_GROWTH_MODE:-defense}"
export RH_NOTIFY_TELEGRAM="${RH_NOTIFY_TELEGRAM:-1}"
export RH_REDACT_ACCOUNTS="${RH_REDACT_ACCOUNTS:-1}"

exec python3 /root/.hermes/scripts/robinhood_mcp_snapshot.py defense