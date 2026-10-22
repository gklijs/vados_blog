"""Serves public/ the way Netlify does, for previewing locally.

Netlify answers /tech/2026 with tech/2026.html and redirects /tech/2026/ to
/tech/2026, even when a tech/2026/ directory exists. Python's plain
http.server shows that directory's listing instead.

Usage: python3 serve.py [port]   (default 8765)
"""

import functools
import http.server
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path != "/" and path.endswith("/"):
            self.send_response(301)
            self.send_header("Location", path.rstrip("/"))
            self.end_headers()
            return
        if path != "/" and os.path.isfile(os.path.join(ROOT, path.lstrip("/") + ".html")):
            self.path = path + ".html"
        super().do_GET()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    handler = functools.partial(Handler, directory=ROOT)
    print(f"Serving {ROOT} at http://localhost:{port}/")
    http.server.ThreadingHTTPServer(("", port), handler).serve_forever()
