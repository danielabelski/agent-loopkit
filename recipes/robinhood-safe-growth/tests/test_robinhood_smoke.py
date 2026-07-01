"""Smoke test for the Robinhood Safe Growth recipe.

Verifies the recipe can be parsed against the canonical validator and that
the read-only guarantees are enforced in the actual files.
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


def test_recipe_does_not_recommend_place_order_imperatively():
    """The recipe body must NEVER instruct the operator to call place_* tools.

    Warnings like "never place orders" or "fail closed if you see place_*"
    are OK — those are guardrails, not instructions.
    """
    text = (RECIPE_DIR / "RECIPE.md").read_text(encoding="utf-8")
    imperative = re.findall(
        r"(?:^|\n)\s*(?:stage\s+\d+\s*[:|]?\s*)?(?:then\s+|now\s+)?(?:call|run|execute|place)\s+`?place_",
        text,
        re.IGNORECASE,
    )
    assert not imperative, (
        f"RECIPE.md contains imperative 'place_*' instructions: {imperative}"
    )


def test_all_stages_explicitly_read_only():
    """Every stage must declare read-only intent in cron.config.yaml."""
    data = __import__("yaml").safe_load(
        (RECIPE_DIR / "cron.config.yaml").read_text(encoding="utf-8")
    )
    for stage in ("stage1", "stage2", "stage3"):
        block = data[stage]
        assert block["no_agent"] is True, f"{stage} must be no_agent=true"
        # All stages are wrappers that call the snapshot script
        assert "safe_growth" in block["script"], f"{stage} script should call safe_growth wrapper"


def test_prompts_have_no_real_tokens():
    """No prompt file should contain a real token-shaped string."""
    for env_file in ["snapshot.env", "defense.env", "mission.env"]:
        path = RECIPE_DIR / "prompts" / env_file
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        assert not re.search(r"sk-[A-Za-z0-9]{20,}", content), (
            f"prompts/{env_file} contains an OpenAI-shaped token"
        )
        assert not re.search(r"ghp_[A-Za-z0-9]{20,}", content), (
            f"prompts/{env_file} contains a GitHub PAT"
        )


def test_env_template_substitution_is_safe():
    """Filling placeholders must not produce a real token-shaped string."""
    content = (RECIPE_DIR / "examples" / "env.template").read_text(encoding="utf-8")
    safe_values = {
        "RH_MCP_TOKEN_FILE": "/run/secrets/robinhood_mcp_token",
        "RH_SAFE_GROWTH_MODE": "entry",
        "RH_NOTIFY_TELEGRAM": "1",
        "RH_REDACT_ACCOUNTS": "1",
        "RH_MISSION_NOTES_FILE": "/run/state/robinhood_notes",
        "RH_UNIVERSE": "SPY,QQQ,MSFT",
        "RH_SAFEZONE_THRESHOLD": "0.55",
        "RH_MAX_DAILY_TRADES": "1",
        "RH_RISK_TOLERANCE": "conservative",
        "RH_LANGUAGE": "Spanish",
        "RH_TIMEZONE": "America/New_York",
        "RH_DEFENSE_MAX_LATE_ENTRIES": "0",
        "RH_DEFENSE_TRAILING_STOP_PCT": "2.0",
        "RH_DEFENSE_SAFEZONE_BOOST": "0.05",
        "RH_MISSION_LOOKBACK_DAYS": "5",
        "RH_MISSION_FAVOR_MIN_TRADES": "2",
        "RH_MISSION_PAUSE_MIN_LOSSES": "3",
        "RH_MISSION_NEVER_EXECUTES": "1",
        "MAX_CONSECUTIVE_ERRORS": "4",
    }
    substituted = content
    for k, v in safe_values.items():
        substituted = substituted.replace(f"#{k}#=__replace_me__", f"#{k}#={v}")
        substituted = substituted.replace(f"{k}=__replace_me__", f"{k}={v}")
    assert not re.search(r"sk-[A-Za-z0-9]{20,}", substituted), (
        "Substituted env template contains a real-looking OpenAI key"
    )