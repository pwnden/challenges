from urllib.error import HTTPError
from urllib.request import urlopen


def get(path):
    try:
        with urlopen("http://app:8000" + path, timeout=5) as response:
            return response.status, response.read().decode()
    except HTTPError as error:
        return error.code, error.read().decode()


def check():
    for path in ("/", "/about", "/healthz", "/robots.txt"):
        status, body = get(path)
        assert status == 200 and "pwnden{" not in body, path
    assert "/archive/" not in get("/robots.txt")[1]
    for path in ("/archive/site-backup.txt", "/archive/site-backup.txt?download=1",
                 "/archive/", "/missing"):
        status, body = get(path)
        assert status == 404 and "pwnden{" not in body, path
    print("public archive works; the backup is outside public routes")


if __name__ == "__main__":
    check()
