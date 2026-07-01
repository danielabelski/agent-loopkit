# Security & secrets

Recipes in this repo are **templates**, not runnable artifacts. Every recipe references secrets (page tokens, API keys, customer data) by path or env-var name. **Real values are never committed.**

## The secret layout

There is no single secret layout this repo requires. Each recipe declares its expected layout in `examples/env.template` — typically a path like `/run/secrets/<service>/<key>` or `~/.secure/<service>/<key>.txt`. Operators are responsible for:

- Creating the file before deploying the recipe.
- Locking down permissions (0600 or 0400, owned by the recipe's runtime user).
- Wiring the file path into the deploy env so the recipe reads it.

A common pattern (matching the layout the maintainer's own runtime uses) is:

```
~/.secure/
├── <service>/
│   ├── api_key.txt
│   └── <key_name>.txt
```

But this is **not** the only valid shape. Adapt the recipe's `examples/env.template` to whatever layout your runtime expects.

## What must NEVER be committed

- Real access tokens, refresh tokens, API keys.
- Real customer data (leads, conversations, contact lists).
- Real history files from production runs.
- Real brand assets that include customer logos or photos.
- `.env` files with real values. Use `examples/env.template` instead.

## The `examples/env.template` convention

Every recipe ships with `examples/env.template`. It lists every env var the loop expects, with **placeholder** values:

```bash
# examples/env.template — NO real values
<SERVICE>_API_KEY=__replace_me__
<SERVICE>_TOKEN_FILE=/run/secrets/<service>/token
<BRAND_ASSET_PATH>=/absolute/path/to/your/brand-asset.jpg
```

Operators copy it to `.env` (or to the deploy env) and replace the placeholders. The `__replace_me__` sentinel is detected by the CI secrets scanner and fails the build if it ever ships with a real token.

## CI secrets scanner

The repo's CI runs a basic secret scanner on every PR. It greps for known token formats:

| Pattern | Service |
|---|---|
| `ghp_[A-Za-z0-9]{20,}` | GitHub PAT |
| `github_pat_[A-Za-z0-9_]{20,}` | GitHub fine-grained PAT |
| `xox[abprs]-[A-Za-z0-9-]{10,}` | Slack token |
| `sk-[A-Za-z0-9]{20,}` | OpenAI API key |
| `sk-proj-[A-Za-z0-9]{20,}` | OpenAI project key |
| `EAA[A-Za-z0-9]{50,}` | Facebook long-lived token |

A real token found in a PR auto-rejects the PR. If you need to ship a real token (e.g., a deploy key) **do not** — open an issue instead and we'll find a workaround.

## Reporting a vulnerability

If you find a real secret in a public mirror of this repo, **do not open a public issue**. Email the maintainer directly (see GitHub profile) or open a private security advisory via GitHub's "Security" tab on the repo page.

## Brand assets

Brand assets in `assets/brand/` are illustrative only. If you're adapting a recipe for a different business, replace **all** of:

- The logo file.
- Any contact numbers (WhatsApp, phone, etc.) referenced in the recipe's prompt.
- The brand name in `cron.config.yaml` and the prompt file.
- The account IDs + tokens in your deploy env.

Leaving any of the original brand assets in place will cause the loop to publish under the wrong identity.

## Compliance

Recipes that touch regulated data (lead capture, payment info, health data, etc.) should add a `compliance.md` to their directory explaining the controls in place. This is a **per-recipe** requirement, not enforced by the repo-level validator — recipe authors know their domain best.

Examples of what to document:

- What PII the recipe collects, where it's stored, and how long.
- Whether the recipe transmits data over TLS and to which endpoints.
- Whether there's an opt-out / deletion path for the data subject.
- Whether any third-party processor (e.g., Facebook, OpenAI) has a DPA in place.

If your recipe collects leads and you skip `compliance.md`, the reviewer will likely ask for it before merging.