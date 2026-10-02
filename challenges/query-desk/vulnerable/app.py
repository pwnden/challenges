"""A real SQLite search target with a replaceable query policy."""
from contextlib import closing
from http.server import ThreadingHTTPServer
import json
import os
import sqlite3
from urllib.parse import parse_qs, urlsplit

from policy import search
from web.server import TargetHandler


def lookup(name):
    with closing(sqlite3.connect(":memory:")) as database:
        database.execute("CREATE TABLE members (name TEXT, note TEXT, public INTEGER)")
        database.executemany("INSERT INTO members VALUES (?, ?, ?)", [
            ("mira", "전시 안내를 정리하는 사람", 1),
            ("sol", "야간 게시판을 관리하는 사람", 1),
            ("keeper", os.environ["FLAG"], 0),
        ])
        return search(database, name)


class Handler(TargetHandler):
    reply = TargetHandler.send
    def do_GET(self):
        if self.assets():
            return
        url = urlsplit(self.path)
        if url.path == "/healthz":
            self.reply(200, "ok", "text/plain")
            return
        if url.path not in ("/", "/api/search"):
            self.reply(404, "찾을 수 없습니다.", "text/plain")
            return
        name = parse_qs(url.query, keep_blank_values=True).get("name", [""])[0]
        if len(name) > 256:
            self.reply(400, "검색어는 256자 이내로 입력하세요.", "text/plain")
            return
        try:
            query, rows = lookup(name)
            result = {"query": query, "matches": [{"name": row[0], "note": row[1]} for row in rows]}
        except sqlite3.Error:
            result = {"error": "검색 조건의 문법을 확인하세요.", "matches": []}
        if url.path == "/api/search":
            self.reply(200, json.dumps(result, ensure_ascii=False), "application/json")
            return
        self.page(200, result)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
