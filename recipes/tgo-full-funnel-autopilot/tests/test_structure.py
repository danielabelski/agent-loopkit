"""Structural test for the TGO Full Funnel Autopilot recipe.

Verifies:
- All required files exist.
- RECIPE.md sections are present and tables have the minimum rows.
- prompts/system.txt is substantive.
- cron.config.yaml parses and has the expected fields.
- examples/env.template uses placeholders, not real secrets.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

RECIPE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = RECIPE_DIR.parent.parent


def test_required_files_exist():
    required = [
        RECIPE_DIR / "RECIPE.md",
        RECIPE_DIR / "cron.config.yaml",
        RECIPE_DIR / "prompts" / "system.txt",
        RECIPE_DIR / "examples" / "env.template",
    ]
    for p in required:
        assert p.exists(), f"Missing required file: {p.relative_to(REPO_ROOT)}"


def test_recipe_md_sections():
    text = (RECIPE_DIR / "RECIPE.md").read_text(encoding="utf-8")
    required = [
        "What this loop does",
        "Why this loop exists",
        "Variables you must change",
        "The prompt",
        "Schedule",
        "Skills the agent loads",
        "Inputs",
        "Outputs",
        "Secrets required",
        "Failure modes",
        "Pitfalls",
        "Verification checklist",
    ]
    for section in required:
        pattern = re.compile(rf"^#{{2,3}}\s+{re.escape(section)}", re.MULTILINE | re.IGNORECASE)
        assert pattern.search(text), f"RECIPE.md missing section: {section}"


def test_recipe_md_variables_table_has_at_least_3_rows():
    text = (RECIPE_DIR / "RECIPE.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| `\w+` \|", text, re.MULTILINE)
    assert len(rows) >= 3, f"Variables table has only {len(rows)} rows; need >= 3"


def test_recipe_md_failure_modes_has_at_least_3_rows():
    text = (RECIPE_DIR / "RECIPE.md").read_text(encoding="utf-8")
    fm_match = re.search(
        r"##\s+Failure modes.*?(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL
    )
    assert fm_match, "Failure modes section missing"
    fm_rows = re.findall(r"^\| .+\| .+\| .+\|", fm_match.group(0), re.MULTILINE)
    data_rows = [r for r in fm_rows if not re.match(r"^\|\s*-+\s*\|", r)]
    assert len(data_rows) >= 3, f"Failure modes table has only {len(data_rows)} data rows; need >= 3"


def test_recipe_md_verification_checklist_has_at_least_3_items():
    text = (RECIPE_DIR / "RECIPE.md").read_text(encoding="utf-8")
    vc_match = re.search(
        r"##\s+Verification checklist.*?(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL
    )
    assert vc_match, "Verification checklist section missing"
    items = re.findall(r"^- \[[ x]\] .+", vc_match.group(0), re.MULTILINE)
    assert len(items) >= 3, f"Verification checklist has only {len(items)} items; need >= 3"


def test_system_prompt_is_substantive():
    content = (RECIPE_DIR / "prompts" / "system.txt").read_text(encoding="utf-8").strip()
    assert len(content) >= 500, f"system.txt too short ({len(content)} chars); need substantive prompt"


def test_cron_config_yaml_parses_and_has_required_fields():
    data = yaml.safe_load((RECIPE_DIR / "cron.config.yaml").read_text(encoding="utf-8"))
    assert isinstance(data, dict), "cron.config.yaml is not a mapping"
    assert "schedule" in data, "cron.config.yaml missing 'schedule'"
    assert "delivery" in data, "cron.config.yaml missing 'delivery'"
    assert "skills" in data and len(data["skills"]) >= 1, "cron.config.yaml missing 'skills'"


def test_env_template_uses_placeholders_not_real_tokens():
    content = (RECIPE_DIR / "examples" / "env.template").read_text(encoding="utf-8")
    assert "__replace_me__" in content, "env.template missing __replace_me__ placeholder"
    # Make sure no real token slipped in
    assert not re.search(r"ghp_[A-Za-z0-9]{20,}", content), "env.template contains a real GitHub PAT"
    assert not re.search(r"EAA[A-Za-z0-9]{50,}", content), "env.template contains a real FB token"


def test_recipe_references_resolve():
    """All recipe-relative links should resolve to a file that exists in the recipe directory."""
    text = (RECIPE_DIR / "RECIPE.md").read_text(encoding="utf-8")
    # Find markdown links of the form ([text](relative/path))
    links = re.findall(r"\]\((?!https?://|#)([^)]+)\)", text)
    for link in links:
        # Strip anchors
        link_path = link.split("#", 1)[0]
        if not link_path:
            continue
        resolved = (RECIPE_DIR / link_path).resolve()
        assert resolved.exists(), f"Broken link in RECIPE.md: {link} -> {resolved}"


def test_no_committed_secrets_anywhere():
    """Grep the whole recipe directory for known token formats."""
    patterns = [
        (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "GitHub PAT"),
        (re.compile(r"sk-[A-Za-z0-9]{20,}"), "OpenAI key"),
        (re.compile(r"EAA[A-Za-z0-9]{50,}"), "Facebook token"),
    ]
    for f in RECIPE_DIR.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix not in {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".template"}:
            continue
        if f.name == "env.template":
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pattern, name in patterns:
            assert not pattern.search(content), f"{f.relative_to(REPO_ROOT)} contains a real {name}"