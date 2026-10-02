import runpy
get = runpy.run_path('solve/solve.py')['get']
status, body, headers = get('/')
assert status == 200 and '작업 노트' in body and 'pwnden{' not in body
session = next(value.split(';')[0] for value in headers.get_all('Set-Cookie') if value.startswith('paper_sid='))
for cookie in ['', 'paper_role=staff', 'paper_sid=forged; paper_role=staff', session + '; paper_role=staff', session + '; paper_role=guest']:
    status, body, _ = get('/key', cookie)
    assert status == 403 and 'pwnden{' not in body, cookie
assert 'guest' in get('/', session + '; paper_role=staff')[1]
assert get('/healthz')[0] == 200
assert get('/missing')[0] == 404
print('guest browsing works and client role claims cannot change the server session')
