# About this catalog

## What it is

A catalog of **reusable playbooks for autonomous AI agent loops**. Each recipe under `recipes/` is a self-contained package: the agent's prompt, the schedule, the scripts, the secrets layout, the failure modes, and the verification checklist.

The catalog is intentionally heterogeneous. Different recipes cover different domains (lead funnels, digital-assets pipelines, content generation), different cadences (4×/day, 3×/day, daily), and different platforms (Facebook, Etsy, Pinterest, GitHub). The shape is consistent so you can read them in any order, but the contents reflect what each domain actually requires.

## Provenance

The first recipes in this catalog were extracted from production cron flows running inside the maintainer's own agent runtime. Those extractions happened in 2026 and are public on the assumption that:

- The **shape** of a recipe (prompt + schedule + scripts + secrets + failure modes) is useful to anyone building agent loops, regardless of platform.
- The **specifics** of any one recipe (business name, brand asset, region) are illustrative only — every recipe has a "Variables you must change" table that walks you through replacing them.

The extraction process for each recipe is documented in `docs/adapting-an-existing-loop.md`. The shape conventions are in `RECIPE_TEMPLATE.md`.

## What this catalog is NOT

- **Not a runtime.** Recipes don't ship an agent. They describe how to wire one up in your runtime of choice (Hermes Agent, GitHub Actions, K8s CronJob, plain `cron`). See `docs/deployment-targets.md` for translations.
- **Not a hosted service.** There's no API, no SaaS, no shared execution. Each operator runs their own copy.
- **Not a one-size-fits-all framework.** The recipe shape is opinionated, but the catalog doesn't claim every cron-driven agent loop fits the shape. If yours doesn't, that's a feature — open an issue and we'll discuss whether to extend the template.

## How new recipes get added

Anyone can submit a PR. The maintainer reviews for:

1. **Structure compliance** — automated by `scripts/validate_recipe.py`.
2. **Failure mode realism** — every recipe needs ≥3 documented failure modes from actual production experience.
3. **Variable generality** — no recipe hardcodes a specific business's name, region, or brand. Generic placeholders only.
4. **Secret handling** — no real tokens, ever. The CI scans for them.
5. **Test coverage** — every recipe ships with `tests/test_structure.py` and at least one smoke test.

The process is documented in `CONTRIBUTING.md`. The bar is "would someone unfamiliar with this domain be able to adapt this recipe in an afternoon?"

## License

MIT. See `LICENSE`. Recipes are templates; the **brand assets, tokens, and customer data referenced in any recipe must not be reused as-is** for a different business. See `SECURITY.md`.

## Maintainer

[@ooovenenoso](https://github.com/ooovenenoso). Issues are the source of truth — there's no Discord, no mailing list, no DMs.