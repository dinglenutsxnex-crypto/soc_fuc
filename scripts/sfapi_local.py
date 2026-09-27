"""Local auth server: answers POST/GET /api with exact 7-byte Success. Stdlib only."""
from http.server import BaseHTTPRequestHandler, HTTPServer

BODY = b'Success'

class H(BaseHTTPRequestHandler):
    def _ok(self):
        try:
            ln = int(self.headers.get('Content-Length', 0) or 0)
        except Exception:
            ln = 0
        if ln:
            self.rfile.read(ln)
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', str(len(BODY)))
        self.end_headers()
        self.wfile.write(BODY)
    def do_GET(self):
        self._ok()
    def do_POST(self):
        self._ok()
    def log_message(self, *a):
        print('REQ', self.command, self.path)

print('sfapi on 127.0.0.1:8000')
HTTPServer(('127.0.0.1', 8000), H).serve_forever()
