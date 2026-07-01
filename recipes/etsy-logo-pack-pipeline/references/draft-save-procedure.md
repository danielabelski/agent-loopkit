# Etsy draft save — the procedure that decides "draft vs publish"

This is the **single most important guardrail** in Stage 1. Etsy has a copy-listing flow that lets you start from a template listing. If the template is **active**, copying from it and clicking the generic `Save` / `Guardar` button **updates the active listing** — not a new draft. The fix is to verify the button text before clicking.

## The procedure

1. Navigate to `/listing-editor/copy/<ETSY_COPY_LISTING_ID>`.
2. Wait for the editor to load (`ETSY_EDITOR_WAIT_ROUNDS` rounds).
3. **Clean up inherited template media** (see "Asset cleanup" below).
4. **Upload** the new pack's mockup + 4 logos + buyer ZIP.
5. Set title, tags, description, price, quantity.
6. **Verify the save button text** before clicking:
   - The element `#shop-manager--listing-save` must contain `Save as draft` or `Guardar como borrador`.
   - If it contains only `Save` or `Guardar`, **fail closed** — exit without clicking.
7. Click the button.

## Why "Save as draft" verification matters

Without this check, Etsy will:

- If the template listing is **inactive**: create a new draft. Correct.
- If the template listing is **active** (any state except deleted/expired): update the **active** listing with the new pack's content. The previous listing is gone. This is the failure mode that has actually happened in production.

The original template listing (`ETSY_COPY_LISTING_ID`) must be **kept inactive** in Etsy admin. If you re-activate it for any reason, the cron will silently overwrite it on the next batch.

## Asset cleanup (must do before upload)

Etsy's `Eliminar todo` button is **not reliable**. The proven procedure:

```javascript
// Repeat until #media has zero delete buttons left
while (document.querySelectorAll('#media button[data-testid="image-delete-button"]').length > 0) {
  const buttons = document.querySelectorAll('#media button[data-testid="image-delete-button"]');
  for (const btn of buttons) {
    btn.click();
    await sleep(1500);   // wait for the deletion animation + DOM update
  }
  // Safety: don't loop forever
  if (--maxIterations <= 0) throw new Error('Media cleanup did not converge');
}
```

If the cleanup does not reach zero delete buttons in `ETSY_EDITOR_WAIT_ROUNDS * 2` attempts, the draft runner **fails closed**. It is better to skip a batch than to publish with inherited template media.

## Digital files (buyer ZIP)

Same pattern — remove every inherited digital file before uploading:

```javascript
while (document.querySelectorAll('#field-digitalFiles button[data-testid="digital_file_action_remove"]').length > 0) {
  const buttons = document.querySelectorAll('#field-digitalFiles button[data-testid="digital_file_action_remove"]');
  for (const btn of buttons) {
    btn.click();
    await sleep(1000);
  }
}
```

Then upload the pack's buyer ZIP via `#field-digitalFiles input[type="file"]`.

**Mega packs** (more than 4 logos) use up to Etsy's 5-file limit via `digital_files: [...]` in `listing-data.etsy-draft.json`. Each ZIP must stay under Etsy's per-file upload limit (currently 20 MB).

## Tags

Etsy tag input can be disabled when copied template tags are still present. The cleanup function `removeExistingTags` must:

- Match both Spanish and English aria labels.
- `addTag` must **skip** (not crash) if `#listing-tags-input` remains disabled after cleanup.

## Title

The title is `theme.title` + style variant so drafts are not visually or textually generic. Example:

```
Moderation Guardian Bot Logo Pack — Sapphire Cybernetic (4 Logos + Mockup + ZIP)
```

The `— Sapphire Cybernetic` suffix is the **style direction** name, not the theme. This is what makes 4 packs in the same theme still feel distinct in the catalog.

---

## Human challenge recovery

If Etsy presents a login, DataDome challenge, or "verify you're human" page:

1. **Stop the cron immediately** — do not retry from the same state.
2. Launch the noVNC browser using the Etsy profile.
3. Operator completes only the challenge (login / CAPTCHA / 2FA).
4. Close the browser (release the profile lock).
5. Re-run the draft step or wait for the next cron batch.

The proven noVNC pattern (see `references/novnc-recovery.md` if vendored) uses Xvfb + fluxbox + Playwright Chromium + x11vnc + websockify + a Cloudflare quick tunnel.

---

## Failure modes specific to draft save

| Symptom | Likely cause |
|---|---|
| Button text is `Save` not `Save as draft` | Template listing became active. Stop cron, deactivate template. |
| Cleanup loop hangs | Etsy's editor DOM changed. Inspect in noVNC, update selector. |
| Digital file upload fails (size) | ZIP > 20 MB. Split into multiple digital files. |
| Save succeeds but draft has template photos | Cleanup did not converge. Increase `ETSY_EDITOR_WAIT_ROUNDS` or fail closed. |
| Tags can't be added | Existing template tags still present. `removeExistingTags` is incomplete. |