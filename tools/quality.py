"""Check evidence-backed author reviews and report demonstrated quality points."""

import argparse
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import re
import tomllib

from validate import InvalidChallenge, repository_path, table, text


def load_rubric(root):
    data = json.loads((root / 'quality/rubric.json').read_text())
    table(data, 'rubric', {'version', 'criteria'}, {'version', 'criteria'})
    if type(data['version']) is not int or data['version'] != 2:
        raise InvalidChallenge('unsupported quality rubric version')
    criteria = data['criteria']
    if not isinstance(criteria, dict) or not criteria:
        raise InvalidChallenge('rubric.criteria must be a nonempty table')
    for key, item in criteria.items():
        table(item, key, {'title', 'weight', 'check', 'evidence_kind'}, {'title', 'weight', 'check', 'evidence_kind'})
        if type(item['weight']) not in (int, float) or not math.isfinite(item['weight']) or item['weight'] <= 0:
            raise InvalidChallenge('criterion weight must be a positive finite number')
        for field in ['title', 'check', 'evidence_kind']:
            text(item[field], key + '.' + field)
    if sum(item['weight'] for item in criteria.values()) != 100:
        raise InvalidChallenge('rubric weights must total 100')
    return data


def source_digest(root, slug, evidence_paths=()):
    """Bind the review to the exercise, shared knowledge and grading definition."""
    paths = [root / 'contract.toml', root / 'quality/rubric.json']
    metadata = tomllib.loads((root / 'challenges' / slug / 'challenge.toml').read_text())
    if 'compose' in metadata and (root / 'web').exists():
        paths.extend(path for path in (root / 'web').rglob('*')
                     if path.is_file() and not {'node_modules', 'dist', '__pycache__'} & set(path.parts)
                     and path.suffix not in {'.pyc', '.pyo'})
    paths.extend(repository_path(root.resolve(), root, value, 'evidence.path', regular=True)
                 for value in evidence_paths)
    for directory in [root / 'challenges' / slug, root / 'knowledge']:
        paths.extend(path for path in directory.rglob('*')
                     if path.is_file() and '__pycache__' not in path.parts
                     and '.git' not in path.parts and path.suffix not in {'.pyc', '.pyo'})
    digest = hashlib.sha256()
    for path in sorted(set(paths)):
        relative = path.relative_to(root).as_posix()
        checked = repository_path(root.resolve(), root, relative, 'review source', regular=True)
        data = checked.read_bytes()
        digest.update(relative.encode() + b'\0' + str(len(data)).encode() + b'\0' + data)
    return digest.hexdigest()


def validate_review(root, slug, rubric, record):
    fields = {'slug', 'rubric_version', 'reviewed_at', 'reviewer', 'source_sha256', 'criteria'}
    table(record, slug, fields, fields)
    if record['slug'] != slug or type(record['rubric_version']) is not int or record['rubric_version'] != rubric['version']:
        raise InvalidChallenge(f'{slug}: review identity or rubric version mismatch')
    text(record['reviewer'], 'reviewer')
    if not isinstance(record['reviewed_at'], str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', record['reviewed_at']):
        raise InvalidChallenge(f'{slug}: reviewed_at must be an ISO date')
    date.fromisoformat(record['reviewed_at'])
    table(record['criteria'], 'review.criteria', rubric['criteria'], rubric['criteria'])
    points, covered = 0, 0
    pending, improvements = [], []
    for key, criterion in rubric['criteria'].items():
        item = record['criteria'][key]
        table(item, key, {'level', 'reason', 'evidence', 'improvement'}, {'level', 'reason', 'evidence', 'improvement'})
        text(item['reason'], key + '.reason')
        if not isinstance(item['improvement'], str):
            raise InvalidChallenge(f'{key}: improvement must be a string')
        if not isinstance(item['evidence'], list):
            raise InvalidChallenge(f'{key}: evidence must be an array')
        level = item['level']
        if level is None:
            pending.append(key)
            text(item['improvement'], key + '.pending action')
        else:
            if type(level) is not int or not 0 <= level <= 4:
                raise InvalidChallenge(f'{key}: level must be null or an integer from 0 to 4')
            if not item['evidence']:
                raise InvalidChallenge(f'{key}: a scored criterion needs evidence')
            if level < 3:
                text(item['improvement'], key + '.improvement')
            points += criterion['weight'] * level / 4
            covered += criterion['weight']
        for evidence in item['evidence']:
            table(evidence, 'evidence', {'path', 'quote', 'kind'}, {'path', 'quote', 'kind'})
            if evidence['kind'] != criterion['evidence_kind']:
                raise InvalidChallenge(f'{key}: needs {criterion["evidence_kind"]} evidence')
            path = repository_path(root.resolve(), root, evidence['path'], 'evidence.path', regular=True)
            if path.is_relative_to((root / 'quality').resolve()):
                raise InvalidChallenge('review cannot cite quality scores as its own evidence')
            quote = text(evidence['quote'], 'evidence.quote')
            if re.fullmatch(r'::[a-z]+(?:\{.*\})?', quote.strip()):
                raise InvalidChallenge(f'{key}: citation needs content, not only a markup label')
            if quote not in path.read_text(encoding='utf-8'):
                raise InvalidChallenge(f'{key}: evidence quote no longer matches {evidence["path"]}')
        if item['improvement']:
            improvements.append({'criterion': key, 'action': item['improvement']})
    references = [evidence['path'] for item in record['criteria'].values() for evidence in item['evidence']]
    if record['source_sha256'] != source_digest(root, slug, references):
        raise InvalidChallenge(f'{slug}: stale quality review; inspect changed sources and reassess')
    return {'slug': slug, 'points': points, 'reviewed_weight': covered,
            'pending': pending, 'improvements': improvements}


def check_catalog(root):
    root = root.resolve()
    rubric = load_rubric(root)
    manifests = sorted((root / 'challenges').glob('*/challenge.toml'))
    if not manifests:
        raise InvalidChallenge('no challenges found')
    slugs = {path.parent.name for path in manifests}
    reviews = root / 'quality/reviews'
    if {path.stem for path in reviews.glob('*.json')} != slugs:
        raise InvalidChallenge('quality reviews must cover exactly the current challenge catalog')
    results = []
    for manifest in manifests:
        slug = manifest.parent.name
        path = repository_path(root, root, f'quality/reviews/{slug}.json', 'review', regular=True)
        record = json.loads(path.read_text())
        result = validate_review(root, slug, rubric, record)
        result['title'] = tomllib.loads(manifest.read_text())['title']
        results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--json', action='store_true', help='include all follow-up actions as JSON')
    options = parser.parse_args()
    try:
        results = check_catalog(options.repo)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'quality: {error}\n')
    if options.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for item in results:
            print(f'{item["slug"]}: {item["points"]:g}/100; reviewed {item["reviewed_weight"]}%'
                  f'; pending {", ".join(item["pending"]) or "none"}')
        print(f'Checked {len(results)} author reviews. Scores are recorded judgments, not learner success rates.')


if __name__ == '__main__':
    main()
