"""Immutable publication input, clean-tree gate and failed-gate non-publication."""

import io
from pathlib import Path
from contextlib import redirect_stdout
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import Mock

from publish import extract_snapshot, gate_snapshot, publish
from runtime import ExecutionError, Result
from validate import InvalidChallenge


class PublishTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='pwnden-publish-test-')
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / 'challenges'
        self.root.mkdir()
        self.remote = Path(tmp.name) / 'published.git'
        subprocess.run(['git', 'init', '--bare', str(self.remote)], check=True, capture_output=True)
        self.git('init', '--initial-branch=main')
        self.git('config', 'user.name', 'Author test')
        self.git('config', 'user.email', 'author@example.invalid')
        # Fixture repositories use their own hooks and need no personal signing key.
        self.git('config', 'core.hooksPath', '.git/hooks')
        self.git('config', 'commit.gpgsign', 'false')
        self.git('remote', 'add', 'origin', str(self.remote))
        (self.root / '.gitignore').write_text('.authoring/\nignored\n')
        (self.root / 'data').write_text('committed data')
        self.git('add', '.')
        self.git('commit', '-m', 'test(publish): initialize fixture')
        self.revision = self.git('rev-parse', 'HEAD').strip()

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, check=True, capture_output=True, text=True).stdout

    def remote_revision(self):
        return subprocess.run(['git', '--git-dir', str(self.remote), 'rev-parse', '--verify', 'refs/heads/main'],
                              capture_output=True, text=True)

    def test_pushes_only_verified_commit_without_ignored_files(self):
        (self.root / 'ignored').write_text('local content')
        seen = []
        def gate(snapshot, commands, timeout):
            seen.append(snapshot)
            self.assertEqual((snapshot / 'data').read_text(), 'committed data')
            self.assertFalse((snapshot / 'ignored').exists())
            self.assertFalse((snapshot / '.git').exists())
        self.assertEqual(publish(self.root, gate=gate), self.revision)
        self.assertEqual(self.remote_revision().stdout.strip(), self.revision)
        self.assertFalse(seen[0].exists())

    def test_check_and_failed_gate_do_not_publish(self):
        publish(self.root, check=True, gate=lambda *args: None)
        self.assertNotEqual(self.remote_revision().returncode, 0)
        def fail(*args):
            raise ExecutionError('verification failed')
        with self.assertRaisesRegex(ExecutionError, 'verification failed'):
            publish(self.root, gate=fail)
        self.assertNotEqual(self.remote_revision().returncode, 0)
        self.assertEqual([p.name for p in (self.root / '.authoring').iterdir()], ['publish.lock'])

    def test_overlapping_check_is_rejected_and_lock_released_after_failure(self):
        def overlap(*args):
            with self.assertRaisesRegex(InvalidChallenge, 'another publication check'):
                publish(self.root, gate=lambda *args: self.fail('must not run concurrently'))
            raise ExecutionError('failed gate')
        with self.assertRaisesRegex(ExecutionError, 'failed gate'):
            publish(self.root, gate=overlap)
        self.assertNotEqual(self.remote_revision().returncode, 0)
        publish(self.root, check=True, gate=lambda *args: None)
        self.assertNotEqual(self.remote_revision().returncode, 0)

    def test_gate_reports_failure_stage_and_stops_following_checks(self):
        commands = Mock()
        commands.redact.side_effect = lambda message: message
        commands.run.side_effect = [Result(0, 'quality passed\n'), ExecutionError('regression broke')]
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaisesRegex(ExecutionError, r'\[2/5\] Author-tool regressions: failed'):
            gate_snapshot(self.root, commands, 123)
        self.assertIn('[1/5] Quality evidence: passed', output.getvalue())
        self.assertEqual(commands.run.call_count, 2)
        self.assertEqual(commands.run.call_args.kwargs['progress'], '[2/5] Author-tool regressions')

    def test_dirty_tree_and_edit_during_verification_block_publication(self):
        (self.root / 'data').write_text('edited')
        with self.assertRaisesRegex(InvalidChallenge, 'worktree must be clean'):
            publish(self.root, gate=lambda *args: self.fail('must not verify'))
        self.git('restore', 'data')
        def edit(*args):
            (self.root / 'data').write_text('changed during verification')
        with self.assertRaisesRegex(InvalidChallenge, 'worktree must be clean'):
            publish(self.root, gate=edit)
        self.assertNotEqual(self.remote_revision().returncode, 0)

    def test_head_change_during_verification_blocks_publication(self):
        def commit(*args):
            self.git('commit', '--allow-empty', '-m', 'test(publish): change verified revision')
        with self.assertRaisesRegex(InvalidChallenge, 'changed during verification'):
            publish(self.root, gate=commit)
        self.assertNotEqual(self.remote_revision().returncode, 0)

    def test_archive_rejects_escaping_links_and_paths(self):
        for name, target in [('../outside', None), ('linked', '/outside'), ('linked', '../../outside')]:
            with self.subTest(name=name, target=target), tempfile.TemporaryDirectory() as tmp:
                archive = Path(tmp) / 'archive.tar'
                destination = Path(tmp) / 'snapshot'
                destination.mkdir()
                with tarfile.open(archive, 'w') as output:
                    entry = tarfile.TarInfo(name)
                    if target:
                        entry.type, entry.linkname = tarfile.SYMTYPE, target
                        output.addfile(entry)
                    else:
                        entry.size = 1
                        output.addfile(entry, io.BytesIO(b'x'))
                with self.assertRaises(InvalidChallenge):
                    extract_snapshot(archive, destination)


if __name__ == '__main__':
    unittest.main()
