# Recipe: TGO Full Funnel Autopilot (lead-funnel loop)

> A 3×/day agent loop that picks a fresh local-business niche, generates a landing page, generates a square Facebook post image and a vertical story, runs a reviewer gate, publishes to Facebook, and posts a price-comment reply to comments asking for pricing — all without operator intervention.

**Slug:** `tgo-full-funnel-autopilot`
**Domain:** local-business / lead-funnel / Facebook
**Cadence:** `0 1,15,20 * * *` (3×/day — morning, mid-afternoon, evening)
**Owner:** [@ooovenenoso](https://github.com/ooovenenoso)
**Status:** **production** (paused for review as of 2026-06-20)
**Provenance:** extracted from a production cron running inside [Hermes Agent](https://github.com/ooovenenoso/hermes-agent) for Tech Guru Online (TGO), a Puerto Rico digital-funnel agency.

---

## What this loop does

Every run the agent:

1. Reads a `campaigns.jsonl` history file to avoid previously used niches, offers, hooks, image concepts, and story concepts.
2. Picks **one concrete local-business niche** with buyer intent (e.g., *rotulación de vehículos en Bayamón* — never a generic category).
3. Generates a **landing page** at a quality bar equal to the prior best demos in the directory (themed loader, niche-specific motion, CTA).
4. **Deploys the landing** to Vercel and verifies the public URL with curl before continuing.
5. Generates a **square Facebook post image** (1080×1080) and a **vertical story image** (1080×1920), both with the brand logo integrated *naturally* by the image model (not pasted on).
6. Runs a **reviewer gate**: verifies the Vercel URL, image dimensions, brand correctness, and absence of placeholder leakage.
7. **Publishes** the post to the configured Facebook Page with a Spanish caption.
8. **Appends a JSON line** to `history/campaigns.jsonl` with all relevant fields.
9. A separate **comment guard loop** (`comment-keyword-private-reply-bot`) reads the same history, fetches the page's recent posts, and posts a fixed Spanish reply whenever a comment contains pricing intent (`$350`, `costo base`, `Website Starter`, etc.) — but only if no such comment from the Page already exists.

## Why this loop exists

The agency was posting one campaign per day manually — researching niches, designing images, drafting captions, posting to Facebook, and replying to "cuánto cuesta" comments. At 3×/day, that work is untenable for a single human. This loop replaces the **whole pipeline** end-to-end so the agency can run non-stop without a content team.

The comment guard is a separate concern: it has its own loop and its own failure modes. Combining them into one prompt would create a prompt that can't be reasoned about.

---

## Variables you must change

> Before this loop will run for **your** business, you must change every row in this table.
> The recipe will not work as-is without these edits.

| Variable | Where | Default in this recipe | What to change it to |
|---|---|---|---|
| `BUSINESS_NAME` | `prompts/system.txt` | `Tech Guru Online` | Your business / agency name |
| `BRAND_LOGO_PATH` | `assets/brand/logo.jpg` | TGO circular logo (teal/white/blue) | Your logo (square, ~512×512 minimum) |
| `PRIMARY_REGION` | `prompts/system.txt` | `Puerto Rico` | Where your customers are |
| `WHATSAPP_NUMBER` | `prompts/system.txt` | `+1 787 000 0000` (placeholder) | Your WhatsApp business number |
| `LANGUAGE` | `prompts/system.txt` | `Spanish (es-PR)` | `Spanish`, `English`, or bilingual |
| `OFFER_PRICE` | `examples/env.template` | `$350 (Website Starter)` | Your price point + offer name |
| `FACEBOOK_PAGE_ID` | `examples/env.template` | Tech Guru Online Page id | Your Facebook Page id |
| `FACEBOOK_PAGE_TOKEN` | `examples/env.template` (path only) | `~/.hermes/secure/facebook/tgo_page_access_token.txt` | Path to your page token file |
| `HISTORY_FILE` | `cron.config.yaml` (`output.history`) | `history/campaigns.jsonl` | Path where the loop appends each run |
| `LANDING_OUTPUT_DIR` | `cron.config.yaml` (`output.landings`) | `landings/` | Where the loop drops generated landings |
| `SITE_SYNC_SCRIPT` | `cron.config.yaml` (`output.site_sync`) | `~/.hermes/scripts/tgo_site_content_sync.py` | Your site-sync script |
| `SCHEDULE` | `cron.config.yaml` (`schedule`) | `0 1,15,20 * * *` | Your cadence (recommend ≥2h spacing) |
| `MAX_POSTS_PER_RUN` | `examples/env.template` (`TGO_DAILY_FUNNEL_MAX_POSTS`) | `3` | Max campaigns to publish per run |

---

## The prompt

The agent's system prompt is in [`prompts/system.txt`](prompts/system.txt). The contract every run must satisfy:

```
1. Read <HISTORY_FILE> and avoid previously used niches, offers, hooks, image concepts, and story concepts.
2. Pick ONE concrete <PRIMARY_REGION> local-business niche with buyer intent. Never a generic category.
3. Create a landing page at <LANDING_OUTPUT_DIR>/<timestamp>-<slug>/ with a themed loader, niche-specific motion, and a clear CTA to <WHATSAPP_NUMBER>.
4. Deploy the landing to Vercel (NPM_CONFIG_CACHE=<cache> npx --yes vercel@latest --prod --yes).
   Verify the public URL with curl. Do not treat a local file as complete.
5. Generate a 1080×1080 Facebook post image AND a 1080×1920 story. Attach <BRAND_LOGO_PATH> as an
   input_image reference to the image model. Do NOT paste/superimpose logos, URL strips, or banners —
   the image model must integrate the real brand naturally.
6. Run the reviewer gate (see references/reviewer-gate.md). Reject and retry if any check fails.
7. Publish to the Facebook Page with a <LANGUAGE> caption. Verify the permalink.
8. Append a JSON object to <HISTORY_FILE> with niche, slug, offer, landing_path, landing_url,
   image_path, story_path, caption, reviewer_status, post ids/permalink, timestamp.
9. Run <SITE_SYNC_SCRIPT> so the marketing site reflects the new campaign.
```

The full prompt (with quality bar, niche-picking heuristics, and the image-prompt template) is in `prompts/system.txt`.

## Schedule

```cron
0 1,15,20 * * *
```

Three runs per day: early morning, mid-afternoon, evening. Spacing matters — image generation takes 60–120s and Vercel deploys can take another 30–60s; you want buffer between runs so a slow API call doesn't queue the next one.

If you drop below 3×/day, reduce to a single off-peak hour and accept that the comment guard will run separately per cadence.

## Skills the agent loads

| Skill | Why |
|---|---|
| `facebook-platform-automation` | The Facebook Graph API calls (post, fetch, comment) |
| `local-business-funnel-autopilot` | Niche selection, caption tone, CTA conventions |
| `local-web-service-deployment` | Vercel deploy + URL verification |
| `image-generation-workflows` | Image model invocation with reference images |

If you adapt this recipe for a non-Facebook channel, swap `facebook-platform-automation` for the matching skill (LinkedIn, X, etc.).

---

## Inputs (what the agent reads)

| Input | What it is |
|---|---|
| `history/campaigns.jsonl` | Append-only log of every campaign the loop has produced |
| `assets/brand/logo.jpg` | The brand logo (required, not optional) |
| `<reference_dir>/drafts/*.png` | Prior approved Facebook post images (style reference) |
| `<reference_dir>/stories/*.jpg` | Prior approved story images (style reference) |
| `references/niche-pool.txt` | The candidate niches the loop is allowed to draw from |

## Outputs (what the agent writes)

| Output | Where it lands |
|---|---|
| Landing page directory | `<LANDING_OUTPUT_DIR>/<YYYYMMDD>-HHMM-<slug>/` |
| Square post image | `<LANDING_OUTPUT_DIR>/<slug>/fb-post.jpg` |
| Vertical story image | `<LANDING_OUTPUT_DIR>/<slug>/story.jpg` |
| Vercel deployment | `<slug>.vercel.app` (verified before publish) |
| Facebook post | On the configured Page, with verified permalink |
| History JSON line | Appended to `<HISTORY_FILE>` |
| Site campaigns JSON | Updated via `<SITE_SYNC_SCRIPT>` |

## Secrets required

| Secret | Source | Purpose |
|---|---|---|
| `<BUSINESS>_PAGE_ACCESS_TOKEN` | `~/.hermes/secure/facebook/<slug>_page_access_token.txt` | Post to Page, fetch comments |
| `<BUSINESS>_USER_ACCESS_TOKEN` | `~/.hermes/secure/facebook/<slug>_user_access_token.txt` | Verify `pages_manage_engagement` permission |
| `<IMAGE_MODEL_API_KEY>` | `~/.hermes/secure/openai/api_key.txt` (or other provider) | Generate square + story |
| `NPM_CONFIG_CACHE` | env var | Isolate the Vercel npx cache per host |

**Never commit real secrets.** See [`SECURITY.md`](../../SECURITY.md). The CI secrets scanner rejects any PR that ships a real token.

---

## Failure modes

| Symptom | Cause | Recovery |
|---|---|---|
| Loop runs but posts nothing | History file full of recent niches (≥30 entries) | Operator widens `references/niche-pool.txt` or pauses for a day |
| Image model times out at minute 4 | Provider rate limit hit | Retry with backoff; degrade to a text-only post if the image model is down for >1 hour |
| Same niche posted twice in one day | History append failed mid-run on the first attempt | Idempotency guard: dedupe by `(niche, day)` from `<HISTORY_FILE>` before posting; alert operator if a dup slips through |
| Page token returns 401 | Token expired (60-day for page tokens, 90-day for user tokens) | Operator rotates the token files; loop pauses silently until updated (no posts, no errors in `<HISTORY_FILE>`) |
| Vercel deploy returns 401 | Local Vercel auth expired | `npx vercel login` again; the next deploy will pick up the new auth |
| Image has the wrong logo | Image model ignored the input_image reference | Reject in the reviewer gate; retry with a more explicit image prompt that names the logo; if it fails 2×, degrade to text-only |
| Story is 1080×1920 but uses the wrong template | Image model misread the style reference | Reviewer gate compares to `<reference_dir>/stories/*.jpg`; reject + regenerate with the prior story as `image_url` instead of just text |
| Comment guard posts a duplicate | The guard ran before the post hit the page's `/comments` edge | Idempotency check (`has_price_comment`) re-reads after POST and reverts if it doesn't find its own comment; alert operator if reverted count > 2/day |
| Landing deployed but URL is 404 | Vercel domain propagation lag | Wait 60s and re-curl. If still 404, the deploy failed — abort the post |

## Pitfalls

- **Don't paste the logo onto a generated image.** The image model has to integrate the real logo *naturally* into the scene. If you can't attach the logo as an `input_image` reference, stop and report a blocker — don't ship a generic/overlaid creative.
- **Don't skip the reviewer gate.** The gate is the difference between "ran 200 times" and "shipped 200 posts that look like the brand."
- **Don't post a niche you've already used in the last 30 days.** The dedup is the whole point. If the pool is exhausted, *expand the pool*, don't lower the bar.
- **Don't change the loader quality bar.** A "minimal placeholder" landing tanks the brand. The themed loader is non-negotiable.
- **Don't let the comment guard spam.** It checks for an existing price-comment from the Page before posting. If you disable that check, you will get the same WhatsApp CTA in your own comments 200 times a day.
- **Don't run more than 3×/day** without re-validating the niche pool. The pool has a finite freshness budget.

---

## Verification checklist

Before deploying this recipe to a new account, or after any change to `prompts/system.txt` / `cron.config.yaml`:

- [ ] `python3 scripts/validate_recipe.py recipes/tgo-full-funnel-autopilot/` exits 0.
- [ ] `pytest recipes/tgo-full-funnel-autopilot/tests/` is green.
- [ ] `prompts/system.txt` parses as a single coherent prompt (no markdown rendering issues).
- [ ] `cron.config.yaml` validates against your scheduler (Hermes, GH Actions, etc.).
- [ ] All `examples/env.template` placeholders are replaced in your deploy env (CI secrets scanner confirms).
- [ ] Brand asset in `assets/brand/logo.jpg` is the *real* brand asset, ≥512×512, square.
- [ ] `<HISTORY_FILE>` exists and is writable by the loop's runtime user.
- [ ] One dry run with a throwaway history file completes end-to-end: niche → landing → image → reviewer → publish → append.
- [ ] One dry run of the comment guard finds no duplicates and posts at most `MAX_NEW_COMMENTS_PER_RUN` comments.
- [ ] The site-sync script runs after the main loop and the marketing site reflects the new campaign within one cron tick.

---

## Adapting this recipe

To fork this loop for a different agency / market:

1. Copy `recipes/tgo-full-funnel-autopilot/` to `recipes/<your-slug>-funnel/`.
2. Update **every** row in the **Variables** table.
3. Replace `assets/brand/logo.jpg` with your brand asset.
4. Replace the niche pool in `references/niche-pool.txt` with your region's niches.
5. Replace the comment guard's pricing-regex in `scripts/comment-keyword-private-reply-bot.py` with your offer's keywords.
6. Re-run the verification checklist.
7. Open a PR if you want to share the adaptation.

## Related recipes

_None yet. This is the first recipe in the catalog._

---

## Changelog

- **1.0.0** (2026-07-01) — initial extraction from production TGO cron.
- **0.9.x** — internal iterations while the loop was running in production for Tech Guru Online.