#!/usr/bin/env python3
"""Stdlib-only validation for skill folders."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ALLOWED_PROPERTIES = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
ALLOWED_GROUP_LAYOUTS = {
    "single_skill",
    "single_visible_orchestrator_with_workers",
    "multi_skill_group",
    "hybrid_group",
}
ALLOWED_GROUP_MEMBERSHIP_TYPES = {
    "merge_into_parent",
    "internal_worker",
    "reusable_satellite_skill",
    "shared_module",
}
INTERNAL_WORKER_REQUIRED_FIELDS = {
    "worker_id",
    "purpose",
    "specialist_role",
    "classification_packet",
    "inputs",
    "outputs",
    "write_zone",
    "read_zone",
    "required_evidence",
    "risk_gates",
    "failure_modes",
    "retry_limit",
    "stop_rules",
    "handoff_packet",
    "context_review_checkpoint",
    "group_membership_type",
}


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


def is_kebab(value: str) -> bool:
    return bool(re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$", value)) and "--" not in value


def path_is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def worker_field_present(text: str, field: str) -> bool:
    pattern = rf"(?im)^\s*(?:[-*]\s*)?(?:#+\s*)?`?{re.escape(field)}`?\s*:"
    return bool(re.search(pattern, text))


def validate_worker_markdown(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"Cannot read {path}: {exc}"]
    missing = sorted(field for field in INTERNAL_WORKER_REQUIRED_FIELDS if not worker_field_present(text, field))
    if missing:
        errors.append(f"{path.name} missing worker contract field(s): {', '.join(missing)}")
    return errors


def validate_group_layout(skill_path: Path) -> list[str]:
    errors: list[str] = []
    workers_dir = skill_path / "group" / "workers"
    if not workers_dir.exists():
        return errors
    if not workers_dir.is_dir():
        return ["group/workers exists but is not a directory"]

    nested_skill_files = sorted(path.relative_to(skill_path) for path in workers_dir.rglob("SKILL.md"))
    for nested in nested_skill_files:
        errors.append(f"Internal worker folders must use WORKER.md, not nested SKILL.md: {nested}")

    worker_markdown_files = sorted(workers_dir.glob("*/WORKER.md"))
    registry_path = workers_dir / "registry.json"
    if worker_markdown_files and not registry_path.exists():
        errors.append("group/workers/registry.json is required when internal WORKER.md files exist")
        return errors
    if not registry_path.exists():
        return errors

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return errors + [f"group/workers/registry.json is invalid JSON: {exc}"]
    except OSError as exc:
        return errors + [f"Cannot read group/workers/registry.json: {exc}"]

    if not isinstance(registry, dict):
        return errors + ["group/workers/registry.json must contain a JSON object"]

    layout = registry.get("group_layout")
    if layout not in ALLOWED_GROUP_LAYOUTS:
        errors.append(f"group/workers/registry.json has unknown group_layout: {layout!r}")

    workers = registry.get("workers", [])
    if not isinstance(workers, list):
        errors.append("group/workers/registry.json field 'workers' must be a list")
        workers = []

    registered_internal_paths: set[Path] = set()
    seen_ids: set[str] = set()
    for index, worker in enumerate(workers):
        if not isinstance(worker, dict):
            errors.append(f"registry workers[{index}] must be an object")
            continue
        worker_id = str(worker.get("worker_id", "")).strip()
        membership = worker.get("group_membership_type")
        rel_path_value = str(worker.get("path", "")).strip()
        if not worker_id:
            errors.append(f"registry workers[{index}] missing worker_id")
        elif not is_kebab(worker_id):
            errors.append(f"registry worker_id must be kebab-case: {worker_id!r}")
        elif worker_id in seen_ids:
            errors.append(f"duplicate worker_id in registry: {worker_id}")
        seen_ids.add(worker_id)

        if membership not in ALLOWED_GROUP_MEMBERSHIP_TYPES:
            errors.append(f"registry worker {worker_id or index} has unknown group_membership_type: {membership!r}")
        if not rel_path_value:
            errors.append(f"registry worker {worker_id or index} missing path")
            continue

        target = (registry_path.parent / rel_path_value).resolve()
        if membership == "internal_worker":
            if target.name != "WORKER.md":
                errors.append(f"internal worker {worker_id or index} path must point to WORKER.md")
                continue
            if not path_is_relative_to(target, workers_dir):
                errors.append(f"internal worker {worker_id or index} path must stay under group/workers")
            if not target.exists():
                errors.append(f"internal worker {worker_id or index} path does not exist: {rel_path_value}")
                continue
            registered_internal_paths.add(target)
            errors.extend(validate_worker_markdown(target))
        elif membership == "reusable_satellite_skill":
            if target.name != "SKILL.md":
                errors.append(f"reusable satellite {worker_id or index} path should point to a standalone SKILL.md")
        elif membership == "shared_module":
            errors.append(f"registry worker {worker_id or index} is shared_module; put shared modules in shared_modules[]")

    for worker_md in worker_markdown_files:
        if worker_md.resolve() not in registered_internal_paths:
            errors.append(f"internal WORKER.md is not registered: {worker_md.relative_to(skill_path)}")

    shared_modules = registry.get("shared_modules", [])
    if shared_modules and not isinstance(shared_modules, list):
        errors.append("group/workers/registry.json field 'shared_modules' must be a list")
        shared_modules = []
    for index, module in enumerate(shared_modules):
        if not isinstance(module, dict):
            errors.append(f"registry shared_modules[{index}] must be an object")
            continue
        module_id = str(module.get("module_id", "")).strip()
        membership = module.get("group_membership_type")
        rel_path_value = str(module.get("path", "")).strip()
        if not module_id:
            errors.append(f"registry shared_modules[{index}] missing module_id")
        if membership != "shared_module":
            errors.append(f"shared module {module_id or index} must use group_membership_type shared_module")
        if not rel_path_value:
            errors.append(f"shared module {module_id or index} missing path")
            continue
        target = (registry_path.parent / rel_path_value).resolve()
        if not path_is_relative_to(target, skill_path):
            errors.append(f"shared module {module_id or index} path must stay inside the skill package")
        elif not target.exists():
            errors.append(f"shared module {module_id or index} path does not exist: {rel_path_value}")

    return errors


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

    group_errors = validate_group_layout(skill_path)
    if group_errors:
        return False, "; ".join(group_errors)

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
