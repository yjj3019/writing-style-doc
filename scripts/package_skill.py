#!/usr/bin/env python3
"""Create a reproducible skill ZIP and external provenance/checksum files."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from sync_style import read_version
from validate_repo import skill_files, validate


def package(root, output):
    validate(root)
    skill = root / "skills/writing-style-doc"
    output = output.resolve()
    if output == skill.resolve() or skill.resolve() in output.parents:
        raise ValueError("Output ZIP must be outside the skill directory")
    if output.suffix != ".zip":
        raise ValueError("Output must have a .zip extension")
    output.parent.mkdir(parents=True, exist_ok=True)
    entries = []
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for path in skill_files(root):
            name = path.relative_to(skill.parent).as_posix()
            data = path.read_bytes()
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
            entries.append({"path": name, "sha256": hashlib.sha256(data).hexdigest()})
    with ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError("Generated archive failed integrity verification")
    # Do not attribute builds outside a Git checkout to an unrelated parent checkout.
    commit = None
    if (root / ".git").exists():
        try:
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(root), text=True, stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError):
            pass
    try:
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=str(root), text=True, stderr=subprocess.DEVNULL).strip()) if commit else None
    except (OSError, subprocess.CalledProcessError):
        dirty = None
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    manifest = {"version": read_version(root), "source_commit": commit, "source_dirty": dirty,
                "archive": output.name, "archive_sha256": digest, "files": entries}
    output.with_suffix(".manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output.with_suffix(".sha256").write_text(digest + "  " + output.name + "\n", encoding="utf-8")
    return manifest


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or root / "dist" / ("writing-style-doc-" + read_version(root) + ".zip")
    try:
        result = package(root, output)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print("Created " + str(output) + " (" + str(len(result["files"])) + " files); manifest and SHA256 saved alongside")


if __name__ == "__main__":
    main()
