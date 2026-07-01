# Authoring a recipe

This doc covers how to write a **new** recipe from scratch. If you're adapting an existing loop, see [`adapting-an-existing-loop.md`](adapting-an-existing-loop.md).

---

## Recipe shape (recap)

Every recipe lives in `recipes/<slug>/` and has this shape:

```
recipes/<slug>/
├── RECIPE.md
├── cron.config.yaml
├── prompts/
│   └── system.txt
├── scripts/                 (optional)
├── assets/                  (optional)
│   └── brand/
├── references/              (optional)
├── examples/
│   └── env.template
└── tests/
    ├── test_structure.py
    └── test_smoke.py
```

The validator enforces this shape. Skip a required file and the build fails.

---

## Step 1 — Pick the slug

The slug is the recipe's URL identifier. It must be:

- Lowercase, hyphenated, ≤64 chars.
- A noun phrase, not a verb (e.g., `tgo-full-funnel-autopilot`, not `autopilot-the-funnel`).
- Domain-specific when the loop is domain-specific (`tgo-full-funnel-autopilot`, not `full-funnel-autopilot`).

Domain-agnostic loops are encouraged but rare. If your loop is "every Monday, summarize the week's GitHub issues," the slug is `weekly-github-issue-summarizer`, not `summarize-issues`.

## Step 2 — Write the prompt first

The prompt is the canonical contract. Write it in `prompts/system.txt` before you write `RECIPE.md`. The recipe's failure modes and verification checklist should be derivable from what the prompt does.

A good recipe prompt:

- Names the **business context** explicitly (name, region, language, contact CTA).
- Lists the **operating procedure** as numbered steps, each with a concrete artifact ("append a JSON line", "deploy to Vercel", "POST to /<page_id>/photos").
- Calls out the **brand assets the agent must use** with absolute paths.
- Names the **inputs it reads** (history files, reference images, niche pool) and **outputs it writes** (deploy URL, history append, post permalink).
- Ends with a **JSON summary shape** so the operator can parse the run report.

## Step 3 — Enumerate the variables

A variable is any string in the recipe that someone adapting it would need to change. The most common variables:

- `BUSINESS_NAME`
- `BRAND_LOGO_PATH`
- `PRIMARY_REGION`
- `LANGUAGE`
- `WHATSAPP_NUMBER` (or equivalent CTA)
- `OFFER_PRICE` (if the recipe has a comment guard)
- All env var names listed in `examples/env.template`

For each, write a row in `RECIPE.md`'s **Variables you must change** table:

| Variable | Where | Default in this recipe | What to change it to |
|---|---|---|---|

The validator requires at least 3 rows. If you can only think of 3, the recipe isn't adaptable enough.

## Step 4 — Document the failure modes

Every recipe must include a `Failure modes` table with at least 3 rows. Each row:

- **Symptom** — what the operator sees (chat message, log line, alert).
- **Cause** — the underlying technical reason.
- **Recovery** — what the operator or the loop does to fix it.

Production recipes should have **at least 8 rows**. The TGO recipe ships with 9.

## Step 5 — Write the verification checklist

The `Verification checklist` section is what an operator copies into a PR description when they're adapting the recipe. Each item should be a concrete, mechanical check — "the validator exits 0", not "the recipe feels right".

At least 3 items. Production recipes typically have 8–10.

## Step 6 — Add tests

`tests/test_structure.py` — verifies the recipe's structural invariants (sections present, tables have minimum rows, files exist, no committed secrets).

`tests/test_smoke.py` — runs the canonical validator against the recipe and verifies the prompt mentions the brand asset.

Copy the structure from `recipes/tgo-full-funnel-autopilot/tests/` and adjust the regex patterns / paths.

## Step 7 — Run the validators

```bash
python scripts/validate_recipe.py --all
python scripts/validate_repo.py
python -m pytest -v
```

All three must pass. If `validate_recipe.py` complains, the message tells you exactly which section / row count is short.

## Step 8 — Open the PR

PR body should include:

- One-paragraph pitch for the loop.
- A "this is a new recipe" tag.
- The validation output (`[OK] <slug>`, `0 issue(s)`, `X passed`).
- If you've run the loop in production, a link to the operator log or issue tracker showing it ran cleanly for ≥1 month.

---

## Common mistakes

1. **The prompt is generic.** "You are a helpful assistant that helps with marketing" is not a recipe prompt. Name the business, name the cadence, name the artifact.
2. **Variables table has rows that aren't actually variables.** "Customize for your needs" is not a variable row.
3. **Failure modes are aspirational, not observed.** "If X happens, fix it" without a real incident is filler. Real failure modes come from production.
4. **The cron schedule doesn't match the operator's needs.** If your loop needs to run every 30s, that's a recipe for a polling agent — different shape.
5. **You forgot `tests/`.** A recipe without tests is a recipe that will rot.

## Recipe length budget

- `RECIPE.md`: aim for 8–15 KB. If you're pushing past 20 KB, split into `references/*.md` and link from `RECIPE.md`.
- `prompts/system.txt`: aim for 2–8 KB. Anything shorter is probably under-specified.
- `cron.config.yaml`: 1–3 KB is normal.
- `tests/`: 3–6 KB across the two files.

If your recipe exceeds these, it's probably two recipes.