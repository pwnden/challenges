"""Regression checks for author-owned manifest validation."""

from pathlib import Path
import tempfile
import unittest

from validate import InvalidChallenge, load_contract, validate_manifest


CONTRACT = "version = 1\nsolve_network = 'default'\nsolve_timeout_seconds = 60\nattack_rejected_exit = 3\n"
FILE = """schema = 1
slug = "sample"
title = "Sample"
category = "rev"
files = ["data.bin"]
[flag]
mode = "sha256"
sha256 = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
[solve]
image = "python:3.13.15-slim"
command = ["python3", "solve.py"]
"""


class ValidateTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='pwnden-format-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.directory = self.root / 'challenges' / 'sample'
        self.directory.mkdir(parents=True)
        (self.root / 'contract.toml').write_text(CONTRACT)
        (self.directory / 'data.bin').write_bytes(b'data')
        self.definition = load_contract(self.root)

    def check(self, metadata):
        manifest = self.directory / 'challenge.toml'
        manifest.write_text(metadata)
        return validate_manifest(self.root, manifest, self.definition)

    def test_file_with_defaults(self):
        self.assertEqual(self.check(FILE)['slug'], 'sample')

    def test_invalid_metadata(self):
        cases = {
            'unknown field': FILE.replace('schema = 1', 'schema = 1\nunknown = true'),
            'nested unknown field': FILE + 'extra = true\n',
            'missing title': FILE.replace('title = "Sample"\n', ''),
            'title type': FILE.replace('title = "Sample"', 'title = 123'),
            'slug mismatch': FILE.replace('slug = "sample"', 'slug = "other"'),
            'version mismatch': FILE.replace('schema = 1', 'schema = 2'),
            'boolean version': FILE.replace('schema = 1', 'schema = true'),
            'category': FILE.replace('category = "rev"', 'category = "invalid"'),
            'hash': FILE.replace('a' * 64, 'not-a-digest'),
            'image option': FILE.replace('python:3.13.15-slim', '--help'),
            'empty command': FILE.replace('["python3", "solve.py"]', '[]'),
            'missing file': FILE.replace('data.bin', 'missing.bin'),
            'outside file': FILE.replace('data.bin', '../../../outside.bin'),
            'nonportable file': FILE.replace('data.bin', 'C:/outside.bin'),
            'timeout': FILE + 'timeout_seconds = 0\n',
            'writable type': FILE + 'writable = 1\n',
        }
        for name, metadata in cases.items():
            with self.subTest(name=name), self.assertRaises(InvalidChallenge):
                self.check(metadata)

    def test_service_and_patch(self):
        (self.directory / 'compose.yaml').write_text('services: {}')
        (self.directory / 'patched.yaml').write_text('services: {}')
        service = FILE.replace('category = "rev"', 'category = "web"\ncompose = "compose.yaml"').replace('mode = "sha256"', 'mode = "generated"')
        service = service.replace('sha256 = "' + 'a' * 64 + '"\n', '')
        service += """[[endpoints]]
name = "web"
service = "app"
port = 8000
protocol = "http"
[patched]
compose = "patched.yaml"
check = ["python3", "test.py"]
"""
        self.check(service)
        self.check(service + 'image = ""\n')
        for invalid in [service.replace('port = 8000', 'port = 65536'), service.replace('protocol = "http"', 'protocol = "udp"'), service + 'image = "--help"\n']:
            with self.subTest(metadata=invalid), self.assertRaises(InvalidChallenge):
                self.check(invalid)

    def test_symlink_outside_repository(self):
        outside = tempfile.TemporaryDirectory(prefix='pwnden-outside-')
        self.addCleanup(outside.cleanup)
        target = Path(outside.name) / 'data.bin'
        target.write_bytes(b'data')
        link = self.directory / 'linked.bin'
        try:
            link.symlink_to(target)
        except OSError as error:
            self.skipTest(f'symlink unavailable: {error}')
        with self.assertRaisesRegex(InvalidChallenge, 'outside'):
            self.check(FILE.replace('data.bin', 'linked.bin'))

    def test_invalid_contract(self):
        for definition in [CONTRACT + 'extra = true\n', CONTRACT.replace('version = 1', 'version = 0'), CONTRACT.replace('solve_timeout_seconds = 60', 'solve_timeout_seconds = -1'), CONTRACT.replace('attack_rejected_exit = 3', 'attack_rejected_exit = 125')]:
            (self.root / 'contract.toml').write_text(definition)
            with self.subTest(definition=definition), self.assertRaises(InvalidChallenge):
                load_contract(self.root)


if __name__ == '__main__':
    unittest.main()
