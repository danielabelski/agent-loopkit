# Changelog

All notable changes to this repository are documented here. Dates are in
`YYYY-MM-DD`. Versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Recipe #2: `etsy-logo-pack-pipeline` — 3-stage pipeline (generate + Etsy draft + Pinterest pin) extracted from 3 production crons.
- Validator extended to accept multi-stage `cron.config.yaml` shapes and `prompts/*.env` files (script-only recipes don't need `prompts/system.txt`).

## [0.1.0] — 2026-07-01

### Added
- Initial private release of the `agent-loopkit` repo.
- Repo description: "Reusable playbooks for autonomous AI agent loops — copy, customize, ship."
- Tagline: *copy · customize · ship*.
- Recipe #1: `tgo-full-funnel-autopilot`.
- Branding assets (`assets/banner.svg`, `assets/logo.svg`, `assets/icon.svg`).
- Recipe validator + repo validator + pytest suite (16 tests at v0.1.0).
- `.github/workflows/validate.yml` CI.

[Unreleased]: https://github.com/ooovenenoso/agent-loopkit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ooovenenoso/agent-loopkit/releases/tag/v0.1.0