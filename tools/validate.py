"""Validate the problem contract and all challenge manifests without a runner."""

import argparse
from pathlib import Path, PurePosixPath
import re
import tomllib


class InvalidChallenge(ValueError):
    pass


def table(value, name, allowed, required=()):
    if not isinstance(value, dict):
        raise InvalidChallenge(f"{name} must be a table")
    unknown = value.keys() - set(allowed)
    missing = set(required) - value.keys()
    if unknown:
        raise InvalidChallenge(f"{name}: unknown fields {', '.join(sorted(unknown))}")
    if missing:
        raise InvalidChallenge(f"{name}: missing fields {', '.join(sorted(missing))}")
    return value


def text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise InvalidChallenge(f"{name} must be a nonempty string")
    return value


def integer(value, name, minimum=1, maximum=None):
    if type(value) is not int or value < minimum or (maximum is not None and value > maximum):
        raise InvalidChallenge(f"{name} must be an integer in the allowed range")
    return value


def strings(value, name, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        raise InvalidChallenge(f"{name} must be {'a nonempty' if nonempty else 'an'} array")
    for item in value:
        if not isinstance(item, str) or item == '':
            raise InvalidChallenge(f"{name} must contain nonempty strings")
    return value


def image(value, name):
    value = text(value, name)
    if value.startswith('-') or value != value.strip():
        raise InvalidChallenge(f"{name} must be an image reference")


def inside(root, path):
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise InvalidChallenge(f"{path} is outside the challenges repository")
    return resolved


def repository_path(root, directory, value, name, regular=False):
    value = text(value, name)
    if PurePosixPath(value).is_absolute() or '\\' in value or ':' in value:
        raise InvalidChallenge(f"{name} must be a portable relative repository path")
    path = inside(root, directory / value)
    if not path.exists() or (regular and not path.is_file()):
        raise InvalidChallenge(f"{name}: {value} must exist{' as a regular file' if regular else ''}")
    return path


def load_contract(root):
    path = inside(root, root / 'contract.toml')
    with path.open('rb') as source:
        definition = tomllib.load(source)
    fields = {'version', 'solve_network', 'solve_timeout_seconds', 'attack_rejected_exit'}
    table(definition, 'contract', fields, fields)
    integer(definition['version'], 'contract.version')
    text(definition['solve_network'], 'contract.solve_network')
    integer(definition['solve_timeout_seconds'], 'contract.solve_timeout_seconds')
    integer(definition['attack_rejected_exit'], 'contract.attack_rejected_exit', maximum=124)
    return definition


def markdown(root, directory, value, name):
    path = repository_path(root, directory, value, name, regular=True)
    if path.suffix.lower() != '.md':
        raise InvalidChallenge(f"{name} must be a Markdown file")
    with path.open('rb') as source:
        content = source.read((1 << 20) + 1)
    if len(content) > 1 << 20:
        raise InvalidChallenge(f"{name} must be at most 1 MiB")
    try:
        text(content.decode('utf-8'), name)
    except UnicodeDecodeError as error:
        raise InvalidChallenge(f"{name} must be UTF-8") from error
    return path


def validate_manifest(root, manifest, definition):
    root = root.resolve()
    manifest = inside(root, manifest)
    directory = manifest.parent
    with manifest.open('rb') as source:
        data = tomllib.load(source)
    table(data, 'challenge', {'schema', 'slug', 'title', 'category', 'files', 'compose', 'endpoints', 'flag', 'solve', 'patched', 'content', 'player'}, {'schema', 'slug', 'title', 'category', 'flag', 'solve', 'content'} | ({'player'} if definition['version'] >= 4 else set()))
    if integer(data['schema'], 'schema') != definition['version']:
        raise InvalidChallenge(f"schema must match contract version {definition['version']}")
    slug = text(data['slug'], 'slug')
    if len(slug) > 40 or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug != directory.name:
        raise InvalidChallenge('slug must be portable and match the challenge directory')
    text(data['title'], 'title')
    if data['category'] not in ('web', 'pwn', 'rev', 'crypto', 'forensics', 'misc'):
        raise InvalidChallenge('unsupported category')
    content = table(data['content'], 'content', {'description', 'hints', 'walkthrough'}, {'description', 'walkthrough'})
    paths = [markdown(root, directory, content['description'], 'content.description')]
    hints = strings(content.get('hints', []), 'content.hints')
    if len(hints) > 10:
        raise InvalidChallenge('content.hints supports at most 10 steps')
    paths.extend(markdown(root, directory, hint, 'content.hints') for hint in hints)
    paths.append(markdown(root, directory, content['walkthrough'], 'content.walkthrough'))
    if len(set(paths)) != len(paths):
        raise InvalidChallenge('content documents must use distinct files')
    files = strings(data.get('files', []), 'files')
    for value in files:
        repository_path(root, directory, value, 'files')
    solve = table(data['solve'], 'solve', {'image', 'command', 'network', 'timeout_seconds', 'writable'}, {'image', 'command'})
    image(solve['image'], 'solve.image')
    strings(solve['command'], 'solve.command', nonempty=True)
    text(solve.get('network', definition['solve_network']), 'solve.network')
    integer(solve.get('timeout_seconds', definition['solve_timeout_seconds']), 'solve.timeout_seconds')
    if type(solve.get('writable', False)) is not bool:
        raise InvalidChallenge('solve.writable must be a boolean')
    flag = table(data['flag'], 'flag', {'mode', 'sha256'}, {'mode'})
    compose = data.get('compose', '')
    if not isinstance(compose, str):
        raise InvalidChallenge('compose must be a string')
    endpoints = data.get('endpoints', [])
    if not isinstance(endpoints, list):
        raise InvalidChallenge('endpoints must be an array of tables')
    if compose:
        repository_path(root, directory, compose, 'compose', regular=True)
        if flag['mode'] != 'generated' or flag.get('sha256', '') != '':
            raise InvalidChallenge('service challenge needs generated flag without sha256')
    else:
        digest = flag.get('sha256', '')
        if not files or endpoints or 'patched' in data or flag['mode'] != 'sha256':
            raise InvalidChallenge('file challenge needs files and sha256 flag without endpoints or patched')
        if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-fA-F]{64}', digest):
            raise InvalidChallenge('flag.sha256 must be a 64-digit hex digest')
    names = set()
    for endpoint in endpoints:
        table(endpoint, 'endpoint', {'name', 'service', 'port', 'protocol'}, {'name', 'service', 'port', 'protocol'})
        name = text(endpoint['name'], 'endpoint.name')
        text(endpoint['service'], 'endpoint.service')
        integer(endpoint['port'], 'endpoint.port', maximum=65535)
        if endpoint['protocol'] not in ('http', 'tcp') or name in names:
            raise InvalidChallenge('endpoint needs a unique name and http or tcp protocol')
        names.add(name)
    if 'player' in data:
        player = table(data['player'], 'player', {'tools'}, {'tools'})
        tools = strings(player['tools'], 'player.tools', nonempty=True)
        if len(set(tools)) != len(tools) or any(tool not in ('web', 'files', 'terminal') for tool in tools):
            raise InvalidChallenge('player.tools must contain unique web, files or terminal tools')
        if 'web' in tools and not any(endpoint['protocol'] == 'http' for endpoint in endpoints):
            raise InvalidChallenge('web tool requires a declared HTTP endpoint')
        if 'files' in tools and not files:
            raise InvalidChallenge('files tool requires distribution files')
    if 'patched' in data:
        patched = table(data['patched'], 'patched', {'compose', 'check', 'image'}, {'compose', 'check'})
        if not compose:
            raise InvalidChallenge('patched needs a service challenge')
        repository_path(root, directory, patched['compose'], 'patched.compose', regular=True)
        strings(patched['check'], 'patched.check', nonempty=True)
        if 'image' in patched and patched['image'] != '':
            image(patched['image'], 'patched.image')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    root = parser.parse_args().repo.resolve()
    try:
        definition = load_contract(root)
        manifests = sorted((root / 'challenges').glob('*/challenge.toml'))
        if not manifests:
            raise InvalidChallenge('no challenge.toml files found')
        for manifest in manifests:
            try:
                validate_manifest(root, manifest, definition)
            except (OSError, ValueError) as error:
                raise InvalidChallenge(f"{manifest.relative_to(root)}: {error}") from error
            print(f"valid {manifest.parent.name} (contract {definition['version']})")
    except (OSError, ValueError) as error:
        parser.exit(1, f"validate: {error}\n")
    print(f"Validated {len(manifests)} challenges.")


if __name__ == '__main__':
    main()
