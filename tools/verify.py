"""Verify challenge targets, solutions, patches and cleanup with Python and Docker."""

import argparse
import hashlib
from pathlib import Path
import secrets

from runtime import Docker, ExecutionError
from validate import InvalidChallenge, load_contract, validate_manifest


def discover(root, slugs=()):
    definition = load_contract(root)
    if definition['version'] != 5:
        raise InvalidChallenge('author execution verifier supports contract version 5')
    manifests = sorted((root / 'challenges').glob('*/challenge.toml'))
    if not manifests:
        raise InvalidChallenge('no challenge.toml files found')
    records = []
    for manifest in manifests:
        metadata = validate_manifest(root, manifest, definition)
        metadata['solve'] = {**{'network': definition['solve_network'],
                                'timeout_seconds': definition['solve_timeout_seconds'],
                                'writable': False}, **metadata['solve']}
        records.append((manifest.parent, metadata))
    requested = set(slugs)
    missing = requested - {metadata['slug'] for _, metadata in records}
    if missing:
        raise InvalidChallenge(f'unknown challenges: {", ".join(sorted(missing))}')
    selected = [(directory, metadata) for directory, metadata in records
                if not requested or metadata['slug'] in requested]
    return definition, selected


def check_solution(result, expected, *, digest=False):
    if result.code:
        raise ExecutionError(f'solution failed with exit code {result.code}: {result.stderr.strip()}')
    value = result.stdout.strip()
    if digest:
        matches = hashlib.sha256(value.encode('utf-8')).hexdigest() == expected.lower()
    else:
        matches = value == expected
    if not matches:
        raise ExecutionError('solution did not return the expected flag')


def check_attack(result, flag, rejected_exit):
    if result.stdout.strip() == flag:
        raise ExecutionError('attack still returns the flag against the patched target')
    if result.code not in (0, rejected_exit):
        raise ExecutionError(f'patched attack has an unexpected exit code {result.code}: {result.stderr.strip()}')


def verify_problem(docker, root, directory, metadata, definition):
    solve = metadata['solve']
    if not metadata.get('compose'):
        result = docker.tool(directory, metadata, 'none', solve['image'], solve['command'])
        check_solution(result, metadata['flag']['sha256'], digest=True)
        return
    flag = 'pwnden{' + secrets.token_hex(16) + '}'
    # Resolve and check both definitions before launching the first target.
    vulnerable = docker.project(root, directory, metadata, flag)
    patched = docker.project(root, directory, metadata, flag, patched=True) if 'patched' in metadata else None
    with vulnerable.running():
        network = vulnerable.network(solve['network'])
        result = docker.tool(directory, metadata, network, solve['image'], solve['command'])
        check_solution(result, flag)
        if patched is not None:
            with patched.running():
                network = patched.network(solve['network'])
                attack = docker.tool(directory, metadata, network, solve['image'], solve['command'])
                check_attack(attack, flag, definition['attack_rejected_exit'])
                image = metadata['patched'].get('image') or solve['image']
                result = docker.tool(directory, metadata, network, image, metadata['patched']['check'])
                if result.code:
                    raise ExecutionError(f'patched functional check failed with exit code {result.code}: {result.stderr.strip()}')


def verify_catalog(root, slugs=(), *, docker=None, prepare_timeout=300):
    root = root.resolve()
    definition, records = discover(root, slugs)
    docker = docker or Docker(prepare_timeout=prepare_timeout)
    try:
        with docker.commands.signals():
            docker.prerequisites()
            for directory, metadata in records:
                print(f'Verifying {metadata["slug"]}...', flush=True)
                verify_problem(docker, root, directory, metadata, definition)
                print(f'verified {metadata["slug"]} (solution, declared patch checks, cleanup)', flush=True)
    except (OSError, ValueError, ExecutionError) as error:
        raise ExecutionError(docker.commands.redact(str(error))) from error
    return len(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('slugs', nargs='*', help='selected challenges; defaults to the entire catalog')
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--prepare-timeout', type=int, default=300,
                        help='seconds for image preparation and service startup (default: 300)')
    options = parser.parse_args()
    if options.prepare_timeout <= 0:
        parser.error('--prepare-timeout must be positive')
    try:
        count = verify_catalog(options.repo, options.slugs, prepare_timeout=options.prepare_timeout)
    except (OSError, ValueError, ExecutionError) as error:
        parser.exit(1, f'verify: {error}\n')
    print(f'Verified {count} challenges.')


if __name__ == '__main__':
    main()
