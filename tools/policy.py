"""Runtime-owned limits shared by author service and toolbox execution."""

CPU_LIMIT = 2
MEMORY_LIMIT = '2g'
PID_LIMIT = 256
OUTPUT_LIMIT = 8 * 1024 * 1024
TMP_OPTIONS = 'rw,exec,nosuid,nodev,size=128m'
TOOL_ENV = {'HOME': '/home/pwnden', 'XDG_CACHE_HOME': '/tmp/.cache',
            'POCL_CACHE_DIR': '/tmp/pocl-cache', 'POCL_MAX_PTHREAD_COUNT': '2',
            'OMP_NUM_THREADS': '2'}
SECURITY_OPTIONS = {'no-new-privileges', 'no-new-privileges:true',
                    'no-new-privileges:false', 'no-new-privileges=true',
                    'no-new-privileges=false'}


def service_policy(service):
    """The consumer, rather than an exercise declaration, owns these limits."""
    for key in ('cpu_period', 'cpu_quota', 'cpu_rt_period', 'cpu_rt_runtime',
                'mem_reservation', 'mem_swappiness', 'oom_score_adj'):
        service.pop(key, None)
    deploy = service.get('deploy')
    if deploy:
        deploy.pop('resources', None)
    service.update(cpus=CPU_LIMIT, mem_limit=MEMORY_LIMIT, memswap_limit=MEMORY_LIMIT,
                   pids_limit=PID_LIMIT, oom_kill_disable=False, read_only=True, shm_size='64m',
                   cgroup='private', cap_drop=['ALL'],
                   security_opt=['no-new-privileges:true'],
                   logging={'driver': 'local', 'options': {'max-size': '10m', 'max-file': '3'}})
    service.setdefault('labels', {})['pwnden.runtime-policy'] = 'docker-v2'
    service['labels']['pwnden.managed'] = 'true'
    # Replace an author /tmp mount, retaining other explicitly declared data mounts.
    service['volumes'] = [mount for mount in service.get('volumes') or []
                          if mount.get('target', '').rstrip('/') != '/tmp']
    for mount in service['volumes']:
        if mount['type'] == 'volume':
            mount['volume'] = {'nocopy': True}
        elif mount['type'] == 'tmpfs':
            mount['tmpfs'] = {'size': 256*1024**2, 'mode': 0o1777}
    service['tmpfs'] = [entry.split(':', 1)[0]+':rw,exec,nosuid,nodev,size=256m,nr_inodes=32768'
                        for entry in service.get('tmpfs') or []
                        if entry.split(':', 1)[0].rstrip('/') != '/tmp']
    service['tmpfs'].append('/tmp:' + TMP_OPTIONS)


def tool_options(writable):
    uid, gid = 10001, 10001
    options = ['--user', f'{uid}:{gid}', '--read-only', '--cgroupns', 'private',
               '--cpus', str(CPU_LIMIT), '--memory', MEMORY_LIMIT,
               '--memory-swap', MEMORY_LIMIT, '--pids-limit', str(PID_LIMIT),
               '--tmpfs', '/tmp:' + TMP_OPTIONS,
               '--tmpfs', f'/home/pwnden:rw,nosuid,nodev,uid={uid},gid={gid},size=64m',
               '--log-driver', 'local',
               '--log-opt', 'max-size=10m', '--log-opt', 'max-file=3']
    for key, value in TOOL_ENV.items():
        options.extend(['--env', f'{key}={value}'])
    return options
