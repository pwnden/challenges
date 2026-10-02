"""Compile shared prerequisite notes into player briefs using contract v5 Markdown."""

import argparse
from pathlib import Path
import re


INCLUDE = re.compile(r'^::knowledge\{concepts="([^"\n]+)"\}\n::[ \t]*$', re.MULTILINE)
KEY = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')


def contained(root, path):
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'{path.name} must stay inside the repository')
    return path


def compile_brief(root, source):
    text = contained(root, source).read_text(encoding='utf-8')

    def include(match):
        keys = match[1].split(',')
        if len(keys) != len(set(keys)) or not all(KEY.fullmatch(key) for key in keys):
            raise ValueError('knowledge concepts need distinct lowercase concept IDs')
        documents = []
        for key in keys:
            path = contained(root, root / 'knowledge' / f'{key}.md')
            document = path.read_text(encoding='utf-8').strip()
            title, separator, body = document.partition('\n')
            if not separator or not title.startswith('# ') or not body.strip() or '\n::' in document:
                raise ValueError(f'{key}: expected a title and Markdown body without MDC blocks')
            documents.append('### ' + title[2:] + '\n' + body)
        return '::knowledge\n\n' + '\n\n'.join(documents) + '\n::'

    result = INCLUDE.sub(include, text)
    if re.search(r'^::knowledge\{concepts=', result, re.MULTILINE):
        raise ValueError('knowledge include must be an empty block with quoted comma-separated IDs')
    return result.rstrip() + '\n'


def check_brief(root, directory):
    source = directory / 'BRIEFING.md'
    if source.exists() or source.is_symlink():
        target = contained(root, directory / 'README.md')
        if target.read_text(encoding='utf-8') != compile_brief(root, source):
            raise ValueError(f'{directory.name}: run python3 tools/content.py {directory.name} to refresh prerequisites')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('slugs', nargs='*')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.repo.resolve()
    try:
        if any(not KEY.fullmatch(slug) for slug in args.slugs):
            raise ValueError('select scenario IDs, not filesystem paths')
        directories = [root / 'challenges' / slug for slug in args.slugs] if args.slugs else sorted((root / 'challenges').iterdir())
        for directory in directories:
            contained(root, directory)
            source = directory / 'BRIEFING.md'
            if not source.exists():
                if args.slugs:
                    raise ValueError(f'{directory.name}: no BRIEFING.md source')
                continue
            if args.check:
                check_brief(root, directory)
            else:
                target = contained(root, directory / 'README.md')
                if target.is_symlink():
                    raise ValueError('generated README must be a regular repository file')
                target.write_text(compile_brief(root, source), encoding='utf-8', newline='\n')
            print(('checked ' if args.check else 'updated ') + directory.name)
    except (OSError, ValueError) as error:
        parser.exit(1, f'content: {error}\n')


if __name__ == '__main__':
    main()
