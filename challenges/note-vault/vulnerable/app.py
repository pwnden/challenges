from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import ThreadingHTTPServer
import json
import os
import secrets
from urllib.parse import parse_qs, urlsplit

from policy import read_note
from web.server import TargetHandler

NOTES = {
    1: {"id": 1, "owner": "guest", "title": "Welcome", "body": "Your first private note."},
    2: {"id": 2, "owner": "admin", "title": "Recovery key", "body": os.environ["FLAG"]},
}
SESSIONS = {}


class Handler(TargetHandler):
    def reply(self, status, data, *, cookie=None):
        if urlsplit(self.path).path.startswith('/notes/') and 'text/html' in self.headers.get('Accept', ''):
            self.page(status, data, (cookie,) if cookie else ())
            return
        self.send(status, json.dumps(data), 'application/json', (cookie,) if cookie else ())

    def user(self):
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get("Cookie", ""))
        except Exception:
            return None
        token = cookie.get("session")
        return SESSIONS.get(token.value) if token else None

    def do_GET(self):
        if self.assets():
            return
        path = urlsplit(self.path).path
        if path == "/healthz":
            self.reply(200, {"status": "ok"})
            return
        user = self.user()
        if path == "/":
            self.page(200, {"site": "개인 메모 사이트", "user": user,
                            "notes": [{"id": note["id"], "title": note["title"]}
                                      for note in NOTES.values() if note["owner"] == user]})
            return
        if path != "/api/notes" and not path.startswith(("/api/notes/", "/notes/")):
            self.reply(404, {"error": "not_found"})
            return
        if user is None:
            self.reply(401, {"error": "sign_in_required"})
            return
        if path == "/api/notes":
            self.reply(200, [{"id": note["id"], "title": note["title"]}
                             for note in NOTES.values() if note["owner"] == user])
            return
        try:
            note_id = int(path.rsplit("/", 1)[1])
        except ValueError:
            self.reply(400, {"error": "invalid_note_id"})
            return
        note = read_note(NOTES, note_id, user)
        if note is None:
            self.reply(404, {"error": "not_found"})
        elif path.startswith("/notes/"):
            self.page(200, note)
        else:
            self.reply(200, note)

    def do_POST(self):
        if urlsplit(self.path).path != "/login":
            self.reply(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 4096:
                self.reply(400, {"error": "invalid_body"})
                return
            body = self.rfile.read(length).decode("utf-8")
            is_json = self.headers.get("Content-Type", "").split(";", 1)[0] == "application/json"
            data = json.loads(body) if is_json else {key: values[0] for key, values in parse_qs(body).items()}
            if not isinstance(data, dict):
                raise ValueError("expected an object")
        except (ValueError, UnicodeDecodeError):
            self.reply(400, {"error": "invalid_body"})
            return
        if data.get("username") != "guest" or data.get("password") != "guest":
            self.reply(401, {"error": "invalid_credentials"})
            return
        token = secrets.token_hex(24)
        SESSIONS[token] = "guest"
        cookie = f"session={token}; HttpOnly; SameSite=Lax; Path=/"
        if is_json:
            self.reply(200, {"user": "guest"}, cookie=cookie)
        else:
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", "/")
            self.send_header("Set-Cookie", cookie)
            self.send_header("Content-Length", "0")
            self.end_headers()


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
