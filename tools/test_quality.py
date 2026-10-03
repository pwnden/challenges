"""Review coverage, weighted scores, evidence and source freshness boundaries."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from quality import check_catalog, load_rubric, source_digest, validate_review
from validate import InvalidChallenge

ROOT = Path(__file__).resolve().parents[1]


class QualityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / 'quality/reviews').mkdir(parents=True)
        (self.root / 'knowledge').mkdir()
        (self.root / 'knowledge/base.md').write_text('Shared starting knowledge.\n')
        (self.root / 'contract.toml').write_text('version = 7\n')
        (self.root / 'quality/rubric.json').write_bytes((ROOT / 'quality/rubric.json').read_bytes())
        self.directory = self.root / 'challenges/sample'
        self.directory.mkdir(parents=True)
        (self.directory / 'challenge.toml').write_text('title = "Sample"\n')
        (self.directory / 'README.md').write_text('Observed boundary.\n')
        self.rubric = load_rubric(self.root)
        criteria = {}
        for key, item in self.rubric['criteria'].items():
            criteria[key] = {'level': None if key in {'browser', 'learner'} else 3,
                             'reason': 'Evidence was inspected.', 'improvement': ''}
            criteria[key]['evidence'] = [] if criteria[key]['level'] is None else [
                {'path': 'challenges/sample/README.md', 'quote': 'Observed boundary.',
                 'kind': item['evidence_kind']}]
            if criteria[key]['level'] is None:
                criteria[key]['improvement'] = 'Run and record this session.'
        self.record = {'slug': 'sample', 'rubric_version': 1, 'reviewed_at': '2026-10-03',
                       'reviewer': 'Test reviewer', 'criteria': criteria}
        self.refresh()

    def refresh(self):
        paths = [e['path'] for item in self.record['criteria'].values() for e in item['evidence']]
        self.record['source_sha256'] = source_digest(self.root, 'sample', paths)
        (self.root / 'quality/reviews/sample.json').write_text(json.dumps(self.record))

    def check(self):
        return validate_review(self.root, 'sample', self.rubric, self.record)

    def test_unverified_does_not_gain_points_or_coverage(self):
        result = check_catalog(self.root)[0]
        self.assertEqual((result['points'], result['reviewed_weight']), (60, 80))
        self.assertEqual(result['pending'], ['browser', 'learner'])
        self.assertEqual(len(result['improvements']), 2)
        self.record['criteria']['goal']['level'] = 4
        self.assertEqual(self.check()['points'], 62.5)

    def test_failed_is_evaluated_and_distinct_from_unverified(self):
        self.record['criteria']['goal'].update(level=0, improvement='Correct the missing objective.')
        result = self.check()
        self.assertEqual((result['points'], result['reviewed_weight']), (52.5, 80))
        self.assertNotIn('goal', result['pending'])

    def test_changed_challenge_shared_knowledge_and_rubric_are_stale(self):
        for relative in ['challenges/sample/README.md', 'knowledge/base.md', 'quality/rubric.json']:
            path = self.root / relative
            original = path.read_bytes()
            path.write_bytes(original + b'\n')
            with self.subTest(path=relative), self.assertRaisesRegex(InvalidChallenge, 'stale'):
                self.check()
            path.write_bytes(original)
        self.check()

    def test_referenced_control_change_is_stale_even_when_quote_remains(self):
        (self.root / 'control.py').write_text('Observed boundary.\nold_control\n')
        self.record['criteria']['controls']['evidence'][0]['path'] = 'control.py'
        self.refresh()
        (self.root / 'control.py').write_text('Observed boundary.\nnew_control\n')
        with self.assertRaisesRegex(InvalidChallenge, 'stale'):
            self.check()

    def test_shared_service_source_change_invalidates_service_review(self):
        (self.directory / 'challenge.toml').write_text('title = "Sample"\ncompose = "compose.yaml"\n')
        (self.root / 'web').mkdir()
        (self.root / 'web/server.py').write_text('old implementation\n')
        self.refresh()
        (self.root / 'web/server.py').write_text('new implementation\n')
        with self.assertRaisesRegex(InvalidChallenge, 'stale'):
            self.check()

    def test_missing_and_orphan_reviews_fail(self):
        path = self.root / 'quality/reviews/sample.json'
        original = path.read_bytes()
        path.unlink()
        with self.assertRaisesRegex(InvalidChallenge, 'exactly'):
            check_catalog(self.root)
        path.write_bytes(original)
        (path.parent / 'orphan.json').write_bytes(original)
        with self.assertRaisesRegex(InvalidChallenge, 'exactly'):
            check_catalog(self.root)

    def test_invalid_levels_missing_criteria_and_unsupported_versions(self):
        original = copy.deepcopy(self.record)
        for level in [-1, 5, True, 3.5, '3']:
            self.record = copy.deepcopy(original)
            self.record['criteria']['goal']['level'] = level
            with self.subTest(level=level), self.assertRaises(InvalidChallenge):
                self.check()
        self.record = copy.deepcopy(original)
        del self.record['criteria']['goal']
        with self.assertRaisesRegex(InvalidChallenge, 'missing'):
            self.check()
        self.record = copy.deepcopy(original)
        self.record['rubric_version'] = 2
        with self.assertRaisesRegex(InvalidChallenge, 'version'):
            self.check()

    def test_pending_partial_and_scored_need_actions_or_evidence(self):
        original = copy.deepcopy(self.record)
        for key, field, value in [('browser', 'improvement', ''), ('goal', 'reason', ''),
                                  ('goal', 'evidence', [])]:
            self.record = copy.deepcopy(original)
            self.record['criteria'][key][field] = value
            with self.subTest(key=key, field=field), self.assertRaises(InvalidChallenge):
                self.check()
        self.record = copy.deepcopy(original)
        self.record['criteria']['goal']['level'] = 2
        with self.assertRaisesRegex(InvalidChallenge, 'improvement'):
            self.check()

    def test_citations_require_existing_quote_and_correct_evidence_kind(self):
        evidence = self.record['criteria']['execution']['evidence'][0]
        evidence['kind'] = 'source'
        with self.assertRaisesRegex(InvalidChallenge, 'recorded-execution'):
            self.check()
        evidence['kind'] = 'recorded-execution'
        evidence['quote'] = 'Absent quotation.'
        with self.assertRaisesRegex(InvalidChallenge, 'quote'):
            self.check()
        evidence['quote'] = '::objective'
        with self.assertRaisesRegex(InvalidChallenge, 'content'):
            self.check()

    def test_evidence_cannot_escape_or_use_scores_to_justify_itself(self):
        evidence = self.record['criteria']['goal']['evidence'][0]
        evidence['path'] = '../outside.md'
        with self.assertRaisesRegex(InvalidChallenge, 'outside'):
            self.check()
        evidence['path'] = 'quality/rubric.json'
        with self.assertRaisesRegex(InvalidChallenge, 'own evidence'):
            self.check()
        evidence['path'] = 'challenges/sample/escape.md'
        (self.directory / 'escape.md').symlink_to(self.root.parent / 'outside.md')
        with self.assertRaisesRegex(InvalidChallenge, 'outside'):
            self.check()

    def test_current_catalog_has_complete_fresh_reviews(self):
        results = check_catalog(ROOT)
        slugs = {path.parent.name for path in (ROOT / 'challenges').glob('*/challenge.toml')}
        self.assertEqual({item['slug'] for item in results}, slugs)
        self.assertTrue(all(0 <= item['points'] <= item['reviewed_weight'] <= 100 for item in results))


if __name__ == '__main__':
    unittest.main()
