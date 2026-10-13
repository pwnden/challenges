"""Check the shared layout rules, the generator's conformance and the real catalog."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import layout
from create import create

REPOSITORY = Path(__file__).resolve().parents[1]
REVIEW = '# review\n'


class LayoutTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='pwnden-layout-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        (self.root / 'contract.toml').write_bytes((REPOSITORY / 'contract.toml').read_bytes())
        (self.root / 'knowledge').mkdir()
        (self.root / 'knowledge/catalog.toml').write_text('concepts = []\n')

    def make(self, slug, **options):
        destination, _ = create(self.root, slug, **options)
        review = self.root / 'quality/text-reviews' / slug
        review.mkdir(parents=True)
        (review / '2026-01-01-review.md').write_text(REVIEW)
        return destination

    def rules(self, destination):
        return {rule for rule, _ in layout.check_challenge(self.root, destination)}

    def test_generated_problems_follow_the_layout(self):
        for slug, options in [('file-sample', {'kind': 'file', 'category': 'rev', 'hints': 2}),
                              ('web-sample', {'kind': 'service', 'category': 'web', 'hints': 1}),
                              ('patched-sample', {'kind': 'service', 'category': 'web', 'patched': True})]:
            with self.subTest(slug=slug):
                self.assertEqual(layout.check_challenge(self.root, self.make(slug, **options)), [])

    def test_current_catalog_follows_the_layout(self):
        self.assertEqual(layout.check_catalog(REPOSITORY), [])

    def test_authoring_title_and_sections_are_enforced(self):
        destination = self.make('authoring-sample', kind='file', category='rev')
        path = destination / 'AUTHORING.md'
        text = path.read_text(encoding='utf-8')
        path.write_text(text.replace('## 난도 근거', '## 난도'), encoding='utf-8')
        self.assertEqual(self.rules(destination), {'authoring'})
        path.write_text(text.replace('# 시나리오 작성 기록', '# 다른 제목', 1), encoding='utf-8')
        self.assertEqual(self.rules(destination), {'authoring'})
        path.write_text(text + '\n## 추가 기록\n\n내용\n', encoding='utf-8')
        self.assertEqual(self.rules(destination), set())

    def test_walkthrough_vocabulary_and_order_are_enforced(self):
        destination = self.make('walkthrough-sample', kind='file', category='rev')
        path = destination / 'solve/README.md'
        text = path.read_text(encoding='utf-8')
        path.write_text(text.replace('## 조사 과정', '## 조사 순서'), encoding='utf-8')
        self.assertEqual(self.rules(destination), {'walkthrough'})
        path.write_text('## 드러난 보안 원리\n\n내용\n\n## 조사 과정\n\n내용\n', encoding='utf-8')
        self.assertEqual(self.rules(destination), {'walkthrough'})
        path.write_text('## 조사 과정\n\n```\n## 조사 순서\n```\n\n## 드러난 보안 원리\n\n내용\n', encoding='utf-8')
        self.assertEqual(self.rules(destination), set())

    def test_hints_are_plain_text(self):
        destination = self.make('hint-sample', kind='file', category='rev', hints=1)
        (destination / 'hints/1.md').write_text('## 제목\n\n내용\n', encoding='utf-8')
        self.assertEqual(self.rules(destination), {'hints'})

    def test_readme_blocks_are_enforced(self):
        destination = self.make('readme-sample', kind='file', category='rev')
        path = destination / 'README.md'
        text = path.read_text(encoding='utf-8')
        path.write_text(text.replace('::message', '::note', 1), encoding='utf-8')
        self.assertEqual(self.rules(destination), {'readme-message'})
        path.write_text(text.replace('::submission', '::answer', 1), encoding='utf-8')
        self.assertEqual(self.rules(destination), {'readme-blocks'})

    def test_service_files_and_policy_names_are_enforced(self):
        destination = self.make('service-sample', kind='service', category='web', patched=True)
        (destination / 'vulnerable/refund_policy.py').write_text('')
        self.assertEqual(self.rules(destination), {'policy-name'})
        (destination / 'vulnerable/refund_policy.py').unlink()
        compose = destination / 'compose.yaml'
        compose.write_text(compose.read_text(encoding='utf-8').replace('    internal: true\n', ''), encoding='utf-8')
        self.assertEqual(self.rules(destination), {'compose'})
        compose.write_text(compose.read_text(encoding='utf-8') + '    ports: ["8000:8000"]\n', encoding='utf-8')
        self.assertEqual(self.rules(destination), {'compose'})

    def test_unknown_entries_and_missing_review_are_reported(self):
        destination = self.make('entry-sample', kind='file', category='rev')
        (destination / 'notes.txt').write_text('')
        self.assertEqual(self.rules(destination), {'entries'})
        (destination / 'notes.txt').unlink()
        (self.root / 'quality/text-reviews/entry-sample/2026-01-01-review.md').unlink()
        self.assertEqual(self.rules(destination), {'text-review'})

    def test_listed_exceptions_hide_one_gap_and_must_not_go_stale(self):
        destination = self.make('exception-sample', kind='file', category='rev')
        path = destination / 'README.md'
        path.write_text(path.read_text(encoding='utf-8').replace('::message', '::note', 1), encoding='utf-8')
        key = ('exception-sample', 'readme-message')
        with patch.dict(layout.EXCEPTIONS, {key: 'test'}, clear=True):
            self.assertEqual(layout.check_catalog(self.root), [])
        with patch.dict(layout.EXCEPTIONS, {}, clear=True):
            self.assertEqual(len(layout.check_catalog(self.root)), 1)
        path.write_text(path.read_text(encoding='utf-8').replace('::note', '::message', 1), encoding='utf-8')
        with patch.dict(layout.EXCEPTIONS, {key: 'test'}, clear=True):
            self.assertIn('no longer needed', layout.check_catalog(self.root)[0])


if __name__ == '__main__':
    unittest.main()
