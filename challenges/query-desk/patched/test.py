import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen


def get(path):
    try:
        with urlopen("http://app:8000" + path, timeout=5) as response:
            return response.status, response.read().decode()
    except HTTPError as error:
        return error.code, error.read().decode()


def search(name):
    status, body = get("/api/search?" + urlencode({"name": name}))
    assert status == 200
    return json.loads(body)


def check():
    for name, note in (("mira", "전시 안내를 정리하는 사람"), ("sol", "야간 게시판을 관리하는 사람")):
        result = search(name)
        assert result["matches"] == [{"name": name, "note": note}]
        assert "?" in result["query"]
    for name in ("", "keeper", "'", "' OR 1=1 -- ", "' OR public=0 -- ", "mira' -- ", "<script>alert(1)</script>"):
        result = search(name)
        assert "error" not in result and result["matches"] == [], name
    status, body = get("/?" + urlencode({"name": "<script>alert(1)</script>"}))
    assert status == 200 and json.loads(body)['matches'] == []
    status, body = get("/?" + urlencode({"name": "' OR 1=1 -- "}))
    assert status == 200 and "pwnden{" not in body
    assert get("/api/search?" + urlencode({"name": "x" * 257}))[0] == 400
    assert get("/healthz") == (200, "ok")
    assert get("/missing")[0] == 404
    print("public search works; quotes and SQL expressions stay input data")


if __name__ == "__main__":
    check()
