#!/usr/bin/env python3
"""Package only the installable skill after checking generated instructions."""
import argparse
from pathlib import Path
import subprocess
import sys
from zipfile import ZIP_DEFLATED, ZipFile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("writing-style-doc.zip"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable, str(root / "scripts/sync_style.py"), "--check"], check=True)
    skill = root / "skills/writing-style-doc"
    files = sorted(p for p in skill.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    if args.output.resolve() == skill.resolve() or skill.resolve() in args.output.resolve().parents:
        parser.error("Output ZIP must be outside the skill directory")
    with ZipFile(args.output, "w", ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(skill.parent).as_posix())
    print(f"Created {args.output} ({len(files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
