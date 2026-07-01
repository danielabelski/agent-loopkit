# Recipe: Robinhood Safe Growth (Equity decision-support, 3-stage daily)

> A read-only daily-decision pipeline for a Robinhood Agentic equity account: morning entry idea, afternoon defense check, and nightly Mission Control review — all without placing orders. The pipeline produces recommendations in Spanish; real-money execution is gated on explicit per-action operator approval.

**Slug:** `robinhood-safe-growth`
**Domain:** brokerage / equities / decision-support
**Cadence:**
- Stage 1 — Entry Decision: `15 16 * * 1-5` (Mon-Fri 10:15 ET / cron 16:15 UTC, after opening volatility)
- Stage 2 — Afternoon Defense: `45 20 * * 1-5` (Mon-Fri 14:45 ET / 20:45 UTC, before close)
- Stage 3 — Mission Control: `30 4 * * 2-6` (Tue-Sat 04:30 UTC, after close)

**Owner:** [@ooovenenoso](https://github.com/ooovenenoso)
**Status:** **production** (paused for review as of 2026-06-15)
**Provenance:** extracted from 3 production crons running inside Hermes Agent against Robinhood's Agentic MCP trading endpoint (`agent.robinhood.com/mcp/trading`).

---

## What this loop does

A **3-stage, read-only** pipeline that produces equity recommendations for a Robinhood Agentic account. **Nothing is placed, cancelled, or modified without explicit operator approval per action.**

```
[Stage 1: Entry Decision]    Mon-Fri 10:15 ET
        ↓ (cron 15 16 * * 1-5 UTC)
   read-only snapshot of account / portfolio / positions / quotes
        ↓
   decide: SAFEZONE/CASH | DEFENSIVE | GROWTH
        ↓
   recommend ≤1 entry idea (ETF/megacap from allowed universe)
        ↓
   if attractive → offer REVIEW_equity_order step (still no place)

[Stage 2: Afternoon Defense] Mon-Fri 14:45 ET
        ↓ (cron 45 20 * * 1-5 UTC)
   read open positions + market into close
        ↓
   recommend: HOLD | CASH | EXIT_REVIEW
        ↓
   no new late-day entries unless exceptional + low-risk

[Stage 3: Mission Control]   Tue-Sat 04:30 UTC (after close)
        ↓ (cron 30 4 * * 2-6)
   evaluate: was cash better? which symbols over/underperformed?
        ↓
   tune local notes: favor/pause symbols, safezone threshold
        ↓
   NEVER executes trades
```

**Critical:** all three stages are **read-only** by prompt and by wrapper. The MCP `tools/call` invocations are restricted to a whitelist:

- Read: `get_accounts`, `get_portfolio`, `get_equity_positions`, `get_equity_orders`, `get_equity_quotes`, `get_equity_tradability`, historicals
- Review: `review_equity_order` (preflight, still no execution)
- **Banned:** `place_*`, `cancel_*`, `replace_*`, `add_*`, `remove_*`, `create_*`, `update_*`, `follow_*`, `unfollow_*`

Cash is a valid daily decision. The pipeline does not promise zero loss.

## Why this loop exists

Manually checking a brokerage account every weekday morning and afternoon, plus reviewing the prior day after close, is a 30-minute daily commitment that is easy to forget and easy to do inconsistently. This pipeline:

- Surfaces a structured recommendation in the operator's chat at the right times.
- Keeps the operator's decision discipline consistent (safezone threshold, universe, posture).
- Records what the system would have recommended, so the operator can compare against actual results.
- **Refuses** to place orders on its own — every real-money action is still an explicit operator click.

It is **not** an autonomous trading bot. It is decision-support with hard local guardrails.

---

## Variables you must change

> Before this loop will run for **your** account, you must change every row in this table.

| Variable | Where | Default in this recipe | What to change it to |
|---|---|---|---|
| `RH_MCP_TOKEN_FILE` | `examples/env.template` | `/root/.hermes/secure/robinhood_mcp_token.json` | Path to your saved MCP access token |
| `RH_UNIVERSE` | `prompts/snapshot.env` | `SPY,QQQ,DIA,IWM,VOO,VTI,QQQM,SCHD,MSFT,AAPL,GOOGL,AMZN,NVDA` | Your conservative tradable universe |
| `RH_SAFEZONE_THRESHOLD` | `prompts/snapshot.env` | `0.55` | Confidence below which the system recommends CASH |
| `RH_MAX_DAILY_TRADES` | `prompts/snapshot.env` | `1` | Maximum recommended entries per day |
| `RH_RISK_TOLERANCE` | `prompts/snapshot.env` | `conservative` | `conservative` / `balanced` / `aggressive` |
| `RH_LANGUAGE` | `prompts/snapshot.env` | `Spanish (es-PR)` | Output language for the operator report |
| `RH_TIMEZONE` | `prompts/snapshot.env` | `America/New_York` | Your local timezone for stage 1/2 cron alignment |
| `STAGE1_CRON` | `cron.config.yaml` | `15 16 * * 1-5` (UTC) | Your morning entry decision time |
| `STAGE2_CRON` | `cron.config.yaml` | `45 20 * * 1-5` (UTC) | Your afternoon defense time |
| `STAGE3_CRON` | `cron.config.yaml` | `30 4 * * 2-6` (UTC) | Your nightly Mission Control time |
| `RH_NOTIFY_TELEGRAM` | `examples/env.template` | `1` | Whether to deliver recommendations to chat |
| `RH_REDACT_ACCOUNTS` | `examples/env.template` | `1` | Redact account numbers in stdout (strongly recommended ON) |

---

## The three configs

This pipeline is **read-only + LLM reasoning**. The "prompts" here are the deterministic inputs the snapshot script reads.

### Stage 1 — `prompts/snapshot.env`

```bash
# Universe + thresholds
RH_UNIVERSE=SPY,QQQ,DIA,IWM,VOO,VTI,QQQM,SCHD,MSFT,AAPL,GOOGL,AMZN,NVDA
RH_SAFEZONE_THRESHOLD=0.55
RH_MAX_DAILY_TRADES=1
RH_RISK_TOLERANCE=conservative
RH_LANGUAGE=Spanish (es-PR)
RH_TIMEZONE=America/New_York

# Allowed read tools (whitelist)
RH_ALLOWED_TOOLS=get_accounts,get_portfolio,get_equity_positions,get_equity_orders,get_equity_quotes,get_equity_tradability,get_historicals

# Banned tools (defense in depth — prompt also enforces)
RH_BANNED_TOOLS=place_equity_order,place_option_order,cancel_order,replace_order,add_to_watchlist,remove_from_watchlist,create_watchlist,update_watchlist,follow,unfollow
```

### Stage 2 — `prompts/defense.env`

```bash
# Defense-stage overrides
RH_DEFENSE_MAX_LATE_ENTRIES=0     # default: no new entries in the last 90 min of trading
RH_DEFENSE_TRAILING_STOP_PCT=2.0  # recommendation: review positions trailing >2%
```

### Stage 3 — `prompts/mission.env`

```bash
# Mission Control evaluation parameters
RH_MISSION_LOOKBACK_DAYS=5       # how many prior days to evaluate
RH_MISSION_FAVOR_MIN_TRADES=2    # promote symbol to "favor" if profitable in >=2 of last 5 sessions
RH_MISSION_PAUSE_MIN_LOSSES=3    # pause symbol if loss in >=3 of last 5 sessions
RH_MISSION_NEVER_EXECUTES=1      # hard guard: Mission Control never places orders
```

## Schedules

```cron
# Stage 1: Entry Decision (Mon-Fri 10:15 ET / 16:15 UTC, after opening volatility)
15 16 * * 1-5

# Stage 2: Afternoon Defense (Mon-Fri 14:45 ET / 20:45 UTC, before close)
45 20 * * 1-5

# Stage 3: Mission Control (Tue-Sat 04:30 UTC, after Monday-Friday closes)
30 4 * * 2-6
```

The 3-stage cadence has specific reasons:

- **Entry** is after opening volatility settles (10:15 ET = ~30 min after open).
- **Defense** is before the close (14:45 ET = 75 min before close) so the operator has time to act on the recommendation.
- **Mission Control** runs after the close, with the next-day skip on Saturday so it doesn't run on Sunday open.

If you change `RH_TIMEZONE`, update these cron expressions to match the new local time.

## Skills the operator loads

| Skill | Why |
|---|---|
| `trading-bot-operations` | Safe-growth posture, no-trade-is-a-failure-mode, risk bounds, broker precision rules |
| `devops/trading-bot-operations::references/robinhood-agentic-safe-growth-crons` | The canonical entry/defense/mission architecture + hard guardrails |
| `native-mcp` | MCP initialize / notifications / tools/call patterns |

The crons themselves are **script-only** wrappers (`no_agent: true`) — they call `python3 robinhood_mcp_snapshot.py <mode>` which produces a structured JSON snapshot. The LLM reasoning happens in a separate chat session, where the operator reviews the snapshot and asks follow-ups. **The cron does not call an LLM** by design — that keeps the hot path simple and the cost flat.

---

## Inputs (what the scripts read)

| Input | What it is |
|---|---|
| `robinhood_mcp_token.json` | OAuth/PKCE access token for `agent.robinhood.com/mcp/trading` |
| MCP `get_accounts` | Discovers `agentic_allowed=true` account |
| MCP `get_portfolio` | Cash + positions + day P/L |
| MCP `get_equity_positions` | Open positions (the `agentic_allowed=true` account only) |
| MCP `get_equity_orders` | Today's open + filled orders |
| MCP `get_equity_quotes` | Real-time prices for the configured universe |
| MCP `get_equity_tradability` | Which symbols are tradable on the agentic account |
| `prompts/*.env` | The per-stage config files |

## Outputs (what the scripts write)

| Output | Where it lands |
|---|---|
| Per-run JSON snapshot | stdout (the cron delivers it to the operator's chat) |
| Account numbers redacted | Output never includes the full account number; only `••••XXXX` (last 4 digits) |
| Mission Control notes | Appended to `~/.hermes/state/robinhood_safe_growth_notes.json` (symbol favor/pause) |

## Secrets required

| Secret | Source | Purpose |
|---|---|---|
| `RH_MCP_ACCESS_TOKEN` | `~/.hermes/secure/robinhood_mcp_token.json` (read by snapshot script) | MCP session auth |
| `RH_MCP_REFRESH_TOKEN` | same file | Token refresh |
| `RH_MCP_CLIENT_ID` | same file | Dynamic client registration ID |

**Never commit real tokens.** See [`SECURITY.md`](../../SECURITY.md). The CI secrets scanner rejects any PR with a real `Mcp-Session-Id` or refresh token.

---

## Failure modes

| Symptom | Cause | Recovery |
|---|---|---|
| Stage fails with `401 Unauthorized` | MCP access token expired | Run the OAuth/PKCE refresh flow; the next snapshot will re-auth |
| Stage fails with `agentic_allowed=true` not found | Account discovery missed it, or wrong account | Re-run `get_accounts`; verify the agentic account is still active in Robinhood |
| Stage posts a recommendation the operator can't act on | Market is closed / extended hours | Defense stage is the only one that touches existing positions; Entry after-hours is banned by default |
| Stage recommends CASH when the operator wanted GROWTH | SAFEZONE_THRESHOLD too conservative OR the operator explicitly authorized GROWTH but didn't update the env | Bump `RH_SAFEZONE_THRESHOLD` to 0.5 or lower; OR change `RH_RISK_TOLERANCE=balanced` if the operator explicitly approved it |
| Account numbers leak in chat | `RH_REDACT_ACCOUNTS=0` | Set it back to `1`; the snapshot script has a `redact_text()` that masks `account_number` fields to `••••XXXX` |
| Mission Control "favor" a symbol that just had one lucky day | `RH_MISSION_FAVOR_MIN_TRADES=1` is too lax | Bump to `2` or `3`; require profit in 2+ of last 5 sessions before promoting |
| Defense stage recommends an exit-review but the operator misses it | Delivery target is wrong / `RH_NOTIFY_TELEGRAM=0` | Verify the cron `delivery: origin`; verify the chat integration; if silent, check `~/.hermes/logs/` |
| Cron fires on Saturday/Sunday | Wrong cron expression | Verify `* * 1-5` (Mon-Fri) for stages 1+2 and `* * 2-6` (Tue-Sat) for stage 3 |

## Pitfalls

- **Don't** add `place_equity_order` to the allowed tool list — the script rejects it, the prompt rejects it, and the CI rejects any PR that does it. Defense in depth.
- **Don't** lower `RH_SAFEZONE_THRESHOLD` below 0.45 to "always pick something." That defeats the safezone.
- **Don't** activate high-frequency watchers while still planning. Decide the cadence, run for a week, then adjust.
- **Don't** treat commission-free as cost-free: spread, slippage, regulatory sell fees, and cash-account settlement still matter.
- **Don't** trust the default account — verify `agentic_allowed=true` before each session. The default account may not be the agentic one.
- **Don't** accept "no trades today" as success. Zero trades in an evaluation window is a failure mode — diagnose why.
- **Don't** rely on `python3 -c` style one-off scripts to fix this pipeline. Use the canonical `ensure_*` pattern from `references/non-disruptive-continuous-runner.md`.

---

## Verification checklist

Before deploying this recipe to a new account, or after any change to the snapshot script:

- [ ] `python3 scripts/validate_recipe.py recipes/robinhood-safe-growth/` exits 0.
- [ ] `pytest recipes/robinhood-safe-growth/tests/` is green.
- [ ] `bash -n scripts/robinhood_safe_growth_entry.sh scripts/robinhood_safe_growth_defense.sh scripts/robinhood_safe_growth_mission.sh` exits 0.
- [ ] `python3 -m py_compile <snapshot.py>` exits 0 (if vendoring the script).
- [ ] MCP OAuth/PKCE token file exists at `RH_MCP_TOKEN_FILE` with valid access + refresh tokens.
- [ ] OAuth flow tested manually once: `initialize` + `notifications/initialized` + `tools/list` succeed.
- [ ] `get_accounts` returns exactly one account with `agentic_allowed=true`. If multiple or zero, fail closed.
- [ ] `RH_REDACT_ACCOUNTS=1` is set. Verify by running the snapshot once and inspecting stdout.
- [ ] `RH_BANNED_TOOLS` whitelist includes every `place_*` / `cancel_*` / `replace_*` / `add_*` / `remove_*` / `create_*` / `update_*` / `follow_*` / `unfollow_*` tool name from the discovered tool list.
- [ ] One dry run of Stage 1 produces a SAFEZONE/CASH recommendation when the universe is bearish (the default behavior — verify "no trade today" is acceptable output).
- [ ] One dry run of Stage 2 reads open positions and outputs HOLD or CASH (no place_* calls).
- [ ] One dry run of Stage 3 appends a note to `robinhood_safe_growth_notes.json` without ever calling `place_*`.

---

## Adapting this recipe

To fork this pipeline for a different broker (e.g., Alpaca, Tradier, Schwab):

1. Copy `recipes/robinhood-safe-growth/` to `recipes/<broker>-safe-growth/`.
2. Replace `scripts/robinhood_mcp_snapshot.py` with the broker's read-only API client (the wrapper shape is identical).
3. Update `examples/env.template` with the broker's auth path.
4. Update the allowed/banned tool lists in `prompts/snapshot.env` to match the broker's API.
5. Re-validate (this recipe's validator runs against the new directory).

The architecture (entry / defense / mission-control) is broker-agnostic. The hard part is always the read-only wrapper.

---

## Related recipes

- [`tgo-full-funnel-autopilot`](../tgo-full-funnel-autopilot/) — Facebook lead-funnel cron. Same multi-stage shape but different domain.
- [`etsy-logo-pack-pipeline`](../etsy-logo-pack-pipeline/) — 3-stage Etsy + Pinterest pipeline. Same multi-stage shape, script-only with a different channel.

---

## Changelog

- **1.0.0** (2026-07-01) — initial extraction from the 3 production crons (`15edb14d1d80`, `afd12aba28e9`, `6ad5790b89a2`).
- **0.9.x** — internal iterations while the pipeline ran against Robinhood's Agentic MCP in production.