"""Capture small real HTTP exchanges from a deterministic local lab fixture.

The fixture models two lab identities and an unprotected legacy export route.
Its logs are teaching evidence, not records from a real production incident.
Run from this challenge directory to regenerate only its distribution files.
"""
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

EXPORTS = {
    "7": ("ops", "pwnden{scheduled_backup_receipt}"),
    "9": ("guest", "pwnden{my_own_export_receipt}"),
    "42": ("ops", "pwnden{follow_the_request_not_the_clock}"),
}
IDENTITIES = {"Bearer operator-lab": "ops", "Bearer guest-lab": "guest"}


def capture():
    access, audit = [], []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_GET(self):
            user = IDENTITIES.get(self.headers.get("Authorization"), "anonymous")
            export = EXPORTS.get(self.path.rsplit("/", 1)[-1])
            guarded = self.path.startswith("/secure-exports/")
            status = 401 if user == "anonymous" else 404 if export is None else 403 if guarded and user != export[0] else 200
            payload = ({"recovery_key": export[1]} if status == 200 else {"error": "request_denied"})
            request_id = f"req-{201 + len(access)}"
            timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
            access.append({"timestamp": timestamp, "request_id": request_id, "user": user,
                           "method": "GET", "path": self.path, "status": status})
            audit.append({"timestamp": timestamp, "request_id": request_id, "action": "export",
                          "owner": export[0] if export else None, "response": payload})
            body = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        for token, path in [
            ("operator-lab", "/exports/7"),
            ("guest-lab", "/exports/9"),
            ("guest-lab", "/secure-exports/42"),
            ("guest-lab", "/exports/99"),
            ("guest-lab", "/exports/42"),
            ("operator-lab", "/exports/7"),
        ]:
            request = Request(f"http://127.0.0.1:{server.server_port}" + path,
                              headers={"Authorization": "Bearer " + token})
            try:
                with urlopen(request, timeout=5) as response:
                    response.read()
            except HTTPError as error:
                error.read()
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)
    root = Path(__file__).resolve().parents[1] / "files"
    root.mkdir(exist_ok=True)
    header = "# Local lab HTTP capture. UTC timestamps; one request per JSON line.\n"
    (root / "access.log").write_text(header + "\n".join(json.dumps(row) for row in access) + "\n", encoding="utf-8", newline="\n")
    # Worker events are deliberately in reverse order: correlate by request ID.
    (root / "audit.jsonl").write_text("\n".join(json.dumps(row) for row in reversed(audit)) + "\n", encoding="utf-8", newline="\n")
    print("Captured six real lab exchanges into files/access.log and files/audit.jsonl")


if __name__ == "__main__":
    capture()
