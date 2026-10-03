"""Blind inputs, robust median scoring and preservation of dissenting evidence."""

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from quality import source_digest
from validate import InvalidChallenge

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('review_panel', ROOT / '.agents/skills/challenge-reviewer/scripts/panel.py')
PANEL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PANEL)


class ReviewPanelTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.root = self.directory / 'source'
        (self.root / 'challenges/sample').mkdir(parents=True)
        (self.root / 'quality/reviews').mkdir(parents=True)
        (self.root / 'quality/reviews/sample.json').write_text('{"old_score": 99}')
        (self.root / 'quality/rubric.json').write_bytes((ROOT / 'quality/rubric.json').read_bytes())
        (self.root / 'contract.toml').write_text('version = 7\n')
        (self.root / 'challenges/sample/challenge.toml').write_text('title = "Sample"\n')
        (self.root / 'challenges/sample/README.md').write_text('Boundary observed.\n')
        (self.root / 'knowledge').mkdir()
        (self.root / 'knowledge/base.md').write_text('Shared context.\n')
        self.snapshot = self.directory / 'snapshot'
        PANEL.prepare(self.root, 'sample', self.snapshot)
        self.ballots = [self.ballot(index) for index in range(1, 4)]

    def ballot(self, index):
        criteria = {}
        for key, definition in PANEL.load_rubric(self.snapshot)['criteria'].items():
            pending = key == 'explanation'
            criteria[key] = {'level': None if pending else 3,
                             'reason': f'Judge {index} inspected {key}.',
                             'improvement': 'Record a real session.' if pending else '',
                             'evidence': [] if pending else [{'path': 'challenges/sample/README.md',
                                                            'quote': 'Boundary observed.',
                                                            'kind': definition['evidence_kind']}]}
        identity = f'judge-{index}'
        review = {'slug': 'sample', 'rubric_version': 2, 'reviewed_at': '2026-10-03',
                  'reviewer': identity, 'criteria': criteria}
        references = [e['path'] for item in criteria.values() for e in item['evidence']]
        review['source_sha256'] = source_digest(self.snapshot, 'sample', references)
        return {'judge_id': identity, 'model': PANEL.MODEL, 'reasoning_effort': 'low',
                'lens': f'Perspective {index}', 'first_pass': 'Read the brief before answers.', 'review': review}

    def aggregate(self, ballots=None, count=3):
        return PANEL.aggregate(self.snapshot, 'sample', ballots or self.ballots, count)

    def test_blinded_copy_and_existing_output_are_protected(self):
        self.assertFalse((self.snapshot / 'quality/reviews').exists())
        self.assertEqual((self.snapshot / 'challenges/sample/README.md').read_bytes(),
                         (self.root / 'challenges/sample/README.md').read_bytes())
        with self.assertRaises(FileExistsError):
            PANEL.prepare(self.root, 'sample', self.snapshot)
        with self.assertRaises(InvalidChallenge):
            PANEL.prepare(self.root, 'sample', self.root / 'inside')

    def test_median_points_and_original_reasons_are_retained(self):
        self.ballots[1]['review']['criteria']['goal']['level'] = 4
        self.ballots[2]['review']['criteria']['goal']['level'] = 4
        original = copy.deepcopy(self.ballots)
        candidate, audit = self.aggregate()
        self.assertEqual(candidate['criteria']['goal']['level'], 4)
        self.assertEqual(audit['summary']['points'], 68.75)
        self.assertEqual(audit['summary']['reviewed_weight'], 87.5)
        self.assertEqual(audit['distribution']['goal']['levels'], {'judge-1': 3, 'judge-2': 4, 'judge-3': 4})
        self.assertEqual(audit['ballots'], original)
        self.assertEqual(self.ballots, original)
        for index in range(1, 4):
            self.assertIn(f'Judge {index}', candidate['criteria']['goal']['reason'])

    def test_large_spread_blocks_final_score_without_losing_proposed_median(self):
        self.ballots[0]['review']['criteria']['goal'].update(level=1, improvement='Fix objective evidence.')
        candidate, audit = self.aggregate()
        self.assertIsNone(candidate['criteria']['goal']['level'])
        self.assertEqual(audit['distribution']['goal']['proposed_median'], 3)
        self.assertIn('goal', audit['needs_adjudication'])
        self.assertEqual(audit['summary']['points'], 56.25)
        self.assertIn('Fix objective evidence.', candidate['criteria']['goal']['improvement'])

    def test_minority_failure_is_not_hidden_by_close_scores(self):
        for index, ballot in enumerate(self.ballots):
            ballot['review']['criteria']['goal'].update(level=0 if index == 0 else 1,
                                                        improvement='Investigate failed goal.')
        candidate, audit = self.aggregate()
        self.assertIsNone(candidate['criteria']['goal']['level'])
        self.assertIn('goal', audit['needs_adjudication'])

    def test_partial_verification_and_all_unverified_remain_distinct(self):
        self.ballots[0]['review']['criteria']['goal'].update(level=None, evidence=[], improvement='Check missing evidence.')
        candidate, audit = self.aggregate()
        self.assertIsNone(candidate['criteria']['goal']['level'])
        self.assertIn('goal', audit['needs_adjudication'])
        self.assertIsNone(candidate['criteria']['explanation']['level'])
        self.assertNotIn('explanation', audit['needs_adjudication'])
        self.assertEqual(audit['distribution']['explanation']['unverified_judges'], 3)

    def test_five_judges_have_an_odd_median(self):
        ballots = [self.ballot(index) for index in range(1, 6)]
        for index, ballot in enumerate(ballots):
            ballot['review']['criteria']['goal']['level'] = 3 if index < 2 else 4
        candidate, audit = self.aggregate(ballots, 5)
        self.assertEqual(candidate['criteria']['goal']['level'], 4)
        self.assertEqual(audit['judge_count'], 5)

    def test_duplicate_wrong_model_and_wrong_count_are_rejected(self):
        original = copy.deepcopy(self.ballots)
        self.ballots[1] = copy.deepcopy(self.ballots[0])
        with self.assertRaisesRegex(InvalidChallenge, 'unique'):
            self.aggregate()
        self.ballots = copy.deepcopy(original)
        self.ballots[0]['model'] = 'another-model'
        with self.assertRaisesRegex(InvalidChallenge, 'gpt-6-luna'):
            self.aggregate()
        self.ballots = original
        with self.assertRaisesRegex(InvalidChallenge, 'exactly'):
            self.aggregate(self.ballots[:2])

    def test_changed_snapshot_is_rejected(self):
        (self.snapshot / 'challenges/sample/README.md').write_text('Modified input.\n')
        with self.assertRaisesRegex(InvalidChallenge, 'snapshot changed'):
            self.aggregate()

    def test_invented_citation_is_rejected(self):
        self.ballots[0]['review']['criteria']['goal']['evidence'][0]['quote'] = 'Invented claim.'
        with self.assertRaisesRegex(InvalidChallenge, 'quote'):
            self.aggregate()

    def test_source_symlink_is_rejected_before_copy(self):
        (self.root / 'challenges/sample/link').symlink_to(self.directory / 'private')
        with self.assertRaisesRegex(InvalidChallenge, 'symlinks'):
            PANEL.prepare(self.root, 'sample', self.directory / 'new-snapshot')


if __name__ == '__main__':
    unittest.main()
