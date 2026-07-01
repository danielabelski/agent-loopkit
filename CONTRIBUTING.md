# Contributing to agent-loopkit

Thanks for landing here. This repo is a catalog of **reusable playbooks for autonomous AI agent loops**. The recipe shape is opinionated on purpose: every recipe in `recipes/` looks the same so you can read them in any order, audit them quickly, and adapt them with confidence.

## TL;DR

1. Copy `RECIPE_TEMPLATE.md` → `recipes/<your-slug>/RECIPE.md`.
2. Fill in every section. The validator will reject incomplete recipes.
3. Add `cron.config.yaml` + `prompts/system.txt`.
4. Run `python3 scripts/validate_recipe.py recipes/<your-slug>/` — must exit 0.
5. Add a smoke test under `recipes/<your-slug>/tests/`.
6. Open a PR. CI will lint, validate, and run the smoke test.

---

## What "good" looks like for a recipe

A good recipe in this repo:

- **Solves one loop, not a system.** If your loop depends on three other cron jobs, that's three recipes — extract them.
- **Has a verifiable artifact.** The loop produces something the operator can see (a post, a file, a deployment, a webhook call). "The agent reflects" is not an artifact.
- **Documents its own failure modes.** If you can't list three ways it can break in production, you haven't run it in production yet.
- **Uses generic variable names.** Replace `Tech Guru Online` with `<BUSINESS_NAME>`. Brand assets live in `assets/brand/` and are easy to swap.
- **Has a smoke test.** A 30-line pytest that proves the prompt parses, the history file is appendable, and a dry run completes without writing to live APIs.

## Recipe structure (canonical)

```
recipes/<slug>/
├── RECIPE.md             # the canonical playbook (required)
├── cron.config.yaml      # the schedule + delivery settings (required)
├── prompts/
│   └── system.txt        # the agent's system prompt (required)
├── scripts/              # any helpers the loop depends on (optional)
├── assets/               # logos, references, sample posts (optional)
│   └── brand/            # brand assets the agent must use
├── references/           # longer docs the agent reads mid-run (optional)
├── examples/
│   └── env.template      # required env vars (NO real values)
└── tests/
    ├── test_structure.py # validator-driven structural test
    └── test_smoke.py     # one dry-run that proves the loop wires up
```

## Authoring workflow

1. **Open an issue** first describing the loop you want to add. Recipes are heavier than a code PR — getting alignment up front saves a round trip.
2. **Branch off `main`** as `recipe/<slug>`.
3. **Copy the scaffold:**
   ```bash
   cp -r templates/scaffold recipes/<your-slug>
   ```
4. **Fill in the scaffold.** Don't skip sections; the validator catches the ones that are empty.
5. **Validate locally:**
   ```bash
   python3 scripts/validate_recipe.py recipes/<your-slug>/
   pytest recipes/<your-slug>/tests/
   ```
6. **Open a PR** with the slug and a one-paragraph pitch in the body.
7. **CI runs**: structural validation, smoke test, link checker, secrets scan.
8. **Reviewer signs off.** A reviewer will run the recipe's smoke test against a fresh sandbox to confirm it wires up.

## Style

- **Tone:** concise, direct, no marketing language. The recipe is for engineers, not buyers.
- **Language:** English. Even if the recipe's prompt is in Spanish/French/etc., `RECIPE.md` is always English.
- **Variable naming:** `<PLACEHOLDER_LIKE_THIS>` in docs, `BUSINESS_NAME` in actual config (no angle brackets in code).
- **No emojis.** Decorative emojis (`🟢🟡🔴`, `📚`, `⚠️`) make recipes harder to skim. Use bold text for emphasis.
- **Code in fences** with the language tag (` ```python `, ` ```yaml `, ` ```cron `).
- **One sentence per line** in failure-mode tables.

## Secrets — never commit them

- Tokens, page IDs, customer data, live history files → **never in this repo**.
- Recipes reference them by **path** (e.g., `~/.hermes/secure/facebook/tgo_page_access_token.txt`) and the deploy env provides them.
- See [`SECURITY.md`](SECURITY.md) for the exact layout.
- The CI runs a secrets scan on every PR; if it finds a real token, the PR is auto-rejected.

## Releases

Recipes follow semver within their own directory:

- **MAJOR** — change the loop's behavior such that previous history files are no longer valid.
- **MINOR** — add a new variable, a new prompt section, or a new failure mode without breaking existing runs.
- **PATCH** — fix a typo, clarify a doc, or patch a script.

When you bump a recipe's version, also add an entry to the repo-level `CHANGELOG.md`.

## Code of conduct

Be useful. Don't be clever. If a recipe you wrote breaks for someone else, you fix it; if you can't, you deprecate it explicitly and link to the replacement.

## Questions?

Open an issue with the `question` label. There's no Discord, no mailing list, no DMs — issues are the source of truth.