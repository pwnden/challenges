"""Check author runtime isolation against reachable host and peer controls on Linux."""

import argparse
from contextlib import ExitStack
import json
from pathlib import Path
import socket

from create import IMAGE
from runtime import Docker, ExecutionError, OWNER_LABEL, Project, isolated_config


def check_isolation(root, *, docker=None):
    root = root.resolve()
    docker = docker or Docker()
    name = f'pwnden-author-{docker.owner[:12]}-isolation'
    control = name + '-control'
    solve = {'image': IMAGE, 'network': 'default', 'timeout_seconds': 30, 'writable': False}
    metadata = {'slug': 'isolation', 'solve': solve, 'endpoints': [{'name': 'web', 'service': 'app'}]}
    cfg = {'name': name, 'services': {'app': {
        'image': IMAGE, 'command': ['python3', '-m', 'http.server', '8000', '--directory', '/tmp'],
        'read_only': True, 'networks': {'default': None},
        'healthcheck': {'test': ['CMD', 'python3', '-c',
                               'import urllib.request; urllib.request.urlopen("http://127.0.0.1:8000", timeout=2).read()'],
                        'interval': '1s', 'timeout': '3s', 'retries': 10}}},
        'networks': {'default': {'name': name + '_default'}}}
    project = Project(docker, root, name, isolated_config(root, root, metadata, name, cfg), None)

    def remove_network():
        ids = docker.call('network', 'ls', '-q', '--filter', f'label={OWNER_LABEL}={docker.owner}',
                          '--filter', f'name=^{control}$', cleanup=True).stdout.split()
        if ids:
            docker.call('network', 'rm', *ids, cleanup=True)

    with docker.commands.signals(), ExitStack() as stack:
        docker.prerequisites()
        docker.prepare_image(IMAGE)
        stack.callback(remove_network)
        docker.call('network', 'create', '--internal', '--label', f'{OWNER_LABEL}={docker.owner}', control)
        network = json.loads(docker.call('network', 'inspect', control).stdout)[0]
        host = network['IPAM']['Config'][0]['Gateway']
        listener = stack.enter_context(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        try:
            listener.bind((host, 0))
        except OSError as error:
            raise ExecutionError('host control requires a locally accessible Linux Docker bridge') from error
        listener.listen(8)
        port = listener.getsockname()[1]
        stack.callback(docker.remove_tool, control)
        docker.call('run', '-d', '--name', control, '--label', f'{OWNER_LABEL}={docker.owner}',
                    '--network', control, '--read-only', '--cap-drop', 'ALL',
                    '--security-opt', 'no-new-privileges', IMAGE,
                    'python3', '-m', 'http.server', '8000', '--directory', '/tmp')
        container = json.loads(docker.call('inspect', control).stdout)[0]
        peer = container['NetworkSettings']['Networks'][control]['IPAddress']
        positive = f'''import socket,time
socket.create_connection(({host!r},{port}),timeout=2).close()
deadline=time.monotonic()+5
while True:
    try:
        socket.create_connection(('127.0.0.1',8000),timeout=1).close()
        break
    except OSError:
        if time.monotonic()>=deadline: raise
        time.sleep(0.05)
'''
        docker.call('exec', control, 'python3', '-c', positive)
        print('Host and separate-network positive controls are reachable.', flush=True)
        with project.running():
            probe = f'''import socket,urllib.request
assert urllib.request.urlopen('http://app:8000/',timeout=3).status==200
for label,host,port in [('Internet IPv4','1.1.1.1',443),('Internet DNS','example.com',443),
                        ('Internet IPv6','2606:4700:4700::1111',443),
                        ('host',{host!r},{port}),('other network',{peer!r},8000)]:
    try:
        connection=socket.create_connection((host,port),timeout=2)
    except OSError:
        print('blocked',label)
    else:
        connection.close()
        raise SystemExit('forbidden connection succeeded: '+label)
print('same-problem HTTP passed')
'''
            result = docker.tool(root, metadata, project.network('default'), IMAGE, ['python3', '-c', probe])
            if result.code:
                raise ExecutionError(f'isolation probe failed: {result.stderr.strip()}')
            print(result.stdout, end='', flush=True)
    print('Isolation check and control cleanup passed.', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    options = parser.parse_args()
    try:
        check_isolation(options.repo)
    except (OSError, ValueError, ExecutionError) as error:
        parser.exit(1, f'isolation: {error}\n')


if __name__ == '__main__':
    main()
