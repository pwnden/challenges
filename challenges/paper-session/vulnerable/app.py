"""Real cookies with a server-owned guest session and replaceable role policy."""
from html import escape
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
import secrets
from urllib.parse import urlsplit
from policy import role

SID = secrets.token_hex(24)
SESSIONS = {SID: 'guest'}
STYLE = 'body{max-width:48rem;margin:2rem auto;padding:1rem;background:#101722;color:#dae4f2;font:17px/1.7 sans-serif}input,button{font:inherit;padding:.5rem}a{color:#8bbfff}section{margin:1.5rem 0}'


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body, kind='text/plain', cookies=()):
        data = body.encode()
        self.send_response(status)
        self.send_header('Content-Type', kind + '; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        for value in cookies:
            self.send_header('Set-Cookie', value)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        cookie = SimpleCookie()
        cookie.load(self.headers.get('Cookie', ''))
        values = {key: item.value for key, item in cookie.items()}
        path = urlsplit(self.path).path
        if path == '/healthz':
            self.reply(200, 'ok')
        elif path == '/key':
            self.reply(200, '창고 복구 키\n' + os.environ['FLAG']) if role(values, SESSIONS) == 'staff' else self.reply(403, '복구 키는 staff 등급에서 읽을 수 있습니다.')
        elif path == '/':
            current = role(values, SESSIONS)
            cookies = () if values.get('paper_sid') == SID else ('paper_sid=' + SID + '; HttpOnly; Path=/; SameSite=Lax', 'paper_role=guest; Path=/; SameSite=Lax')
            body = '<h1>종이 창고</h1><p>초대 받은 사람은 공개 작업 노트를 읽을 수 있습니다.</p>'
            body += '<p>현재 서버가 판단한 등급: <strong>' + escape(current) + '</strong></p>'
            body += '<section><h2>작업 노트</h2><p>게스트 등급은 guest, 창고 운영 등급은 staff입니다. 운영자는 <a href="/key">복구 키</a>를 보관합니다.</p></section>'
            body += '<section><h2>브라우저 쿠키 편집</h2><p>이 실험용 편집기는 내 브라우저의 paper_role 값을 바꿉니다. 저장 후 서버 판단과 복구 키 응답을 확인하세요.</p><form id="edit"><label>paper_role <input id="claim" value="guest" maxlength="32" pattern="[a-z]+" required></label> <button>저장</button></form></section>'
            body += '<script>const value=document.cookie.split("; ").find(x=>x.startsWith("paper_role="));if(value)document.getElementById("claim").value=decodeURIComponent(value.split("=")[1]);document.getElementById("edit").addEventListener("submit",e=>{e.preventDefault();document.cookie="paper_role="+encodeURIComponent(document.getElementById("claim").value)+"; Path=/; SameSite=Lax";location.reload();});</script>'
            self.reply(200, '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>종이 창고</title><style>' + STYLE + '</style><body>' + body + '</body></html>', 'text/html', cookies)
        else:
            self.reply(404, '페이지를 찾을 수 없습니다.')


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
