"""A static server that gzips text like GitHub Pages does (Lighthouse needs it: plain http.server sends no
compression and makes the homepage look slow).

Usage: .venv/Scripts/python -I tools/qa/gzserve.py [port] [root]    (defaults: 8080, the site root)
"""
import gzip
import http.server
import sys
from pathlib import Path

ROOT = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path(__file__).resolve().parents[2]
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
TEXT = (".html", ".css", ".js", ".svg", ".json", ".webmanifest", ".txt", ".xml")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def send_head(self):
        path = Path(self.translate_path(self.path))
        if path.is_dir():
            if not self.path.split("?")[0].endswith("/"):
                return super().send_head()
            path = path / "index.html"
        if not path.exists():
            body = (ROOT / "404.html").read_bytes()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            from io import BytesIO
            return BytesIO(body)
        if path.suffix in TEXT and "gzip" in self.headers.get("Accept-Encoding", ""):
            body = gzip.compress(path.read_bytes(), 6)
            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(str(path)))
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            from io import BytesIO
            return BytesIO(body)
        return super().send_head()


http.server.ThreadingHTTPServer.allow_reuse_address = True
http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
