#!/usr/bin/env python3
"""Print reproducible metadata for instructions stored at a historical commit."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from validate_repo import instruction_bytes


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--variant', choices=('full', 'short', 'skill'), required=True)
    args = parser.parse_args()
    try:
        commit = subprocess.check_output(['git', 'rev-parse', args.commit + '^{commit}'], cwd=str(root), text=True, stderr=subprocess.DEVNULL).strip()
        version = subprocess.check_output(['git', 'show', commit + ':VERSION'], cwd=str(root), text=True, stderr=subprocess.DEVNULL).strip()
        record = {'guidance_commit': commit, 'guidance_version': version, 'variant': args.variant}
        record['guidance_sha256'] = hashlib.sha256(instruction_bytes(root, record)).hexdigest()
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        parser.error('Cannot read exact guidance from Git history: ' + str(exc))
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
