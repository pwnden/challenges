"""A real SQLite search target with a replaceable query policy."""
from contextlib import closing
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import sqlite3
from urllib.parse import parse_qs, urlsplit

from policy import search

STYLE = """body{max-width:52rem;margin:3rem auto;padding:1rem;background:#101722;color:#dae4f2;font:17px/1.7 sans-serif}
input,button{font:inherit;padding:.6rem;border:1px solid #6489ad;border-radius:.3rem}
pre{overflow:auto;background:#182334;padding:1rem}table{width:100%;border-collapse:collapse}
td,th{text-align:left;border-bottom:1px solid #34455c;padding:.7rem}a{color:#8bbfff}"""


def lookup(name):
    with closing(sqlite3.connect(":memory:")) as database:
        database.execute("CREATE TABLE members (name TEXT, note TEXT, public INTEGER)")
        database.executemany("INSERT INTO members VALUES (?, ?, ?)", [
            ("mira", "전시 안내를 정리하는 사람", 1),
            ("sol", "야간 게시판을 관리하는 사람", 1),
            ("keeper", os.environ["FLAG"], 0),
        ])
        return search(database, name)


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body, kind="text/html"):
        payload = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", kind + "; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
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
        table = "".join("<tr><td>" + escape(row["name"]) + "</td><td>" + escape(row["note"]) + "</td></tr>"
                        for row in result["matches"])
        details = ('<p role="status">' + escape(result["error"]) + '</p>' if "error" in result else
                   '<h2>이번 검색에 사용한 조건</h2><pre>' + escape(result["query"]) + '</pre>')
        body = ('<h1>회원 검색 데스크</h1><p>공개 회원 mira와 sol의 소개를 검색할 수 있습니다.</p>'
                '<form action="/" method="get"><label>회원 이름 <input name="name" value="' + escape(name, quote=True) +
                '" maxlength="256"></label> <button>검색</button></form>' + details +
                '<h2>검색 결과</h2><table><thead><tr><th>닉네임</th><th>소개</th></tr></thead><tbody>' + table +
                '</tbody></table><p>public = 1은 공개 회원, public = 0은 비공개 회원을 뜻합니다.</p>')
        self.reply(200, '<!doctype html><html lang="ko"><meta charset="utf-8">'
                   '<meta name="viewport" content="width=device-width, initial-scale=1">'
                   '<title>회원 검색 데스크</title><style>' + STYLE + '</style><body>' + body + '</body></html>')


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
