"""Create a scenario authoring scaffold using this repository's challenge contract."""

import argparse
import json
from pathlib import Path
import re
import shutil

from validate import InvalidChallenge, image, inside, load_contract, validate_manifest


TEMPLATES = Path(__file__).resolve().parent / 'templates'
IMAGE = 'python:3.13.15-slim-trixie@sha256:7c61056e61ac89e852de05f3dc6fa51a6dd2181797bceed46aa725dd7cb2cd3b'
CATEGORIES = ('web', 'pwn', 'rev', 'crypto', 'forensics', 'misc')
RESERVED = {'con', 'prn', 'aux', 'nul', *(f'com{i}' for i in range(1, 10)), *(f'lpt{i}' for i in range(1, 10))}


def quoted(value):
    return json.dumps(value, ensure_ascii=False)


def render(name, values):
    source = (TEMPLATES / name).read_text(encoding='utf-8')
    return re.sub(r'\{\{([A-Z_]+)\}\}', lambda match: values[match[1]], source)


def scaffold(root, slug, *, kind, category, title=None, difficulty=1, hints=3, patched=False, toolbox=IMAGE):
    root = root.resolve()
    definition = load_contract(root)
    if definition['version'] != 5:
        raise InvalidChallenge('creation templates support contract version 5; update templates before using another version')
    if len(slug) > 40 or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in RESERVED:
        raise InvalidChallenge('slug must be 1–40 lowercase letters/digits separated by hyphens, and usable as a Windows directory')
    if kind not in ('file', 'service') or category not in CATEGORIES:
        raise InvalidChallenge('choose file/service and a supported category')
    if type(hints) is not int or not 0 <= hints <= 10:
        raise InvalidChallenge('hints must be between 0 and 10')
    if type(difficulty) is not int or not 1 <= difficulty <= 5:
        raise InvalidChallenge('difficulty must be between 1 and 5')
    if patched and kind != 'service':
        raise InvalidChallenge('patch checks require a service problem')
    title = title if title is not None else slug.replace('-', ' ').title()
    if not isinstance(title, str) or not title.strip():
        raise InvalidChallenge('title must be nonempty')
    image(toolbox, 'image')
    if re.search(r'\s|#', toolbox):
        raise InvalidChallenge('image must be a single Dockerfile image reference')
    values = {'SCHEMA': str(definition['version']), 'SLUG': quoted(slug), 'TITLE': quoted(title),
              'CATEGORY': quoted(category), 'DIFFICULTY': str(difficulty), 'IMAGE': toolbox, 'IMAGE_TOML': quoted(toolbox),
              'HINTS': quoted([f'hints/{i}.md' for i in range(1, hints + 1)]),
              'NETWORK': quoted(definition['solve_network'])}
    files = {
        'challenge.toml': render(f'{kind}/challenge.toml', values),
        'README.md': render(f'{kind}/README.md', values),
        'AUTHORING.md': render('common/authoring.md', values),
        'solve/README.md': render('common/walkthrough.md', values),
        'solve/solve.py': render('common/solve.py', values),
    }
    for i in range(1, hints + 1):
        files[f'hints/{i}.md'] = render('common/hint.md', {'STEP': str(i)})
    if kind == 'file':
        files['files/data.txt'] = render('file/data.txt', values)
    else:
        for output in ('compose.yaml', 'vulnerable/Dockerfile', 'vulnerable/app.py', '.dockerignore'):
            files[output] = render('service/' + output, values)
        if patched:
            files['challenge.toml'] += '\n[patched]\ncompose = "compose.patched.yaml"\ncheck = ["python3", "patched/test.py"]\n'
            files['compose.patched.yaml'] = render('service/compose.patched.yaml', values)
            files['patched/app.py'] = files['vulnerable/app.py']
            files['patched/test.py'] = render('service/patched/test.py', values)
    parent = inside(root, root / 'challenges')
    destination = parent / slug
    # Check lexically too: an existing dangling link belongs to its author.
    if destination.exists() or destination.is_symlink():
        raise InvalidChallenge(f'challenge already exists: {slug}')
    return destination, files, definition


def create(root, slug, *, dry_run=False, **options):
    destination, files, definition = scaffold(root, slug, **options)
    if dry_run:
        return destination, list(files)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation arbitrates competing generators and protects existing work.
    destination.mkdir()
    try:
        for name, content in files.items():
            path = destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('x', encoding='utf-8', newline='\n') as output:
                output.write(content)
        validate_manifest(root, destination / 'challenge.toml', definition)
    except BaseException:
        # Only this invocation's newly reserved, repository-contained directory.
        if destination.resolve().is_relative_to(root.resolve()) and not destination.is_symlink():
            shutil.rmtree(destination)
        raise
    return destination, list(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('slug')
    parser.add_argument('--kind', choices=('file', 'service'), required=True,
                        help='file resources or a starter HTTP service')
    parser.add_argument('--category', choices=CATEGORIES, required=True)
    parser.add_argument('--title', help='display title; defaults to the slug as words')
    parser.add_argument('--difficulty', type=int, choices=range(1, 6), default=1,
                        help='1 Intro, 2 Easy, 3 Medium, 4 Hard, 5 Expert (default: 1)')
    parser.add_argument('--hints', type=int, default=3, help='ordered hints, 0–10 (default: 3)')
    parser.add_argument('--patched', action='store_true', help='add service patch and functional-check scaffolds')
    parser.add_argument('--image', dest='toolbox', default=IMAGE, help='Python 3 toolbox and service base image')
    parser.add_argument('--dry-run', action='store_true', help='list files without writing them')
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    options = vars(parser.parse_args())
    root = options.pop('repo').resolve()
    slug = options.pop('slug')
    try:
        destination, files = create(root, slug, **options)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'create: {error}\n')
    prefix = 'Would create' if options['dry_run'] else 'Created'
    print(f'{prefix} {destination.relative_to(root).as_posix()}')
    for name in files:
        print(f'  {name}')
    if not options['dry_run']:
        print('Format validation passed. Complete the scenario briefing, hints, report and solution before publication.')


if __name__ == '__main__':
    main()
