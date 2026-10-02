"""Problem-specific tmpfs workspace shared until the verification environment ends."""
import hashlib
from itertools import chain
import json
import tarfile
import tempfile
from pathlib import Path

from budget import admission, Cost

IMAGE = 'busybox:1.37.0-musl@sha256:5cec3fc171c87218698e85a52af7087de727372aae264a787b8112901a5b0092'
OPTIONS = 'size=256m,nosuid,nodev,nr_inodes=32768,uid=10001,gid=10001,mode=0700'
COST = Cost(250_000_000, 512*1024**2, 32, 1)
SIZE, INODES = 256*1024**2, 32768


def ensure_workspace(docker, directory, network):
    previous = set(docker.workspaces)
    try:
        return _ensure_workspace(docker, directory, network)
    except Exception:
        for project in set(docker.workspaces)-previous:
            remove_workspace(docker, project)
        raise


def _ensure_workspace(docker, directory, network):
    from runtime import ExecutionError, OWNER_LABEL
    directory = Path(directory)
    project = docker.network_projects.get(network, f'pwnden-author-{docker.owner[:12]}-file-'+hashlib.sha256(str(directory).encode()).hexdigest()[:8])
    name, volume = project+'-workspace', project+'_pwnden-workspace'
    docker.prepare_image(IMAGE)
    with admission(docker.call, interrupted=lambda: docker.commands.interrupted) as check:
        exists = docker.call('container', 'ls', '--all', '--filter', 'name=^/'+name+'$', '--format', '{{.ID}}').stdout.strip()
        if exists:
            check_workspace(docker, project)
            docker.call('exec', name, '/bin/test', '-f', '/state/ready')
            return volume
        check(COST)
        if docker.call('volume', 'ls', '--filter', 'name=^'+volume+'$', '--format', '{{.Name}}').stdout.strip():
            raise ExecutionError('workspace volume exists without its keeper; stop the environment before retrying')
        with tempfile.TemporaryFile() as archive:
            with tarfile.open(fileobj=archive, mode='w') as output:
                size = entries = 0
                # tarfile never follows symlinks; only regular files and directories
                # may contribute bytes, and special input files are rejected.
                for path in chain((directory,), directory.rglob('*')):
                    info = output.gettarinfo(str(path), arcname=str(path.relative_to(directory)))
                    if not (info.isfile() or info.isdir() or info.issym()):
                        raise ExecutionError('workspace input must be a file, directory or symlink')
                    size += info.size
                    entries += 1
                    if size > SIZE or entries > INODES:
                        raise ExecutionError('problem source exceeds the temporary workspace quota')
                    info.uid = info.gid = 10001
                    info.uname = info.gname = ''
                    info.mode = (info.mode & 0o777) | (0o700 if info.isdir() else 0o600)
                    if info.isfile():
                        with path.open('rb') as source:
                            output.addfile(info, source)
                    else:
                        output.addfile(info)
            archive.seek(0)
            labels = [f'{OWNER_LABEL}={docker.owner}', 'pwnden.managed=true', 'pwnden.kind=workspace',
                      'pwnden.project='+project, 'pwnden.workspace-policy=tmpfs-v1']
            flags = [part for label in labels for part in ('--label', label)]
            docker.workspaces[project] = volume  # Cleanup also owns partial initialization.
            docker.call('volume', 'create', '--driver', 'local', '--opt', 'type=tmpfs', '--opt', 'device=tmpfs', '--opt', 'o='+OPTIONS, *flags, volume)
            actual, = json.loads(docker.call('volume', 'inspect', volume).stdout)
            if actual['Labels'].get(OWNER_LABEL) != docker.owner or actual['Options'] != {'type':'tmpfs','device':'tmpfs','o':OPTIONS}:
                raise ExecutionError('workspace volume ownership or quota changed')
            docker.call('create', '--name', name, '--network', 'none', '--user', '10001:10001',
                        '--read-only', '--cgroupns', 'private', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
                        '--cpus', '0.25', '--memory', '512m', '--memory-swap', '512m', '--pids-limit', '32',
                        '--log-driver', 'local', '--log-opt', 'max-size=10m', '--log-opt', 'max-file=3',
                        '--tmpfs', '/state:rw,noexec,nosuid,nodev,size=1m,nr_inodes=32,uid=10001,gid=10001,mode=0700',
                        '--mount', 'type=volume,source='+volume+',target=/challenge,volume-nocopy',
                        '--entrypoint', '/bin/sleep', *flags, IMAGE, '2147483647')
            docker.call('start', name)
            docker.call('exec', '-i', name, '/bin/tar', '-x', '-f', '-', '-C', '/challenge', input=archive)
            docker.call('exec', name, '/bin/touch', '/state/ready')
    return volume


def check_workspace(docker, project):
    from runtime import ExecutionError, OWNER_LABEL
    item, = json.loads(docker.call('container', 'inspect', project+'-workspace').stdout)
    cfg, host = item['Config'], item['HostConfig']
    labels = cfg.get('Labels') or {}
    volumes = json.loads(docker.call('volume', 'inspect', project+'_pwnden-workspace').stdout)
    if (labels.get(OWNER_LABEL) != docker.owner or labels.get('pwnden.project') != project
            or labels.get('pwnden.kind') != 'workspace' or labels.get('pwnden.workspace-policy') != 'tmpfs-v1'
            or cfg['Image'] != IMAGE or cfg['User'] != '10001:10001'
            or cfg['Entrypoint'] != ['/bin/sleep'] or cfg['Cmd'] != ['2147483647']
            or not item['State']['Running'] or host['NetworkMode'] != 'none' or not host['ReadonlyRootfs']
            or host['NanoCpus'] != COST.cpus or host['Memory'] != COST.memory or host['MemorySwap'] != COST.memory
            or host['PidsLimit'] != COST.pids or host['CapDrop'] != ['ALL'] or host.get('CapAdd')
            or host['SecurityOpt'] != ['no-new-privileges'] or host['CgroupnsMode'] != 'private'
            or host.get('Privileged') or host.get('PortBindings') or host.get('Devices') or host.get('DeviceRequests')
            or host.get('PidMode') or host.get('UTSMode') or host.get('UsernsMode') or host.get('IpcMode') != 'private'
            or host['Tmpfs'] != {'/state':'rw,noexec,nosuid,nodev,size=1m,nr_inodes=32,uid=10001,gid=10001,mode=0700'}
            or host['LogConfig'] != {'Type':'local','Config':{'max-file':'3','max-size':'10m'}}
            or len(item['Mounts']) != 1 or len(volumes) != 1 or volumes[0]['Driver'] != 'local'
            or volumes[0]['Labels'].get(OWNER_LABEL) != docker.owner
            or volumes[0]['Options'] != {'type': 'tmpfs', 'device': 'tmpfs', 'o': OPTIONS}):
        raise ExecutionError('existing workspace ownership or quota changed')
    mount, = item['Mounts']
    if mount['Type'] != 'volume' or mount['Name'] != project+'_pwnden-workspace' or mount['Destination'] != '/challenge' or not mount['RW']:
        raise ExecutionError('workspace mount changed')


def remove_workspace(docker, project):
    if project not in docker.workspaces:
        return
    with admission(lambda *args, **kwargs: docker.call(*args, cleanup=True, **kwargs), accounting=False):
        _remove_workspace(docker, project)


def _remove_workspace(docker, project):
    from runtime import OWNER_LABEL
    if project not in docker.workspaces:
        return
    volume = docker.workspaces[project]
    ids = docker.call('container', 'ls', '--all', '--filter', 'name=^/'+project+'-workspace$', '--filter',
                      f'label={OWNER_LABEL}={docker.owner}', '--format', '{{.ID}}', cleanup=True).stdout.split()
    if ids:
        docker.call('rm', '-f', '-v', *ids, cleanup=True)
    names = docker.call('volume', 'ls', '--filter', 'name=^'+volume+'$', '--filter',
                        f'label={OWNER_LABEL}={docker.owner}', '--format', '{{.Name}}', cleanup=True).stdout.split()
    if names:
        docker.call('volume', 'rm', *names, cleanup=True)
    docker.workspaces.pop(project, None)
