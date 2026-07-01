# TGO Full Funnel Autopilot — operating procedure (FLOW)

This is the canonical operating procedure the agent reads at the start of every run. It mirrors the production `FLOW.md` extracted from the TGO automation root.

---

# Tech Guru Online automated growth flow

Purpose: 3x/day create non-repeating niche campaign assets for local-business web/landing-page funnels.

Per run:

1. Read `/root/techguruonline-automation/history/campaigns.jsonl` and avoid previously used niches, offers, hooks, image concepts, and story concepts.

2. Pick one concrete Puerto Rico/local-business niche with buyer intent.

3. Create a landing page/demo artifact under `/root/techguruonline-automation/landings/<timestamp>-<slug>/`.

4. Build a high-quality site at the same level as the prior Barber and Window Tint demos, not a minimal placeholder. Every generated landing must include a **theme-based** Tech Guru Online loader/preloader modeled after the Barber loader quality: a first-load overlay using `/assets/tgo-logo.jpg` (or the landing's copied TGO logo asset), `class="loader"`/equivalent, pulsing TGO brand feel, and subtle niche-specific visual/motion cues (for example barber pole/clipper motion for barbers, water/soap spin for lavanderías, airflow/fan motion for aires, glass shine for cristalerías). It must feel custom to the selected niche, not like a generic spinner. Include short text such as `BUILDING DIGITAL FUNNELS...` or a Spanish niche equivalent. The loader must auto-hide with CSS animation or a small script after ~1–1.5s and must not block interaction permanently. Verify the generated `index.html`/CSS includes the themed loader before deployment.

5. Deploy that landing/demo to Vercel using local auth (`NPM_CONFIG_CACHE=/root/.npm-vercel npx --yes vercel@latest --prod --yes`) and verify the public URL with curl/browser before continuing. Do not treat a local file as complete unless Vercel is blocked.

6. Generate the square Facebook post image with GPT Image 2 using `/root/techguruonline-automation/assets/tgo-logo.jpg` as a REQUIRED input image/reference plus the prior Barber/Window Tint square references. Do not only mention the logo in text: attach/pass the logo file to the image-generation request as an `input_image`/data URL reference. Do not manually paste/superimpose logos, URL strips, or bottom banners onto the photo; GPT Image should integrate the real TGO logo/teal-blue-white brand naturally into the generated scene. If the logo reference file cannot be attached, stop and report a blocker rather than publishing a generic/overlaid creative.

7. Generate the vertical story in the same layout/style as the prior stories: top white bar, large rounded hero card, title/subtitle, URL pill, CTA button, footer note. Use `/root/techguruonline-automation/assets/tgo-logo.jpg` as a REQUIRED input image/reference for the story too; no pasted/superimposed elements.

8. Run a reviewer gate before Facebook publishing: verify Vercel works, images exist, story is 1080x1920 or previous-story compatible, visual style matches Barber/Window Tint, TGO branding/logo is clearly based on the real circular TGO logo reference (teal center, white TGO letters, blue/white dotted ring) and integrated naturally, no generic placeholder logo, no broken text, no awkward overlays, and no Window Tint/prospect leakage.

9. Publish the approved square image + Spanish caption to the Tech Guru Online Facebook Page using the secure page id and token files; verify permalink.

10. Append a JSON object to `/root/techguruonline-automation/history/campaigns.jsonl` with niche, slug, offer, landing_path, landing_url, image_path, story_path, caption, reviewer_status, post ids/permalink, timestamp.

11. Keep tone compact, business-like, direct. CTA: WhatsApp `<WHATSAPP_NUMBER>`. Avoid Window Tint/client/prospect-specific content unless the operator explicitly approves.

---

## Website sync

The site-sync script reads the history and updates the marketing site's `tgoCampaigns.json`, then builds the site. Run it after every successful publish.