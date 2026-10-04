"""Execution boundaries, interruption and cleanup of author-owned verification."""

import copy
from contextlib import nullcontext, redirect_stdout
import csv
import json
import io
import os
from pathlib import Path
import signal
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from runtime import (Commands, Docker, ExecutionError, GATEWAY_KEYS, OWNER_LABEL,
                     Project, Result, check_network, isolated_config, toolbox_mount)
from validate import InvalidChallenge
from policy import tool_options
from budget import limits, tool_cost


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        admission_mock = patch('runtime.admission', side_effect=lambda *a, **kw: nullcontext())
        admission_mock.start()
        self.addCleanup(admission_mock.stop)
        temporary = tempfile.TemporaryDirectory(prefix='pwnden-author-policy-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.directory = self.root / 'challenges' / 'sample'
        self.directory.mkdir(parents=True)
        (self.directory / 'Dockerfile').write_text('FROM scratch\n')
        (self.directory / 'data').write_text('data')
        self.project = 'pwnden-author-test'
        self.metadata = {'solve': {'network': 'default'}, 'endpoints': [{'name': 'web', 'service': 'app'}]}
        self.cfg = {'name': self.project,
                    'services': {'app': {'build': {'context': str(self.directory), 'dockerfile': 'Dockerfile'},
                                         'environment': {'FLAG': 'pwnden{test}'},
                                         'ports': [{'target': 8000, 'published': '8000'}],
                                         'healthcheck': {'test': ['CMD', 'check']},
                                         'networks': {'default': None}}},
                    'networks': {'default': {'name': self.project + '_default'}},
                    'volumes': {'data': {'name': self.project + '_data'}}}

    def isolate(self, cfg=None):
        return isolated_config(self.root, self.directory, self.metadata, self.project, cfg or self.cfg)

    def test_tighter_cpu_ceiling_matches_admission_and_execution(self):
        with patch.dict(os.environ, {'PWNDEN_CONTAINER_CPUS': '1'}):
            result = self.isolate()['services']['app']
            options = tool_options(False)
            self.assertEqual(result['cpus'], 1)
            self.assertEqual(options[options.index('--cpus')+1], '1')
            self.assertEqual(tool_cost().cpus, 1_000_000_000)
            self.assertEqual(limits({'NCPU': 4, 'MemTotal': 8*1024**3}).cpus, 4_000_000_000)
            self.assertEqual(result['mem_limit'], '2g')
            self.assertTrue(result['read_only'])

    def test_invalid_cpu_ceiling_is_rejected_before_execution(self):
        for value in ('0', '3', '-1', '1.5', ' 1', 'one'):
            with self.subTest(value=value), patch.dict(os.environ, {'PWNDEN_CONTAINER_CPUS': value}):
                for operation in (self.isolate, lambda: tool_options(False), tool_cost,
                                  lambda: limits({'NCPU': 4, 'MemTotal': 8*1024**3})):
                    with self.assertRaisesRegex(ExecutionError, 'must be 1 or 2'):
                        operation()

    def test_preserves_target_and_enforces_all_networks(self):
        self.cfg['networks']['private'] = {'name': self.project + '_private'}
        self.cfg['services']['app']['security_opt'] = ['no-new-privileges:false']
        before = copy.deepcopy(self.cfg)
        result = self.isolate()
        self.assertEqual(self.cfg, before)
        app = result['services']['app']
        self.assertNotIn('ports', app)
        for field in ['environment', 'healthcheck', 'networks']:
            self.assertEqual(app[field], before['services']['app'][field])
        self.assertEqual(app['cap_drop'], ['ALL'])
        self.assertEqual(app['security_opt'], ['no-new-privileges:true'])
        for network in result['networks'].values():
            self.assertTrue(network['internal'])
            self.assertEqual(network['driver_opts'], dict.fromkeys(GATEWAY_KEYS, 'isolated'))

    def test_rejects_host_access(self):
        values = {'privileged': True, 'use_api_socket': True, 'devices': ['/dev/kvm'],
                  'cap_add': ['SYS_ADMIN'], 'pid': 'host', 'ipc': 'host',
                  'network_mode': 'host', 'provider': {'type': 'host'},
                  'credential_spec': {'file': '/credentials'}, 'volumes_from': ['other'],
                  'gpus': ['all'], 'device_cgroup_rules': ['a *:* rwm'],
                  'post_start': [{'command': 'true', 'privileged': True}],
                  'pre_start': [{'command': 'true', 'privileged': True}],
                  'pre_stop': [{'command': 'true', 'privileged': True}],
                  'userns_mode': 'host', 'cgroup': 'host', 'cgroup_parent': '/host',
                  'runtime': 'custom', 'uts': 'host'}
        for key, value in values.items():
            cfg = copy.deepcopy(self.cfg)
            cfg['services']['app'][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(InvalidChallenge, 'host privileges'):
                self.isolate(cfg)

    def test_rejects_custom_security_profiles(self):
        for option in ('seccomp:unconfined', 'apparmor:unconfined', 'seccomp:/host/profile',
                       'systempaths:unconfined', 'label:disable'):
            cfg = copy.deepcopy(self.cfg)
            cfg['services']['app']['security_opt'] = [option]
            with self.subTest(option=option), self.assertRaisesRegex(InvalidChallenge, 'security profile'):
                self.isolate(cfg)

    def test_bounded_storage_rejects_writable_host_mounts_and_replicas(self):
        for setting in ({'scale': 2}, {'deploy': {'replicas': 0}},
                        {'volumes': [{'type':'bind', 'source':str(self.directory), 'target':'/data'}]}):
            cfg = copy.deepcopy(self.cfg)
            cfg['services']['app'].update(setting)
            with self.subTest(setting=setting), self.assertRaises(InvalidChallenge):
                self.isolate(cfg)
        result = self.isolate()
        self.assertEqual(result['volumes']['data']['driver_opts'],
                         {'type':'tmpfs', 'device':'tmpfs', 'o':'size=256m,nosuid,nodev,nr_inodes=32768,mode=1777'})

    def test_author_limits_cannot_override_runtime_policy(self):
        app = self.cfg['services']['app']
        app.update(cpus=99, mem_limit='64g', memswap_limit=-1, pids_limit=-1,
                   cpu_quota=-1, oom_kill_disable=True, read_only=False,
                   deploy={'resources': {'limits': {'cpus': '99', 'memory': '64g'}}},
                   logging={'driver': 'syslog'}, tmpfs=['/tmp:size=1g', '/run:size=1m'],
                   volumes=[{'type': 'tmpfs', 'target': '/tmp'}])
        result = self.isolate()['services']['app']
        self.assertEqual((result['cpus'], result['mem_limit'], result['memswap_limit'], result['pids_limit']),
                         (2, '2g', '2g', 256))
        self.assertTrue(result['read_only'])
        self.assertFalse(result['oom_kill_disable'])
        self.assertNotIn('cpu_quota', result)
        self.assertNotIn('resources', result['deploy'])
        self.assertEqual(result['logging']['driver'], 'local')
        self.assertEqual(result['volumes'], [])
        self.assertEqual(result['tmpfs'], ['/run:rw,exec,nosuid,nodev,size=256m,nr_inodes=32768', '/tmp:rw,exec,nosuid,nodev,size=128m'])

    def test_rejects_external_and_unowned_resources(self):
        changes = [('networks', 'external', True), ('networks', 'name', 'unrelated'),
                   ('networks', 'driver', 'host'), ('networks', 'driver_opts', {'custom': 'host'}),
                   ('volumes', 'external', True), ('volumes', 'name', 'shared'),
                   ('volumes', 'driver_opts', {'device': '/home'})]
        for kind, field, value in changes:
            cfg = copy.deepcopy(self.cfg)
            cfg[kind]['default' if kind == 'networks' else 'data'][field] = value
            with self.subTest(kind=kind, field=field), self.assertRaises(InvalidChallenge):
                self.isolate(cfg)

    def test_repository_sources_and_build_permissions(self):
        outside = self.root.parent / 'outside-input'
        for resource in ['bind', 'context', 'dockerfile', 'secret', 'config', 'env_file', 'cache_from', 'cache_to']:
            cfg = copy.deepcopy(self.cfg)
            app = cfg['services']['app']
            if resource == 'bind':
                app['volumes'] = [{'type': 'bind', 'source': str(outside), 'target': '/outside', 'read_only': True}]
            elif resource in ('context', 'dockerfile'):
                app['build'][resource] = str(outside)
            elif resource in ('secret', 'config'):
                cfg[resource + 's'] = {'input': {'file': str(outside)}}
            elif resource == 'env_file':
                app['env_file'] = [{'path': str(outside), 'required': False}]
            else:
                attribute = 'src' if resource == 'cache_from' else 'dest'
                app['build'][resource] = [f'type=local,{attribute}={outside}']
            with self.subTest(resource=resource), self.assertRaisesRegex(InvalidChallenge, 'outside'):
                self.isolate(cfg)
        for field in ['ssh', 'privileged', 'entitlements', 'additional_contexts']:
            cfg = copy.deepcopy(self.cfg)
            cfg['services']['app']['build'][field] = ['host']
            with self.subTest(field=field), self.assertRaisesRegex(InvalidChallenge, 'host build'):
                self.isolate(cfg)

    def test_symlink_and_normalized_cache_traversal(self):
        with tempfile.TemporaryDirectory(prefix='pwnden-author-outside-') as tmp:
            outside = Path(tmp)
            link = self.directory / 'link'
            try:
                link.symlink_to(outside, target_is_directory=True)
            except OSError as error:
                self.skipTest(str(error))
            for path in [link / 'cache', link / '..' / 'cache']:
                cfg = copy.deepcopy(self.cfg)
                cfg['services']['app']['build']['cache_to'] = [f'type=local,dest={path}']
                with self.subTest(path=path), self.assertRaisesRegex(InvalidChallenge, 'outside'):
                    self.isolate(cfg)

    def test_accepts_internal_mounts_and_cache_csv(self):
        app = self.cfg['services']['app']
        app['volumes'] = [{'type': 'bind', 'source': str(self.directory / 'data'), 'target': '/data', 'read_only': True},
                          {'type': 'volume', 'source': 'data', 'target': '/state'},
                          {'type': 'tmpfs', 'target': '/tmp'}]
        app['build']['cache_to'] = ['TYPE=local,"dest=cache,output"']
        self.isolate()
        mount = toolbox_mount(self.directory / 'a,b c', False)
        self.assertIn(f'source={self.directory / "a,b c"}', next(csv.reader([mount])))
        self.assertTrue(mount.endswith(',readonly'))

    def test_live_network_ownership_and_complete_isolation(self):
        network = {'Id': 'id', 'Name': self.project + '_default', 'Driver': 'bridge', 'Internal': True,
                   'Options': dict.fromkeys(GATEWAY_KEYS, 'isolated'),
                   'Labels': {'com.docker.compose.project': self.project,
                              'com.docker.compose.network': 'default'}}
        check_network(network, self.project)
        cases = [{'Internal': False}, {'Driver': 'host'}, {'Name': 'outside'}, {'Labels': {}},
                 {'Options': {GATEWAY_KEYS[0]: 'isolated'}},
                 {'Options': {**network['Options'], 'unexpected': 'true'}}]
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaises(ExecutionError):
                check_network({**network, **changes}, self.project)

    def test_partial_start_failure_cleans_frozen_project(self):
        docker = Docker()
        project = Project(docker, self.directory, self.project, self.isolate(), {'FLAG': 'secret'})
        calls = []
        def call(*args, **kwargs):
            calls.append((args, kwargs))
            if 'create' in args:
                raise ExecutionError('failed after resources were created')
            if '{{json .Config.Volumes}}' in args:
                return Result(0, 'null')
            return Result(0)
        with patch.object(docker, 'call', side_effect=call), self.assertRaisesRegex(ExecutionError, 'failed after'):
            with project.running():
                self.fail('should not start')
        down = next(kwargs for args, kwargs in calls if 'down' in args)
        self.assertTrue(down['cleanup'])
        self.assertEqual(json.loads(down['input']), project.cfg)
        self.assertEqual(len([args for args, _ in calls if '--filter' in args]), 3)

    def test_cleanup_failure_cannot_report_success(self):
        docker = Docker()
        project = Project(docker, self.directory, self.project, self.isolate(), {})
        with patch.object(project, 'compose', return_value=Result(0)), \
             patch.object(project, 'check_mounts'), \
             patch.object(project, 'networks', return_value=[]), \
             patch.object(docker, 'call', side_effect=lambda *args, **kw: Result(0, 'null' if '{{json .Config.Volumes}}' in args else 'leftover')):
            with self.assertRaisesRegex(ExecutionError, 'cleanup left project containers'):
                with project.running():
                    pass

    def test_tool_policy_and_timeout_cleanup(self):
        docker = Docker()
        metadata = {'solve': {'writable': False, 'timeout_seconds': 3}}
        calls = []
        def call(*args, **kwargs):
            calls.append((args, kwargs))
            if args[0] == 'start':
                raise ExecutionError('timeout')
            if '{{json .Config.Volumes}}' in args:
                return Result(0, 'null')
            if args[0] == 'ps':
                return Result(0, 'owned-id\n')
            return Result(0)
        with patch.object(docker, 'call', side_effect=call), self.assertRaisesRegex(ExecutionError, 'timeout'):
            docker.tool(self.directory, metadata, 'none', 'image', ['solve'])
        run, options = next((args, kwargs) for args, kwargs in calls if args[0] == 'create')
        for value in ['--cap-drop', 'ALL', 'no-new-privileges', f'{OWNER_LABEL}={docker.owner}',
                      '--read-only', '--user', '10001:10001', '--pids-limit', '256',
                      '--memory-swap', '2g', '/tmp:rw,exec,nosuid,nodev,size=128m']:
            self.assertIn(value, run)
        self.assertEqual(next(kwargs['timeout'] for args, kwargs in calls if args[0] == 'start'), 3)
        removal = next((args, kwargs) for args, kwargs in calls if args[0] == 'rm')
        self.assertTrue(removal[1]['cleanup'])
        self.assertEqual(removal[0][-1], 'owned-id')

    def test_commands_timeout_and_interrupt_allow_cleanup(self):
        commands = Commands()
        with self.assertRaisesRegex(ExecutionError, 'timed out'):
            commands.run([sys.executable, '-c', 'import time; time.sleep(10)'], timeout=0.02)
        self.assertIsNone(commands.child)
        commands.interrupted = 2
        with self.assertRaisesRegex(ExecutionError, 'interrupted'):
            commands.run([sys.executable, '-c', 'pass'])
        self.assertEqual(commands.run([sys.executable, '-c', 'pass'], cleanup=True).code, 0)

    def test_commands_bound_output_and_still_accept_input(self):
        commands = Commands()
        for stream in ('stdout', 'stderr'):
            with self.subTest(stream=stream), self.assertRaisesRegex(ExecutionError, 'output exceeded'):
                commands.run([sys.executable, '-c',
                              f'import sys; sys.{stream}.buffer.write(b"x" * (9 * 1024 * 1024))'], timeout=3)
        result = commands.run([sys.executable, '-c',
                               'import sys; sys.stdout.write(sys.stdin.read()); sys.stderr.write("error")'],
                              input='input', timeout=3)
        self.assertEqual((result.stdout, result.stderr), ('input', 'error'))

    def test_generated_flags_are_redacted(self):
        commands = Commands()
        commands.secrets.add('pwnden{secret}')
        with self.assertRaises(ExecutionError) as caught:
            commands.run([sys.executable, '-c', 'import sys; sys.stderr.write("pwnden{secret}"); sys.exit(1)'])
        self.assertNotIn('pwnden{secret}', str(caught.exception))

    def test_failure_includes_stdout_diagnostics_and_redacts_before_truncation(self):
        commands = Commands()
        secret = 'pwnden{' + 's' * 5000 + '}'
        commands.secrets.add(secret)
        with self.assertRaises(ExecutionError) as caught:
            commands.run([sys.executable, '-c',
                          'import sys; print("failed problem: " + sys.argv[1]); sys.exit(1)', secret])
        self.assertIn('failed problem: [redacted flag]', str(caught.exception))
        self.assertNotIn('s' * 20, str(caught.exception))

    def test_long_stage_reports_progress_while_preserving_captured_output(self):
        monotonic = time.monotonic
        origin = monotonic()
        output = io.StringIO()
        with patch('runtime.time.monotonic', side_effect=lambda: (monotonic() - origin) * 100), redirect_stdout(output):
            result = Commands().run([sys.executable, '-c',
                                     'import time; print("captured"); time.sleep(0.5)'],
                                    progress='Isolation', timeout=300)
        self.assertIn('Isolation: running', output.getvalue())
        self.assertEqual(result.stdout, 'captured\n')
        self.assertNotIn('captured', output.getvalue())

    @unittest.skipIf(sys.platform == 'win32', 'POSIX child signal handler')
    def test_parent_timeout_allows_child_cleanup(self):
        marker = self.root / 'cleaned'
        source = ('import pathlib,signal,time,sys; '
                  f'signal.signal(signal.SIGTERM, lambda *_: (pathlib.Path({str(marker)!r}).write_text("cleaned"), sys.exit(0))); '
                  'print("ready",flush=True); time.sleep(30)')
        with self.assertRaisesRegex(ExecutionError, 'timed out'):
            Commands().run([sys.executable, '-c', source], timeout=1, timeout_grace=3)
        self.assertEqual(marker.read_text(), 'cleaned')

    @unittest.skipIf(sys.platform == 'win32', 'POSIX child signal handler')
    def test_interrupt_ends_child_that_ignores_termination(self):
        commands = Commands()
        source = 'import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(30)'
        timer = threading.Timer(0.5, commands.interrupt, args=(signal.SIGTERM, None))
        started = time.monotonic()
        timer.start()
        try:
            with self.assertRaisesRegex(ExecutionError, 'interrupted'):
                commands.run([sys.executable, '-c', source], timeout=20)
        finally:
            timer.cancel()
            timer.join()
        self.assertLess(time.monotonic() - started, 5)
        self.assertIsNone(commands.child)


if __name__ == '__main__':
    unittest.main()
