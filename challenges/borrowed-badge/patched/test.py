import runpy
functions = runpy.run_path('solve/solve.py')
get, read = functions['get'], functions['read']
assert read('locker/team-notes') == (200, '팀 회의는 금요일입니다.')
assert get('/history?resource=locker%2Fteam-notes')[0] == 200
assert get('/version?resource=locker%2Fteam-notes&version=r1') == (200, '팀 회의는 목요일입니다.')
for resource in ['locker/team-admin', 'locker/team-notes-backup', 'locker/personal-draft', 'locker/TEAM-notes', 'locker/team-*']:
    status, body = read(resource)
    assert status == 403 and 'pwnden{' not in body, resource
    for route in ['/history', '/version']:
        status, body = get(route + '?' + functions['urlencode']({'resource': resource, 'version': 'r1'}))
        assert status == 403 and 'pwnden{' not in body, (route, resource)
assert read('')[0] == 400
assert read('x' * 129)[0] == 400
assert get('/healthz')[0] == 200
assert get('/')[0] == 200 and 'pwnden{' not in get('/')[1]
print('shared current and historical notes remain readable; private current and historical documents stay denied')
