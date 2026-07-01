#!/usr/bin/env bash
# Etsy Logo Pack Pipeline — Stage 3 launcher (Pinterest)
#
# Publishes already-drafted Etsy packs as Pinterest pins. Dry-run by default.
# Set PINTEREST_DRY_RUN=0 ONLY after Kevin explicitly authorizes publishing.

set -euo pipefail

LOG_DIR="${OUTPUT_ARCHIVE_DIR:-/root/etsy-logo-packs}/logs"
mkdir -p "${LOG_DIR}"
TS="$(date -u +%Y%m%d-%H%M%S)"

DRY_RUN_FLAG=""
if [[ "${PINTEREST_DRY_RUN:-1}" == "1" ]]; then
  DRY_RUN_FLAG="--dry-run"
fi

/usr/bin/python3 /root/.hermes/scripts/pinterest_publish_worker.py ${DRY_RUN_FLAG} \
  > "${LOG_DIR}/pinterest-${TS}.log" 2>&1