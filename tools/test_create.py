"""Check generated contracts, safe creation and unfinished authoring behavior."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from create import create, scaffold
from validate import InvalidChallenge, load_contract, validate_manifest


REPOSITORY = Path(__file__).resolve().parents[1]


class CreateTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='pwnden-create-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        (self.root / 'contract.toml').write_bytes((REPOSITORY / 'contract.toml').read_bytes())
        (self.root / 'knowledge').mkdir()
        (self.root / 'knowledge/catalog.toml').write_text('concepts = []\n')

    def metadata(self, destination):
        return validate_manifest(self.root, destination / 'challenge.toml', load_contract(self.root))

    def test_file_service_and_optional_patch(self):
        for slug, kind, category, patched in [('file-test', 'file', 'rev', False), ('web-test', 'service', 'web', False), ('patched-test', 'service', 'web', True)]:
            with self.subTest(kind=kind, patched=patched):
                destination, files = create(self.root, slug, kind=kind, category=category, patched=patched)
                metadata = self.metadata(destination)
                self.assertEqual(metadata['slug'], slug)
                self.assertEqual(metadata['difficulty'], 1)
                self.assertIn('AUTHORING.md', files)
                authoring = (destination / 'AUTHORING.md').read_text(encoding='utf-8')
                self.assertIn('선수 지식과 학습 내용', authoring)
                self.assertIn('선언한 값: 1', authoring)
                self.assertNotIn('{{', authoring)
                self.assertEqual(metadata['player']['tools'], ['web'] if kind == 'service' else ['files', 'terminal'])
                self.assertEqual(metadata['player']['cli'], [])
                self.assertEqual(metadata['content']['hints'], [])
                self.assertFalse((destination / 'hints').exists())
                brief = (destination / 'README.md').read_text(encoding='utf-8')
                self.assertIn('::resources', brief)
                self.assertNotIn('::knowledge', brief)
                self.assertEqual('patched' in metadata, patched)
                self.assertEqual('compose' in metadata, kind == 'service')
                self.assertNotIn('network', metadata['solve'])
                self.assertNotIn('timeout_seconds', metadata['solve'])
                self.assertNotIn('writable', metadata['solve'])
                self.assertTrue(all((destination / name).is_file() for name in files))
                self.assertIn('@sha256:', metadata['solve']['image'])
                for name in files:
                    if name.endswith('.py'):
                        compile((destination / name).read_text(encoding='utf-8'), name, 'exec')
                for name in ['solve/solve.py'] + (['patched/test.py'] if patched else []):
                    result = subprocess.run([sys.executable, '-B', str(destination / name)], capture_output=True, text=True, check=False)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse(result.stdout)
                    self.assertIn('TODO', result.stderr)

    def test_title_roundtrip_and_hint_limits(self):
        title = '문제 "A"\n이모지 🧩 {{IMAGE}}'
        destination, _ = create(self.root, 'custom', kind='file', category='misc', title=title, hints=0)
        metadata = self.metadata(destination)
        self.assertEqual(metadata['title'], title)
        self.assertEqual(metadata['content']['hints'], [])
        self.assertFalse((destination / 'hints').exists())
        destination, _ = create(self.root, 'ten-hints', kind='file', category='crypto', hints=10, difficulty=5)
        self.assertEqual(len(self.metadata(destination)['content']['hints']), 10)
        self.assertEqual(self.metadata(destination)['difficulty'], 5)
        self.assertIn('선언한 값: 5', (destination / 'AUTHORING.md').read_text(encoding='utf-8'))

    def test_dry_run_and_invalid_options_write_nothing(self):
        create(self.root, 'preview', kind='service', category='web', dry_run=True)
        self.assertFalse((self.root / 'challenges').exists())
        invalid = [
            {'slug': '../escape'}, {'slug': 'Upper'}, {'slug': 'a' * 41}, {'slug': 'con'},
            {'slug': 'lpt1'}, {'slug': 'two--hyphens'}, {'category': 'unknown'},
            {'kind': 'unknown'}, {'hints': -1}, {'hints': 11}, {'hints': True},
            {'title': '  '}, {'patched': True}, {'toolbox': '--help'},
            {'difficulty': 0}, {'difficulty': 6}, {'difficulty': True}, {'difficulty': '2'},
            {'toolbox': 'python:3\nRUN something'},
        ]
        for options in invalid:
            with self.subTest(options=options), self.assertRaises(InvalidChallenge):
                scaffold(self.root, **({'slug': 'sample', 'kind': 'file', 'category': 'misc'} | options))
            self.assertFalse((self.root / 'challenges').exists())

    def test_existing_work_and_links_are_preserved(self):
        destination = self.root / 'challenges' / 'existing'
        destination.mkdir(parents=True)
        marker = destination / 'my-work.txt'
        marker.write_text('keep this', encoding='utf-8')
        with self.assertRaisesRegex(InvalidChallenge, 'already exists'):
            create(self.root, 'existing', kind='file', category='rev')
        self.assertEqual(list(destination.iterdir()), [marker])
        self.assertEqual(marker.read_text(encoding='utf-8'), 'keep this')
        link = destination.parent / 'dangling'
        try:
            link.symlink_to(destination.parent / 'absent', target_is_directory=True)
        except OSError as error:
            self.skipTest(f'symlink unavailable: {error}')
        with self.assertRaisesRegex(InvalidChallenge, 'already exists'):
            create(self.root, 'dangling', kind='file', category='rev')
        self.assertTrue(link.is_symlink())

    def test_outside_parent_and_unknown_contract_are_rejected(self):
        temporary = tempfile.TemporaryDirectory(prefix='pwnden-create-outside-')
        self.addCleanup(temporary.cleanup)
        outside = Path(temporary.name)
        parent = self.root / 'challenges'
        try:
            parent.symlink_to(outside, target_is_directory=True)
        except OSError as error:
            self.skipTest(f'symlink unavailable: {error}')
        with self.assertRaisesRegex(InvalidChallenge, 'outside'):
            create(self.root, 'sample', kind='file', category='rev')
        self.assertEqual(list(outside.iterdir()), [])
        parent.unlink()
        contract = self.root / 'contract.toml'
        contract.write_text(contract.read_text().replace('version = 7', 'version = 8'))
        with self.assertRaisesRegex(InvalidChallenge, 'update templates'):
            create(self.root, 'sample', kind='file', category='rev')
        self.assertFalse(parent.exists())

    def test_declared_network_is_used_by_service(self):
        contract = self.root / 'contract.toml'
        contract.write_text(contract.read_text().replace('solve_network = "default"', 'solve_network = "exercise-net"'))
        destination, _ = create(self.root, 'network-test', kind='service', category='web')
        self.assertIn('networks: ["exercise-net"]', (destination / 'compose.yaml').read_text())
        self.assertNotIn('network', self.metadata(destination)['solve'])

    def test_primary_cli_and_terminal_selection(self):
        destination, _ = create(self.root, 'cli-service', kind='service', category='web', cli=['curl', 'jq'])
        self.assertEqual(self.metadata(destination)['player'], {'tools': ['web', 'terminal'], 'cli': ['curl', 'jq']})
        for names in [['Nmap'], ['nmap -sT'], ['curl', 'curl']]:
            with self.subTest(names=names), self.assertRaises(InvalidChallenge):
                create(self.root, 'invalid-cli', kind='file', category='misc', cli=names)
        self.assertFalse((self.root / 'challenges' / 'invalid-cli').exists())

    def test_failed_generation_cleans_only_its_new_directory(self):
        destination = self.root / 'challenges' / 'failed'
        sibling = destination.parent / 'preserved'
        sibling.mkdir(parents=True)
        with patch('create.validate_manifest', side_effect=InvalidChallenge('bad template')):
            with self.assertRaisesRegex(InvalidChallenge, 'bad template'):
                create(self.root, 'failed', kind='file', category='rev')
        self.assertFalse(destination.exists())
        self.assertTrue(sibling.is_dir())

    def test_concurrent_creation_has_one_owner(self):
        (self.root / 'challenges').mkdir()
        def attempt(_):
            try:
                create(self.root, 'shared', kind='file', category='rev')
                return True
            except (OSError, InvalidChallenge):
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(attempt, range(2))), [False, True])
        self.metadata(self.root / 'challenges' / 'shared')

    def test_cli_from_another_directory(self):
        command = [sys.executable, '-B', str(REPOSITORY / 'tools' / 'create.py'), 'cli-test', '--kind', 'file', '--category', 'rev', '--cli', 'python3', '--cli', 'sha256sum', '--repo', str(self.root)]
        preview = subprocess.run(command + ['--dry-run'], cwd=self.root, capture_output=True, text=True, check=False)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertIn('Would create challenges/cli-test', preview.stdout)
        self.assertFalse((self.root / 'challenges').exists())
        created = subprocess.run(command, cwd=self.root, capture_output=True, text=True, check=False)
        self.assertEqual(created.returncode, 0, created.stderr)
        self.assertIn('Format validation passed', created.stdout)
        self.assertEqual(self.metadata(self.root / 'challenges' / 'cli-test')['player']['cli'], ['python3', 'sha256sum'])
        default = subprocess.run(command[:-2] + ['--dry-run'], cwd=self.root, capture_output=True, text=True, check=False)
        self.assertEqual(default.returncode, 0, default.stderr)
        self.assertIn('Would create challenges/cli-test', default.stdout)


if __name__ == '__main__':
    unittest.main()
