#!/usr/bin/env python3
"""Validate repository structure; semantic writing quality is assessed separately."""
import ast
from datetime import date
import json
import hashlib
import html
import subprocess
import unicodedata
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from sync_style import read_version, render, text_block

ROOT = Path(__file__).resolve().parents[1]


def without_fences(text):
    """Keep prose and heading contents; ignore fenced code and HTML comments."""
    lines, fence = [], None
    for line in text.splitlines():
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence is None and match:
            fence = (match.group(1)[0], len(match.group(1)))
            continue
        if fence is not None:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= fence[1] and not match.group(2).strip():
                fence = None
            continue
        lines.append(line)
    return re.sub(r"<!--.*?-->", "", "\n".join(lines), flags=re.S)


def prose(text):
    text = without_fences(text)
    return re.sub(r"(`+).*?\1", lambda m: " " * len(m.group(0)), text, flags=re.S)


def balanced(text, start, opener, closer):
    """Return the closing delimiter, respecting escapes and nested pairs."""
    depth, i = 1, start + 1
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == opener:
            depth += 1
        elif text[i] == closer:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None


def reference_id(text):
    return " ".join(text.split()).casefold()


def destination(text):
    text = text.strip()
    if text.startswith("<"):
        end = text.find(">")
        return text[1:end] if end >= 0 else None
    return re.split(r"\s", text, 1)[0] if text else None


def markdown_links(text):
    """Extract inline, explicit/collapsed reference, and defined shortcut links."""
    text = prose(text)
    definitions = {}
    targets, errors = [], []
    pattern = re.compile(r"^ {0,3}\[([^]\n]+)\]:[ \t]*(.*)$", re.M)
    for match in pattern.finditer(text):
        target = destination(match.group(2))
        if target:
            definitions.setdefault(reference_id(match.group(1)), target)
            targets.append(target)
    text = pattern.sub("", text)
    i = 0
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] != "[":
            i += 1
            continue
        end = balanced(text, i, "[", "]")
        if end is None:
            i += 1
            continue
        label = text[i + 1:end]
        nxt = end + 1
        if nxt < len(text) and text[nxt] == "(":
            close = balanced(text, nxt, "(", ")")
            if close is not None:
                target = destination(text[nxt + 1:close])
                if target:
                    targets.append(target)
                i = close + 1
                continue
        if nxt < len(text) and text[nxt] == "[":
            close = balanced(text, nxt, "[", "]")
            if close is not None:
                key = reference_id(text[nxt + 1:close] or label)
                if key not in definitions:
                    errors.append("undefined reference link: " + key)
                else:
                    targets.append(definitions[key])
                i = close + 1
                continue
        key = reference_id(label)
        if key in definitions:
            targets.append(definitions[key])
        # An undefined shortcut is literal Markdown prose, not a broken link.
        i = end + 1
    return targets, errors


def heading_anchors(text):
    text = without_fences(text)
    found, used = set(), set()
    headings = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            headings.append(match.group(1))
        elif index > 0 and re.fullmatch(r" {0,3}(?:=+|-+)\s*", line) and lines[index - 1].strip():
            headings.append(lines[index - 1].strip())
    for heading in headings:
        heading = re.sub(r"!?\[([^]]+)\]\([^)]*\)", r"\1", heading)
        heading = re.sub(r"<[^>]*>", "", heading)
        heading = html.unescape(heading).strip().lower()
        heading = re.sub(r"(?<!\w)_([^_\n]+)_(?!\w)", r"\1", heading)
        heading = re.sub(r"[*`~]", "", heading)
        base = "".join(ch for ch in heading if ch in " -_" or unicodedata.category(ch)[0] in "LNM").replace(" ", "-")
        candidate, suffix = base, 0
        while candidate in used:
            suffix += 1
            candidate = base + "-" + str(suffix)
        used.add(candidate)
        found.add(candidate)
    found.update(re.findall(r'<a\s+[^>]*(?:id|name)=["\']([^"\']+)["\']', text, re.I))
    return found


def contained(path, root):
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def check_links(path, root, payload=None):
    targets, errors = markdown_links(path.read_text(encoding="utf-8"))
    payload = None if payload is None else {item.resolve() for item in payload}
    for target in dict.fromkeys(targets):
        parsed = urlsplit(html.unescape(target))
        if parsed.scheme or parsed.netloc:
            continue
        local = path if not parsed.path else (root / unquote(parsed.path).lstrip("/")) if parsed.path.startswith("/") else (path.parent / unquote(parsed.path))
        if not contained(local, root):
            errors.append("relative link escapes allowed root")
            continue
        if not local.exists():
            errors.append("relative link target does not exist: " + parsed.path)
            continue
        if payload is not None and local.resolve() not in payload:
            errors.append("local target is absent from installable ZIP: " + parsed.path)
        if parsed.fragment and local.suffix.lower() == ".md":
            fragment = unquote(parsed.fragment)
            if fragment not in heading_anchors(local.read_text(encoding="utf-8")):
                errors.append("heading/custom anchor does not exist: " + fragment)
    return errors


def validate_record(record):
    required = {"date", "guidance_commit", "guidance_version", "variant", "platform",
                "model", "settings", "unknown_reason", "input", "output", "checks", "overall",
                "schema_version", "guidance_sha256", "style_sample_ids"}
    if not isinstance(record, dict) or set(record) != required:
        raise ValueError("evaluation record must have exactly the documented fields")
    if record["schema_version"] != 2:
        raise ValueError("evaluation record schema_version must be 2")
    if not isinstance(record["guidance_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", record["guidance_sha256"]):
        raise ValueError("guidance_sha256 must identify the exact applied instructions")
    sample_ids = record["style_sample_ids"]
    if not isinstance(sample_ids, list) or any(not isinstance(item, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", item) for item in sample_ids) or len(set(sample_ids)) != len(sample_ids):
        raise ValueError("style_sample_ids must be unique, safe identifiers")
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
    if checks["style"]["verdict"] in ("pass", "fail") and not sample_ids:
        raise ValueError("assessing personal style requires actual style sample identifiers")
    values = [check["verdict"] for check in checks.values()]
    expected = "fail" if "fail" in values else "pass" if all(v == "pass" for v in values) else "unassessed"
    if record["overall"] != expected:
        raise ValueError("overall must be fail for any failed axis; pass requires all four passes")


def instruction_bytes(root, record):
    """Read the exact historical instructions, never substituting current files."""
    variant = record["variant"]
    path = {"full": "STYLE.md", "short": "platforms/chatgpt.md", "skill": "skills/writing-style-doc/SKILL.md"}[variant]
    try:
        data = subprocess.check_output(["git", "show", record["guidance_commit"] + ":" + path], cwd=str(root), stderr=subprocess.DEVNULL)
        version = subprocess.check_output(["git", "show", record["guidance_commit"] + ":VERSION"], cwd=str(root), stderr=subprocess.DEVNULL).decode("utf-8").strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("evaluation guidance commit/files unavailable; fetch full history") from exc
    if version != record["guidance_version"]:
        raise ValueError("evaluation guidance version differs from its commit")
    if variant == "full":
        data = data.decode("utf-8").split("\n---\n", 1)[1].strip().encode("utf-8")
    elif variant == "short":
        section = data.decode("utf-8").split("## 짧은 버전", 1)[1]
        match = re.search(r"```text\n(.*?)\n```", section, re.S)
        if not match:
            raise ValueError("historical short instructions are missing")
        data = match.group(1).encode("utf-8")
    return data


def validate_provenance(root, record):
    if hashlib.sha256(instruction_bytes(root, record)).hexdigest() != record["guidance_sha256"]:
        raise ValueError("evaluation guidance hash differs from its commit")
    for sample_id in record["style_sample_ids"]:
        sample = root / "evaluation/samples" / (sample_id + ".md")
        if sample.is_symlink() or not sample.is_file() or not contained(sample, root):
            raise ValueError("personal style sample is unavailable: " + sample_id)


def skill_files(root):
    skill = root / "skills/writing-style-doc"
    references = skill / "references"
    # Checking individual files misses a symlink in any parent directory.
    for directory in (root, root / "skills", skill, references):
        if directory.is_symlink() or not directory.is_dir() or not contained(directory, root):
            raise ValueError("skill payload directories must be real directories within the repository")
    allowed = [skill / "SKILL.md"] + sorted(references.glob("*.md"))
    for path in allowed:
        if path.is_symlink() or not path.is_file() or not contained(path, skill):
            raise ValueError("skill payload must contain regular files within the skill directory")
    for path in allowed:
        errors = check_links(path, skill, payload=allowed)
        if errors:
            raise ValueError(str(path.relative_to(skill)) + ": " + "; ".join(errors))
    return allowed


def validate(root, verify_history=False):
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
            record = json.loads(path.read_text(encoding="utf-8"))
            validate_record(record)
            if verify_history:
                validate_provenance(root, record)
            elif record["style_sample_ids"]:
                for sample_id in record["style_sample_ids"]:
                    if not (root / "evaluation/samples" / (sample_id + ".md")).is_file():
                        raise ValueError("personal style sample unavailable")
        except (ValueError, TypeError) as exc:
            raise ValueError(path.name + ": " + str(exc)) from exc
    skill_files(root)


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-history", action="store_true", help="Verify exact guidance hashes and versions against Git history")
    args = parser.parse_args()
    try:
        validate(ROOT, verify_history=args.verify_history)
    except (ValueError, IndexError, OSError, SyntaxError, TypeError) as exc:
        print("Validation failed: " + str(exc), file=sys.stderr)
        return 1
    print("Repository checks passed; " + ("evaluation source history verified" if args.verify_history else "evaluation history not checked (use --verify-history in a full Git checkout)") + ". Semantic quality and external URLs assessed separately.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
