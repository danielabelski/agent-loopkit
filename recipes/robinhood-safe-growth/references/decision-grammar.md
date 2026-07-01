# Decision grammar — SAFEZONE / DEFENSIVE / GROWTH

Each stage outputs a **mode** plus a **recommended action**. The grammar is fixed so the operator can quickly parse the chat message at a glance.

## The three modes

### SAFEZONE / CASH

The system recommends doing nothing — staying in cash.

Triggers (any one is enough):

- Confidence in any direction < `RH_SAFEZONE_THRESHOLD` (default 0.55).
- Universe-wide bearish setup (multiple ETFs red on the day, VIX elevated).
- Recent session had a loss; cooldown period active.
- Account has options-level-mismatch (agentic account lost options permission).
- Operator has set `RH_RISK_TOLERANCE=conservative` and there's no clear edge.

**Output template:**

```
mode: SAFEZONE / CASH
razón: <one sentence>
recomendación: mantener efectivo
próximo paso: ningún trade hoy; revisar mañana en Stage 1
```

### DEFENSIVE

There are open positions and the system recommends reviewing them.

Triggers:

- Any open position trailing > `RH_DEFENSE_TRAILING_STOP_PCT` (default 2%).
- Open position hit daily loss limit.
- Market context deteriorated intraday (close < open on SPY/QQQ).

**Output template:**

```
mode: DEFENSIVE
posiciones abiertas: <count>
alertas: <list of position_ids with rationale>
recomendación: HOLD | CASH | EXIT_REVIEW (con sugerencia específica)
próximo paso: revisar manualmente antes del cierre
```

### GROWTH

The system recommends an entry idea (Stage 1 only).

Triggers:

- Confidence ≥ `RH_SAFEZONE_THRESHOLD`.
- Setup matches a known pattern (EMA pullback, breakout, mean-reversion, etc.).
- Within allowed universe.
- Not in cooldown.

**Output template:**

```
mode: GROWTH
símbolo candidato: <SYMBOL>
dirección: BUY | SELL
nivel de entrada sugerido: <price or "a mercado">
stop-loss: <price>
take-profit: <price>
tamaño sugerido: <shares or % of buying power>
razón: <one sentence>
próximo paso: puedo hacer REVIEW si apruebas (no ejecuto)
```

## The banned actions

No stage output ever recommends:

- `place_*` order (the system does not place orders).
- `cancel_*` (operator can cancel manually).
- `replace_*` (operator can replace manually).
- Any watchlist mutation.
- After-hours entries.
- Options (unless explicitly enabled per `references/mcp-setup.md`).

If the system recommends "review an order," the operator runs `review_equity_order` themselves in their MCP client. The recipe's cron never calls `review_equity_order` — that's also a manual step.

## Cooldown rules

After a session with a loss, the next Stage 1 run defaults to SAFEZONE/CASH for `RH_COOLDOWN_DAYS` (default 1). The cooldown resets when:

- The operator acknowledges the loss manually.
- A new day starts without a fresh loss.
- `RH_COOLDOWN_DAYS` is set to 0 (no cooldown).

This is the simplest "no-trade-is-a-failure-mode" mitigation: after a loss, the default is CASH, not "find a recovery trade."

## Mission Control tuning

Mission Control (Stage 3) tunes the recipe's notes file based on the prior week's performance:

| Symbol outcome | Action |
|---|---|
| Profitable ≥ `RH_MISSION_FAVOR_MIN_TRADES` of last 5 sessions | Add to "favor" list |
| Loss in ≥ `RH_MISSION_PAUSE_MIN_LOSSES` of last 5 sessions | Add to "pause" list |
| Mixed / no clear signal | No change |

The favor/pause list feeds into the Stage 1 prompt for the next week. Symbols in "pause" are still in `RH_UNIVERSE` but get a confidence penalty. Symbols in "favor" get a confidence boost.

**Mission Control never auto-removes symbols from the universe.** That's an explicit operator decision.

## What this grammar is NOT

- **Not** a strategy. The grammar is the *output format*; the strategy (which setup, which signal, what confidence threshold) is up to the operator.
- **Not** advice. The system says "candidate BUY of VOO at $X" — it doesn't say "you should buy VOO." The operator decides.
- **Not** guaranteed. SAFEZONE/CASH can still lose to opportunity cost. GROWTH can still lose money. The grammar is honest about uncertainty.

## Example Stage 1 output (good day)

```
mode: GROWTH
símbolo candidato: VOO
dirección: BUY
nivel de entrada: a mercado ($485.20)
stop-loss: $479.10 (~1.25%)
take-profit: $498.40 (~2.7%)
tamaño sugerido: 4% del buying power
razón: SPY en soporte, VIX bajo, RV/IV neutral, dentro del universo.
       Sin pérdidas recientes. Cooldown limpio.
próximo paso: puedo hacer REVIEW si apruebas
```

## Example Stage 1 output (no-edge day)

```
mode: SAFEZONE / CASH
razón: confianza máxima del universo = 0.42 (umbral 0.55).
       Mercado lateral, sin catalizador claro.
recomendación: mantener efectivo
próximo paso: ningún trade hoy; revisar mañana en Stage 1.
```

## Example Stage 2 output (defensive day)

```
mode: DEFENSIVE
posiciones abiertas: 2
alertas:
  - VOO: trailing -2.3% desde entrada (umbral -2.0%)
  - MSFT: trailing -0.8% (OK)
recomendación: revisar VOO para HOLD vs EXIT_REVIEW
próximo paso: cerrar Stage 2 con la decisión manual antes de las 16:00 ET
```