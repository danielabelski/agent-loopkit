"""Smoke test for the recipe validator.

Validates that scripts/validate_recipe.py works against the TGO recipe shipped
in this repo, and that scripts/validate_repo.py accepts the current repo shape.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def test_validator_runs_on_tgo_recipe():
    """The TGO recipe shipped with the repo must pass validation."""
    tgo = REPO / "recipes" / "tgo-full-funnel-autopilot"
    if not tgo.exists():
        pytest.skip("TGO recipe not present yet — only relevant once recipe is added")
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "validate_recipe.py"), str(tgo)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Recipe validator failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    )


def test_repo_validator_passes():
    """The repo-level structure validator must pass on the current repo."""
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "validate_repo.py")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Repo validator failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    )


def test_recipe_validator_detects_missing_section(tmp_path):
    """If a RECIPE.md is missing a required section, the validator must catch it."""
    fake = tmp_path / "broken-recipe"
    fake.mkdir()
    (fake / "RECIPE.md").write_text(
        "# Broken\n\n## What this loop does\nA loop.\n",
        encoding="utf-8",
    )
    (fake / "cron.config.yaml").write_text("schedule: '0 * * * *'\ndelivery: origin\n", encoding="utf-8")
    (fake / "prompts").mkdir()
    (fake / "prompts" / "system.txt").write_text("A system prompt that is long enough to pass.\n" * 5, encoding="utf-8")
    (fake / "examples").mkdir()
    (fake / "examples" / "env.template").write_text("X=__replace_me__\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "validate_recipe.py"), str(fake)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, "Validator must reject a recipe missing required sections"
    assert "Variables" in result.stdout or "missing" in result.stdout.lower()