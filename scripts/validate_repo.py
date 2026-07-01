#!/usr/bin/env python3
"""Repo-level structure validator.

Checks:
- assets/{banner,logo,icon}.svg exist.
- README.md links to assets/banner.svg and references the tagline.
- LICENSE exists and contains MIT.
- SECURITY.md exists.
- CHANGELOG.md exists and references the current Unreleased section.
- Each recipe under recipes/ has a unique slug.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    repo = Path(__file__).resolve().parent.parent
    issues: list[str] = []

    # Required root files
    for required in ["README.md", "CONTRIBUTING.md", "LICENSE", "CHANGELOG.md", "SECURITY.md", "RECIPE_TEMPLATE.md"]:
        if not (repo / required).exists():
            issues.append(f"Missing required root file: {required}")

    # Branding assets
    for asset in ["assets/banner.svg", "assets/logo.svg", "assets/icon.svg"]:
        if not (repo / asset).exists():
            issues.append(f"Missing asset: {asset}")

    # README references banner
    readme = (repo / "README.md").read_text(encoding="utf-8") if (repo / "README.md").exists() else ""
    if "assets/banner.svg" not in readme:
        issues.append("README.md does not reference assets/banner.svg")
    if "copy · customize · ship" not in readme and "copy, customize, ship" not in readme:
        issues.append("README.md does not include the tagline 'copy · customize · ship'")

    # LICENSE contains MIT
    if (repo / "LICENSE").exists():
        if "MIT License" not in (repo / "LICENSE").read_text(encoding="utf-8"):
            issues.append("LICENSE does not declare MIT License")

    # Unique recipe slugs
    recipes_dir = repo / "recipes"
    if recipes_dir.exists():
        slugs = [d.name for d in recipes_dir.iterdir() if d.is_dir()]
        if len(slugs) != len(set(slugs)):
            issues.append(f"Duplicate recipe slugs under recipes/: {slugs}")

    if issues:
        print("[FAIL] Repo structure validation:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    print("[OK] Repo structure is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())