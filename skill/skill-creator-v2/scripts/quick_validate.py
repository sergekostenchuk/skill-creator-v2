#!/usr/bin/env python3
"""Stdlib-only validation for skill folders."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ALLOWED_PROPERTIES = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}


def parse_simple_frontmatter(text: str) -> tuple[dict[str, str], str | None]:
    """Parse the simple YAML subset used by skill frontmatter.

    This intentionally avoids PyYAML so packaging works in a fresh Python
    environment. It supports `key: value` and `key: |` block scalars, which are
    enough for Codex/Claude skill metadata.
    """
    if not text.startswith("---\n"):
        return {}, "No YAML frontmatter found"

    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    if not match:
        return {}, "Invalid frontmatter format"

    lines = match.group(1).splitlines()
    result: dict[str, str] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line.startswith((" ", "\t")):
            return {}, f"Unexpected indented frontmatter line: {line.strip()}"
        if ":" not in line:
            return {}, f"Invalid frontmatter line: {line}"
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if not key:
            return {}, "Empty frontmatter key"
        if value in {"|", ">"}:
            block: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or lines[i].startswith("\t") or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            result[key] = "\n".join(block).strip()
            continue
        result[key] = value.strip("\"'")
        i += 1
    return result, None


def validate_skill(skill_path: str | Path) -> tuple[bool, str]:
    """Validate a skill folder."""
    skill_path = Path(skill_path)
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")
    frontmatter, error = parse_simple_frontmatter(content)
    if error:
        return False, error

    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = frontmatter.get("name", "").strip()
    if not re.match(r"^[a-z0-9-]+$", name):
        return False, f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens only)"
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
    if len(name) > 64:
        return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."

    description = frontmatter.get("description", "").strip()
    if not description:
        return False, "Description cannot be empty"
    if "<" in description or ">" in description:
        return False, "Description cannot contain angle brackets (< or >)"
    if len(description) > 1024:
        return False, f"Description is too long ({len(description)} characters). Maximum is 1024 characters."

    compatibility = frontmatter.get("compatibility", "").strip()
    if compatibility and len(compatibility) > 500:
        return False, f"Compatibility is too long ({len(compatibility)} characters). Maximum is 500 characters."

    return True, "Skill is valid!"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        return 1

    valid, message = validate_skill(sys.argv[1])
    print(message)
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())

