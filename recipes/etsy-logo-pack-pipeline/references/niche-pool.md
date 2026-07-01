# Seed themes — Discord / SaaS bot logo packs

> The default `THEMES` list embedded in `etsy_logo_pack_worker.py`. When the catalog is empty, the worker falls back to this list as the seed inventory. Once Stage 2 has approved real themes, this list is never used again.

## Categories

- **seed-discord-bots** (default): the 20 themes below.
- **seed-saas-bots**: future expansion (Notion bots, Slack bots, etc.).

## The 20 default themes

| Slug | Title | Concepts |
|---|---|---|
| `moderation-guardian` | Moderation Guardian Bot Logo Pack | shield visor guardian robot / ban-hammer energy badge / community safety sentinel / audit log scanner |
| `ticket-support` | Ticket Support Bot Logo Pack | ticket visor support robot / help desk beacon / chat bubble service / priority queue assistant |
| `music-dj` | Music DJ Bot Logo Pack | headphone DJ robot / audio waveform mascot / neon turntable bot / bass pulse cyber face |
| `analytics-dashboard` | Analytics Dashboard Bot Logo Pack | data orb robot / chart visor analytics bot / growth signal mascot / dashboard radar android |
| `ai-chat-assistant` | AI Chat Assistant Bot Logo Pack | speech halo AI robot / neural chat mascot / assistant core android / conversation orbit bot |
| `giveaway-prize` | Giveaway Prize Bot Logo Pack | gift box robot / prize wheel mascot / confetti crown bot / raffle ticket android |
| `leveling-xp` | Leveling XP Bot Logo Pack | XP crystal robot / rank badge mascot / progress meter bot / achievement crown android |
| `verification-captcha` | Verification Bot Logo Pack | checkmark shield robot / secure gate android / identity scanner bot / verified badge mascot |
| `economy-shop` | Economy Shop Bot Logo Pack | coin vault robot / marketplace bot mascot / wallet hologram android / shopkeeper AI face |
| `crypto-wallet` | Crypto Wallet Bot Logo Pack | blockchain cube robot / wallet shield android / token orbit bot / ledger core mascot |
| `gaming-lfg` | Gaming LFG Bot Logo Pack | controller visor robot / squad finder mascot / game lobby android / matchmaking core bot |
| `stream-alerts` | Stream Alerts Bot Logo Pack | live signal robot / broadcast beacon bot / notification bell android / stream pulse mascot |
| `calendar-events` | Calendar Events Bot Logo Pack | calendar visor robot / event clock mascot / schedule orbit bot / reminder bell android |
| `polls-voting` | Polls Voting Bot Logo Pack | ballot robot mascot / voting check android / survey pulse bot / poll chart face |
| `welcome-onboarding` | Welcome Onboarding Bot Logo Pack | welcome portal robot / friendly greeter bot / doorway halo mascot / member onboarding android |
| `anti-raid-defense` | Anti Raid Defense Bot Logo Pack | fortress shield robot / raid radar android / threat scanner bot / defense core mascot |
| `translation-global` | Translation Bot Logo Pack | globe visor robot / language orbit mascot / speech translate android / multilingual AI face |
| `role-management` | Role Management Bot Logo Pack | role badge robot / permission key android / tier crown bot / access control mascot |
| `social-notifier` | Social Notifier Bot Logo Pack | notification orbit robot / social signal mascot / megaphone cyber bot / multi-channel alert android |
| `knowledge-base` | Knowledge Base Bot Logo Pack | book visor robot / database crystal mascot / FAQ assistant bot / wisdom archive android |

## Why these themes

Each one is:

- **Specific** (not "general bot", but "Moderation Guardian") — Etsy shoppers search by use case.
- **Visualizable** — each concept can be a clean mascot badge.
- **Non-trademark** — none match known brands directly.
- **Repeatable** — the 4 concepts per theme can each stand on their own as a logo.

## Refreshing

The list is intentionally short (20 themes). Stage 2 generates new ones from the `CATEGORIES × STYLE_WORDS` matrix:

```python
CATEGORIES = {
    'automation':   ['Workflow', 'Scheduler', 'Backup', 'Sync', 'Pipeline', ...],
    'security':     ['Firewall', 'Access Control', 'Threat Watch', ...],
    'community':    ['Member Match', 'Reputation', 'Welcome Flow', ...],
    'commerce':     ['Price Watch', 'Deal Finder', 'Inventory', ...],
    'content':      ['Content Planner', 'Clip Maker', 'Meme Queue', ...],
    'ai-data':      ['Knowledge Search', 'Data Scout', 'Insight Engine', ...],
}
STYLE_WORDS = ['Neon', 'Cyber', 'Quantum', 'Signal', 'Nova', 'Pulse', ...]
```

A new theme = `f"{category_word} {style_word} Bot"` + 4 generated concepts. This produces 60+ candidates per refill.

---

## Anti-patterns (themes to NEVER add)

- Generic themes (`General Bot Pack`, `Utility Bot`, `Multi-purpose Bot`) — Etsy shoppers don't search these.
- Brand-derived names (`Slack Clone Bot`, `Notion Bot`, `Discord Verified`) — trademark risk.
- Single-concept themes (`Welcome Bot Pack` with no other concepts) — Etsy images need 4 distinct visuals.
- Themes that overlap with an existing theme's slug prefix (e.g., `moderation-guardian-v2`) — the catalog dedup treats these as the same theme.

---

## Refresh cadence

The seed list is the floor, not the ceiling. Stage 2 should approve ~50 new themes per month. After 6 months in production, the seed list itself becomes irrelevant — only Stage 2's output matters.