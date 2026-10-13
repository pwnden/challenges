"""Check that every challenge follows the shared directory and document layout."""

import argparse
from pathlib import Path
import re
import tomllib

ALLOWED_ENTRIES = {'README.md', 'BRIEFING.md', 'AUTHORING.md', 'challenge.toml', 'compose.yaml',
                   'compose.patched.yaml', '.dockerignore', '.gitattributes', 'files', 'hints',
                   'solve', 'patched', 'vulnerable', 'authoring'}
AUTHORING_TITLE = '# 시나리오 작성 기록'
AUTHORING_SECTIONS = ['시나리오 설정', '학습 목표와 대상', '선수 지식과 학습 내용', '의도된 풀이',
                      '개념 관계', '난도 근거', '다른 풀이와 정답 노출', '검증과 리뷰']
WALKTHROUGH_SECTIONS = ['조사 결과', '조사 과정', '의뢰 완료 확인', '드러난 보안 원리']
WALKTHROUGH_REQUIRED = ['조사 과정', '드러난 보안 원리']
README_BLOCKS = ['message', 'objective', 'resources', 'submission']
POLICY_NAMES = {'policy.py', 'policy.json'}

# Known gaps in older problems. Each entry names the rule, the reason and what ends it.
# A listed gap that no longer exists is reported, so the list can only shrink.
EXCEPTIONS = {}


def headings(path, level):
    """Return the headings of one Markdown level, ignoring fenced code."""
    found, fenced = [], False
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('```'):
            fenced = not fenced
        elif not fenced and (match := re.match(r'(#{1,6}) (.+?)\s*$', line)) and len(match[1]) == level:
            found.append(match[2])
    return found


def in_order(found, allowed):
    positions = [allowed.index(name) for name in found if name in allowed]
    return positions == sorted(positions) and len(set(found)) == len(found)


def check_challenge(root, directory, reviews=True):
    slug = directory.name
    problems = []

    def add(rule, message):
        problems.append((rule, message))

    manifest = tomllib.loads((directory / 'challenge.toml').read_text(encoding='utf-8'))
    for entry in sorted(path.name for path in directory.iterdir()):
        if entry not in ALLOWED_ENTRIES and entry != '.DS_Store':
            add('entries', f'unknown top-level entry {entry}')
    for name in ('README.md', 'AUTHORING.md', 'solve/README.md'):
        if not (directory / name).is_file():
            add('files', f'missing {name}')

    readme = directory / 'README.md'
    if readme.is_file():
        blocks = re.findall(r'^::(\w+)', readme.read_text(encoding='utf-8'), re.M)
        found = [name for name in blocks if name in README_BLOCKS]
        if found not in (README_BLOCKS, README_BLOCKS[1:]):
            add('readme-blocks', f'README.md blocks {found} must be {README_BLOCKS} in order; message is optional')

    authoring = directory / 'AUTHORING.md'
    if authoring.is_file():
        if headings(authoring, 1) != [AUTHORING_TITLE[2:]]:
            add('authoring', f'AUTHORING.md needs the single title "{AUTHORING_TITLE}"')
        found = headings(authoring, 2)
        if found[:len(AUTHORING_SECTIONS)] != AUTHORING_SECTIONS:
            add('authoring', f'AUTHORING.md sections must start with {AUTHORING_SECTIONS}; found {found}')

    walkthrough = directory / 'solve/README.md'
    if walkthrough.is_file():
        if headings(walkthrough, 1):
            add('walkthrough', 'solve/README.md must not use a level-1 heading')
        found = headings(walkthrough, 2)
        unknown = [name for name in found if name not in WALKTHROUGH_SECTIONS]
        if unknown or not in_order(found, WALKTHROUGH_SECTIONS):
            add('walkthrough', f'solve/README.md sections must be an ordered subset of {WALKTHROUGH_SECTIONS}; found {found}')
        for name in WALKTHROUGH_REQUIRED:
            if name not in found:
                add('walkthrough', f'solve/README.md needs the section "{name}"')

    for hint in sorted((directory / 'hints').glob('*.md')):
        if re.search(r'^#{1,6} ', hint.read_text(encoding='utf-8'), re.M):
            add('hints', f'{hint.name} must be plain text without headings')

    if 'compose' in manifest:
        for name in ('vulnerable/Dockerfile', 'vulnerable/app.py'):
            if not (directory / name).is_file():
                add('service', f'missing {name}')
        for name in ('compose.yaml', 'compose.patched.yaml'):
            path = directory / name
            if path.is_file() and re.search(r'^\s*ports:', path.read_text(encoding='utf-8'), re.M):
                add('compose', f'{name} must not publish ports; the platform provides ingress')
        compose = directory / 'compose.yaml'
        if compose.is_file() and 'internal: true' not in compose.read_text(encoding='utf-8'):
            add('compose', 'compose.yaml must declare an internal default network')
        if (directory / 'vulnerable/web/App.vue').is_file() and not (directory / '.dockerignore').is_file():
            add('service', 'a Vue service needs .dockerignore')
        for folder in ('vulnerable', 'patched'):
            for path in sorted((directory / folder).glob('*')) if (directory / folder).is_dir() else ():
                if 'policy' in path.name and path.name not in POLICY_NAMES:
                    add('policy-name', f'{folder}/{path.name} must be named policy.py or policy.json')
        if 'patched' in manifest:
            if not (directory / 'compose.patched.yaml').is_file():
                add('service', 'missing compose.patched.yaml')
            if not any((directory / 'patched' / name).is_file() for name in ('app.py', 'policy.py', 'policy.json')):
                add('service', 'patched/ needs app.py, policy.py or policy.json')
            if not any((directory / 'patched' / name).is_file() for name in ('test.py', 'test.sh')):
                add('service', 'patched/ needs test.py or test.sh')

    if reviews and not any((root / 'quality/text-reviews' / slug).glob('*.md')):
        add('text-review', f'quality/text-reviews/{slug}/ needs a Markdown review')
    return problems


def check_catalog(root, reviews=True):
    root = root.resolve()
    reported, used = [], set()
    for manifest in sorted((root / 'challenges').glob('*/challenge.toml')):
        slug = manifest.parent.name
        for rule, message in check_challenge(root, manifest.parent, reviews):
            if (slug, rule) in EXCEPTIONS:
                used.add((slug, rule))
            else:
                reported.append(f'{slug}: {message}')
    for slug, rule in sorted(set(EXCEPTIONS) - used):
        reported.append(f'{slug}: listed exception {rule} is no longer needed; remove it from layout.EXCEPTIONS')
    return reported


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    reported = check_catalog(parser.parse_args().repo)
    for line in reported:
        print(line)
    if reported:
        parser.exit(1, f'layout: {len(reported)} problems\n')
    print('layout: every challenge follows the shared layout')


if __name__ == '__main__':
    main()
