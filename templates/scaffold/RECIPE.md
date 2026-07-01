# Recipe Template

> Copy this file into `recipes/<your-slug>/RECIPE.md` and fill in every section.
> The validator (`scripts/validate_recipe.py`) will reject recipes with empty
> "Variables", "Failure modes", or "Verification checklist" sections.

---

# Recipe: <short-human-name>

> One-line summary: what does this loop do, for whom, and how often.

**Slug:** `<kebab-case-id>`
**Domain:** `<vertical>` (e.g., local-business, e-commerce, devops, content)
**Cadence:** `<cron expression>` (e.g., `0 1,15,20 * * *`)
**Owner:** `<github-handle>`
**Status:** `<draft | production | paused | deprecated>`

---

## What this loop does

<2-4 sentences. The agent reads/writes which systems? What artifact does it produce? What does success look like in one sentence?>

## Why this loop exists

<1-2 sentences. What manual work does it replace? What signal does it watch for? What does it do when that signal fires?>

## Variables you must change

> Before this loop will run for **your** business, you must change the following.
> Each row is a placeholder; the recipe will not work as-is without these edits.

| Variable | Where | Default in this recipe | What to change it to |
|---|---|---|---|
| `BUSINESS_NAME` | `prompts/system.txt` | `<e.g. Tech Guru Online>` | Your business name |
| `BRAND_LOGO_PATH` | `assets/brand/` | `<logo.jpg>` | Your logo file |
| `NICHE_HISTORY_FILE` | `cron.config.yaml` | `history/campaigns.jsonl` | Where the loop appends each run |
| `<PAGE_ACCESS_TOKEN>` | `examples/env.template` | `<tgo_page_access_token>` | Your Facebook/LinkedIn/etc. page token |
| `<SCHEDULE>` | `cron.config.yaml` | `0 1,15,20 * * *` | Your cadence |

---

## The prompt

The agent's system prompt lives in [`prompts/system.txt`](prompts/system.txt). It must:

1. Read the history file first and avoid previously used values.
2. Pick a concrete `<noun>` (not a generic category).
3. Produce the artifact (post, email, alert, etc.) — never a placeholder.
4. Verify the artifact (preview URL, lint pass, etc.) before publishing.
5. Append a JSON line to the history file with all relevant fields.

Excerpt (see the full file for the canonical version):

```text
You are the <BUSINESS_NAME> <ROLE> loop. Every run:
1. Read <HISTORY_FILE> and avoid previously used <ENTITIES>.
2. Pick one concrete <NICHE> with buyer intent in <REGION>.
3. <STEP 3>
4. <STEP 4>
5. <STEP 5 — publish / commit / notify>
6. Append a JSON object to <HISTORY_FILE> with <FIELDS>.
```

## Schedule

```cron
<cron expression — explain why this cadence>
```

## Skills the agent loads

| Skill | Why |
|---|---|
| `<skill-name>` | <one line> |
| `<skill-name>` | <one line> |

---

## Inputs (what the agent reads)

- `<path 1>` — <what it is>
- `<path 2>` — <what it is>
- `<api endpoint>` — <what it queries>

## Outputs (what the agent writes)

- `<artifact>` — <where it lands>
- `<history file>` — <one JSON line per run>
- `<log file>` — <append-only audit trail>

## Secrets required

| Secret | Source | Purpose |
|---|---|---|
| `<NAME>` | `<env var / file path>` | <one line> |
| `<NAME>` | `<env var / file path>` | <one line> |

**Never commit real secrets.** See [`SECURITY.md`](../../SECURITY.md) for the layout.

---

## Failure modes

> This is the most important section. Document every way this loop can fail in production
> and how the agent or the operator should respond. The recipe validator rejects recipes
> with fewer than three concrete failure modes.

| Symptom | Cause | Recovery |
|---|---|---|
| Loop runs but posts nothing | History file full of recent niches | Lower `MAX_RECENT_NICHE_AGE` or widen the niche pool |
| Loop times out at minute 4 | Image generation API slow | Add retry with backoff; degrade to text-only post |
| Same niche posted twice in one day | History append failed mid-run | Idempotency guard: dedupe by `(niche, day)` before posting |
| Page token returns 401 | Token expired | Operator rotates token; loop pauses until updated |

## Pitfalls

- **Don't `<anti-pattern>`** — <why and what to do instead>.
- **Don't `<anti-pattern>`** — <why and what to do instead>.
- **Don't `<anti-pattern>`** — <why and what to do instead>.

---

## Verification checklist

Before merging a change to this recipe, or before deploying it to a new account:

- [ ] `python3 scripts/validate_recipe.py recipes/<slug>/` exits 0.
- [ ] `pytest tests/` is green.
- [ ] Manual smoke test: run the prompt once with a test history file and confirm the artifact lands.
- [ ] History file append works (the new run appears at the bottom).
- [ ] Secrets are read from the correct env-var / file path and never logged.
- [ ] Brand asset is the *real* brand asset, not a generic placeholder.
- [ ] Cadence matches the agreed SLA (no accidental 1-minute polling).

---

## Adapting this recipe

To fork this loop for a new business:

1. Copy the directory to a new slug.
2. Update the **Variables** table and `prompts/system.txt`.
3. Replace brand assets in `assets/brand/`.
4. Rotate all secrets in `examples/env.template` to your own (real values go in your deploy env, **not** in this repo).
5. Run the verification checklist above.
6. Open a PR if you want to share the adaptation back upstream.

## Related recipes

- `<link to related recipe>` — <one-line difference>
- `<link to related recipe>` — <one-line difference>

---

## Changelog

- **v1.0.0** — initial extraction from production cron.
- **v0.x** — internal iterations while the loop was running in production.

> Keep this section in sync with the repo-level `CHANGELOG.md` when you bump versions.