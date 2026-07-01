# MCP setup — Robinhood Trading MCP

The Robinhood Safe Growth recipe talks to Robinhood's **Agentic MCP trading endpoint** (`agent.robinhood.com/mcp/trading`). This document covers the OAuth/PKCE flow, the tool whitelist, and the read-only wrapper pattern.

## Endpoint

| URL | Purpose |
|---|---|
| `https://agent.robinhood.com/mcp/trading` | MCP JSON-RPC endpoint (initialize, notifications, tools/call) |
| `https://agent.robinhood.com/oauth/trading/register` | Dynamic client registration |
| `https://robinhood.com/oauth` | Authorization endpoint (user-facing login) |
| `https://api.robinhood.com/oauth2/token/` | Token endpoint (exchange code → access + refresh) |

## OAuth flow (PKCE + S256)

The MCP requires:

- **Dynamic client registration** (no static client_id / client_secret).
- **PKCE S256** for the authorization-code flow.
- **Public client** (`token_endpoint_auth_method: none`).

A noVNC browser is the recommended human login surface because the OAuth consent screen can require MFA + sensitive permission review (the MCP requests real trading scopes).

### Callback capture pitfall

OAuth codes are single-use and short-lived. The callback URL pattern is:

```
https://your-app/callback?code=AUTH_CODE&state=STATE
```

A common bug: a subsequent request to `/favicon.ico` (no `code` param) overwrites the saved `code` value with empty. The wrapper must:

- Only write the `code` to disk if `code` is present in the query string.
- Log every callback request for audit.
- Use a per-session state value to prevent CSRF.

## MCP session lifecycle

Every snapshot run follows this sequence:

```
POST /mcp/trading
Headers: Authorization: Bearer <access_token>
         Content-Type: application/json
         Accept: application/json, text/event-stream

1. initialize
   → returns server capabilities + Mcp-Session-Id header (save it)

2. notifications/initialized
   (no response, fire-and-forget)

3. tools/list (optional, once per session)
   → returns the available tool names + schemas

4. tools/call (per read)
   → name=tool_name, arguments={...}
   → returns structuredContent (or text, parsed as JSON)

5. (next run) re-initialize, get new session id
```

The snapshot script handles all 5 steps. Tokens rotate when the access token expires (use the refresh token to get a new pair).

## Tool whitelist (read-only)

| Tool | Read/Write | Allowed? |
|---|---|---|
| `get_accounts` | read | ✅ |
| `get_portfolio` | read | ✅ |
| `get_equity_positions` | read | ✅ |
| `get_equity_orders` | read | ✅ |
| `get_equity_quotes` | read | ✅ |
| `get_equity_tradability` | read | ✅ |
| `get_historicals` | read | ✅ |
| `review_equity_order` | preflight (no execution) | ✅ (Stage 1 only) |
| `review_option_order` | preflight | ❌ (no options) |
| `place_equity_order` | **WRITE** | ❌ BANNED |
| `place_option_order` | **WRITE** | ❌ BANNED |
| `cancel_order` | **WRITE** | ❌ BANNED |
| `replace_order` | **WRITE** | ❌ BANNED |
| `add_to_watchlist` | **WRITE** | ❌ BANNED |
| `remove_from_watchlist` | **WRITE** | ❌ BANNED |
| `create_watchlist` | **WRITE** | ❌ BANNED |
| `update_watchlist` | **WRITE** | ❌ BANNED |
| `follow` | **WRITE** | ❌ BANNED |
| `unfollow` | **WRITE** | ❌ BANNED |

The `RH_BANNED_TOOLS` env var enforces this at the script level. The prompt also restates the list. The CI rejects any PR that removes these from the banned list.

## Account distinction (critical)

Robinhood accounts can be:

- **Regular** margin / cash accounts (no `agentic_allowed` flag, or `agentic_allowed=false`).
- **Agentic** accounts (`agentic_allowed=true`).

Only the agentic account is authorized for trading through this MCP. The script's `redact_text()` masks account numbers in stdout (`••••XXXX`), but the script does **not** trade from any account — the snapshot just identifies which one *would* be tradable.

**Pitfall:** do not assume the default account is the agentic account. Always re-query `get_accounts` per session.

## After-hours + options

By default:

- **No after-hours trading.** Entry stage fires Mon-Fri 10:15 ET; Defense stage fires Mon-Fri 14:45 ET. Anything outside regular hours is not in scope.
- **No options.** `review_option_order` / `place_option_order` are not in the allowed tool list. If you want options, you must explicitly authorize them AND change `RH_ALLOWED_TOOLS` AND update the prompt — three independent gates.

## Token storage

Save OAuth artifacts to a single JSON file:

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "client_id": "...",
  "expires_at": "2026-07-01T18:00:00Z"
}
```

Recommended path: `~/.hermes/secure/robinhood_mcp_token.json` (chmod 0600, owned by the recipe's runtime user).

The CI secrets scanner rejects any PR with a `Mcp-Session-Id` or token-shaped string. The script never logs the access_token value.