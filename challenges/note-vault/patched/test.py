from http.cookiejar import CookieJar
import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener


def request(client, path, data=None):
    headers = {"Content-Type": "application/json"} if data is not None else {}
    payload = json.dumps(data).encode() if data is not None else None
    try:
        with client.open(Request("http://app:8000" + path, data=payload, headers=headers), timeout=5) as response:
            return response.status, response.read()
    except HTTPError as error:
        return error.code, error.read()


def check():
    client = build_opener(HTTPCookieProcessor(CookieJar()))
    assert request(client, "/healthz")[0] == 200
    assert request(client, "/api/notes/1")[0] == 401
    assert request(client, "/login", {"username": "guest", "password": "wrong"})[0] == 401
    assert request(client, "/login", {"username": "guest", "password": "guest"})[0] == 200
    status, body = request(client, "/api/notes")
    assert status == 200 and json.loads(body) == [{"id": 1, "title": "Welcome"}]
    status, body = request(client, "/api/notes/1")
    assert status == 200 and json.loads(body)["body"] == "Your first private note."
    assert request(client, "/notes/1")[0] == 200
    for path in ("/api/notes/2", "/notes/2", "/api/notes/999"):
        status, body = request(client, path)
        assert status == 404 and b"pwnden{" not in body
    assert request(client, "/api/notes/not-a-number")[0] == 400
    form_client = build_opener(HTTPCookieProcessor(CookieJar()))
    login = Request("http://app:8000/login", data=urlencode({"username": "guest", "password": "guest"}).encode())
    with form_client.open(login, timeout=5) as response:
        assert response.status == 200 and json.load(response)['user'] == 'guest'
    assert request(form_client, "/notes/1")[0] == 200
    assert request(form_client, "/notes/2")[0] == 404
    print("guest notes work; private notes stay private")


if __name__ == "__main__":
    check()
