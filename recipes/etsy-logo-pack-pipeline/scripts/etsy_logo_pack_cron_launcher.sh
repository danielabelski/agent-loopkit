#!/usr/bin/env bash
# Etsy Logo Pack Pipeline — Stage 1 launcher
#
# Detached wrapper that the cron calls. The real worker lives at
# /root/.hermes/scripts/etsy_logo_pack_worker.py — we deliberately do NOT
# vendor it here because it changes often and we want the canonical copy to
# live next to its data files.
#
# This wrapper exists so the cron-config file can reference a stable path
# inside the agent-loopkit checkout. When you adapt this recipe for your
# own Etsy shop, replace the WORKDIR with your own automation root.

set -euo pipefail

WORKDIR="${OUTPUT_ARCHIVE_DIR:-/root/etsy-logo-packs}"
LOG_DIR="${WORKDIR}/logs"
mkdir -p "${LOG_DIR}"
TS="$(date -u +%Y%m%d-%H%M%S)"

# Default to draft mode (never click Publish). Override only if you have a
# specific reason and have verified the recipe's verification checklist.
export ETSY_CREATE_DRAFTS="${ETSY_CREATE_DRAFTS:-1}"
export ETSY_NOTIFY_DISCORD="${ETSY_NOTIFY_DISCORD:-0}"

# Launch detached so cron is not killed by the Hermes cron agent timeout.
nohup /usr/bin/python3 /root/.hermes/scripts/etsy_logo_pack_worker.py \
  > "${LOG_DIR}/run-${TS}.log" 2>&1 < /dev/null &

exit 0