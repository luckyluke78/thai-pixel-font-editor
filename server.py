"""Local server for the pixel font editor: open, click, see the real font. No terminal steps.

  GET  /              the editor (editor.html), which loads the glyphs by itself
  GET  /glyphs        the glyphs JSON (the one source)
  POST /glyphs        save the JSON, run the build and the look-alike check, answer with the check text
  GET  /<Name>-Regular.woff2   the freshly built font, used by the editor's live preview

Listens on 127.0.0.1 only. Start it from this folder:
  python3 server.py      then open http://127.0.0.1:8720
To edit from a phone or iPad on the same Wi-Fi: HOST=0.0.0.0 python3 server.py, then open http://<this Mac's IP>:8720
(anyone on that Wi-Fi can reach it while it runs; use it at home, not on public Wi-Fi)
"""
import json
import os
import subprocess
import sys
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from build import stem

HERE = Path(__file__).resolve().parent
SRC = HERE / "glyphs.json"
EDITOR = "editor.html"
PORT = int(os.environ.get("PORT", 8720))
HOST = os.environ.get("HOST", "127.0.0.1")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(HERE), **k)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.path = "/" + EDITOR
        if self.path.split("?")[0] == "/glyphs":
            return self.send(200, SRC.read_text("utf-8"))
        return super().do_GET()

    def do_POST(self):
        if self.path != "/glyphs":
            return self.send(404, '{"error": "not found"}')
        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        try:
            data = json.loads(raw)
            assert isinstance(data.get("glyphs"), dict) and data["glyphs"]
        except (ValueError, AssertionError):
            return self.send(400, '{"error": "not a glyphs JSON"}')
        SRC.write_text(json.dumps(data, ensure_ascii=False, indent=1), "utf-8")
        run = lambda script: subprocess.run([sys.executable, script], cwd=HERE, capture_output=True, text=True)
        build = run("build.py")
        if build.returncode:
            return self.send(200, json.dumps({"ok": False, "built": False, "report": build.stderr[-1500:]}))
        check = run("check.py")
        return self.send(200, json.dumps({"ok": check.returncode == 0, "built": True, "report": check.stdout.strip()}))

    def log_message(self, fmt, *args):
        # quiet: one line per save; a missing file (a browser asking for favicon.ico and the like) is not an error
        if args and str(args[0]).startswith("POST"):
            sys.stderr.write(time.strftime("%H:%M:%S") + " saved and rebuilt\n")


if __name__ == "__main__":
    name = json.loads(SRC.read_text("utf-8")).get("name") or "My Pixel Font"
    if not (HERE / (stem(name) + ".woff2")).exists():  # first run on a fresh clone
        subprocess.run([sys.executable, "build.py"], cwd=HERE, check=True)
    try:
        server = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError:
        sys.exit(f"The editor is already running (port {PORT} is taken). Open http://127.0.0.1:{PORT} in Chrome.")
    print(f"Thai Pixel Font Editor: http://127.0.0.1:{PORT}  (keep this window open; Ctrl+C stops it)", flush=True)
    if HOST != "127.0.0.1":
        ip = subprocess.run(["ipconfig", "getifaddr", "en0"], capture_output=True, text=True).stdout.strip()
        print(f"On your phone or iPad (same Wi-Fi): http://{ip or '<this Mac IP>'}:{PORT}", flush=True)
    server.serve_forever()
