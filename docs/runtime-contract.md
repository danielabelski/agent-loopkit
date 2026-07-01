# Runtime contract — what every recipe assumes about its host

A "recipe" in this repo is a template. The host that runs the recipe — Hermes Agent, GitHub Actions, plain `cron`, K8s CronJob, etc. — must satisfy a few invariants for the recipe to behave the way `RECIPE.md` says it will.

This document is for recipe authors. If you want to deploy a recipe to a target that doesn't satisfy these invariants, you must either:

1. Adapt the target to satisfy them, or
2. Document the deviation in the recipe's `references/runtime-contract.md`.

---

## Required invariants

### 1. Schedule is honored

The host must run the loop at the cadence declared in `cron.config.yaml`'s `schedule` field. If a run is missed (host down, OOM, etc.), the host must not backfill — missed runs are missed. Recipes that need backfill should declare it in `references/runtime-contract.md`.

### 2. Inputs are read-only

The host must mount or expose the files declared in `cron.config.yaml`'s `inputs` map. The recipe treats those paths as **read-only**: it must not modify the brand asset, the niche pool, or the reference images.

### 3. Outputs are writable

The host must provide write access to the directories declared in `cron.config.yaml`'s `outputs` map. The recipe appends to the history file; it must not truncate it.

### 4. Secrets are sourced from the secret layout

The host must provide the secrets declared in `RECIPE.md`'s `Secrets required` table at the paths/env vars listed in `examples/env.template`. The recipe never reads secrets from any other source.

The default secret layout (matching Hermes Agent) is `~/.hermes/secure/<service>/<name>.txt`. Override per recipe if your runtime uses a different layout.

### 5. Skills are loaded before the prompt

The host must load the skills declared in `cron.config.yaml`'s `skills` array **before** the agent's first turn. Skills are not optional — they encode the agent's domain knowledge.

### 6. Toolsets are constrained

The host must restrict the agent's tools to the set declared in `cron.config.yaml`'s `enabled_toolsets`. A recipe that doesn't declare `enabled_toolsets` is unverified and may be refused by the host.

### 7. Failure semantics

If a run raises, the host must:

- Append a record to the history file with `status: "error"`.
- Surface the error to the operator (Telegram, email, GitHub issue, etc.).
- Not auto-retry unless the recipe's `cron.config.yaml` has a `retry` block.

The host must **auto-pause** the cron after `cron.config.yaml.limit.max_consecutive_errors` consecutive failures. A paused cron requires operator intervention to resume.

### 8. Idempotency

Recipes are designed to be idempotent within a single run. The host must not run the same recipe concurrently from two different nodes — recipes do not implement cross-node locks.

---

## Deployment targets

| Target | Satisfies contract? | Notes |
|---|---|---|
| Hermes Agent cron | Yes (default) | All invariants are native. |
| GitHub Actions cron | Partial | Inputs must be checked into the repo or fetched from a secret. Outputs must land in the repo (PR) or an external storage. Skills become inline prompt fragments. |
| K8s CronJob | Yes | Mount inputs as ConfigMaps; mount secrets as Secret volumes. |
| Plain `cron` + shell | Partial | No skill loading. Prompts become shell variables. The recipe author must write a `runner.sh`. |

See [`deployment-targets.md`](deployment-targets.md) for the concrete translation for each target.