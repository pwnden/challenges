"""Concept identities, references and prerequisite graph validation."""
import json
import re
from pathlib import Path
import tempfile
import unittest

from create import create
from validate import InvalidChallenge, load_concepts, load_contract, required_concepts, validate_learning_catalog, validate_manifest

ROOT = Path(__file__).resolve().parents[1]


class LearningTests(unittest.TestCase):
    def test_concept_index_covers_catalog_in_prerequisite_order(self):
        concepts = load_concepts(ROOT)
        reading = re.findall(r'^\| `([^`]+)` \|', (ROOT / 'knowledge/README.md').read_text(), re.MULTILINE)
        self.assertEqual(len(reading), len(set(reading)))
        self.assertEqual(set(reading), set(concepts))
        positions = {key: index for index, key in enumerate(reading)}
        for key, item in concepts.items():
            for parent in item['requires']:
                self.assertLess(positions[parent], positions[key], f'{parent} prepares {key}')

    def test_published_learning_order_covers_catalog_and_precedes_required_practice(self):
        guide = (ROOT / 'docs/learning-order.md').read_text()
        order = re.findall(r'^\| \d+ \| \[[^\]]+\]\(\.\./challenges/([^/]+)/README\.md\)', guide, re.MULTILINE)
        records = [validate_manifest(ROOT, path, load_contract(ROOT))
                   for path in sorted((ROOT / 'challenges').glob('*/challenge.toml'))]
        self.assertEqual(len(order), len(set(order)), 'each exercise has one recommended position')
        self.assertEqual(set(order), {item['slug'] for item in records}, 'update the guide when exercises change')
        concepts = load_concepts(ROOT)
        positions = {slug: index for index, slug in enumerate(order)}
        for item in records:
            needed = required_concepts(item['learning']['requires'], concepts)
            for teacher in records:
                if needed & set(teacher['learning']['teaches']):
                    self.assertLess(positions[teacher['slug']], positions[item['slug']],
                                    f'{teacher["slug"]} prepares {item["slug"]}')

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / 'knowledge').mkdir()
        (self.root / 'contract.toml').write_bytes((ROOT / 'contract.toml').read_bytes())
        self.definition = load_contract(self.root)
        self.items = [{'id': key, 'title': key, 'requires': [], 'related': []} for key in ['base', 'ownership', 'export']]
        self.items[1]['requires'] = ['base']
        self.items[2]['requires'] = ['ownership']
        self.write()

    def write(self):
        lines = []
        for item in self.items:
            lines += ['[[concepts]]', *[f'{key} = {json.dumps(value)}' for key, value in item.items()]]
            (self.root / 'knowledge' / (item['id'] + '.md')).write_text('# Concept\n\nExplanation.\n')
        (self.root / 'knowledge/catalog.toml').write_text('\n'.join(lines))

    def test_creation_and_prerequisite_closure(self):
        path, _ = create(self.root, 'sample', kind='file', category='misc', requires=['ownership'], teaches=['export'])
        item = validate_manifest(self.root, path / 'challenge.toml', self.definition)
        self.assertEqual(item['learning'], {'requires': ['ownership'], 'teaches': ['export']})
        validate_learning_catalog(self.root, [item], self.definition)
        for field, value in [('requires', ['missing']), ('teaches', ['export', 'export']), ('requires', 'ownership'), ('teaches', ['ownership'])]:
            invalid = (path / 'challenge.toml').read_text().replace(f'{field} = '+json.dumps(item['learning'][field]), f'{field} = '+json.dumps(value))
            (path / 'challenge.toml').write_text(invalid)
            with self.subTest(field=field, value=value), self.assertRaises(InvalidChallenge):
                validate_manifest(self.root, path / 'challenge.toml', self.definition)
            # Restore each independent case.
            (path / 'challenge.toml').write_text(invalid.replace(f'{field} = '+json.dumps(value), f'{field} = '+json.dumps(item['learning'][field])))

    def test_missing_duplicate_self_and_cyclic_concepts(self):
        for invalid in ['missing', 'ownership', 'export']:
            self.items[1]['requires'] = [invalid]
            self.write()
            with self.subTest(invalid=invalid), self.assertRaises(InvalidChallenge):
                load_concepts(self.root)
        self.items[1]['requires'] = []
        self.items.append(dict(self.items[0]))
        self.write()
        with self.assertRaisesRegex(InvalidChallenge, 'duplicate'):
            load_concepts(self.root)

    def test_problem_cycles_and_transitive_self_requirement(self):
        self.items[1]['requires'] = []
        self.items[2]['requires'] = []
        self.write()
        records = [ {'slug': 'a', 'learning': {'requires': ['ownership'], 'teaches': ['export']}},
                    {'slug': 'b', 'learning': {'requires': ['export'], 'teaches': ['ownership']}} ]
        with self.assertRaisesRegex(InvalidChallenge, 'cycle'):
            validate_learning_catalog(self.root, records, self.definition)
        self.items[2]['requires'] = ['ownership']
        self.write()
        with self.assertRaisesRegex(InvalidChallenge, 'already required'):
            validate_learning_catalog(self.root, [{'slug': 'a', 'learning': {'requires': ['export'], 'teaches': ['ownership']}}], self.definition)

    def test_concept_documents_remain_contained(self):
        document = self.root / 'knowledge/base.md'
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        outside = Path(temporary.name) / 'outside.md'
        outside.write_text('# Outside\n\nPrivate.\n')
        document.unlink()
        document.symlink_to(outside)
        with self.assertRaisesRegex(InvalidChallenge, 'outside'):
            load_concepts(self.root)


if __name__ == '__main__':
    unittest.main()
