"""Evidence provenance, ambiguous records and patched policy semantics."""
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import runpy
import tempfile
import tomllib
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1] / 'challenges'


class EvidenceTests(unittest.TestCase):
    def test_password_evidence_selects_one_candidate_and_matches_submission_digest(self):
        directory = ROOT / 'hash-lantern'
        account = dict(line.split('=', 1) for line in (directory / 'files/account.txt').read_text().splitlines())
        candidates = (directory / 'files/candidates.txt').read_text().splitlines()
        matches = [item for item in candidates if hashlib.sha256(item.encode()).hexdigest() == account['password_hash']]
        self.assertEqual(matches, ['pwnden{rainboat27}'])
        self.assertTrue(all(item.startswith('pwnden{') and item.endswith('}') for item in candidates))
        metadata = tomllib.loads((directory / 'challenge.toml').read_text())
        self.assertEqual(hashlib.sha256(matches[0].encode()).hexdigest(), metadata['flag']['sha256'])
        self.assertNotEqual(hashlib.sha256(b'rainboat27').hexdigest(), account['password_hash'])

    def test_archive_matches_its_reproducible_author_source(self):
        directory = ROOT / 'false-label'
        archive = runpy.run_path(str(directory / 'authoring/build.py'))['archive']
        self.assertEqual((directory / 'files/banner.png').read_bytes(), archive())

    def test_dns_capture_uses_actual_messages_and_retransmits_one_chunk(self):
        directory = ROOT / 'dns-detour'
        capture = runpy.run_path(str(directory / 'authoring/capture.py'))['capture']
        assemble = runpy.run_path(str(directory / 'solve/solve.py'))['assemble']
        rows = capture()
        self.assertEqual(len(rows), 10)
        for identity in range(1001, 1006):
            pair = [row for row in rows if row['id'] == identity]
            self.assertEqual([row['direction'] for row in pair], ['Q', 'R'])
            self.assertEqual(pair[0]['qname'], pair[1]['qname'])
        expected = b'pwnden{dns_leaks_data_ok}'
        self.assertEqual(base64.b32decode(assemble(rows)), expected)
        stored = [json.loads(line) for line in (directory / 'files/dns.jsonl').read_text().splitlines()]
        self.assertEqual(assemble(stored), assemble(rows))
        self.assertEqual(assemble(list(reversed(stored))), assemble(rows))

    def test_dns_missing_and_conflicting_chunks_are_rejected_but_responses_are_not_data(self):
        directory = ROOT / 'dns-detour'
        assemble = runpy.run_path(str(directory / 'solve/solve.py'))['assemble']
        rows = [json.loads(line) for line in (directory / 'files/dns.jsonl').read_text().splitlines()]
        only_responses = [row for row in rows if row['direction'] == 'R']
        with self.assertRaisesRegex(ValueError, 'both query chunks'):
            assemble(only_responses)
        missing = [row for row in rows if not row['qname'].startswith('1-')]
        with self.assertRaisesRegex(ValueError, 'both query chunks'):
            assemble(missing)
        conflict = copy.deepcopy(next(row for row in rows if row['direction'] == 'Q' and row['qname'].startswith('1-')))
        conflict['qname'] = '1-' + 'A' * 20 + '.sync.box.test'
        with self.assertRaisesRegex(ValueError, 'conflicting copies'):
            assemble(rows + [conflict])


class PolicyTests(unittest.TestCase):
    def test_role_patch_preserves_server_roles_and_rejects_client_claims(self):
        directory = ROOT / 'paper-session'
        vulnerable = runpy.run_path(str(directory / 'vulnerable/policy.py'))['role']
        patched = runpy.run_path(str(directory / 'patched/policy.py'))['role']
        sessions = {'known-guest': 'guest', 'known-staff': 'staff'}
        forged = {'paper_sid': 'known-guest', 'paper_role': 'staff'}
        self.assertEqual(vulnerable(forged, sessions), 'staff')
        self.assertEqual(patched(forged, sessions), 'guest')
        self.assertEqual(patched({'paper_sid': 'forged', 'paper_role': 'staff'}, sessions), 'guest')
        self.assertEqual(patched({'paper_sid': 'known-staff', 'paper_role': 'guest'}, sessions), 'staff')

    def test_path_patch_checks_directory_boundaries_and_symlink_targets(self):
        locate = runpy.run_path(str(ROOT / 'path-parcel/patched/policy.py'))['locate']
        with tempfile.TemporaryDirectory() as name:
            public = Path(name) / 'public'
            public.mkdir()
            outside = Path(name) / 'private'
            outside.mkdir()
            self.assertEqual(locate(public, './file.txt'), public / 'file.txt')
            for request in ['../private/key.txt', '../public-other/key.txt', str(outside / 'key.txt')]:
                with self.subTest(request=request), self.assertRaises(PermissionError):
                    locate(public, request)
            try:
                (public / 'link').symlink_to(outside, target_is_directory=True)
            except OSError as error:
                self.skipTest(f'symlink unavailable: {error}')
            with self.assertRaises(PermissionError):
                locate(public, 'link/key.txt')

    def test_local_policy_distinguishes_current_and_historical_reads_with_deny_precedence(self):
        with patch.dict(os.environ, {'FLAG': 'synthetic-test-key'}):
            module = runpy.run_path(str(ROOT / 'borrowed-badge/vulnerable/app.py'))
        allowed = module['allowed']
        self.assertFalse(allowed('read', 'locker/team-admin'))
        self.assertTrue(allowed('read-history', 'locker/team-admin'))
        self.assertTrue(allowed('read-version', 'locker/team-admin'))
        self.assertFalse(allowed('write', 'locker/team-admin'))
        self.assertFalse(allowed('read', 'locker/personal-draft'))
        module['POLICY']['Statement'].append({'Effect': 'Deny', 'Action': 'read*', 'Resource': 'locker/team-admin'})
        for action in ['read', 'read-history', 'read-version']:
            self.assertFalse(allowed(action, 'locker/team-admin'))
            self.assertTrue(allowed(action, 'locker/team-notes'))


if __name__ == '__main__':
    unittest.main()
