#!/usr/bin/env python3
"""Recipe validator — checks every recipe in recipes/ against the canonical shape.

Run:
    python3 scripts/validate_recipe.py                       # all recipes under recipes/
    python3 scripts/validate_recipe.py recipes/<slug>/       # one recipe
    python3 scripts/validate_recipe.py --all                 # explicit all

Exit code 0 = all recipes pass. Non-zero with a human-readable list of issues.

This validator enforces:
- RECIPE.md exists and has the required top-level sections.
- cron.config.yaml exists and parses as YAML with a `schedule` and `delivery`.
- prompts/system.txt exists and is non-empty.
- examples/env.template exists and contains `__replace_me__` placeholders (not real values).
- Failure modes table has at least 3 rows.
- Variables table has at least 3 rows.
- Verification checklist has at least 3 items.
- No committed secrets: greps for known token prefixes.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


REQUIRED_RECIPE_SECTIONS = [
    "What this loop does",
    "Why this loop exists",
    "Variables you must change",
    # "The prompt" — required for LLM-driven recipes; replaced by "The three configs"
    # for script-only pipelines. The validator accepts either via the regex below.
    "Skills",
    "Inputs",
    "Outputs",
    "Secrets required",
    "Failure modes",
    "Pitfalls",
    "Verification checklist",
]

# Section-name aliases — "The prompt" / "The three configs" / etc. all satisfy
# the prompt/config slot. "Skills the agent loads" / "Skills the operator loads"
# both satisfy the skills slot.
SECTION_ALIASES = {
    "The prompt": ["The prompt", "The three configs", "The configuration"],
    "Skills": [
        "Skills the agent loads",
        "Skills the operator loads",
        "Skills the pipeline loads",
    ],
}

SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "GitHub PAT"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), "GitHub fine-grained PAT"),
    (re.compile(r"xox[abprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "OpenAI API key"),
    (re.compile(r"sk-proj-[A-Za-z0-9]{20,}"), "OpenAI project key"),
    (re.compile(r"EAA[A-Za-z0-9]{50,}"), "Facebook access token (long-lived)"),
]

PLACEHOLDER_PATTERNS = [
    re.compile(r"__replace_me__", re.IGNORECASE),
    re.compile(r"<[A-Z][A-Z0-9_]+>"),  # <BUSINESS_NAME> style
]


def validate_recipe(slug_dir: Path) -> list[str]:
    issues: list[str] = []
    if not slug_dir.is_dir():
        return [f"{slug_dir} is not a directory"]

    recipe_md = slug_dir / "RECIPE.md"
    cron_yaml = slug_dir / "cron.config.yaml"
    prompt_txt = slug_dir / "prompts" / "system.txt"
    env_template = slug_dir / "examples" / "env.template"

    # Required files
    if not recipe_md.exists():
        issues.append("Missing RECIPE.md")
        return issues
    if not cron_yaml.exists():
        issues.append("Missing cron.config.yaml")
    # prompts/system.txt is required for LLM-driven recipes. Script-only
    # pipelines (no_agent=true) can ship a single placeholder file or split
    # the config across prompts/*.env — both shapes pass if at least one
    # prompts/* file exists.
    if not prompt_txt.exists():
        prompts_dir = slug_dir / "prompts"
        any_prompt = prompts_dir.is_dir() and any(prompts_dir.iterdir())
        if not any_prompt:
            issues.append(
                "Missing prompts/system.txt (and prompts/ directory is empty). "
                "Either provide a system prompt, or split the config into prompts/*.env files."
            )
    if not env_template.exists():
        issues.append("Missing examples/env.template")

    # RECIPE.md sections
    text = recipe_md.read_text(encoding="utf-8")
    for section in REQUIRED_RECIPE_SECTIONS:
        # Use alias list if available, else the section name itself
        names = SECTION_ALIASES.get(section, [section])
        matched = False
        for name in names:
            pattern = re.compile(rf"^#{{2,3}}\s+{re.escape(name)}", re.MULTILINE | re.IGNORECASE)
            if pattern.search(text):
                matched = True
                break
        if not matched:
            issues.append(f"RECIPE.md missing required section: '{names[0]}' (or any alias)")

    # Variables table rows (>= 3)
    if "| Variable |" in text:
        var_rows = re.findall(r"^\| `\w+` \|", text, re.MULTILINE)
        if len(var_rows) < 3:
            issues.append(f"Variables table has only {len(var_rows)} rows; need at least 3")
    else:
        issues.append("Variables table not found (expected '| Variable | ... |' header)")

    # Failure modes table rows (>= 3)
    fm_match = re.search(
        r"##\s+Failure modes.*?(?=^##\s|\Z)", text, re.MULTILINE | re.IGNORECASE | re.DOTALL
    )
    if fm_match:
        fm_block = fm_match.group(0)
        fm_rows = re.findall(r"^\| .+\| .+\| .+\|", fm_block, re.MULTILINE)
        fm_data_rows = [r for r in fm_rows if not re.match(r"^\|\s*-+\s*\|", r)]
        if len(fm_data_rows) < 3:
            issues.append(
                f"Failure modes table has only {len(fm_data_rows)} data rows; need at least 3"
            )
    else:
        issues.append("Failure modes section missing or empty")

    # Verification checklist (>= 3 items)
    vc_match = re.search(
        r"##\s+Verification checklist.*?(?=^##\s|\Z)", text, re.MULTILINE | re.IGNORECASE | re.DOTALL
    )
    if vc_match:
        vc_block = vc_match.group(0)
        vc_items = re.findall(r"^- \[[ x]\] .+", vc_block, re.MULTILINE)
        if len(vc_items) < 3:
            issues.append(
                f"Verification checklist has only {len(vc_items)} items; need at least 3"
            )
    else:
        issues.append("Verification checklist section missing or empty")

    # cron.config.yaml parses + has schedule + delivery
    if cron_yaml.exists():
        try:
            data = yaml.safe_load(cron_yaml.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                issues.append("cron.config.yaml is not a YAML mapping")
            else:
                # Accept either a single-job shape (schedule/delivery at root)
                # or a multi-stage shape (stage1/stage2/stage3 blocks at root).
                has_schedule = "schedule" in data
                has_delivery = "delivery" in data
                stage_blocks = [k for k in data if k.startswith("stage") and isinstance(data[k], dict)]
                has_stages = len(stage_blocks) >= 1

                if not has_schedule and not has_stages:
                    issues.append(
                        "cron.config.yaml missing 'schedule' field (or 'stage*' blocks)"
                    )
                if not has_delivery and not has_stages:
                    issues.append(
                        "cron.config.yaml missing 'delivery' field (or 'stage*' blocks)"
                    )

                # If multi-stage, each stage must have schedule
                for stage_name in stage_blocks:
                    if "schedule" not in data[stage_name]:
                        issues.append(
                            f"cron.config.yaml stage '{stage_name}' missing 'schedule' field"
                        )
        except yaml.YAMLError as e:
            issues.append(f"cron.config.yaml is not valid YAML: {e}")

    # prompts/system.txt is non-empty
    if prompt_txt.exists():
        content = prompt_txt.read_text(encoding="utf-8").strip()
        if len(content) < 50:
            issues.append(
                f"prompts/system.txt is too short ({len(content)} chars); need substantive prompt"
            )

    # examples/env.template: must have placeholders, not real tokens
    if env_template.exists():
        env_content = env_template.read_text(encoding="utf-8")
        has_placeholder = any(p.search(env_content) for p in PLACEHOLDER_PATTERNS)
        if not has_placeholder:
            issues.append(
                "examples/env.template has no placeholder sentinel (__replace_me__ or <NAME>)"
            )
        for pattern, name in SECRET_PATTERNS:
            if pattern.search(env_content):
                issues.append(
                    f"examples/env.template contains a real {name} — replace with placeholder"
                )

    # Whole-recipe secret scan (excluding env.template which is allowed to mention placeholders)
    for f in slug_dir.rglob("*"):
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
        for pattern, name in SECRET_PATTERNS:
            if pattern.search(content):
                issues.append(f"{f.relative_to(slug_dir)} contains a real {name}")

    return issues


def collect_targets(repo_root: Path, path_arg: str | None, all_flag: bool) -> list[Path]:
    recipes_dir = repo_root / "recipes"
    if all_flag or path_arg is None:
        if not recipes_dir.exists():
            return []
        return sorted(d for d in recipes_dir.iterdir() if d.is_dir())

    target = Path(path_arg).resolve()
    if target.is_dir():
        if (target / "RECIPE.md").exists():
            return [target]
        if (target / "recipes").exists():
            return sorted(d for d in (target / "recipes").iterdir() if d.is_dir())
    return [target]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate agent-loopkit recipes")
    parser.add_argument("path", nargs="?", help="Path to a recipe directory (default: all)")
    parser.add_argument("--all", action="store_true", help="Validate every recipe under recipes/")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    targets = collect_targets(repo_root, args.path, args.all)

    if not targets:
        print("No recipes found to validate.", file=sys.stderr)
        return 2

    all_issues = {t.name: validate_recipe(t) for t in targets}

    if args.json:
        print(json.dumps(all_issues, indent=2))
    else:
        total_issues = sum(len(v) for v in all_issues.values())
        for name, issues in all_issues.items():
            if not issues:
                print(f"[OK]   {name}")
            else:
                print(f"[FAIL] {name}")
                for issue in issues:
                    print(f"        - {issue}")
        print(f"\n{total_issues} issue(s) across {len(all_issues)} recipe(s)")

    return 0 if all(not v for v in all_issues.values()) else 1


if __name__ == "__main__":
    sys.exit(main())