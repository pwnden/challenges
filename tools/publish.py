"""Verify a committed catalog snapshot and publish that commit to main."""

import argparse
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile

from runtime import Commands, ExecutionError
from validate import InvalidChallenge, inside


def committed_state(root, commands):
    actual = commands.run(['git', 'rev-parse', '--show-toplevel'], cwd=root).stdout.strip()
    if Path(actual).resolve() != root.resolve():
        raise InvalidChallenge('--repo must be the challenges Git repository root')
    branch = commands.run(['git', 'symbolic-ref', '--quiet', '--short', 'HEAD'], cwd=root).stdout.strip()
    if branch != 'main':
        raise InvalidChallenge('publish selects a committed main branch')
    if commands.run(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=root).stdout:
        raise InvalidChallenge('commit authoring changes before publishing; the worktree must be clean')
    return commands.run(['git', 'rev-parse', 'HEAD'], cwd=root).stdout.strip()


def extract_snapshot(archive, destination):
    """Extract Git's portable source archive without following escaping links."""
    root = destination.resolve()
    with tarfile.open(archive, mode='r:') as source:
        for member in source:
            name = PurePosixPath(member.name)
            if name.is_absolute() or '\\' in member.name or ':' in member.name:
                raise InvalidChallenge('catalog archive has a nonportable path')
            path = inside(root, destination / member.name)
            if member.isdir():
                path.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                path.parent.mkdir(parents=True, exist_ok=True)
                with source.extractfile(member) as data, path.open('xb') as output:
                    shutil.copyfileobj(data, output)
                path.chmod(member.mode & 0o777)
            elif member.issym():
                target = PurePosixPath(member.linkname)
                if target.is_absolute() or '\\' in member.linkname or ':' in member.linkname:
                    raise InvalidChallenge('catalog archive has a nonportable symlink')
                inside(root, path.parent / member.linkname)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.symlink_to(member.linkname)
            else:
                raise InvalidChallenge('catalog archive has an unsupported entry')


def gate_snapshot(snapshot, commands, prepare_timeout):
    result = commands.run([sys.executable, '-B', 'tools/quality.py'], cwd=snapshot, timeout=60)
    print(result.stdout, end='', flush=True)
    commands.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tools', '-p', 'test_*.py'],
                 cwd=snapshot, timeout=300)
    commands.run(['docker', 'build', '--file', 'web/Dockerfile', '--target', 'check', '.'],
                 cwd=snapshot, timeout=prepare_timeout, timeout_grace=30)
    result = commands.run([sys.executable, '-B', 'tools/check_isolation.py'], cwd=snapshot,
                          timeout=300, timeout_grace=300)
    print(result.stdout, end='', flush=True)
    result = commands.run([sys.executable, '-B', 'tools/verify.py', '--prepare-timeout', str(prepare_timeout)],
                          cwd=snapshot, timeout=1800, timeout_grace=300)
    print(result.stdout, end='', flush=True)


def publish(root, *, remote='origin', check=False, prepare_timeout=300, commands=None, gate=gate_snapshot):
    root = root.resolve()
    commands = commands or Commands()
    with commands.signals():
        revision = committed_state(root, commands)
        remotes = commands.run(['git', 'remote'], cwd=root).stdout.splitlines()
        if remote not in remotes:
            raise InvalidChallenge('choose an existing Git remote')
        state = root / '.authoring'
        if state.exists() and (state.is_symlink() or not state.is_dir()):
            raise InvalidChallenge('.authoring must be a directory inside the repository')
        state.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='publish-', dir=state) as tmp:
            directory = Path(tmp)
            snapshot = directory / 'catalog'
            snapshot.mkdir()
            archive = directory / 'catalog.tar'
            with archive.open('xb') as output:
                subprocess.run(['git', 'archive', '--format=tar', revision], cwd=root,
                               stdout=output, stderr=subprocess.PIPE, check=True, timeout=60)
            extract_snapshot(archive, snapshot)
            print(f'Verifying committed catalog {revision}...', flush=True)
            gate(snapshot, commands, prepare_timeout)
            if committed_state(root, commands) != revision:
                raise InvalidChallenge('repository changed during verification; publication cancelled')
            if check:
                print(f'Publication checks passed for {revision}; remote unchanged.', flush=True)
            else:
                # Push exactly the verified commit; Git rejects a non-fast-forward update.
                commands.run(['git', 'push', '--porcelain', '--', remote, f'{revision}:refs/heads/main'],
                             cwd=root, timeout=180)
                print(f'Published {revision} to {remote}/main.', flush=True)
    return revision


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--remote', default='origin', help='existing Git remote (default: origin)')
    parser.add_argument('--check', action='store_true', help='run publication gates without pushing')
    parser.add_argument('--prepare-timeout', type=int, default=300)
    options = parser.parse_args()
    if options.prepare_timeout <= 0:
        parser.error('--prepare-timeout must be positive')
    try:
        publish(options.repo, remote=options.remote, check=options.check, prepare_timeout=options.prepare_timeout)
    except (OSError, ValueError, ExecutionError, subprocess.SubprocessError) as error:
        parser.exit(1, f'publish: {error}\n')


if __name__ == '__main__':
    main()
