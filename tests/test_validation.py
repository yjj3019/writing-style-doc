import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from package_skill import package
from validate_repo import ROOT, check_links, validate_record, skill_files, validate_provenance


class ValidationTests(unittest.TestCase):
    def record(self):
        return {'schema_version': 2, 'guidance_sha256': 'b' * 64, 'style_sample_ids': ['unit-fixture'], 'date': '2026-10-02', 'guidance_commit': 'a' * 40,
                'guidance_version': '1.0.0', 'variant': 'skill', 'platform': 'Codex',
                'model': None, 'settings': None, 'unknown_reason': 'not exposed',
                'input': '가상 입력', 'output': '가상 출력',
                'checks': {k: {'verdict': 'pass', 'evidence': '확인한 출력'}
                           for k in ('facts', 'request', 'style', 'readability')},
                'overall': 'pass'}

    def test_failure_cannot_be_overall_pass(self):
        r = self.record()
        r['checks']['facts']['verdict'] = 'fail'
        with self.assertRaises(ValueError):
            validate_record(r)
        r['overall'] = 'fail'
        validate_record(r)

    def test_style_unknown_cannot_be_certified(self):
        r = self.record()
        r['checks']['style'] = {'verdict': 'unassessed', 'evidence': 'No real samples'}
        with self.assertRaises(ValueError):
            validate_record(r)
        r['overall'] = 'unassessed'
        validate_record(r)

    def test_metadata_and_evidence_required(self):
        base = self.record()
        for mutate in (lambda r: r.update(unknown_reason=''),
                       lambda r: r.update(guidance_commit='main'),
                       lambda r: r['checks']['request'].update(evidence='')):
            with self.subTest(mutate=mutate):
                r = copy.deepcopy(base)
                mutate(r)
                with self.assertRaises(ValueError):
                    validate_record(r)

    def test_links_ignore_code_but_reject_missing_and_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / 'a.md'
            (root / 'valid.md').write_text('valid')
            page.write_text('```md\n[x](not-real.md)\n```\n`[x](no.md)`\n[x](valid.md)\n[x](https://example.com/a)\n')
            self.assertEqual(check_links(page, root), [])
            page.write_text('[x](missing.md)\n[x](../escape.md)')
            self.assertEqual(len(check_links(page, root)), 2)

    def test_reference_link_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / 'a.md'
            page.write_text('[guide][ref]\n\n[ref]: missing.md\n')
            self.assertEqual(len(check_links(page, root)), 1)

    def test_archive_reproducible_and_payload_exact(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'skill.zip'
            first = package(ROOT, out)
            data = out.read_bytes()
            second = package(ROOT, out)
            self.assertEqual(data, out.read_bytes())
            self.assertEqual(first, second)
            with ZipFile(out) as archive:
                self.assertIsNone(archive.testzip())
                self.assertEqual(set(archive.namelist()), {item['path'] for item in first['files']})
                for item in first['files']:
                    self.assertEqual(hashlib.sha256(archive.read(item['path'])).hexdigest(), item['sha256'])
                self.assertIn('writing-style-doc/SKILL.md', archive.namelist())
                self.assertFalse(any('evaluation' in name or name.startswith('/') or '..' in name.split('/') for name in archive.namelist()))
            self.assertEqual(first['archive_sha256'], hashlib.sha256(data).hexdigest())
            self.assertEqual(json.loads(out.with_suffix('.manifest.json').read_text()), first)

    def test_package_rejects_installable_directory(self):
        with self.assertRaises(ValueError):
            package(ROOT, ROOT / 'skills/writing-style-doc/unsafe.zip')

    def test_package_rejects_symlink_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'copy'
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', 'dist', '__pycache__'))
            page = root / 'skills/writing-style-doc/references/examples.md'
            data = page.read_text()
            page.unlink()
            elsewhere = Path(tmp) / 'external.md'
            elsewhere.write_text(data)
            page.symlink_to(elsewhere)
            with self.assertRaises(ValueError):
                package(root, Path(tmp) / 'skill.zip')

    def test_undefined_and_collapsed_reference_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / 'a.md'
            page.write_text('[guide][unknown]\n[missing][]\n')
            self.assertEqual(len(check_links(page, root)), 2)
            page.write_text('[guide][]\n[guide]\n[guide]: a.md\n')
            self.assertEqual(check_links(page, root), [])

    def test_heading_anchors_and_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / 'a.md'
            page.write_text('## 한국어 **설정**\n## 한국어 **설정**\n<a name="custom"></a>\n[x](#한국어-설정)\n[x](#한국어-설정-1)\n[x](#custom)\n[x](#missing)\n', encoding='utf-8')
            errors = check_links(page, root)
            self.assertEqual(errors, ['heading/custom anchor does not exist: missing'])

    def test_cross_file_anchor_and_parenthesized_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'b(x).md').write_text('## Valid\n')
            page = root / 'a.md'
            page.write_text('[x](b(x).md#valid)\n[x](b(x).md#missing)\n')
            self.assertEqual(check_links(page, root), ['heading/custom anchor does not exist: missing'])

    def test_code_and_escaped_brackets_are_not_reference_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / 'a.md'
            page.write_text('~~~md\n[x][unknown]\n~~~\n`[x][unknown]`\n\\[x][unknown]\n')
            self.assertEqual(check_links(page, root), [])

    def test_payload_rejects_reference_to_repo_only_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / 'skills/writing-style-doc'
            (skill / 'references').mkdir(parents=True)
            (root / 'README.md').write_text('Readme')
            (skill / 'SKILL.md').write_text('[x](../../README.md)')
            with self.assertRaises(ValueError):
                skill_files(root)

    def test_payload_rejects_existing_but_unpacked_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / 'skills/writing-style-doc'
            (skill / 'references/nested').mkdir(parents=True)
            (skill / 'references/nested/a.md').write_text('Nested')
            (skill / 'SKILL.md').write_text('[x](references/nested/a.md)')
            with self.assertRaises(ValueError):
                skill_files(root)

    def test_symlink_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / 'skills/writing-style-doc'
            skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_text('Skill')
            real = root / 'elsewhere'
            real.mkdir()
            (real / 'a.md').write_text('External')
            (skill / 'references').symlink_to(real, target_is_directory=True)
            with self.assertRaises(ValueError):
                skill_files(root)

    def test_personal_style_needs_sample_ids(self):
        record = self.record()
        record['style_sample_ids'] = []
        with self.assertRaises(ValueError):
            validate_record(record)

    def test_historical_guidance_hash_mismatch(self):
        # Actual history comes from a tiny isolated fixture, not the user's repository.
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / 'skills/writing-style-doc'
            skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_bytes(b'skill contents\n')
            (root / 'VERSION').write_text('1.0.0\n')
            def git(*args):
                return subprocess.check_output(['git'] + list(args), cwd=str(root), stderr=subprocess.DEVNULL, text=True).strip()
            git('init')
            git('add', '.')
            git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'fixture')
            record = self.record()
            record['guidance_commit'] = git('rev-parse', 'HEAD')
            record['style_sample_ids'] = []
            record['checks']['style'] = {'verdict': 'unassessed', 'evidence': 'No personal samples'}
            record['overall'] = 'unassessed'
            with self.assertRaises(ValueError):
                validate_provenance(root, record)
            record['guidance_sha256'] = hashlib.sha256(b'skill contents\n').hexdigest()
            validate_provenance(root, record)
            record['guidance_version'] = '1.0.1'
            with self.assertRaises(ValueError):
                validate_provenance(root, record)


if __name__ == '__main__':
    unittest.main()
