"""Author-owned Docker execution of the challenges contract."""

from contextlib import contextmanager
import copy
import csv
from dataclasses import dataclass
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import threading
import time
import uuid

from validate import InvalidChallenge, inside
from policy import OUTPUT_LIMIT


GATEWAY_KEYS = ('com.docker.network.bridge.gateway_mode_ipv4',
                'com.docker.network.bridge.gateway_mode_ipv6')
OWNER_LABEL = 'pwnden.author-verification'


class ExecutionError(RuntimeError):
    pass


@dataclass
class Result:
    code: int
    stdout: str = ''
    stderr: str = ''


class Output:
    """Drain one pipe concurrently, keeping a fixed upper bound in memory."""

    def __init__(self, pipe, overflow):
        self.data = bytearray()
        self.pipe, self.overflow = pipe, overflow
        self.thread = threading.Thread(target=self.read, daemon=True)
        self.thread.start()

    def read(self):
        try:
            while chunk := self.pipe.read1(65536):
                remaining = OUTPUT_LIMIT - len(self.data)
                self.data.extend(chunk[:remaining])
                if len(chunk) > remaining:
                    self.overflow.set()
        finally:
            self.pipe.close()

    def text(self):
        return self.data.decode('utf-8', errors='replace')


class Commands:
    """Bound subprocess lifetimes while allowing cleanup after interruption."""

    def __init__(self):
        self.child = None
        self.cleaning = False
        self.interrupted = 0
        self.secrets = set()

    def redact(self, message):
        for secret in self.secrets:
            message = message.replace(secret, '[redacted flag]')
        return message

    def interrupt(self, signum, _frame):
        self.interrupted = signum
        if self.child is not None and self.child.poll() is None and not self.cleaning:
            if os.name == 'nt':
                self.child.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                try:
                    os.killpg(self.child.pid, signum)
                except ProcessLookupError:
                    pass

    @contextmanager
    def signals(self):
        previous = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}
        for sig in previous:
            signal.signal(sig, self.interrupt)
        try:
            yield
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)

    def run(self, args, *, cwd=None, env=None, input=None, timeout=60,
            cleanup=False, check=True, timeout_grace=0):
        if self.interrupted and not cleanup:
            raise ExecutionError('verification interrupted')
        options = {'start_new_session': True} if os.name != 'nt' else {
            'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP}
        self.cleaning = cleanup
        try:
            self.child = subprocess.Popen(
                [str(arg) for arg in args], cwd=cwd, env=env,
                stdin=input if hasattr(input, 'read') else subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                **options)
            overflow = threading.Event()
            stdout, stderr = Output(self.child.stdout, overflow), Output(self.child.stderr, overflow)
            # communicate owns stdin and process waiting; readers own output.
            self.child.stdout = self.child.stderr = None
            if self.interrupted and not cleanup:
                self.interrupt(self.interrupted, None)
            try:
                deadline = time.monotonic() + timeout
                pending = None if input is None or hasattr(input, 'read') else input if isinstance(input, bytes) else input.encode('utf-8')
                while True:
                    if overflow.is_set():
                        self.kill_child()
                        raise ExecutionError('command output exceeded 8 MiB per stream')
                    if self.interrupted and not cleanup:
                        self.finish_child(timeout_grace)
                        raise ExecutionError('verification interrupted')
                    try:
                        self.child.communicate(
                            pending, timeout=min(0.2, max(0, deadline - time.monotonic())))
                        break
                    except subprocess.TimeoutExpired:
                        pending = None
                        if time.monotonic() >= deadline:
                            raise
                for output in (stdout, stderr):
                    while output.thread.is_alive():
                        output.thread.join(timeout=0.05)
                        if overflow.is_set():
                            self.kill_child()
                            raise ExecutionError('command output exceeded 8 MiB per stream')
                        if self.interrupted and not cleanup:
                            self.finish_child(timeout_grace)
                            raise ExecutionError('verification interrupted')
                        if time.monotonic() >= deadline:
                            raise subprocess.TimeoutExpired(args, timeout)
            except subprocess.TimeoutExpired as error:
                self.finish_child(timeout_grace)
                raise ExecutionError(f'{args[0]} timed out after {timeout} seconds') from error
            if overflow.is_set():
                raise ExecutionError('command output exceeded 8 MiB per stream')
            result = Result(self.child.returncode, stdout.text(), stderr.text())
            if self.interrupted and not cleanup:
                raise ExecutionError('verification interrupted')
            if check and result.code:
                raise ExecutionError(self.redact(f'{args[0]} failed ({result.code}): {result.stderr.strip()}'))
            return result
        finally:
            self.child = None
            self.cleaning = False

    def finish_child(self, grace):
        if grace:
            if os.name == 'nt':
                self.child.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                try:
                    os.killpg(self.child.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            try:
                self.child.communicate(timeout=grace)
                return
            except subprocess.TimeoutExpired:
                pass
        self.kill_child()

    def kill_child(self):
        if os.name == 'nt':
            self.child.kill()
        else:
            try:
                os.killpg(self.child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        self.child.communicate()


def repository_source(root, directory, value, *, exists=True, regular=False):
    if not isinstance(value, str) or not value or '://' in value:
        raise InvalidChallenge('execution source must be a repository path')
    raw = Path(value)
    if not raw.is_absolute():
        raw = directory / raw
    # Resolve parent traversal through symlinks as well as a builder's normalized path.
    candidates = (raw, Path(os.path.abspath(raw)))
    for candidate in candidates:
        resolved = inside(root, candidate)
        if exists and not resolved.exists():
            raise InvalidChallenge(f'execution source does not exist: {value}')
        if regular and not resolved.is_file():
            raise InvalidChallenge(f'execution source must be a regular file: {value}')
    return str(inside(root, raw))


def cache_sources(root, directory, entries, attribute):
    for entry in entries or []:
        if '=' not in entry:
            continue
        try:
            attributes = {}
            for field in next(csv.reader([entry], strict=True)):
                key, separator, value = field.partition('=')
                if not separator:
                    raise InvalidChallenge('invalid build cache attributes')
                attributes[key.lower()] = value
        except csv.Error as error:
            raise InvalidChallenge('invalid build cache attributes') from error
        if attributes.get('type') == 'local':
            repository_source(root, directory, attributes.get(attribute), exists=False)


def isolated_config(root, directory, metadata, project, resolved):
    """Validate the complete Compose model and preserve it with isolated networking."""
    cfg = copy.deepcopy(resolved)
    services = cfg.get('services', {})
    networks = cfg.get('networks', {})
    if not isinstance(services, dict) or not services:
        raise InvalidChallenge('service problem must define services')
    network_key = metadata['solve']['network']
    if network_key not in networks:
        raise InvalidChallenge(f'solve network {network_key!r} is not defined')
    for key, network in networks.items():
        if (network.get('external') or network.get('name') != f'{project}_{key}'
                or network.get('driver', 'bridge') != 'bridge'):
            raise InvalidChallenge(f'network {key!r} must be a project-scoped bridge')
        for option, value in (network.get('driver_opts') or {}).items():
            if option not in GATEWAY_KEYS or value != 'isolated':
                raise InvalidChallenge(f'network {key!r} requests unsupported driver options')
        network['driver'] = 'bridge'
        network['internal'] = True
        network['driver_opts'] = dict.fromkeys(GATEWAY_KEYS, 'isolated')
    for key, volume in (cfg.get('volumes') or {}).items():
        if (volume.get('external') or volume.get('name') != f'{project}_{key}'
                or volume.get('driver', 'local') != 'local' or volume.get('driver_opts')):
            raise InvalidChallenge(f'volume {key!r} must be a project-scoped local volume')
    for name, service in services.items():
        if (any(service.get(key) for key in ('privileged', 'use_api_socket', 'devices', 'cap_add',
                                            'gpus', 'device_cgroup_rules', 'provider',
                                            'credential_spec', 'volumes_from'))
                or any(hook.get('privileged') for field in ('post_start', 'pre_stop')
                       for hook in service.get(field) or [])
                or service.get('pid') == 'host' or service.get('ipc') == 'host'
                or service.get('network_mode', '') not in ('', 'none')):
            raise InvalidChallenge(f'service {name!r} requests host privileges')
        for mount in service.get('volumes') or []:
            kind = mount.get('type')
            if kind == 'bind':
                mount['source'] = repository_source(root, directory, mount.get('source'))
            elif kind not in ('volume', 'tmpfs'):
                raise InvalidChallenge(f'service {name!r} has an unsupported mount')
        for entry in service.get('env_file') or []:
            value = entry if isinstance(entry, str) else entry.get('path')
            required = True if isinstance(entry, str) else entry.get('required', True)
            repository_source(root, directory, value, exists=required)
        build = service.get('build')
        if build:
            if any(build.get(key) for key in ('ssh', 'privileged', 'entitlements', 'additional_contexts')):
                raise InvalidChallenge(f'service {name!r} requests host build access')
            context = repository_source(root, directory, build.get('context'))
            build['context'] = context
            if build.get('dockerfile'):
                repository_source(root, Path(context), build['dockerfile'], regular=True)
            cache_sources(root, directory, build.get('cache_from'), 'src')
            cache_sources(root, directory, build.get('cache_to'), 'dest')
        service.pop('ports', None)
        service['cap_drop'] = ['ALL']
        service['security_opt'] = [option for option in service.get('security_opt', [])
                                   if not option.startswith('no-new-privileges')]
        service['security_opt'].append('no-new-privileges:true')
    for kind in ('configs', 'secrets'):
        for name, resource in (cfg.get(kind) or {}).items():
            if resource.get('external'):
                raise InvalidChallenge(f'{kind} {name!r} cannot be external')
            if resource.get('file'):
                resource['file'] = repository_source(root, directory, resource['file'], regular=True)
    for endpoint in metadata.get('endpoints', []):
        if endpoint['service'] not in services:
            raise InvalidChallenge(f'endpoint {endpoint["name"]!r} refers to an unknown service')
    return cfg


def check_network(network, project):
    labels = network.get('Labels') or {}
    options = network.get('Options') or {}
    if (network.get('Driver') != 'bridge' or not network.get('Internal')
            or options != dict.fromkeys(GATEWAY_KEYS, 'isolated')
            or labels.get('com.docker.compose.project') != project
            or network.get('Name') != f'{project}_{labels.get("com.docker.compose.network")}'):
        raise ExecutionError('live problem network is not isolated or project-owned')


def toolbox_mount(directory, writable):
    output = io.StringIO()
    fields = ['type=bind', f'source={directory}', 'target=/challenge']
    if not writable:
        fields.append('readonly')
    csv.writer(output, lineterminator='').writerow(fields)
    return output.getvalue()


class Docker:
    def __init__(self, commands=None, prepare_timeout=300):
        self.commands = commands or Commands()
        self.prepare_timeout = prepare_timeout
        self.owner = uuid.uuid4().hex

    def call(self, *args, **kwargs):
        return self.commands.run(['docker', *args], **kwargs)

    def prerequisites(self):
        version = self.call('version', '--format', '{{.Server.Version}}').stdout.strip()
        try:
            major = int(version.split('.')[0])
        except ValueError as error:
            raise ExecutionError('cannot read Docker Engine version') from error
        if major < 28:
            raise ExecutionError('Docker Engine 28 or newer is required for isolated networks')
        self.call('compose', 'version', '--short')

    def prepare_image(self, image):
        if self.call('image', 'inspect', image, check=False).code:
            self.call('pull', image, timeout=self.prepare_timeout)

    def project(self, root, directory, metadata, flag, *, patched=False):
        suffix = '-patched' if patched else ''
        name = f'pwnden-author-{self.owner[:12]}-{metadata["slug"]}{suffix}'
        files = [metadata['compose']]
        if patched:
            files.append(metadata['patched']['compose'])
        env = {**os.environ, 'FLAG': flag}
        self.commands.secrets.add(flag)
        args = ['compose', '--project-directory', str(directory), '-p', name]
        for file in files:
            args.extend(['-f', file])
        # Check env_file paths before Compose reads their contents into environment.
        preliminary = self.call(*args, 'config', '--no-env-resolution', '--format', 'json',
                                 cwd=directory, env=env).stdout
        isolated_config(root, directory, metadata, name, json.loads(preliminary))
        raw = self.call(*args, 'config', '--format', 'json', cwd=directory, env=env).stdout
        cfg = isolated_config(root, directory, metadata, name, json.loads(raw))
        return Project(self, directory, name, cfg, env)

    def tool(self, directory, metadata, network, image, args):
        self.prepare_image(image)
        name = f'pwnden-author-tool-{uuid.uuid4().hex}'
        writable = metadata['solve']['writable']
        options = ['run', '--rm', '--name', name, '--label', f'{OWNER_LABEL}={self.owner}',
                   '--network', network, '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
                   '--mount', toolbox_mount(directory, writable), '--workdir', '/challenge']
        if writable and hasattr(os, 'geteuid'):
            options.extend(['--user', f'{os.geteuid()}:{os.getegid()}'])
        try:
            result = self.call(*options, '--', image, *args, check=False,
                               timeout=metadata['solve']['timeout_seconds'])
            if result.code < 0 or result.code >= 125:
                raise ExecutionError(self.commands.redact(f'toolbox launch/signal failure: {result.stderr.strip()}'))
            return result
        finally:
            self.remove_tool(name)

    def remove_tool(self, name):
        # Inspect by our unique owner label, never remove a colliding user's container.
        result = self.call('ps', '-aq', '--filter', f'name=^/{name}$', '--filter',
                           f'label={OWNER_LABEL}={self.owner}', cleanup=True)
        ids = result.stdout.split()
        if ids:
            self.call('rm', '-f', '-v', *ids, cleanup=True)


class Project:
    def __init__(self, docker, directory, name, cfg, env):
        self.docker, self.directory, self.name, self.cfg, self.env = docker, directory, name, cfg, env
        self.started = False

    def compose(self, *args, **kwargs):
        return self.docker.call('compose', '--project-directory', str(self.directory), '-p', self.name,
                                '-f', '-', *args, input=json.dumps(self.cfg),
                                cwd=self.directory, env=self.env, **kwargs)

    @contextmanager
    def running(self):
        try:
            self.started = True  # A failed up can already have created project resources.
            self.compose('up', '-d', '--build', '--wait', '--wait-timeout', '60',
                         timeout=self.docker.prepare_timeout)
            self.networks()
            yield self
        finally:
            if self.started:
                self.compose('down', '--volumes', '--remove-orphans', timeout=120, cleanup=True)
                self.assert_removed()

    def networks(self):
        ids = self.docker.call('network', 'ls', '--no-trunc', '--filter',
                               f'label=com.docker.compose.project={self.name}', '--format', '{{.ID}}').stdout.split()
        if not ids:
            raise ExecutionError('problem has no isolated network')
        networks = json.loads(self.docker.call('network', 'inspect', *ids).stdout)
        if len(networks) != len(ids):
            raise ExecutionError('incomplete live network inspection')
        for network in networks:
            check_network(network, self.name)
        return networks

    def network(self, key):
        for network in self.networks():
            if network['Labels'].get('com.docker.compose.network') == key:
                return network['Id']
        raise ExecutionError(f'solve network {key!r} is not running')

    def assert_removed(self):
        for kind, args in (('containers', ('ps', '-aq')), ('networks', ('network', 'ls', '-q')),
                           ('volumes', ('volume', 'ls', '-q'))):
            remaining = self.docker.call(*args, '--filter', f'label=com.docker.compose.project={self.name}',
                                         cleanup=True).stdout.strip()
            if remaining:
                raise ExecutionError(f'cleanup left project {kind}: {self.name}')
