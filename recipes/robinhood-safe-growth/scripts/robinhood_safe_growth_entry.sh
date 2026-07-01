#!/usr/bin/env bash
# Robinhood Safe Growth — Stage 1 launcher (Entry Decision)
#
# Thin wrapper that the cron calls. The real snapshot script lives at
# /root/.hermes/scripts/robinhood_mcp_snapshot.py — we deliberately do
# NOT vendor it here because it changes often and we want the canonical
# copy to live next to its OAuth token file.
#
# This wrapper exists so the cron-config file can reference a stable
# path inside the agent-loopkit checkout.

set -euo pipefail

export RH_SAFE_GROWTH_MODE="${RH_SAFE_GROWTH_MODE:-entry}"
export RH_NOTIFY_TELEGRAM="${RH_NOTIFY_TELEGRAM:-1}"
export RH_REDACT_ACCOUNTS="${RH_REDACT_ACCOUNTS:-1}"

exec python3 /root/.hermes/scripts/robinhood_mcp_snapshot.py entry