#!/usr/bin/env python3
"""Validate repository structure; semantic writing quality is assessed separately."""
import ast
from datetime import date
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from sync_style import read_version, render, text_block

ROOT = Path(__file__).resolve().parents[1]


def prose(text):
    """Ignore fenced/inline code when checking Markdown links."""
    lines, fence = [], None
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            mark = match.group(1)
            if fence is None:
                fence = (mark[0], len(mark))
            elif mark[0] == fence[0] and len(mark) >= fence[1]:
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return re.sub(r"(`+).*?\1", "", "\n".join(lines))


def check_links(path, root):
    errors = []
    text = prose(path.read_text(encoding="utf-8"))
    inline = re.findall(r"!?\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", text)
    definitions = re.findall(r"^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)", text, re.M)
    for link in inline + definitions:
        target = link.strip("<>")
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        local = (path.parent / unquote(parsed.path)).resolve()
        try:
            local.relative_to(root.resolve())
        except ValueError:
            errors.append("relative link escapes repository")
            continue
        if not local.exists():
            errors.append("relative link target does not exist: " + parsed.path)
    return errors


def validate_record(record):
    required = {"date", "guidance_commit", "guidance_version", "variant", "platform",
                "model", "settings", "unknown_reason", "input", "output", "checks", "overall"}
    if not isinstance(record, dict) or set(record) != required:
        raise ValueError("evaluation record must have exactly the documented fields")
    for key in ("date", "guidance_commit", "guidance_version", "platform", "input", "output"):
        if not isinstance(record[key], str) or not record[key].strip():
            raise ValueError("evaluation text field is missing: " + key)
    date.fromisoformat(record["date"])
    if not re.fullmatch(r"[0-9a-f]{40}", record["guidance_commit"]):
        raise ValueError("guidance_commit must be a full commit SHA")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", record["guidance_version"]):
        raise ValueError("guidance_version must be major.minor.patch")
    if record["variant"] not in ("full", "short", "skill"):
        raise ValueError("unknown guidance variant")
    if record["model"] is not None and (not isinstance(record["model"], str) or not record["model"].strip()):
        raise ValueError("model must be nonempty text or null")
    if record["settings"] is not None and not isinstance(record["settings"], dict):
        raise ValueError("settings must be an object or null")
    if not isinstance(record["unknown_reason"], str):
        raise ValueError("unknown_reason must be text")
    if (record["model"] is None or record["settings"] is None) and not record["unknown_reason"].strip():
        raise ValueError("unavailable model/settings require a reason")
    checks = record["checks"]
    if not isinstance(checks, dict) or set(checks) != {"facts", "request", "style", "readability"}:
        raise ValueError("four separate evaluation axes are required")
    for check in checks.values():
        if not isinstance(check, dict) or set(check) != {"verdict", "evidence"}:
            raise ValueError("each evaluation axis needs verdict and evidence")
        if check["verdict"] not in ("pass", "fail", "unassessed"):
            raise ValueError("unknown verdict")
        if not isinstance(check["evidence"], str) or (check["verdict"] != "unassessed" and not check["evidence"].strip()):
            raise ValueError("assessed verdict requires evidence")
    values = [check["verdict"] for check in checks.values()]
    expected = "fail" if "fail" in values else "pass" if all(v == "pass" for v in values) else "unassessed"
    if record["overall"] != expected:
        raise ValueError("overall must be fail for any failed axis; pass requires all four passes")


def skill_files(root):
    skill = root / "skills/writing-style-doc"
    allowed = [skill / "SKILL.md"] + sorted((skill / "references").glob("*.md"))
    for path in allowed:
        if path.is_symlink() or not path.is_file():
            raise ValueError("skill payload must contain regular files only")
    return allowed


def validate(root):
    read_version(root)
    skill = root / "skills/writing-style-doc/SKILL.md"
    if skill.read_text(encoding="utf-8") != render(root):
        raise ValueError("SKILL.md is out of sync; run scripts/sync_style.py")
    short = text_block(root / "platforms/chatgpt.md", "## 짧은 버전")
    if len(short) > 1500:
        raise ValueError("short instructions exceed 1500 characters")
    front = skill.read_text(encoding="utf-8").split("---", 2)[1].strip().splitlines()
    if len(front) != 2 or front[0] != "name: writing-style-doc" or not front[1].startswith("description: "):
        raise ValueError("generated skill metadata is invalid")
    if not json.loads(front[1].split(": ", 1)[1]):
        raise ValueError("skill description is empty")
    for path in sorted(root.rglob("*.md")):
        if any(part in (".git", "dist", "__pycache__") for part in path.parts):
            continue
        errors = check_links(path, root)
        if errors:
            raise ValueError(str(path.relative_to(root)) + ": " + "; ".join(errors))
    for path in list((root / "scripts").glob("*.py")) + list((root / "tests").glob("*.py")):
        ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 8))
    for path in (root / "evaluation/runs").glob("*.json"):
        try:
            validate_record(json.loads(path.read_text(encoding="utf-8")))
        except (ValueError, TypeError) as exc:
            raise ValueError(path.name + ": " + str(exc)) from exc
    skill_files(root)


def main():
    try:
        validate(ROOT)
    except (ValueError, IndexError, OSError, SyntaxError, TypeError) as exc:
        print("Validation failed: " + str(exc), file=sys.stderr)
        return 1
    print("Repository checks passed (semantic quality and external URLs assessed separately)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
