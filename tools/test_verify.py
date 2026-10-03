"""Contract result semantics and complete verification lifetimes."""

from contextlib import contextmanager
import hashlib
from pathlib import Path
import tempfile
import unittest

from create import create
from runtime import Commands, ExecutionError, Result
from verify import check_attack, check_solution, discover, verify_problem


class FakeDocker:
    def __init__(self, *, bad_attack=False, bad_check=False, missing_cli=False):
        self.commands = Commands()
        self.events = []
        self.bad_attack = bad_attack
        self.bad_check = bad_check
        self.missing_cli = missing_cli

    def project(self, root, directory, metadata, flag, *, patched=False):
        self.flag = flag
        self.events.append(('resolve', patched))
        docker = self
        class Target:
            @contextmanager
            def running(self):
                docker.events.append(('start', patched))
                try:
                    yield self
                finally:
                    docker.events.append(('stop', patched))
            def network(self, key):
                return 'patched' if patched else 'vulnerable'
        return Target()

    def tool(self, directory, metadata, network, image, args):
        self.events.append(('tool', network, image, args))
        if network == 'none' and args[0] == 'sh':
            return Result(1 if self.missing_cli else 0)
        if network == 'vulnerable':
            return Result(0, ' \n' + self.flag + '\n')
        if args == ['check']:
            return Result(1 if self.bad_check else 0)
        if self.bad_attack:
            return Result(3, self.flag)
        return Result(3, 'denied')


class VerifyTests(unittest.TestCase):
    def test_file_flag_matches_trimmed_utf8_and_requires_success(self):
        flag = 'pwnden{한글}'
        digest = hashlib.sha256(flag.encode('utf-8')).hexdigest()
        check_solution(Result(0, '\n' + flag + '\t'), digest.upper(), digest=True)
        for result in [Result(1, flag), Result(0, flag + 'diagnostic'), Result(0, '')]:
            with self.subTest(result=result), self.assertRaises(ExecutionError):
                check_solution(result, digest, digest=True)

    def test_generated_flags_compare_whole_output(self):
        check_solution(Result(0, ' pwnden{current}\n'), 'pwnden{current}')
        for result in [Result(0, 'pwnden{old}'), Result(1, 'pwnden{current}')]:
            with self.subTest(result=result), self.assertRaises(ExecutionError):
                check_solution(result, 'pwnden{current}')

    def test_patch_denial_differs_from_failure_and_flag_recovery(self):
        for code in [0, 3]:
            check_attack(Result(code, 'denied'), 'flag', 3)
        for code in [1, 2, 4, 124, 125, 137, -9]:
            with self.subTest(code=code), self.assertRaises(ExecutionError):
                check_attack(Result(code, 'connection failed'), 'flag', 3)
        for code in [0, 3]:
            with self.subTest(code=code), self.assertRaises(ExecutionError):
                check_attack(Result(code, ' flag\n'), 'flag', 3)

    def test_complete_patch_lifecycle_and_override_image(self):
        docker = FakeDocker()
        metadata = {'slug': 'sample', 'compose': 'compose.yaml',
                    'solve': {'network': 'default', 'image': 'solve-image', 'command': ['solve']},
                    'patched': {'image': 'check-image', 'check': ['check']}}
        verify_problem(docker, Path('/root'), Path('/root/challenges/sample'), metadata,
                       {'attack_rejected_exit': 3})
        self.assertEqual(docker.events[:3], [('resolve', False), ('resolve', True), ('start', False)])
        self.assertEqual(docker.events[-2:], [('stop', True), ('stop', False)])
        self.assertRegex(docker.flag, r'^pwnden\{[0-9a-f]{32}\}$')
        self.assertIn(('tool', 'patched', 'check-image', ['check']), docker.events)

    def test_patch_failure_cleans_both_targets(self):
        metadata = {'slug': 'sample', 'compose': 'compose.yaml',
                    'solve': {'network': 'default', 'image': 'image', 'command': ['solve']},
                    'patched': {'check': ['check']}}
        for options in [{'bad_attack': True}, {'bad_check': True}]:
            docker = FakeDocker(**options)
            with self.subTest(options=options), self.assertRaises(ExecutionError):
                verify_problem(docker, Path('/root'), Path('/root/sample'), metadata,
                               {'attack_rejected_exit': 3})
            self.assertEqual(docker.events[-2:], [('stop', True), ('stop', False)])

    def test_cli_checked_offline_before_target_start(self):
        metadata = {'slug': 'sample', 'compose': 'compose.yaml',
                    'player': {'cli': ['nmap', 'ncat']},
                    'solve': {'network': 'default', 'image': 'image', 'command': ['solve']}}
        docker = FakeDocker()
        verify_problem(docker, Path('/root'), Path('/root/sample'), metadata, {'attack_rejected_exit': 3})
        probe = docker.events[0]
        self.assertEqual(probe[:3], ('tool', 'none', 'image'))
        self.assertEqual(probe[3][-3:], ['pwnden-cli-check', 'nmap', 'ncat'])
        docker = FakeDocker(missing_cli=True)
        with self.assertRaisesRegex(ExecutionError, 'CLI is unavailable'):
            verify_problem(docker, Path('/root'), Path('/root/sample'), metadata, {'attack_rejected_exit': 3})
        self.assertEqual(len(docker.events), 1)

    def test_discovery_defaults_selection_and_contract_version(self):
        with tempfile.TemporaryDirectory(prefix='pwnden-author-discovery-') as tmp:
            root = Path(tmp)
            (root / 'contract.toml').write_text('version=6\nsolve_network="default"\nsolve_timeout_seconds=60\nattack_rejected_exit=3\n')
            create(root, 'one', kind='file', category='rev')
            create(root, 'two', kind='service', category='web')
            definition, records = discover(root, ['two'])
            self.assertEqual([metadata['slug'] for _, metadata in records], ['two'])
            self.assertEqual(records[0][1]['solve']['timeout_seconds'], 60)
            self.assertFalse(records[0][1]['solve']['writable'])
            with self.assertRaisesRegex(ValueError, 'unknown challenges'):
                discover(root, ['missing'])
            (root / 'contract.toml').write_text('version=7\nsolve_network="default"\nsolve_timeout_seconds=60\nattack_rejected_exit=3\n')
            with self.assertRaisesRegex(ValueError, 'supports contract version 6'):
                discover(root)


if __name__ == '__main__':
    unittest.main()
