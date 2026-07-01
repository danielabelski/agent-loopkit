# Reviewer Gate — pre-publish checklist

> Every campaign run goes through this gate before publishing. The agent must
> not publish if any check fails. Failed checks trigger a re-roll of the
> affected step (max 2 retries); if still failing after 2 retries, the run
> aborts with a blocker.

## 1. Landing page

- [ ] `index.html` exists in the landing directory.
- [ ] Loader/preloader element is present (`<div class="loader">` or equivalent) and references the brand logo.
- [ ] Loader text contains "BUILDING DIGITAL FUNNELS" or a Spanish niche equivalent.
- [ ] Loader has a CSS keyframe animation that auto-hides it after ≤2s.
- [ ] The page mentions the niche explicitly (h1 / hero copy).
- [ ] WhatsApp CTA link is present and points to the configured number.
- [ ] No leftover placeholders: `Lorem ipsum`, `TODO`, `REPLACE_ME`, `<script>undefined`.

## 2. Vercel deployment

- [ ] `vercel --prod` exit code 0.
- [ ] Output URL returns HTTP 200 via `curl -sI <url>`.
- [ ] URL hostname matches the expected pattern (`*.vercel.app` or custom domain).
- [ ] Page renders the niche content (curl body contains the niche keyword).

## 3. Square post image

- [ ] File exists at `<landings_dir>/<slug>/fb-post.jpg`.
- [ ] Dimensions: 1080×1080 (or ±5% tolerance).
- [ ] The brand logo is visibly integrated (not pasted as a corner watermark).
- [ ] No "Lorem ipsum", no broken text, no awkward overlays.
- [ ] Style matches the prior reference (Barber / Window Tint demos) within the visual rubric.
- [ ] No competitor / prospect leakage (no "Window Tint", no client names).

## 4. Vertical story

- [ ] File exists at `<landings_dir>/<slug>/story.jpg`.
- [ ] Dimensions: 1080×1920 (or ±5% tolerance).
- [ ] Top white bar present, large rounded hero card present, URL pill present, CTA button present.
- [ ] Brand logo is integrated (not pasted).

## 5. Brand identity check

- [ ] Logo color: teal center, white TGO letters, blue/white dotted ring.
- [ ] Caption is in Spanish (es-PR) unless `LANGUAGE` env var overrides.
- [ ] Caption is compact, business-like, direct (no marketing fluff).
- [ ] WhatsApp number in caption matches `WHATSAPP_NUMBER` env var.
- [ ] No internal-only references (other campaigns, internal-only URLs, debugging strings).

## 6. History integrity

- [ ] The chosen niche is NOT present in the last `<LOOKBACK_DAYS>` entries of `<HISTORY_FILE>`.
- [ ] The chosen slug is NOT present in any prior entry.

## Output

The reviewer gate must produce a JSON block at the end of its run:

```json
{
  "pass": true,
  "checks": {
    "landing": "pass",
    "vercel": "pass",
    "image_square": "pass",
    "image_story": "pass",
    "brand": "pass",
    "history": "pass"
  },
  "blockers": []
}
```

If `pass` is `false`, the agent must NOT proceed to publish. It must re-run the failing step up to 2 times. If still failing, the run aborts and the agent reports the blockers in its JSON summary.