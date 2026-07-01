# Adapting an existing loop into a recipe

If you already have a cron-driven agent loop running somewhere (Hermes, GH Actions, plain `cron`), here's the workflow to extract it into a recipe and contribute it back to this catalog.

This is the recipe author's view of the **recipe extraction workflow** — see `CONTRIBUTING.md` for the broader contribution process.

---

## Step 0 — Get alignment

Open an issue using the [new-recipe](../.github/ISSUE_TEMPLATE/new-recipe.md) template. Describe:

- The loop you want to extract.
- The cadence and history volume.
- Whether you're comfortable sharing the prompt publicly (some prompts reveal business secrets).

A reviewer will reply before you start moving code.

---

## Step 1 — Capture the canonical prompt

Find the actual prompt your loop is using. In Hermes this is the `prompt` field on the cron job; in GH Actions it's the body of the prompt the action sends; in plain cron it's the inline text or a file.

Save it verbatim to `recipes/<your-slug>/prompts/system.txt`. Don't paraphrase — the value of the recipe is the exact prompt that works in production.

## Step 2 — Snapshot the operating procedure

If your loop has a `FLOW.md`, a `README.md` with run instructions, or any prose describing the steps, copy it into `recipes/<your-slug>/references/flow.md`. This becomes the canonical operating procedure the agent reads at the start of every run.

## Step 3 — Identify the secrets layout

List every secret your loop reads (page tokens, API keys, customer data). For each:

- The env var name or file path.
- The runtime that provides it (Hermes secure dir, GitHub secrets, K8s secret, etc.).

Drop a `examples/env.template` with placeholders (`__replace_me__`) for each one. **Do not commit real values.**

## Step 4 — Enumerate the failure modes

This is the part most people skip, and it's the most important. Open the operator's chat / issue tracker and grep for "broken", "failed", "double-posted", "rotated token". Every incident is a failure mode.

For each failure mode, write a row in the `Failure modes` table with: symptom, cause, recovery.

The recipe validator requires **at least 3 rows**. A recipe you've been running in production for >1 month should have **at least 8–10 rows**.

## Step 5 — Identify the variables

What's the smallest set of changes someone would need to make to run this loop for a different business?

Common variables:

- Business name.
- Brand logo path.
- Region.
- Language.
- WhatsApp / contact CTA.
- Pricing regex (if the loop has a comment guard).
- History file path.
- Schedule.

Each goes in the `Variables you must change` table with `Default` (the value in this recipe) and `What to change it to` (the value for the new business).

## Step 6 — Write `cron.config.yaml`

Translate your scheduler's job definition into YAML. For Hermes, this is a direct 1:1. For GH Actions or K8s, see [`deployment-targets.md`](deployment-targets.md) for the inverse translation.

The fields the validator requires:

- `schedule` — the cron expression.
- `delivery` — where to send the run report (`origin`, `local`, or `all`).
- `skills` — what skills the agent loads.
- `enabled_toolsets` — what tools the agent can use (defense in depth).

## Step 7 — Sanitize

Grep the recipe directory for:

- Real tokens (`ghp_`, `sk-`, `EAA...`, `xox...`).
- Real customer data (lead CSVs, conversation JSON).
- Real history files (the production `campaigns.jsonl`).
- Real brand assets with customer logos / photos.

Replace all of them with placeholders or generic stand-ins. The CI secrets scanner will catch anything you missed, but it's better to catch it locally first.

## Step 8 — Add tests

Two test files, minimum:

- `tests/test_structure.py` — verifies the recipe shape (sections present, tables have ≥3 rows, files exist).
- `tests/test_smoke.py` — runs the canonical validator against the recipe and verifies the prompt mentions the brand asset.

The recipe validator will give you a checklist.

## Step 9 — Run the validators locally

```bash
python scripts/validate_recipe.py --all
python scripts/validate_repo.py
python -m pytest -v
```

All three must pass before you open a PR.

## Step 10 — Open the PR

PR body should include:

- One-paragraph pitch.
- Link to the original cron job (if it's a private repo, just say so).
- Confirmation that you ran the recipe in production for ≥1 month with no critical incidents.

---

## What goes wrong most often

1. **Forgetting the failure modes.** The recipe passes the validator with 3 throwaway rows but isn't useful. Spend the time.
2. **Vague variables table.** "Change the brand name" is not a variable row. The row must say `BUSINESS_NAME` in column 1 and `Tech Guru Online` in column 3.
3. **Committing the production history file.** It's append-only and may contain real customer data. The `.gitignore` excludes `history/` but if you `git add -f` it you bypass that.
4. **Skipping the smoke test.** A recipe without a smoke test can rot silently when the underlying API changes.

If you hit any of these, fix them before opening the PR — saves a review round trip.