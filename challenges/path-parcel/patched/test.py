import runpy
functions = runpy.run_path('solve/solve.py')
get, view = functions['get'], functions['view']
for name in ['welcome.txt', './welcome.txt', 'guide.txt']:
    status, body = view(name)
    assert status == 200 and 'pwnden{' not in body, name
for name in ['../private/recovery.txt', './../private/recovery.txt', 'sub/../../private/recovery.txt', '/tmp/parcels/private/recovery.txt', '../public-other/test.txt']:
    status, body = view(name)
    assert status == 403 and 'pwnden{' not in body, name
assert view('missing.txt')[0] == 404
assert view('')[0] == 400
assert view('\x00')[0] == 400
assert get('/healthz')[0] == 200
assert get('/')[0] == 200
print('public reads work and normalized paths cannot leave the public directory')
