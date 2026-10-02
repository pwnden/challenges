"""Create eight local commits including a key rotation and configuration rename."""
import gzip
import io
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile

KEY = 'pwnden{deleted_file_live_history}'
OLD_KEY = 'pwnden{retired_scheduler_key}'


def bundle(include_secret=True):
    with tempfile.TemporaryDirectory() as name:
        root = Path(name) / 'source'
        root.mkdir()
        env = {**os.environ, 'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1',
               'GIT_AUTHOR_NAME': 'Lab Maintainer', 'GIT_AUTHOR_EMAIL': 'lab@example.invalid',
               'GIT_COMMITTER_NAME': 'Lab Maintainer', 'GIT_COMMITTER_EMAIL': 'lab@example.invalid',
               'GIT_AUTHOR_DATE': '2026-09-01T12:00:00+00:00', 'GIT_COMMITTER_DATE': '2026-09-01T12:00:00+00:00'}

        def git(*args):
            subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false',
                            *args], cwd=root, env=env, capture_output=True, check=True)

        def commit(message):
            git('add', '--all')
            git('commit', '-qm', message)

        git('init', '--quiet', '--template=', '--initial-branch=main')
        (root / 'README.txt').write_text('Lab scheduler example. No remote repository.\n')
        commit('Create scheduler example')
        (root / 'schedule.txt').write_text('backup=02:00\n')
        commit('Set backup schedule')
        (root / 'config').mkdir()
        key = KEY if include_secret else 'EXAMPLE_ONLY'
        old_key = OLD_KEY if include_secret else 'RETIRED_EXAMPLE'
        (root / 'config/runtime.env').write_text('SCHEDULER_MODE=lab-v1\nRECOVERY_KEY=' + old_key + '\n')
        commit('Add runtime configuration')
        (root / 'config/runtime.env').write_text('SCHEDULER_MODE=lab-v2\nRECOVERY_KEY=' + key + '\n')
        commit('Rotate recovery key for lab-v2; retire lab-v1 key')
        git('mv', 'config/runtime.env', 'config/worker.env')
        commit('Rename runtime configuration for worker')
        (root / 'schedule.txt').write_text('backup=03:00\n')
        commit('Move backup schedule')
        (root / 'config/worker.env').unlink()
        commit('Remove internal configuration from release')
        (root / 'config/example.env').write_text('SCHEDULER_MODE=lab\nRECOVERY_KEY=YOUR_TEST_KEY\n')
        (root / 'config/release.txt').write_text('release=lab-v2\nprivate_config=config/worker.env\n')
        commit('Add public configuration example')
        # Rebuild the index without host-specific inode/ctime values.
        (root / '.git/index').unlink()
        git('read-tree', 'HEAD')
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode='w') as archive:
            for path in [root, *sorted(root.rglob('*'))]:
                info = archive.gettarinfo(str(path), arcname='source/' + str(path.relative_to(root)))
                info.uid = info.gid = info.mtime = 0
                info.uname = info.gname = ''
                info.mode = 0o755 if info.isdir() else 0o644
                if info.isfile():
                    with path.open('rb') as source:
                        archive.addfile(info, source)
                else:
                    archive.addfile(info)
        return gzip.compress(output.getvalue(), mtime=0)


if __name__ == '__main__':
    target = Path(__file__).resolve().parents[1] / 'files'
    target.mkdir(exist_ok=True)
    (target / 'source.tar.gz').write_bytes(bundle())
