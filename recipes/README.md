# recipes/

> The catalog of playbooks in this repo. Each subdirectory is one recipe.

## Browse

| Recipe | Domain | Cadence | Status |
|---|---|---|---|
| [`tgo-full-funnel-autopilot/`](tgo-full-funnel-autopilot/) | Local-business Facebook lead funnel (niche → landing → post → comment guard) | 3×/day (`0 1,15,20 * * *`) | **production** (paused for review) |
| [`etsy-logo-pack-pipeline/`](etsy-logo-pack-pipeline/) | Digital-assets Etsy + Pinterest (3-stage pipeline: generate → draft → pin) | 4×/day + 1×/day | **production** (paused for review) |

## Adding a new recipe

```bash
# 1. Copy the scaffold
cp -r ../templates/scaffold/ ./<your-slug>/

# 2. Fill in RECIPE.md, cron.config.yaml, prompts/system.txt, examples/env.template
$EDITOR ./<your-slug>/RECIPE.md
$EDITOR ./<your-slug>/cron.config.yaml
$EDITOR ./<your-slug>/prompts/system.txt
$EDITOR ./<your-slug>/examples/env.template

# 3. Validate
python ../scripts/validate_recipe.py --all
python ../scripts/validate_repo.py
python -m pytest -v

# 4. Open a PR
gh pr create --title "[RECIPE] <slug> — <one-line summary>"
```

See [`CONTRIBUTING.md`](../CONTRIBUTING.md) for the full process.

## Recipe contract

Every recipe in this directory must satisfy the validator's checks. The non-negotiable requirements:

- `RECIPE.md` has every required section.
- `cron.config.yaml` has `schedule`, `delivery`, and `skills`.
- `prompts/system.txt` is ≥50 chars and substantive.
- `examples/env.template` uses `__replace_me__` placeholders, never real tokens.
- Failure modes table has ≥3 rows.
- Verification checklist has ≥3 items.
- The CI secrets scanner finds no real token patterns anywhere in the recipe.

Recipes that don't pass the validator cannot be merged.