#!/usr/bin/env bash
# TGO Comment Guard launcher
#
# This is a thin wrapper that the cron calls. The real script lives at
# /root/techguruonline-automation/full_funnel_price_comment_guard.py — we
# deliberately do NOT vendor it here because it changes often and we want
# the canonical copy to live next to its data files.
#
# This wrapper exists so the cron-config file can reference a stable path
# inside the agent-loopkit checkout. When you adapt this recipe for your
# own business, replace the WORKDIR with your automation root.

set -euo pipefail

WORKDIR="${TGO_AUTOMATION_ROOT:-/root/techguruonline-automation}"
SCRIPT="${WORKDIR}/full_funnel_price_comment_guard.py"

if [[ ! -f "${SCRIPT}" ]]; then
  echo "[comment-guard] ERROR: ${SCRIPT} not found" >&2
  exit 2
fi

cd "${WORKDIR}"
exec python3 "${SCRIPT}"