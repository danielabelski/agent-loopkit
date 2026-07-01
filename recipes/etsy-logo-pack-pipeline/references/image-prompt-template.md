# Image prompt template — Stage 1 logo generation

The Stage 1 worker constructs a per-logo prompt by composing:

```
English digital product asset for Etsy. Create logo {i} of {n} for a premium Discord bot logo pack.
Theme: {theme.title}.
Concept: {concept}.
Style tonality: {style.name} — {style.style}.
High-conversion marketplace asset, polished commercial quality, centered mascot badge, strong silhouette, crisp edges, vibrant glow, square 1:1.
No readable text, no letters, no watermark, no official Discord logo.
```

Where the variables come from:

| Variable | Source | Example |
|---|---|---|
| `{i}` | `1..LOGOS_PER_PACK` | `1`, `2`, `3`, `4` |
| `{n}` | `LOGOS_PER_PACK` env var | `4` |
| `{theme.title}` | `theme_catalog.json[theme].title` | `Moderation Guardian Bot Logo Pack` |
| `{concept}` | `theme_catalog.json[theme].concepts[i]` | `shield visor guardian robot` |
| `{style.name}` | `STYLE_DIRECTIONS[(used_count + i) % len(STYLE_DIRECTIONS)].name` | `Sapphire Cybernetic Bot` |
| `{style.style}` | same index, `.style` field | `dark navy background, sapphire blue and cyan glow, ...` |

## Style directions (cycle through by used_count)

These are the 5 production style directions, rotated per-pack so successive packs feel visually distinct:

1. **Sapphire Cybernetic Bot** — dark navy + sapphire blue + cyan glow + violet accent
2. **Emerald Automation Bot** — charcoal + emerald green + mint glow + silver highlights
3. **Violet Neural Bot** — deep black-purple + electric violet + magenta glow + cyan rim
4. **Amber Security Bot** — obsidian + amber orange + gold glow + red accent
5. **Arctic Cloud Bot** — midnight blue + icy cyan + white glow + silver gradients

The `style.style` field explicitly forbids text, letters, watermarks, and the official Discord logo — these are the patterns that trigger Etsy auto-rejection.

## Mockup prompt (combined reference image)

The combined mockup is generated separately as a 4-panel grid showing all 4 logos together with a `THEME` badge in the top-right corner derived from the pack title. See `references/mockup-template.md` for the layout.

## Trademark & duplication guardrails

The image prompt does not call out these guards — they live in the **theme catalog auto-reviewer** (Stage 2):

- Theme names must not match known brands (Discord, Slack, Stripe, etc.).
- Theme concepts must not overlap with previously approved themes by >80% similarity.
- Style directions must not match official brand colors to the point of confusion.

These are rejected at the **theme level**, not the image level — once a theme is in `approved` status, Stage 1 trusts it.

---

## Why no LLM in the prompt construction

The prompt is fully **deterministic** — given a theme + style + concept, the output is reproducible. This is on purpose:

- The pipeline runs 16 images per batch. An LLM-generated prompt would burn tokens for nothing.
- Determinism lets us diff past outputs and detect drift in the image provider.
- If the prompt template needs to change, it's a code change with a clear diff.

If you need **non-deterministic** variation (e.g., to avoid Etsy flagging repeated styles), pass a random seed in `worker.env`:

```bash
RANDOMIZE_STYLE_SEED=1   # instead of (used_count + i) % len(STYLE_DIRECTIONS)
```

This trades reproducibility for variety. Default is deterministic.