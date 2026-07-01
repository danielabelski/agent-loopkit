# agent-loopkit

> **Reusable playbooks for autonomous AI agent loops — copy, customize, ship.**

![Banner](assets/banner.png)

Visual system: [`references/visual-identity.md`](references/visual-identity.md) · social preview: [`assets/social-preview.png`](assets/social-preview.png)

A growing catalog of battle-tested **recipes** for autonomous AI agent workflows: each one is a self-contained, opinionated package that captures a cron-driven loop (the agent, the prompt, the schedule, the scripts, the secrets layout, the failure modes) so you can drop it into any scheduler that runs prompts on a cadence and have it working the same day — not the same quarter.

Think of it as a *cookbook* for agent loops: pick a recipe, change the variables, ship.

---

## Why this exists

Autonomous agents are powerful but **brittle at the seams**. The hard part isn't the model call — it's:

- the prompt that frames the loop correctly so the agent doesn't drift or hallucinate
- the schedule cadence that survives weekends and rate limits
- the scripts that handle "I can't reach the API" / "the page id rotated" / "the brand asset is missing"
- the reviewer gate that catches a bad post before it goes live
- the history file that prevents the same niche from being picked twice

This repo packages all of those decisions into one directory per recipe, so you don't have to rediscover them.

## When to use

- You want to **clone an existing autonomous loop** that already runs in production somewhere and adapt it to your own business.
- You're building a **new cron-driven agent loop** and want a vetted template instead of starting from a blank prompt.
- You want to **standardize** how your team ships agent automations so they're auditable, restartable, and replaceable.

**Don't use for:** one-shot scripts, interactive chat agents, or non-recurring tasks. If you only need to run something once, use a plain script.

---

## How a recipe is shaped

Every recipe in `recipes/` follows the same shape so you can read them in any order:

```
recipes/<recipe-slug>/
├── RECIPE.md             # the canonical playbook (the recipe)
├── cron.config.yaml      # the schedule + toolsets + delivery settings
├── prompts/              # the agent's prompt (LLM) or env files (script-only)
│   └── system.txt
├── scripts/              # any helpers the loop depends on
├── assets/               # logos, references, sample posts
├── references/           # longer docs the agent reads mid-run
├── tests/                # structural tests + a tiny smoke test
└── examples/
    └── env.template      # required env vars (no real values)
```

`RECIPE.md` is the heart: it's the human-readable playbook with the goal, the prompt, the schedule, the failure modes, and the verification checklist. If you only read one file per recipe, read that one.

`cron.config.yaml` is the machine-readable counterpart: drop it into any scheduler that supports recurring prompts (Hermes, GitHub Actions, K8s CronJob, plain `cron`) and the loop comes alive.

See `RECIPE_TEMPLATE.md` for the exact template, and `docs/authoring-a-recipe.md` for the workflow to add your own.

---

## Recipes

Browse the full catalog at [`recipes/README.md`](recipes/README.md). Current entries:

| Recipe | Domain | Cadence | Status |
|---|---|---|---|
| [`tgo-full-funnel-autopilot`](recipes/tgo-full-funnel-autopilot/) | Local-business Facebook lead funnel | 3×/day | **production** (paused for review) |
| [`etsy-logo-pack-pipeline`](recipes/etsy-logo-pack-pipeline/) | Digital-assets Etsy + Pinterest | 4×/day + 1×/day | **production** (paused for review) |
| [`robinhood-safe-growth`](recipes/robinhood-safe-growth/) | Read-only equity decision-support | 3×/day (Mon-Fri) | **production** (paused for review) |

Each recipe entry links to its own directory. The catalog is intentionally heterogeneous — different domains, different cadences, different platforms — so you can compare shapes and steal patterns across them.

---

## Quickstart

### 1. Pick a recipe

```bash
git clone https://github.com/ooovenenoso/agent-loopkit.git
cd agent-loopkit
ls recipes/
```

### 2. Copy it to your own project

```bash
cp -r recipes/<recipe-slug> ~/my-agent-loop
cd ~/my-agent-loop
```

Replace `<recipe-slug>` with the directory you want to start from. Every recipe is self-contained — you don't need the rest of the repo to run it.

### 3. Edit the variables

Every recipe has a **"Variables you must change"** section near the top of `RECIPE.md`. Rename, swap the brand asset, point secrets at your accounts, adjust the cadence.

### 4. Drop the cron

Each recipe ships with a `cron.config.yaml` that matches the canonical Hermes shape:

```bash
# For Hermes — see docs/deployment-targets.md for GitHub Actions / K8s / plain cron
hermes cron create \
  --from ./cron.config.yaml \
  --prompt "$(cat prompts/system.txt)"
```

Or wire it into GitHub Actions, a K8s CronJob, or a plain `cron` entry.

### 5. Verify

Each recipe ships with a `tests/` directory that runs the structural validators and a smoke test. The recipe's `RECIPE.md` ends with a verification checklist you can copy-paste.

---

## Repository structure

```
agent-loopkit/
├── README.md                       # you are here
├── RECIPE_TEMPLATE.md              # the canonical recipe shape
├── CONTRIBUTING.md                 # how to add a recipe
├── CHANGELOG.md                    # release notes
├── LICENSE                         # MIT
├── SECURITY.md                     # how secrets are handled
├── CODE_OF_CONDUCT.md              # community norms
├── assets/
│   ├── banner.png                  # README header
│   ├── social-preview.png          # GitHub social preview
│   ├── logo.png                    # project mark
│   └── icon.png                    # small icon
├── recipes/                        # the actual playbooks (see recipes/README.md)
├── templates/                      # blank scaffolds for new recipes
├── scripts/                        # repo-level tools (validate, lint)
├── references/                     # shared reference docs (about, runtime contract)
├── docs/                           # longer guides (authoring, deployment, adapting)
└── .github/
    ├── ISSUE_TEMPLATE/
    └── workflows/
```

For the catalog, see [`recipes/README.md`](recipes/README.md).

---

## Contributing a recipe

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Short version:

1. Copy `RECIPE_TEMPLATE.md` into `recipes/<your-slug>/RECIPE.md`.
2. Fill in every section. The validator will reject recipes with empty "Failure modes" or "Verification" sections.
3. Add `cron.config.yaml` and either `prompts/system.txt` (LLM recipes) or `prompts/*.env` (script-only recipes).
4. Run `python3 scripts/validate_recipe.py recipes/<your-slug>/` — must exit 0.
5. Open a PR. The recipe CI will lint frontmatter, check cross-links, run the smoke test, and scan for committed secrets.

## License

MIT — see [`LICENSE`](LICENSE). Recipes are templates; the **brand assets, tokens, and customer data referenced in any recipe must not be reused as-is** for a different business. See [`SECURITY.md`](SECURITY.md).

---

*Maintained by [@ooovenenoso](https://github.com/ooovenenoso).*