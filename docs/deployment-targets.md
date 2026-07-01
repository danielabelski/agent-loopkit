# Deployment targets

How to run a recipe in this catalog on different scheduling backends.

The canonical target is **Hermes Agent cron** (the host the original recipes were extracted from). This doc covers the translations for other common targets.

---

## 1. Hermes Agent cron (canonical)

```bash
# From the recipe's directory
hermes cronjob create \
  --name "TGO Full Funnel Autopilot" \
  --from cron.config.yaml \
  --prompt "$(cat prompts/system.txt)" \
  --skills facebook-platform-automation,local-business-funnel-autopilot,local-web-service-deployment,image-generation-workflows
```

The companion script-only loop (`scripts/comment-keyword-private-reply-bot.sh`) is registered with `--no-agent`:

```bash
hermes cronjob create \
  --name "TGO Full Funnel \$350 Comment Guard" \
  --schedule "45 1,15,20 * * *" \
  --from scripts/comment-guard-config.yaml \
  --no-agent
```

---

## 2. GitHub Actions cron

```yaml
# .github/workflows/tgo-full-funnel.yml
name: TGO Full Funnel Autopilot
on:
  schedule:
    - cron: '0 1,15,20 * * *'
  workflow_dispatch: {}

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          repository: ooovenenoso/agent-loopkit
          path: agent-loopkit

      - name: Run the loop
        env:
          TGO_PAGE_ACCESS_TOKEN: ${{ secrets.TGO_PAGE_ACCESS_TOKEN }}
          TGO_USER_ACCESS_TOKEN: ${{ secrets.TGO_USER_ACCESS_TOKEN }}
          TGO_IMAGE_API_KEY: ${{ secrets.TGO_IMAGE_API_KEY }}
        run: |
          # Translate the recipe's prompt into a single `hermes` call
          hermes --single-turn \
            --prompt "$(cat agent-loopkit/recipes/tgo-full-funnel-autopilot/prompts/system.txt)" \
            --skills facebook-platform-automation,local-business-funnel-autopilot,local-web-service-deployment,image-generation-workflows \
            --workdir /tmp/tgo-run
```

For the companion script-only loop, replace the `hermes --single-turn` call with `python3 path/to/full_funnel_price_comment_guard.py` and feed the secrets via `secrets.*` as above.

---

## 3. Kubernetes CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: tgo-full-funnel-autopilot
spec:
  schedule: "0 1,15,20 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: agent
              image: ghcr.io/ooovenenoso/hermes-agent:latest
              args: ["--single-turn", "--prompt-file=/recipes/tgo-full-funnel-autopilot/prompts/system.txt"]
              volumeMounts:
                - name: recipes
                  mountPath: /recipes
                  readOnly: true
                - name: tgo-secrets
                  mountPath: /run/secrets/tgo
                  readOnly: true
                - name: tgo-history
                  mountPath: /history
                - name: tgo-landings
                  mountPath: /landings
              env:
                - name: TGO_HISTORY_FILE
                  value: /history/campaigns.jsonl
                - name: TGO_LANDINGS_DIR
                  value: /landings
                - name: TGO_BRAND_LOGO
                  value: /recipes/tgo-full-funnel-autopilot/assets/brand/logo.jpg
              restartPolicy: OnFailure
          volumes:
            - name: recipes
              configMap:
                name: agent-loopkit-recipes
            - name: tgo-secrets
              secret:
                secretName: tgo-secrets
            - name: tgo-history
              persistentVolumeClaim:
                claimName: tgo-history
            - name: tgo-landings
              persistentVolumeClaim:
                claimName: tgo-landings
```

---

## 4. Plain `cron` + shell (lowest common denominator)

If you're running the loop on a VPS with `cron` and shell access:

```cron
# /etc/cron.d/tgo-full-funnel
0 1,15,20 * * * tgo /opt/tgo/run-full-funnel.sh
```

```bash
#!/usr/bin/env bash
# /opt/tgo/run-full-funnel.sh
set -euo pipefail

RECIPE=/opt/agent-loopkit/recipes/tgo-full-funnel-autopilot

# Load secrets
set -a
source /opt/tgo/secrets/tgo.env
set +a

# Invoke the loop. `hermes` is the runtime; without it, you can paste the
# prompt into your LLM CLI of choice (e.g., `claude -p "$(cat $RECIPE/prompts/system.txt)"`).
hermes --single-turn \
  --prompt-file "$RECIPE/prompts/system.txt" \
  --workdir /opt/tgo/run \
  --tools terminal,file,vision,web
```

This pattern works but loses the structured skill loading, the secret-scrubbing, and the consecutive-error auto-pause. Use Hermes when you can.

---

## Choosing a target

| Need | Target |
|---|---|
| Single-tenant, full operator control, every secret inside your infra | Hermes Agent cron |
| Public CI on GitHub, free for public repos | GitHub Actions cron |
| Multi-tenant SaaS, multiple isolated runs | K8s CronJob |
| Legacy VPS, no scheduler framework, want zero deps | Plain `cron` + shell |