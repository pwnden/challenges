"""Build the shared CLI toolbox images that problems declare but Docker does not have yet."""

import argparse
import os
from pathlib import Path
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / 'images/cli/images.toml'


def load(root=ROOT):
    return tomllib.loads((root / 'images/cli/images.toml').read_text(encoding='utf-8'))


def build_args(tag, root=ROOT):
    """The docker build arguments for a known local tag, or None for an image to pull."""
    recipes = load(root)
    recipe = recipes['images'].get(tag)
    if recipe is None:
        return None
    platform = os.environ.get('PWNDEN_IMAGE_PLATFORM') or recipes['platform']
    args = ['build', '--progress=quiet', '--platform', platform, '--target', recipe['target']]
    if 'dockerfile' in recipe:
        args += ['-f', str(root / 'images/cli' / recipe['dockerfile'])]
    return args + ['-t', tag, str(root / 'images/cli')]


def declared(root=ROOT):
    tags = set()
    for manifest in sorted((root / 'challenges').glob('*/challenge.toml')):
        data = tomllib.loads(manifest.read_text(encoding='utf-8'))
        for image in (data['solve']['image'], data.get('patched', {}).get('image', '')):
            if image in load(root)['images']:
                tags.add(image)
    return sorted(tags)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tags', nargs='*', help='image tags; defaults to every tag a problem declares')
    options = parser.parse_args()
    for tag in options.tags or declared():
        args = build_args(tag)
        if args is None:
            parser.exit(1, f'images: no recipe for {tag}\n')
        print(f'building {tag}', flush=True)
        subprocess.run(['docker', *args], check=True)


if __name__ == '__main__':
    main()
