# Security & secrets

Recipes in this repo are **templates**, not runnable artifacts. Every recipe references secrets (page tokens, API keys, customer data) by path or env-var name. **Real values are never committed.**

## The secret layout this repo assumes

By default, recipes assume secrets live under `~/.hermes/secure/<service>/`, e.g.:

```
~/.hermes/secure/facebook/
├── tgo_page_access_token.txt
└── tgo_user_access_token.txt

~/.hermes/secure/openai/
└── api_key.txt
```

This matches the layout the [Hermes Agent](https://github.com/ooovenenoso/hermes-agent) runtime expects. If you're using a different runtime, override the path in the recipe's `cron.config.yaml`.

## What must NEVER be committed

- Real page access tokens, user access tokens, API keys.
- Real customer data (leads, conversations, contact lists).
- Real history files (`history/campaigns.jsonl` from production).
- Real brand assets that include real customer logos or photos.
- `.env` files with real values. Use `examples/env.template` instead.

## The `examples/env.template` convention

Every recipe ships with `examples/env.template`. It lists every env var the loop expects, with **placeholder** values:

```bash
# examples/env.template — NO real values
TGO_PAGE_ACCESS_TOKEN=__replace_me__
TGO_PAGE_ID=__replace_me__
TGO_BRAND_LOGO=/absolute/path/to/your/logo.jpg
TGO_WHATSAPP_NUMBER=+1787XXXXXXXX
```

Operators copy it to `.env` (or to the deploy env) and replace the placeholders. The `__replace_me__` sentinel is detected by the CI secrets scanner and fails the build if it ever ships with a real token.

## CI secrets scanner

The repo's CI runs a basic secret scanner on every PR. It greps for:

- GitHub PATs (`ghp_`, `github_pat_`).
- Slack tokens (`xox[abprs]-`).
- OpenAI keys (`sk-`, `sk-proj-`).
- Facebook tokens (long hex strings in `*.txt`).
- Anything matching the `__replace_me__` escape hatch being changed to a non-placeholder.

A real token found in a PR auto-rejects the PR. If you need to ship a real token (e.g., a deploy key) **do not** — open an issue instead and we'll find a workaround.

## Reporting a vulnerability

If you find a real secret in a public mirror of this repo, **do not open a public issue**. Email the maintainer directly (see GitHub profile) or open a private security advisory via GitHub's "Security" tab on the repo page.

## Brand assets

Brand assets in `assets/brand/` are illustrative only. If you're adapting a recipe for a different business, replace **all** of:

- The logo file.
- The WhatsApp number in `prompts/system.txt`.
- The brand name in `cron.config.yaml` and `prompts/system.txt`.
- The page ID + token in your deploy env.

Leaving any of the original brand assets in place will cause the loop to publish under the wrong identity.

## Compliance

Recipes that touch regulated data (lead capture, payment info, health data) must add a `compliance.md` to their directory explaining the controls. See `recipes/tgo-full-funnel-autopilot/compliance.md` for an example.