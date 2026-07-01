#!/usr/bin/env bash
# Etsy Logo Pack Pipeline — Stage 2 launcher
#
# Autonomous no-human-review theme inventory refill. Generates candidates
# and auto-approves/rejects via deterministic score + dedup + trademark
# checks. See references/theme-lifecycle.md for the state machine.

set -euo pipefail

LOG_DIR="${OUTPUT_ARCHIVE_DIR:-/root/etsy-logo-packs}/logs"
mkdir -p "${LOG_DIR}"
TS="$(date -u +%Y%m%d-%H%M%S)"

THRESHOLD="${APPROVED_THRESHOLD:-32}"
TARGET="${APPROVED_TARGET:-96}"
MAX_CAND="${MAX_CANDIDATES:-120}"

/usr/bin/python3 /root/.hermes/scripts/etsy_theme_catalog_manager.py refill \
  --threshold "${THRESHOLD}" \
  --target-approved "${TARGET}" \
  --max-candidates "${MAX_CAND}" \
  > "${LOG_DIR}/theme-refill-${TS}.log" 2>&1