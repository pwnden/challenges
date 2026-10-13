"""Keep own-inquiry reads and staff pages working while denying other accounts' data and invitations."""
import runpy
from pathlib import Path

Client = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'solve/solve.py'))['Client']


def check():
    client = Client()
    status, state = client.request('/api/desk')
    assert status == 200 and state['user'] == 'member' and state['role'] == 'member'
    assert [t['id'] for t in state['tickets']] == [310]
    status, body = client.request('/api/ticket?id=310')
    assert status == 200 and body['ticket']['owner'] == 'member'
    assert 'invitation_code' not in body['ticket']
    for path in ('/api/ticket?id=311', '/api/ticket?id=-1', '/api/ticket?id=x'):
        assert client.request(path)[0] in (400, 403, 404)
    assert client.request('/api/ticket?id=311')[0] == 403
    assert client.request('/api/ticket?id=999')[0] == 404
    for body in ({}, {'code': ''}, {'code': 1}, {'code': 'wrong'}):
        assert client.request('/api/invitation', body)[0] in (400, 403)
    assert client.request('/api/staff')[0] == 403
    assert client.request('/api/reset', {})[0] == 200
    assert client.request('/api/staff')[0] == 403
    assert Client().request('/api/ticket?id=310')[0] == 401
    print('own inquiries and reset work; other accounts\' inquiries, invitations and staff page stay denied')


if __name__ == '__main__':
    check()
