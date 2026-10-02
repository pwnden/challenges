"""Static target assets cannot expose files outside their presentation directory."""
import http.client
from http.server import ThreadingHTTPServer
from pathlib import Path
import tempfile
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
            (public / 'index.html').write_text('<div id="app"></div>')
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
