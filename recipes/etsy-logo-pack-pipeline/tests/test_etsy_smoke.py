"""Smoke test for the Etsy Logo Pack Pipeline recipe.

Verifies the recipe can be parsed and instantiated against the canonical
recipe validator, and that the env template produces no real tokens when
substituted with placeholder values.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

RECIPE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = RECIPE_DIR.parent.parent


def test_recipe_passes_canonical_validator():
    """Run the repo-level validator against this recipe; it must exit 0."""
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "validate_recipe.py"), str(RECIPE_DIR)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Canonical validator failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    )


def test_env_template_substitution_is_safe():
    """Filling the placeholders must not produce a real token-shaped string."""
    content = (RECIPE_DIR / "examples" / "env.template").read_text(encoding="utf-8")
    safe_values = {
        "ETSY_PROFILE_DIR": "/run/secrets/etsy/profile",
        "ETSY_COPY_LISTING_ID": "0000000000",
        "ETSY_PRICE_USD": "7.99",
        "ETSY_QUANTITY": "999",
        "ETSY_CREATE_DRAFTS": "1",
        "ETSY_NOTIFY_DISCORD": "0",
        "ETSY_EDITOR_WAIT_ROUNDS": "3",
        "IMAGE_PROVIDER": "openai-codex",
        "IMAGE_MODEL": "gpt-image-2-medium",
        "IMAGE_API_KEY_FILE": "/run/secrets/image_api_key",
        "OUTPUT_ARCHIVE_DIR": "/srv/etsy-packs",
        "THEME_CATALOG_FILE": "/srv/etsy-packs/theme_catalog.json",
        "WORKER_STATE_FILE": "/srv/etsy-packs/state.json",
        "APPROVED_THRESHOLD": "32",
        "APPROVED_TARGET": "96",
        "MAX_CANDIDATES": "120",
        "MIN_SCORE_FOR_APPROVE": "70",
        "DUPLICATE_RISK_REJECT": "high",
        "TRADEMARK_RISK_REJECT": "high",
        "PINTEREST_DRY_RUN": "1",
        "PINTEREST_PROFILE_DIR": "/srv/pinterest/profile",
        "PINTEREST_CDP_URL": "http://127.0.0.1:9334",
        "PIN_ABOUT_MAX_CHARS": "100",
        "PIN_TITLE_MAX_CHARS": "100",
        "SKIP_IF_RESULT_EXISTS": "1",
        "DISCORD_WEBHOOK_FILE": "/run/secrets/discord_webhook",
        "PACKS_PER_BATCH": "4",
        "LOGOS_PER_PACK": "4",
        "MIN_APPROVED_THEMES": "4",
        "VNC_DISPLAY": ":77",
        "VNC_PASSWORD_FILE": "/run/secrets/vnc_passwd",
    }
    substituted = content
    for k, v in safe_values.items():
        substituted = substituted.replace(f"_{k}_FILE=__replace_me__", f"_{k}_FILE={v}")
        substituted = substituted.replace(f"{k}=__replace_me__", f"{k}={v}")
    assert not re.search(r"sk-[A-Za-z0-9]{20,}", substituted), (
        "Substituted env template contains a real-looking OpenAI key"
    )


def test_pinterest_dry_run_is_strictly_default():
    """The Pinterest env file MUST default to dry-run=1. This is the safety guard."""
    content = (RECIPE_DIR / "prompts" / "pinterest.env").read_text(encoding="utf-8")
    # Find the PINTEREST_DRY_RUN line
    match = re.search(r"^PINTEREST_DRY_RUN\s*=\s*(\S+)", content, re.MULTILINE)
    assert match, "prompts/pinterest.env missing PINTEREST_DRY_RUN"
    value = match.group(1).strip().strip('"').strip("'")
    assert value == "1", (
        f"PINTEREST_DRY_RUN must default to '1' (dry-run). Got '{value}'. "
        "This is the most critical safety guard — never auto-publish to Pinterest."
    )


def test_recipe_warns_against_publish_not_instructs():
    """The recipe must NOT instruct the agent to click Publish or Publicar.

    Warnings like "never click Publish" or "fail closed if it says Save" are OK —
    those are guardrails, not instructions. Only flag standalone imperative
    instructions.
    """
    text = (RECIPE_DIR / "RECIPE.md").read_text(encoding="utf-8")
    # Look for imperative patterns: starts with verb, or 'stage 1: ... click Publish'
    imperative = re.findall(
        r"(?:^|\n)\s*(?:stage\s+\d+\s*[:|]?\s*)?(?:then\s+|now\s+)?click\s+['\"]?Publish",
        text,
        re.IGNORECASE,
    )
    assert not imperative, (
        f"RECIPE.md contains imperative 'click Publish' instructions: {imperative}"
    )
    imperative_es = re.findall(
        r"(?:^|\n)\s*(?:stage\s+\d+\s*[:|]?\s*)?(?:luego\s+|ahora\s+)?(?:haz\s+clic|hacer\s+clic)\s+['\"]?Publicar",
        text,
        re.IGNORECASE,
    )
    assert not imperative_es, (
        f"RECIPE.md contains imperative 'click Publicar' instructions: {imperative_es}"
    )