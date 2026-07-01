# Theme lifecycle

The Stage 1 worker + Stage 2 refill cron interact with `theme_catalog.json` through a strict state machine. Getting this wrong is the #1 source of "we ran out of themes" or "we re-used a theme that was already published" incidents.

## States

```
approved ──pick_themes()──→ reserved ──etsy_draft_success──→ used
   ↑                            │
   │                            └──release_reserved(error)──→ approved
   │
   └──refill auto-approve──→ approved
```

| State | Meaning |
|---|---|
| `approved` | Eligible for Stage 1 to pick. The default state for themes in inventory. |
| `reserved` | Picked by Stage 1 but the Etsy draft hasn't succeeded yet. Held against the inventory so a second Stage 1 run won't double-pick. |
| `used` | Etsy draft succeeded. Burned — never recycled. |
| `rejected` | Failed quality / dedup / trademark checks. Kept in catalog for audit; not eligible for Stage 1. |

## The invariant

**Used themes are never silently recycled.** If the approved count drops below `MIN_APPROVED_THEMES` (default 4), Stage 1 fails closed. The operator must either:

- Wait for Stage 2 to refill, or
- Manually approve themes from `rejected[]`.

Lowering `MIN_APPROVED_THEMES` is **not** the right answer — it just hides the fact that Stage 2 isn't keeping up.

## Pick semantics

`pick_themes(n=4)` does the following:

1. Read `theme_catalog.json`.
2. Filter to `status == 'approved'`.
3. Sort by `score` descending (so highest-quality themes are picked first).
4. Exclude any slug in `state.json.used_theme_slugs`.
5. Take the top N.
6. Set each picked theme's `status` to `reserved` and write back.
7. Return the picked themes + the updated state.

If fewer than N themes pass the filter, `pick_themes` raises `InsufficientApprovedThemesError`. Stage 1 catches this and reports the count, then fails closed.

## Release semantics

If Stage 1 errors **before** `etsy_draft_success=True`, every theme still in `reserved` is moved back to `approved` with `last_error: <message>`. The state machine is consistent — no theme is ever stuck in `reserved` after a failed run.

If Stage 1 succeeds for some themes and errors after, only the unprocessed themes are released. Successfully processed themes are in `used`.

## Refill semantics

Stage 2 runs `python etsy_theme_catalog_manager.py refill --threshold 32 --target-approved 96 --max-candidates 120`:

1. Count `approved` themes.
2. If `approved < threshold`, generate up to `max_candidates` new candidates.
3. Score each candidate (0-100) using:
   - Title uniqueness vs. existing themes (higher = better).
   - Concept diversity vs. existing themes (higher = better).
   - Keyword relevance (higher = better).
   - Trademark risk (must be `low` or `medium` — `high` rejects).
4. Auto-approve candidates with `score >= MIN_SCORE_FOR_APPROVE` and `duplicate_risk != 'high'`.
5. Stop generating once `approved >= target-approved` OR `max_candidates` reached.
6. Write the updated catalog + a `theme-refill-<timestamp>.log`.

## Backup semantics

The catalog is small (<1 MB) but irreplaceable. Back it up:

```bash
cp /root/etsy-logo-packs/theme_catalog.json /root/backups/theme_catalog-$(date -u +%Y%m%d).json
```

Add a daily backup cron if you don't already have one. Stage 2's output is a single source of truth — if it gets corrupted, the only recovery is from backup.

---

## Debugging "no approved themes" errors

```bash
# 1. Check current state
python /root/.hermes/scripts/etsy_theme_catalog_manager.py summary

# 2. See what got rejected and why
python -c "
import json
catalog = json.load(open('/root/etsy-logo-packs/theme_catalog.json'))
for t in catalog['themes']:
    if t['status'] == 'rejected':
        print(t['slug'], t.get('duplicate_risk'), t.get('score'), t.get('last_rejection_reason'))
" | head -20

# 3. Manually re-approve borderline cases
python -c "
import json
catalog = json.load(open('/root/etsy-logo-packs/theme_catalog.json'))
for t in catalog['themes']:
    if t['status'] == 'rejected' and t.get('score', 0) >= 80:
        t['status'] = 'approved'
        print('Re-approved:', t['slug'])
open('/root/etsy-logo-packs/theme_catalog.json', 'w').write(json.dumps(catalog, indent=2))
"
```

If the catalog itself is corrupt, restore from backup. **Never** edit the catalog with `jq` or a text editor — it's JSON Lines-flavored with nested fields that are easy to break.