"""Prepare blinded review inputs and aggregate independent challenge ballots."""

import argparse
import copy
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import shutil
from statistics import median
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'tools'))
from quality import load_rubric, source_digest, validate_review
from validate import InvalidChallenge, repository_path, table, text

MODEL = 'gpt-6-luna'
SKIP = {'__pycache__', 'node_modules', 'dist', '.git'}


def selected_files(root, slug):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        raise InvalidChallenge('invalid slug')
    repository_path(root, root, f'challenges/{slug}/challenge.toml', 'manifest', regular=True)
    paths = [root / 'contract.toml', root / 'quality/rubric.json']
    for relative in [f'challenges/{slug}', 'knowledge', 'web', 'tools', 'docs']:
        directory = root / relative
        for path in directory.rglob('*'):
            if SKIP & set(path.relative_to(root).parts) or path.suffix in {'.pyc', '.pyo'}:
                continue
            if path.is_symlink():
                raise InvalidChallenge(f'review snapshot does not follow symlinks: {path}')
            if path.is_file():
                paths.append(repository_path(root, root, path.relative_to(root).as_posix(), 'source', regular=True))
    return sorted(set(paths))


def inputs_digest(root, paths):
    digest = hashlib.sha256()
    for path in paths:
        value = path.read_bytes()
        digest.update(path.relative_to(root).as_posix().encode() + b'\0'
                      + str(len(value)).encode() + b'\0' + value)
    return digest.hexdigest()


def new_output(root, destination):
    destination = destination.resolve()
    if destination.is_relative_to(root) or root.is_relative_to(destination):
        raise InvalidChallenge('panel output must be outside the source repository')
    destination.mkdir(parents=True, exist_ok=False)
    return destination


def prepare(root, slug, destination):
    root = root.resolve()
    paths = selected_files(root, slug)
    expected = inputs_digest(root, paths)
    output = new_output(root, destination)
    try:
        for path in paths:
            target = output / path.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
        if inputs_digest(root, selected_files(root, slug)) != expected or inputs_digest(output, selected_files(output, slug)) != expected:
            raise InvalidChallenge('sources changed while preparing the review snapshot')
        index = {'slug': slug, 'input_sha256': expected, 'prepared_at': date.today().isoformat()}
        (output / 'panel-input.json').write_text(json.dumps(index, indent=2) + '\n')
    except Exception:
        shutil.rmtree(output)
        raise
    return index


def aggregate(root, slug, ballots, count):
    root = root.resolve()
    if count not in {3, 5} or len(ballots) != count:
        raise InvalidChallenge('provide exactly 3 or 5 judge ballots matching --judges')
    index = json.loads((root / 'panel-input.json').read_text())
    if index['slug'] != slug or index['input_sha256'] != inputs_digest(root, selected_files(root, slug)):
        raise InvalidChallenge('review input snapshot changed')
    rubric = load_rubric(root)
    identities = set()
    for ballot in ballots:
        fields = {'judge_id', 'model', 'reasoning_effort', 'lens', 'first_pass', 'review'}
        table(ballot, 'ballot', fields, fields)
        identity = text(ballot['judge_id'], 'judge_id')
        if identity in identities or ballot['review']['reviewer'] != identity:
            raise InvalidChallenge('judge IDs must be unique and match review.reviewer')
        identities.add(identity)
        if ballot['model'] != MODEL or ballot['reasoning_effort'] != 'low':
            raise InvalidChallenge('ballot must identify gpt-6-luna with low effort')
        text(ballot['lens'], 'lens')
        text(ballot['first_pass'], 'first_pass')
        validate_review(root, slug, rubric, ballot['review'])
    candidate = {'slug': slug, 'rubric_version': rubric['version'],
                 'reviewed_at': date.today().isoformat(),
                 'reviewer': 'Panel median: ' + ', '.join(sorted(identities)), 'criteria': {}}
    distribution, unresolved = {}, []
    for key in rubric['criteria']:
        votes = [ballot['review']['criteria'][key] for ballot in ballots]
        levels = [item['level'] for item in votes if item['level'] is not None]
        missing = count - len(levels)
        proposed = median(levels) if levels else None
        disputed = bool(levels) and (missing > 0 or max(levels) - min(levels) >= 2
                                     or (min(levels) == 0 and max(levels) > 0))
        distribution[key] = {'levels': {ballot['judge_id']: item['level'] for ballot, item in zip(ballots, votes)},
                             'unverified_judges': missing, 'proposed_median': proposed,
                             'needs_adjudication': disputed}
        if disputed:
            unresolved.append(key)
        reasons = [f'{ballot["judge_id"]} ({item["level"]}): {item["reason"]}' for ballot, item in zip(ballots, votes)]
        evidence, actions = [], []
        for item in votes:
            for citation in item['evidence']:
                if citation not in evidence:
                    evidence.append(copy.deepcopy(citation))
            if item['improvement'] and item['improvement'] not in actions:
                actions.append(item['improvement'])
        if disputed:
            actions.insert(0, 'Recheck disputed evidence and record parent adjudication before assigning a score.')
        candidate['criteria'][key] = {'level': None if disputed else int(proposed) if proposed is not None else None,
                                     'reason': '\n'.join(reasons), 'evidence': evidence,
                                     'improvement': '\n'.join(actions)}
    references = [e['path'] for item in candidate['criteria'].values() for e in item['evidence']]
    candidate['source_sha256'] = source_digest(root, slug, references)
    summary = validate_review(root, slug, rubric, candidate)
    audit = {'slug': slug, 'input_sha256': index['input_sha256'], 'model': MODEL,
             'reasoning_effort': 'low', 'judge_count': count, 'method': 'criterion median',
             'ballots': copy.deepcopy(ballots), 'distribution': distribution,
             'needs_adjudication': unresolved, 'summary': summary, 'adjudications': {}}
    return candidate, audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ['prepare', 'aggregate']:
        sub = commands.add_parser(name)
        sub.add_argument('--repo', type=Path, required=True)
        sub.add_argument('--slug', required=True)
        sub.add_argument('--out', type=Path, required=True)
        if name == 'aggregate':
            sub.add_argument('--judges', type=int, choices=[3, 5], default=3)
            sub.add_argument('--ballot', type=Path, action='append', required=True)
    options = parser.parse_args()
    try:
        if options.command == 'prepare':
            result = prepare(options.repo, options.slug, options.out)
            print(json.dumps(result, indent=2))
        else:
            ballots = [json.loads(path.read_text()) for path in options.ballot]
            candidate, audit = aggregate(options.repo, options.slug, ballots, options.judges)
            destination = new_output(options.repo.resolve(), options.out)
            for name, data in [('candidate', candidate), ('audit', audit)]:
                (destination / (name + '.json')).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
            print(json.dumps({'summary': audit['summary'], 'needs_adjudication': audit['needs_adjudication']}, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'panel: {error}\n')


if __name__ == '__main__':
    main()
