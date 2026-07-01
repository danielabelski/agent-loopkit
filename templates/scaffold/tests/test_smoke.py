"""Smoke test for the TGO Full Funnel Autopilot recipe.

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
        f"Canonical validator failed for TGO recipe:\n"
        f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    )


def test_env_template_substitution_is_safe():
    """Filling the placeholders must not produce a real token-shaped string."""
    content = (RECIPE_DIR / "examples" / "env.template").read_text(encoding="utf-8")
    # Substitute with realistic-looking but obviously fake values.
    safe_values = {
        "TGO_PAGE_ID": "000000000000000",
        "TGO_PAGE_ACCESS_TOKEN_FILE": "/run/secrets/tgo_page_access_token",
        "TGO_IMAGE_API_KEY_FILE": "/run/secrets/image_api_key",
        "TGO_IMAGE_MODEL": "gpt-image-2",
        "NPM_CONFIG_CACHE": "/var/cache/npm-vercel",
        "VERCEL_AUTH_FILE": "/run/secrets/vercel-auth.json",
        "TGO_AUTOMATION_ROOT": "/srv/tgo-automation",
        "TGO_HISTORY_FILE": "/srv/tgo-automation/history/campaigns.jsonl",
        "TGO_LANDINGS_DIR": "/srv/tgo-automation/landings",
        "TGO_BRAND_LOGO": "/srv/tgo-automation/assets/logo.jpg",
        "TGO_DAILY_FUNNEL_MAX_POSTS": "3",
        "TGO_PRICE_GUARD_MAX_COMMENTS": "6",
        "TGO_PRICE_GUARD_MAX_POSTS": "12",
        "TGO_OFFER_PRICE_REGEX": r"(\$\s*350|Website\s+Starter)",
        "TGO_OFFER_REPLY_TEXT": "Hola",
        "TGO_LOOKBACK_DAYS": "30",
    }
    substituted = content
    for k, v in safe_values.items():
        substituted = substituted.replace(f"_FILE=__replace_me__", f"_FILE={v}")
    # Just sanity: must not accidentally contain an OpenAI key shape.
    assert not re.search(r"sk-[A-Za-z0-9]{20,}", substituted), (
        "Substituted env template contains a real-looking OpenAI key"
    )


def test_prompt_contains_required_brand_assets_clause():
    """The system prompt must mention the brand logo path requirement."""
    content = (RECIPE_DIR / "prompts" / "system.txt").read_text(encoding="utf-8")
    assert "assets/tgo-logo.jpg" in content or "tgo-logo.jpg" in content, (
        "system.txt does not mention the required brand logo reference"
    )
    assert "1080x1080" in content or "1080×1080" in content, "system.txt missing square image spec"
    assert "1080x1920" in content or "1080×1920" in content, "system.txt missing story image spec"