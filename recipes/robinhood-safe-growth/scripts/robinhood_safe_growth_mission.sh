#!/usr/bin/env bash
# Robinhood Safe Growth — Stage 3 launcher (Mission Control)

set -euo pipefail

export RH_SAFE_GROWTH_MODE="${RH_SAFE_GROWTH_MODE:-mission}"
export RH_NOTIFY_TELEGRAM="${RH_NOTIFY_TELEGRAM:-0}"
export RH_REDACT_ACCOUNTS="${RH_REDACT_ACCOUNTS:-1}"

exec python3 /root/.hermes/scripts/robinhood_mcp_snapshot.py mission