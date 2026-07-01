# Recipe: Etsy Logo Pack Pipeline (Discord-bot logo pack → Etsy draft → Pinterest pin)

> A 3-stage, fully autonomous pipeline that generates themed Discord/SaaS bot logo packs, saves them as Etsy listing drafts, and reposts them as Pinterest pins — 4×/day — without an LLM in the hot path.

**Slug:** `etsy-logo-pack-pipeline`
**Domain:** digital-assets / Etsy / Pinterest
**Cadence:**
- Stage 1 (generate + draft): `0 0,6,12,18 * * *` (4×/day)
- Stage 2 (theme catalog refill): `30 5 * * *` (1×/day)
- Stage 3 (Pinterest publish): `45 0,6,12,18 * * *` (4×/day, 45 min after Stage 1)

**Owner:** [@ooovenenoso](https://github.com/ooovenenoso)
**Status:** **production** (paused for review as of 2026-06-04)
**Provenance:** extracted from a 3-cron pipeline running inside Hermes Agent — `etsy-logo-pack-draft-cron` skill + `pinterest_publish_cron_launcher.sh`.

---

## What this loop does

A **3-stage pipeline** that turns a permanent theme catalog into published digital listings:

```
[Stage 1: Generate + Etsy Draft]   every 6h
        ↓ (cron 0:00, 6:00, 12:00, 18:00)
   pick 4 approved non-repeating themes
        ↓
   generate 4 logos per pack (gpt-image-2-medium)
        ↓
   build combined mockup + buyer ZIP + manifest
        ↓
   open persistent Etsy browser profile → save as Etsy DRAFT
        ↓
   update theme status (reserved → used)
        ↓
   archive to /root/etsy-logo-packs/<batch-id>/<slug>/

[Stage 2: Theme Catalog Refill]    daily
        ↓ (cron 5:30)
   count approved themes in catalog
        ↓
   if approved < 32, generate candidates (max 120)
        ↓
   score + dedup + trademark-risk check
        ↓
   auto-approve high-score candidates to inventory

[Stage 3: Pinterest Publish]       every 6h, 45 min after Stage 1
        ↓ (cron 0:45, 6:45, 12:45, 18:45)
   find packs with `etsy_draft_success=True` not yet pinned
        ↓
   open dedicated Pinterest account/profile
        ↓
   create pin: title + about (≤100 chars) + URL + image
        ↓
   write `pinterest-publish-result.json` per pack to avoid duplicates
```

**Critical:** the pipeline is **draft-only by design**. Stage 1 clicks `Save as draft` / `Guardar como borrador` and **never** clicks `Publish` / `Publicar`. Stage 3 has a `--publish` flag that is dry-run by default. Etsy/Pinterest are paid-promotion surfaces; a misclick is a real money loss.

## Why this loop exists

Building a digital-products business on Etsy requires:

- A constant flow of fresh listings (the algorithm penalizes inactivity).
- Each listing needs ≥5 images, a buyer ZIP, tags, a price, and a description.
- Manual production caps at ~3 listings/day. The pipeline produces **16 listings/day** (4 packs × 4 logos per batch × 4 batches).

Pinterest is the distribution layer — each listing becomes a pin with a deep link back to the Etsy draft.

The pipeline runs **entirely on scripts and browser automation** — no LLM in the hot path. The LLM cost is zero per run; image generation is the only API cost (4 packs × 4 logos = 16 images/batch).

---

## Variables you must change

> Before this loop will run for **your** business, you must change every row in this table.
> The recipe will not work as-is without these edits.

| Variable | Where | Default in this recipe | What to change it to |
|---|---|---|---|
| `ETSY_PROFILE_DIR` | `examples/env.template` | `/root/.hermes/secure/etsy/pw-visible-profile` | Path to your Etsy browser profile |
| `ETSY_COPY_LISTING_ID` | `examples/env.template` | `1604703223` | Your inactive template listing ID to copy from |
| `ETSY_PRICE_USD` | `examples/env.template` | `7.99` | Your pack price |
| `ETSY_QUANTITY` | `examples/env.template` | `999` | Listing quantity (digital downloads are unlimited) |
| `PINTEREST_PROFILE_DIR` | `examples/env.template` | `/root/snap/chromium/common/pinterest-profile-account2` | Path to your dedicated Pinterest profile |
| `PINTEREST_CDP_URL` | `examples/env.template` | `http://127.0.0.1:9334` | Your Pinterest browser CDP endpoint |
| `OUTPUT_ARCHIVE_DIR` | `examples/env.template` | `/root/etsy-logo-packs` | Where the loop archives generated packs |
| `THEME_CATALOG_FILE` | `examples/env.template` | `/root/etsy-logo-packs/theme_catalog.json` | Path to your permanent theme catalog |
| `IMAGE_PROVIDER` | `prompts/worker.env` | `openai-codex` | Your image provider |
| `IMAGE_MODEL` | `prompts/worker.env` | `gpt-image-2-medium` | Your image model |
| `IMAGE_API_KEY_FILE` | `examples/env.template` | `/root/.hermes/secure/openai/api_key.txt` | Path to your image API key file |
| `DISCORD_WEBHOOK_FILE` | `examples/env.template` | `/root/.hermes/secure/discord/etsy_logo_pack_webhook.json` | Path to your Discord webhook JSON (optional) |
| `ETSY_CREATE_DRAFTS` | `examples/env.template` | `1` | Set to `0` as a second fail-safe when pausing |
| `SCHEDULE_GENERATE` | `cron.config.yaml` | `0 0,6,12,18 * * *` | Your Stage 1 cadence |
| `SCHEDULE_REFILL` | `cron.config.yaml` | `30 5 * * *` | Your Stage 2 cadence |
| `SCHEDULE_PINTEREST` | `cron.config.yaml` | `45 0,6,12,18 * * *` | Your Stage 3 cadence |
| `PACKS_PER_BATCH` | `examples/env.template` | `4` | Packs to generate per Stage 1 run |
| `LOGOS_PER_PACK` | `examples/env.template` | `4` | Logos to generate per pack |

---

## The three configs

This pipeline has **no LLM prompts** — it's all scripts + browser automation. The "prompts" here are the deterministic env files the scripts read.

### Stage 1 — `prompts/worker.env`

```bash
# Image generation provider + model
IMAGE_PROVIDER=openai-codex
IMAGE_MODEL=gpt-image-2-medium

# Inventory gates
PACKS_PER_BATCH=4
LOGOS_PER_PACK=4
MIN_APPROVED_THEMES=4   # fail closed if fewer approved themes exist

# Etsy draft runner
ETSY_PROFILE_DIR=/root/.hermes/secure/etsy/pw-visible-profile
ETSY_COPY_LISTING_ID=1604703223
ETSY_PRICE_USD=7.99
ETSY_QUANTITY=999
ETSY_CREATE_DRAFTS=1
ETSY_NOTIFY_DISCORD=0
ETSY_EDITOR_WAIT_ROUNDS=3
```

The image prompt template (used per logo) is constructed in code from the theme title + concept + style. See `references/image-prompt-template.md` for the full template.

### Stage 2 — `prompts/refill.env`

```bash
# Refill thresholds
APPROVED_THRESHOLD=32
APPROVED_TARGET=96
MAX_CANDIDATES=120

# Quality gates
MIN_SCORE_FOR_APPROVE=70
DUPLICATE_RISK_REJECT=high
```

### Stage 3 — `prompts/pinterest.env`

```bash
PINTEREST_DRY_RUN=1   # ALWAYS 1 unless explicitly publishing
PINTEREST_PROFILE_DIR=/root/snap/chromium/common/pinterest-profile-account2
PINTEREST_CDP_URL=http://127.0.0.1:9334

# Pin content caps (per Pinterest limits)
PIN_ABOUT_MAX_CHARS=100
```

## Schedules

```cron
# Stage 1: generate + Etsy draft (4x/day)
0 0,6,12,18 * * *

# Stage 2: theme catalog refill (1x/day, off-peak)
30 5 * * *

# Stage 3: Pinterest publish (4x/day, 45 min after Stage 1)
45 0,6,12,18 * * *
```

The 45-minute gap between Stage 1 and Stage 3 lets Stage 1 finish the browser work before Stage 3 picks up the new packs. The 5:30 refill runs before Stage 1's 6:00 batch so inventory is ready.

## Skills the operator loads

| Skill | Why |
|---|---|
| `etsy-logo-pack-draft-cron` | The Stage 1 + Stage 2 procedure (asset cleanup, draft save button verification, theme lifecycle) |
| `web-browser-automation` | Playwright/Puppeteer patterns for the visible Etsy + Pinterest profiles |
| `remote-browser-human-handoff` | noVNC launch procedure for DataDome/CAPTCHA recovery |
| `pinterest-publisher-experiment` | Stage 3 dry-run vs. `--publish` semantics |

This recipe runs `no_agent: true` for all three stages — the skills are documentation for operators, not loaded by the agent runtime.

---

## Inputs (what the scripts read)

| Input | What it is |
|---|---|
| `theme_catalog.json` | Permanent theme inventory with `status` field (`approved` / `reserved` / `used` / `rejected`) |
| `state.json` | Worker state — `used_theme_slugs` list, last 50 runs |
| `etsy_logo_pack_worker.py` | The Stage 1 worker (imports `THEMES` if catalog is empty) |
| Etsy template listing | Source of category / digital delivery settings (`ETSY_COPY_LISTING_ID`) |
| Pinterest board list | Determined at runtime from the dedicated account |

## Outputs (what the scripts write)

| Output | Where it lands |
|---|---|
| Pack directory | `<OUTPUT_ARCHIVE_DIR>/<batch-id>/<slug>/` |
| 4 logo PNGs | `<pack>/logo-NN-<concept>.png` |
| Mockup PNG | `<pack>/etsy-mockup-exact-logo-references.png` |
| Buyer ZIP | `<pack>/<title>-bot-logo-pack.zip` |
| `manifest.json` | Per-pack metadata |
| `listing-data.etsy-draft.json` | Pre-shaped payload for the draft runner |
| `etsy-draft-result.json` | Per-pack draft save result |
| `batch-summary.json` | Per-batch roll-up |
| Pinterest result | `<pack>/pinterest-publish-result.json` (idempotency guard) |
| Theme catalog update | `theme_catalog.json` (status transitions) |
| Worker state | `state.json` (appended) |
| Worker logs | `<OUTPUT_ARCHIVE_DIR>/logs/run-<timestamp>.log` |

## Secrets required

| Secret | Source | Purpose |
|---|---|---|
| `<IMAGE>_API_KEY_FILE` | `~/.hermes/secure/<provider>/api_key.txt` | Image generation API auth |
| `<ETSY_PROFILE_DIR>` | `~/.hermes/secure/etsy/<profile>` | Persistent browser profile with login + cookies |
| `<PINTEREST_PROFILE_DIR>` | `~/.hermes/snap/chromium/common/<profile>` | Dedicated Pinterest account profile |
| `<VNC_PASSWORD>` | `~/.hermes/secure/etsy/vnc-passwd` | noVNC password for human challenge recovery |
| `<DISCORD_WEBHOOK>` (optional) | `~/.hermes/secure/discord/<name>.json` | Discord notification webhook |

**Never commit real secrets.** See [`SECURITY.md`](../../SECURITY.md).

---

## Failure modes

| Symptom | Cause | Recovery |
|---|---|---|
| Stage 1 fails with "No approved themes" | Catalog inventory exhausted | Stage 2 should auto-refill; if it didn't, manually run `python etsy_theme_catalog_manager.py refill` |
| Stage 1 saves a *published* listing instead of a draft | Etsy button label changed OR template listing became active | Stop the cron; verify `#shop-manager--listing-save` text says `Save as draft` / `Guardar como borrador`; ensure template listing is **inactive** in Etsy admin |
| Stage 1 leaves template photos/videos in the draft | Etsy's bulk `Eliminar todo` button doesn't clear all media | Operator runs manual recovery; re-run with `ETSY_EDITOR_WAIT_ROUNDS=5` |
| Stage 1 uploads a ZIP larger than Etsy's per-file limit | Mega pack ZIP too big | Split the ZIP; re-run; mega packs use up to 5 digital files via `digital_files: [...]` |
| Stage 2 generates themes that overlap with trademark risk | LLM provider returned generic corporate names | Auto-reviewer rejects `duplicate_risk: high`; operator inspects `theme_catalog.json.rejected[]` for false positives |
| Stage 3 publishes without `--publish` flag | Misconfigured launcher | Re-set `PINTEREST_DRY_RUN=1`; verify pinned items manually in Pinterest admin |
| Worker lock blocks a fresh run | Previous worker died without releasing the lock | The lock is PID-aware: if the PID is dead, the next worker replaces the lock; manually inspect with `cat .generation.lock && ps -p <pid>` |
| Etsy login / DataDome challenge blocks Stage 1 | Etsy anti-bot detection | Operator opens noVNC, completes challenge, releases browser, re-runs |
| Pinterest about-text exceeds 100 chars | Listing description too long | Truncate to 100 chars before publish; the publisher fails closed before clicking Publish |

## Pitfalls

- **Don't click Publish / Publicar in Stage 1.** Drafts only. Etsy Ads must stay off.
- **Don't reuse the Etsy profile for Pinterest (or vice versa).** Each platform has its own dedicated profile to avoid DataDome cross-contamination.
- **Don't** set `ETSY_NOTIFY_DISCORD=1` as the default. Webhooks are for fail-safes, not the primary delivery path.
- **Don't** lower `MIN_APPROVED_THEMES=4` to "always succeed" — if Stage 2 fails to refill, you want Stage 1 to fail closed so you notice.
- **Don't** recycle `used` themes silently. Used themes are burned; new themes must come from Stage 2.
- **Don't** open the visible noVNC browser while Stage 1 is running — Chromium profile locks prevent automation from starting.
- **Don't** use the old Cookie-Editor-only storageState path as the primary solution — Etsy/DataDome may reject it.

---

## Verification checklist

Before deploying this recipe to a new account, or after any change to the worker scripts:

- [ ] `python3 scripts/validate_recipe.py recipes/etsy-logo-pack-pipeline/` exits 0.
- [ ] `pytest recipes/etsy-logo-pack-pipeline/tests/` is green.
- [ ] `python3 -m py_compile scripts/etsy_logo_pack_worker.py scripts/etsy_theme_catalog_manager.py` exits 0.
- [ ] `node --check scripts/local_create_draft.js` exits 0 (if vendoring the runner).
- [ ] `bash -n scripts/etsy_logo_pack_cron_launcher.sh scripts/etsy_theme_catalog_refill_launcher.sh scripts/pinterest_publish_cron_launcher.sh` exits 0.
- [ ] Theme catalog has ≥32 approved themes before Stage 1 runs.
- [ ] Etsy browser profile is logged in (no DataDome challenge).
- [ ] Pinterest browser profile is logged in (no auth challenge).
- [ ] All `examples/env.template` placeholders are replaced in the deploy env.
- [ ] One dry run of Stage 1 saves a **draft** (verify the button text was `Save as draft` / `Guardar como borrador`).
- [ ] One dry run of Stage 2 approves at least one candidate theme (or fails closed if the pool is healthy).
- [ ] One dry run of Stage 3 with `PINTEREST_DRY_RUN=1` produces a `pinterest-publish-result.json` with `dry_run: true` and no live pin created.

---

## Adapting this recipe

To fork this pipeline for a different Etsy shop / niche (e.g., Notion templates instead of Discord bots):

1. Copy `recipes/etsy-logo-pack-pipeline/` to `recipes/<your-niche>-etsy-pipeline/`.
2. Replace the `THEMES` list in the worker with your niche-specific themes.
3. Replace the `STYLE_DIRECTIONS` palette in the worker.
4. Update the `niche_pool` in `references/niche-pool.md`.
5. Re-validate (this recipe's validator runs against the new directory).

---

## Related recipes

- [`tgo-full-funnel-autopilot`](../tgo-full-funnel-autopilot/) — the Facebook lead-funnel cron recipe. Same shape (cron + scripts + history file) but for a different platform and with an LLM agent in the hot loop.

---

## Changelog

- **1.0.0** (2026-07-01) — initial extraction from the 3 production crons (`0b832d60d851`, `b14a367a5bb1`, `dc196651b6e6`).
- **0.9.x** — internal iterations while the pipeline ran in production for the Etsy shop.