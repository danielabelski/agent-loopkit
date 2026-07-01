# Comment guard — keyword private-reply bot

The companion loop that posts the price-comment reply on Tech Guru Online Facebook Page posts.

## What it does

Every run:

1. Reads `history/campaigns.jsonl` to find posts the page has published.
2. Reads `<USER_ACCESS_TOKEN_FILE>` and `<PAGE_ACCESS_TOKEN_FILE>` from disk.
3. Validates the Page identity using the Page token (`GET /me` must return a Page whose name matches `tech\s+guru\s+online`).
4. Builds a candidate set: every campaign post the loop has published, plus the most recent `MAX_POSTS_CHECK` posts from the Page's feed (catches posts that haven't been appended yet).
5. For each candidate post, fetches all comments. If a comment from the Page already matches the price regex (`$350`, `Website Starter`, `costo base`, etc.), skip — already replied.
6. Otherwise, POST a fixed Spanish reply with the WhatsApp CTA.
7. After POST, re-read the comments edge and verify the reply landed. If it didn't, raise and log an error.
8. Cap: at most `MAX_NEW_COMMENTS_PER_RUN` new comments per run. The remainder backfills on the next tick.
9. Append a JSON line to `history/full_funnel_price_comment_log.jsonl` with `post_id`, `action` (`commented` / `skipped` / `skipped_existing` / `error`), `reason`, `comment_id`, `permalink`, `timestamp`.

## Why a separate loop, not part of the main loop

- Different cadence (45 min after the main loop, so the post is on the page before the guard fetches comments).
- Different failure modes (Facebook Graph API rate limits, photo vs feed post comment edges, token rotation).
- Script-only (`no_agent: true`) — no LLM, just deterministic Graph API calls. Keeps cost and latency flat.

## Failure modes specific to the guard

| Symptom | Cause | Recovery |
|---|---|---|
| Graph returns 401 | Page token expired | Operator rotates `tgo_page_access_token.txt` |
| Graph returns 400 "Object does not exist" | Post was deleted or comment edge is on a photo not a feed post | Mark post as `skipped_existing` with reason `object_does_not_exist` so we don't retry forever |
| Same reply posted 2× | Token rotation raced with the read-then-write idempotency check | The re-read after POST catches this and reverts; alert if `error` count > 2/day |
| `pages_manage_engagement` permission missing on the user token | User token doesn't have the engagement scope | Operator re-authorizes the user token with the right scope |
| Guard posts a comment to a non-Page-owned post | Race when the candidate list included a shared/boosted post | Re-validate `from.id == page_id` before POST |

## Pitfalls

- **Don't** POST without re-reading to verify the idempotency guard works. The re-read is the only thing that prevents double-comments.
- **Don't** post a reply to a comment that's already from the Page — that's how you end up with 3 identical comments under one post.
- **Don't** lower the `MAX_NEW_COMMENTS_PER_RUN` cap to 0 "to be safe" — that disables the guard. If you want to pause, pause the cron, don't neuter the cap.
- **Don't** use the Page token for `/{user_id}/...` calls — it only has Page scopes. Use the user token for `/me/permissions` style introspection.