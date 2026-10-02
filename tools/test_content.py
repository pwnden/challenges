"""Shared prerequisite compilation remains reproducible and repository-contained."""
from pathlib import Path
import tempfile
import unittest

from content import check_brief, compile_brief
from create import create
from validate import load_contract, validate_manifest

ROOT = Path(__file__).resolve().parents[1]


class ContentTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        (self.root / 'contract.toml').write_bytes((ROOT / 'contract.toml').read_bytes())
        (self.root / 'knowledge').mkdir()
        (self.root / 'knowledge' / 'cookies.md').write_text('# 쿠키\n\n공통 설명 **강조**.\n', encoding='utf-8')

    def test_creation_compiles_and_shared_change_requires_refresh(self):
        destination, files = create(self.root, 'first', kind='file', category='crypto', concepts=['cookies'])
        self.assertIn('BRIEFING.md', files)
        self.assertIn('../../knowledge/cookies.md', (destination / 'AUTHORING.md').read_text())
        rendered = (destination / 'README.md').read_text()
        self.assertIn('::knowledge\n\n### 쿠키', rendered)
        self.assertIn('공통 설명 **강조**.', rendered)
        self.assertNotIn('concepts=', rendered)
        check_brief(self.root, destination)
        concept = self.root / 'knowledge/cookies.md'
        concept.write_text(concept.read_text() + '\n보완 설명.\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'refresh prerequisites'):
            validate_manifest(self.root, destination / 'challenge.toml', load_contract(self.root))
        (destination / 'README.md').write_text(compile_brief(self.root, destination / 'BRIEFING.md'))
        validate_manifest(self.root, destination / 'challenge.toml', load_contract(self.root))

    def test_unknown_duplicate_and_path_ids_preserve_existing_content(self):
        for concepts in [['unknown'], ['cookies', 'cookies'], ['../cookies']]:
            with self.subTest(concepts=concepts), self.assertRaises(ValueError):
                create(self.root, 'invalid', kind='file', category='crypto', concepts=concepts)
            self.assertFalse((self.root / 'challenges/invalid').exists())
        self.assertIn('공통 설명', (self.root / 'knowledge/cookies.md').read_text())

    def test_outside_symlink_and_invalid_include_are_rejected(self):
        destination = self.root / 'brief.md'
        destination.write_text('::knowledge{concepts="cookies"}\n::\n', encoding='utf-8')
        with tempfile.TemporaryDirectory() as name:
            outside = Path(name) / 'outside.md'
            outside.write_text('# Outside\n\nprivate\n')
            (self.root / 'knowledge/cookies.md').unlink()
            (self.root / 'knowledge/cookies.md').symlink_to(outside)
            with self.assertRaisesRegex(ValueError, 'inside the repository'):
                compile_brief(self.root, destination)
        destination.write_text('::knowledge{concepts="cookies"}\nnonempty\n::\n')
        with self.assertRaisesRegex(ValueError, 'empty block'):
            compile_brief(self.root, destination)


if __name__ == '__main__':
    unittest.main()
