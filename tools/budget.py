"""Serialize container creation and account for all managed Docker ceilings."""
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import time
from execution import ExecutionError

INFO_FORMAT = '{"ID":{{json .ID}},"NCPU":{{.NCPU}},"MemTotal":{{.MemTotal}}}'
MANAGED_LABEL = 'pwnden.managed'


class BudgetError(ExecutionError):
    pass


@dataclass
class Cost:
    cpus: int = 0
    memory: int = 0
    pids: int = 0
    containers: int = 0

    def add(self, other):
        return Cost(self.cpus+other.cpus, self.memory+other.memory,
                    self.pids+other.pids, self.containers+other.containers)


TOOL_COST = Cost(2_000_000_000, 2*1024**3, 256, 1)


def limits(info):
    values = []
    for name, default, multiplier in (
            ('PWNDEN_RUNTIME_CPUS', 8, 1_000_000_000),
            ('PWNDEN_RUNTIME_MEMORY_MIB', 8192, 1024**2),
            ('PWNDEN_RUNTIME_PIDS', 1024, 1),
            ('PWNDEN_RUNTIME_CONTAINERS', 12, 1)):
        value = os.environ.get(name, str(default))
        if not value.isascii() or not value.isdigit() or not 0 < int(value) <= 2**31-1:
            raise BudgetError(f'{name} must be a positive integer')
        values.append(int(value)*multiplier)
    result = Cost(*values)
    result.cpus = min(result.cpus, info['NCPU']*1_000_000_000)
    result.memory = min(result.memory, info['MemTotal'])
    return result


def check(used, requested, maximum):
    total = used.add(requested)
    if (total.cpus > maximum.cpus or total.memory > maximum.memory
            or total.pids > maximum.pids or total.containers > maximum.containers):
        raise BudgetError('pwnden runtime budget exceeded: '
                          f'would use {total.cpus/1e9:.1f}/{maximum.cpus/1e9:.1f} CPUs, '
                          f'{total.memory//1024**2}/{maximum.memory//1024**2} MiB memory, '
                          f'{total.pids}/{maximum.pids} PIDs, '
                          f'{total.containers}/{maximum.containers} containers; '
                          'close another environment or adjust PWNDEN_RUNTIME_*')


def managed(labels, name):
    for entry in labels.split(','):
        key, _, value = entry.partition('=')
        if (key in (MANAGED_LABEL, 'pwnden.runtime-policy')
                or key == 'pwnden.kind' and value in ('tool', 'terminal', 'connector')):
            return True
    return name.startswith(('pwnden-author-tool-', 'pwnden-tool-'))


def live_cost(call):
    rows = call('container', 'ls', '--all', '--format', '{{json .}}').stdout.splitlines()
    used = Cost()
    for line in rows:
        row = json.loads(line)
        if not managed(row.get('Labels', ''), row.get('Names', '')):
            continue
        result = call('container', 'inspect', '--format', '{{json .HostConfig}}', row['ID'], check=False)
        if result.code:
            remaining = call('container', 'ls', '--all', '--filter', 'id='+row['ID'], '--format', '{{.ID}}')
            if not remaining.stdout.strip():
                continue
            raise BudgetError('cannot inspect runtime budget container')
        host = json.loads(result.stdout)
        values = (host.get('NanoCpus'), host.get('Memory'), host.get('PidsLimit'))
        if any(not isinstance(value, int) or value <= 0 for value in values):
            raise BudgetError(f'managed container {row["Names"]} has no resource ceilings; stop and restart its environment')
        used = used.add(Cost(*values, 1))
    return used


@contextmanager
def admission(call, requested=None, *, interrupted=lambda: False, accounting=True):
    # Python author execution is verified on Linux/WSL; the same lock is used
    # by flock in the Go consumer, independently of checkout and user caches.
    import fcntl
    info = json.loads(call('info', '--format', INFO_FORMAT).stdout)
    if not info.get('ID') or info.get('NCPU', 0) <= 0 or info.get('MemTotal', 0) <= 0:
        raise BudgetError('Docker did not report its resource capacity')
    directory = Path('/tmp') / f'pwnden-runtime-{os.geteuid()}'
    directory.mkdir(mode=0o700, exist_ok=True)
    digest = hashlib.sha256(info['ID'].encode()).hexdigest()[:32]
    descriptor = os.open(directory / (digest+'.lock'), os.O_CREAT|os.O_RDWR|os.O_CLOEXEC, 0o600)
    with os.fdopen(descriptor, 'r+') as lock:
        deadline = time.monotonic()+300
        while True:
            if interrupted():
                raise BudgetError('verification interrupted')
            try:
                fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise BudgetError('runtime admission lock unavailable')
                time.sleep(0.05)
        if not accounting:
            yield None
            return
        maximum = limits(info)
        used = live_cost(call)
        checker = lambda cost: check(used, cost, maximum)
        if requested is not None:
            checker(requested)
        yield checker
