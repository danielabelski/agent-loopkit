---
name: New recipe proposal
about: Propose a new recipe to be added to the catalog
title: "[RECIPE] <slug> — <one-line summary>"
labels: ["recipe-proposal", "needs-review"]
assignees: []
---

## What loop are you proposing?

A short description of the agent loop. What does it do, on what cadence, and what artifact does it produce?

## Why should it be in the catalog?

Is this a loop you've already run in production? Or one you want to build out from scratch? If production: where, how long, what success metric.

## Variables

What are the top 3-5 variables someone adapting this recipe would need to change?

## Brand / domain

Is this domain-specific (e.g., local-business, e-commerce) or domain-agnostic?

## Open questions

Anything you're unsure about — the schedule, the failure modes, the secrets layout, etc.

## Checklist

- [ ] I have read `RECIPE_TEMPLATE.md` and `CONTRIBUTING.md`.
- [ ] I have run `python3 scripts/validate_recipe.py recipes/<slug>/` against a draft (if available).
- [ ] I will not commit any real secrets, customer data, or live history files.