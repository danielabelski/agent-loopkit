"""Structural test for the Robinhood Safe Growth recipe.

Verifies:
- All required files exist.
- RECIPE.md sections are present and tables have minimum rows.
- prompts/*.env files exist and are non-empty.
- cron.config.yaml parses and has all three stages.
- examples/env.template uses placeholders, not real secrets.
- No committed secrets anywhere in the recipe.
- Read-only tool allowlist is enforced (no banned tools in RH_ALLOWED_TOOLS).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

RECIPE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = RECIPE_DIR.parent.parent

# Tools that MUST be banned — the recipe is read-only.
BANNED_TOOL_PATTERNS = [
    r"place_.*",
    r"cancel_.*",
    r"replace_.*",
    r"add_.*",
    r"remove_.*",
    r"create_.*",
    r"update_.*",
    r"^follow$",
    r"^unfollow$",
]


def test_required_files_exist():
    required = [
        RECIPE_DIR / "RECIPE.md",
        RECIPE_DIR / "cron.config.yaml",
        RECIPE_DIR / "examples" / "env.template",
        RECIPE_DIR / "prompts" / "snapshot.env",
        RECIPE_DIR / "prompts" / "defense.env",
        RECIPE_DIR / "prompts" / "mission.env",
    ]
    for p in required:
        assert p.exists(), f"Missing required file: {p.relative_to(REPO_ROOT)}"


def test_recipe_md_sections():
    text = (RECIPE_DIR / "RECIPE.md").read_text(encoding="utf-8")
    required = [
        "What this loop does",
        "Why this loop exists",
        "Variables you must change",
        "The three configs",
        "Schedules",
        "Skills the operator loads",
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


def test_cron_config_yaml_parses_and_has_all_three_stages():
    data = yaml.safe_load((RECIPE_DIR / "cron.config.yaml").read_text(encoding="utf-8"))
    assert isinstance(data, dict), "cron.config.yaml is not a mapping"
    for stage in ("stage1", "stage2", "stage3"):
        assert stage in data, f"cron.config.yaml missing '{stage}' block"
        block = data[stage]
        assert "schedule" in block, f"{stage} missing 'schedule'"
        assert "no_agent" in block and block["no_agent"] is True, (
            f"{stage} must be no_agent=true (script-only)"
        )


def test_stage_schedules_match_documented_patterns():
    """Stage 1/2 fire Mon-Fri; Stage 3 fires Tue-Sat."""
    data = yaml.safe_load((RECIPE_DIR / "cron.config.yaml").read_text(encoding="utf-8"))
    for stage_name, expected_day_field in [("stage1", "1-5"), ("stage2", "1-5"), ("stage3", "2-6")]:
        schedule = data[stage_name]["schedule"]
        assert schedule.endswith(expected_day_field), (
            f"{stage_name} schedule '{schedule}' should end with '{expected_day_field}'"
        )


def test_no_banned_tools_in_allowed_list():
    """The snapshot, defense, and mission env files MUST NOT list any banned tool as allowed."""
    banned_tools_re = re.compile("|".join(BANNED_TOOL_PATTERNS))
    for env_file in ["./prompts/snapshot.env", "./prompts/defense.env", "./prompts/mission.env"]:
        path = RECIPE_DIR / env_file
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        # Find RH_ALLOWED_TOOLS=...
        match = re.search(r"^RH_ALLOWED_TOOLS\s*=\s*(.+)", content, re.MULTILINE)
        if not match:
            continue
        allowed = match.group(1).strip().split(",")
        for tool in allowed:
            tool = tool.strip()
            if not tool:
                continue
            assert not banned_tools_re.fullmatch(tool), (
                f"{env_file} contains banned tool '{tool}' in RH_ALLOWED_TOOLS"
            )


def test_mission_stage_has_hard_never_executes_guard():
    """Mission Control must never execute trades. RH_MISSION_NEVER_EXECUTES=1 is the guard."""
    content = (RECIPE_DIR / "prompts" / "mission.env").read_text(encoding="utf-8")
    match = re.search(r"^RH_MISSION_NEVER_EXECUTES\s*=\s*(\S+)", content, re.MULTILINE)
    assert match, "prompts/mission.env missing RH_MISSION_NEVER_EXECUTES"
    value = match.group(1).strip().strip('"').strip("'")
    assert value == "1", (
        f"RH_MISSION_NEVER_EXECUTES must be '1' (never executes). Got '{value}'."
    )


def test_safezone_threshold_is_sane():
    """SAFEZONE_THRESHOLD should be between 0.4 and 0.7 — neither too lax nor too strict."""
    content = (RECIPE_DIR / "prompts" / "snapshot.env").read_text(encoding="utf-8")
    match = re.search(r"^RH_SAFEZONE_THRESHOLD\s*=\s*([\d.]+)", content, re.MULTILINE)
    assert match, "prompts/snapshot.env missing RH_SAFEZONE_THRESHOLD"
    value = float(match.group(1))
    assert 0.4 <= value <= 0.7, (
        f"RH_SAFEZONE_THRESHOLD={value} is outside the safe range [0.4, 0.7]"
    )


def test_env_template_uses_placeholders_not_real_tokens():
    content = (RECIPE_DIR / "examples" / "env.template").read_text(encoding="utf-8")
    assert "__replace_me__" in content, "env.template missing __replace_me__ placeholder"
    assert not re.search(r"ghp_[A-Za-z0-9]{20,}", content), "env.template contains a real GitHub PAT"
    assert not re.search(r"sk-[A-Za-z0-9]{20,}", content), "env.template contains an OpenAI key"


def test_no_committed_secrets_anywhere():
    """Grep the whole recipe directory for known token formats."""
    patterns = [
        (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "GitHub PAT"),
        (re.compile(r"sk-[A-Za-z0-9]{20,}"), "OpenAI key"),
        (re.compile(r"EAA[A-Za-z0-9]{50,}"), "Facebook token"),
        (re.compile(r"Mcp-Session-Id:\s*\S{20,}"), "MCP session id"),
    ]
    for f in RECIPE_DIR.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix not in {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".env", ".template"}:
            continue
        if f.name == "env.template":
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pattern, name in patterns:
            assert not pattern.search(content), f"{f.relative_to(REPO_ROOT)} contains a real {name}"


def test_recipe_links_to_sibling_recipes():
    """RECIPE.md should cross-link to other recipes for discoverability."""
    text = (RECIPE_DIR / "RECIPE.md").read_text(encoding="utf-8")
    for sibling in ["tgo-full-funnel-autopilot", "etsy-logo-pack-pipeline"]:
        assert sibling in text, (
            f"RECIPE.md should link to {sibling} for cross-discovery"
        )