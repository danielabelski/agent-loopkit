# Stage architecture — why 3 stages, why these schedules

The Robinhood Safe Growth recipe splits the daily decision into **three** stages instead of one continuous loop. This is on purpose. Here's the reasoning.

## Why not one continuous loop?

A single daily loop that does entry + defense + mission in one run would have to either:

- Run all three in sequence at one time (e.g., 4:30 AM), missing real-time market context. **Bad** — by the time Mission Control runs, the entry decision is stale.
- Run three times during the day at the right times, but with state shared between runs. **Worse** — shared state across cron invocations is fragile (lock files, partial writes, restart races).

## Why 3 separate crons instead?

- **Entry decision** needs to be at the right moment in the trading day (10:15 ET, after opening volatility).
- **Defense check** needs to be a few hours later, with the positions already on the books (14:45 ET, before close).
- **Mission Control** needs to be after the close, with the full day's data (04:30 UTC = 23:30 ET previous day).

Each stage runs **exactly when its data is fresh and the operator has time to act**.

Each stage is **independent**: the snapshot is recomputed each run. Stage 2 doesn't depend on Stage 1's output; it just re-reads positions. Stage 3 doesn't depend on Stage 1/2 either — it reads its own history.

This decoupling means:

- A Stage 1 failure doesn't block Stage 2.
- The operator can skip a day (pause Stage 1) without breaking Mission Control.
- The cron schedule can be adjusted (e.g., move Entry to 9:45 ET) without touching the others.

## Why script-only (no_agent: true)?

A script-only cron:

- Costs ~zero per run (no LLM tokens).
- Has a predictable latency (the snapshot is fast — MCP `get_*` calls take 1-3s each).
- Produces a structured JSON output the operator can read, save, and review at their own pace.
- Cannot accidentally call `place_*` because there's no LLM to misread a prompt.

The LLM reasoning happens in a separate chat session, where the operator reviews the snapshot, asks follow-up questions, and decides what to do. **The LLM never has write access to the broker.** It only sees the snapshot the script produced.

This is the **opposite** of an autonomous trading bot. The pipeline is decision-support, not autonomous execution.

## Why three different cadences?

| Stage | When (ET) | Cron (UTC) | Why this time? |
|---|---|---|---|
| Entry | 10:15 AM Mon-Fri | `15 16 * * 1-5` | ~30 min after market open, after opening volatility settles |
| Defense | 2:45 PM Mon-Fri | `45 20 * * 1-5` | 75 min before close; gives operator time to act on a recommendation |
| Mission | 11:30 PM Mon-Fri (= 04:30 UTC Tue-Sat) | `30 4 * * 2-6` | After close, with full day data; skips Sunday |

These are **defaults**. The recipe exposes them as `STAGE1_CRON` / `STAGE2_CRON` / `STAGE3_CRON` in `cron.config.yaml`. If your local market opens at a different time, adjust both the cron expression AND the comment.

## Why no_after-hours, no_options by default?

The recipe's default posture is **conservative**. Both after-hours and options add:

- Wider spreads → worse execution.
- Lower liquidity → harder entries/exits.
- Different risk characteristics (overnight gap risk, theta decay, etc.).

If you want to enable them, you must:

1. Add the relevant tools to `RH_ALLOWED_TOOLS`.
2. Update the prompt to acknowledge the new universe.
3. Update the snapshot script to handle the new tool shapes.
4. Run the verification checklist end-to-end before enabling the cron.

Each of these is a separate gate. The recipe makes it explicit that enabling after-hours or options is a multi-step decision, not a one-line toggle.

## What about weekends?

The crons are intentionally:

- Stage 1: Mon-Fri (`* * 1-5`) — markets closed on weekends.
- Stage 2: Mon-Fri (`* * 1-5`) — same.
- Stage 3: Tue-Sat (`* * 2-6`) — runs after Friday's close, doesn't run on Sunday.

If your market has different trading hours, adjust `STAGE*_CRON` accordingly.

## What if I want only one stage?

That's a different recipe. If you only want entry decisions (no defense, no Mission Control), copy the recipe and delete stages 2+3. The recipe shape supports partial deployment — just remove the cron blocks from `cron.config.yaml` and the corresponding `.env` files.