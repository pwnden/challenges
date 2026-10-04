"""Static target assets cannot expose files outside their presentation directory."""
import http.client
import json
from http.server import ThreadingHTTPServer
from pathlib import Path
import tempfile
import re
from threading import Thread
import unittest
from unittest.mock import patch

from web.server import TargetHandler


class TargetTests(unittest.TestCase):
    def test_assets_containment_mime_and_document_negotiation(self):
        class Handler(TargetHandler):
            def do_GET(self):
                if not self.assets():
                    self.page(200, {'user': 'guest'})

        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            public = root / 'public'
            (public / 'assets').mkdir(parents=True)
            (public / 'index.html').write_text('<html><head></head><body><div id="app"></div></body></html>')
            (public / 'assets/app.js').write_text('export default 1')
            (root / 'secret.txt').write_text('synthetic secret')
            with patch('web.server.PUBLIC', public):
                server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
                thread = Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    client = http.client.HTTPConnection(*server.server_address, timeout=3)
                    for path in ['/assets/../../secret.txt', '/assets/%2e%2e/%2e%2e/secret.txt', '/assets/missing.js']:
                        client.request('GET', path)
                        response = client.getresponse()
                        self.assertEqual(response.status, 404)
                        self.assertNotIn(b'synthetic secret', response.read())
                    client.request('GET', '/assets/app.js')
                    response = client.getresponse()
                    self.assertTrue(response.getheader('Content-Type').startswith('text/javascript'))
                    self.assertEqual(response.read(), b'export default 1')
                    for accept, expected in [('text/html', b'<div'), ('application/json', b'"user"')]:
                        client.request('GET', '/', headers={'Accept': accept})
                        response = client.getresponse()
                        self.assertEqual(response.status, 200)
                        self.assertIn(expected, response.read())
                    client.close()
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join()

    def test_html_bootstrap_preserves_status_cookies_and_escaped_document_data(self):
        body = '</script><script>alert(1)</script>& Korean: 한글'

        class Handler(TargetHandler):
            def do_GET(self):
                if self.path == '/denied':
                    self.page(401, {'error': 'sign_in_required'})
                else:
                    self.document(200, body, ('session=fixture; HttpOnly',))

        with tempfile.TemporaryDirectory() as name:
            public = Path(name)
            (public / 'index.html').write_text('<html><head></head><body><div id="app"></div></body></html>')
            with patch('web.server.PUBLIC', public):
                server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
                thread = Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    client = http.client.HTTPConnection(*server.server_address, timeout=3)
                    for path, status, data in [('/document', 200, {'body': body}), ('/denied', 401, {'error': 'sign_in_required'})]:
                        client.request('GET', path, headers={'Accept': 'text/html'})
                        response = client.getresponse()
                        html = response.read().decode('utf-8')
                        self.assertEqual(response.status, status)
                        self.assertEqual(response.getheader('Cache-Control'), 'no-store')
                        self.assertEqual(response.getheader('X-Content-Type-Options'), 'nosniff')
                        self.assertNotIn('<script>alert(1)', html)
                        encoded = re.search(r'<script id="pwnden-page-data" type="application/json">(.*?)</script>', html).group(1)
                        self.assertEqual(json.loads(encoded), {'status': status, 'data': data})
                        if status == 200:
                            self.assertEqual(response.getheader('Set-Cookie'), 'session=fixture; HttpOnly')
                    client.request('GET', '/document', headers={'Accept': 'application/json'})
                    response = client.getresponse()
                    self.assertTrue(response.getheader('Content-Type').startswith('text/plain'))
                    self.assertEqual(response.read().decode('utf-8'), body)
                    client.close()
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join()
