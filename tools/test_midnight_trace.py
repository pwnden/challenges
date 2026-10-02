"""Check that the evidence supports one conclusion, independent of log order."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest


SOURCE = Path(__file__).resolve().parents[1] / 'challenges' / 'midnight-trace'


class MidnightTraceTests(unittest.TestCase):
    def setUp(self):
        self.access = [json.loads(line) for line in (SOURCE / 'files/access.log').read_text().splitlines()
                       if not line.startswith('#')]
        self.audit = [json.loads(line) for line in (SOURCE / 'files/audit.jsonl').read_text().splitlines()]

    def solve(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / 'files').mkdir()
            for filename, rows in [('access.log', self.access), ('audit.jsonl', self.audit)]:
                (root / 'files' / filename).write_text('\n'.join(json.dumps(row) for row in rows), encoding='utf-8')
            return subprocess.run([sys.executable, '-B', str(SOURCE / 'solve/solve.py')], cwd=root,
                                  capture_output=True, text=True, timeout=10)

    def test_distributed_evidence_and_reordered_logs_select_the_same_key(self):
        baseline = self.solve()
        self.assertEqual(baseline.returncode, 0, baseline.stderr)
        metadata = tomllib.loads((SOURCE / 'challenge.toml').read_text())
        self.assertEqual(hashlib.sha256(baseline.stdout.strip().encode()).hexdigest(), metadata['flag']['sha256'])
        self.access.reverse()
        self.audit.sort(key=lambda row: row['request_id'])
        reordered = self.solve()
        self.assertEqual(reordered.returncode, 0, reordered.stderr)
        self.assertEqual(baseline.stdout, reordered.stdout)

    def test_denied_request_does_not_establish_disclosure(self):
        next(row for row in self.access if row['request_id'] == 'req-205')['status'] = 403
        self.assertNotEqual(self.solve().returncode, 0)

    def test_own_export_does_not_establish_disclosure(self):
        next(row for row in self.audit if row['request_id'] == 'req-205')['owner'] = 'guest'
        self.assertNotEqual(self.solve().returncode, 0)

    def test_two_candidate_leaks_are_ambiguous(self):
        next(row for row in self.audit if row['request_id'] == 'req-202')['owner'] = 'ops'
        self.assertNotEqual(self.solve().returncode, 0)

    def test_duplicate_audit_ids_are_ambiguous(self):
        self.audit.append(dict(self.audit[0]))
        self.assertNotEqual(self.solve().returncode, 0)


if __name__ == '__main__':
    unittest.main()
