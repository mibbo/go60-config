"""The Go60 app page (assets/go60.html): Cheat sheet, Guide (how-tos built from the layout) and Lights
(LED preset editor) tabs.

go60-ui serves it from a small local server, so the Lights tab can save config/led-presets.json.
go60-keys cheatsheet writes the same page as a read-only file (Cheat sheet and Guide, lights shown).
go60-ui --app (the hotkey and app launcher) keeps one server running on a fixed port and opens the page
as an Omarchy web app window, or focuses that window if it is already open.
"""

import http.server
import json
import os
import secrets
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import keymap as km
import leds

TEMPLATE = km.SKILL_DIR / "assets" / "go60.html"
APP_PORT = 46060
APP_TITLE = "Go60 app"   # in the page title; the hotkey finds the open window by it
CACHE = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "go60"
STATE_FILE = CACHE / "ui-server.json"
# Characters the Guide tab's Finnish symbols card explains, with the keys that type them.
GUIDE_SYMBOLS = "{}[]()\\|@$€~<>/=?*'\"#&%^`´¨"


def guide_symbols(L):
    out = []
    for ch in GUIDE_SYMBOLS:
        ways = [{"l": l, "i": i, "mods": sorted(mods), "dead": km.is_dead(code, mods)}
                for l, i, mods, code in km.char_ways(L, ch)]
        out.append({"ch": ch, "ways": ways})
    return out


def page_data(L, presets, editable, tab="cheatsheet"):
    labels = [L.describe(b)["label"] for b in L.layers[0]] if L else [""] * 60
    keys = [{"i": i, "pos": km.position_name(i), "where": km.position_words(i), "finger": km.finger(i),
             "label": labels[i], "p": list(km.POSITIONS[i])} for i in range(60)]
    return {"keys": keys, "layout": km.cheatsheet_data(L) if L else None, "editable": editable, "tab": tab,
            "symbols": guide_symbols(L) if L else [],
            "leds": {"presets": presets, "stock": leds.STOCK_EFFECTS, "max": leds.MAX_PRESETS,
                     "file": leds.display_path()}}


def render(data, token=""):
    page = TEMPLATE.read_text(encoding="utf-8")
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return page.replace("/*__GO60_DATA__*/null", blob).replace("__GO60_TOKEN__", token)


def load_presets_quietly():
    try:
        return leds.load()
    except (OSError, ValueError) as e:
        print(f"warning: LED presets not shown ({leds.PRESETS_FILE}: {e})", file=sys.stderr)
        return []


def write_static(L, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(page_data(L, load_presets_quietly(), editable=False)), encoding="utf-8")


def open_in_browser(target):
    subprocess.Popen(["xdg-open", str(target)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)


def serve(port=0, open_it=True, tab="cheatsheet", layout_file=None, background=False):
    token = secrets.token_urlsafe(16)

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def reply(self, code, body, ctype="application/json"):
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", f"{ctype}; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/ping":
                return self.reply(200, json.dumps({"go60": True, "pid": os.getpid()}))
            if self.path not in ("/", "/index.html"):
                return self.reply(404, '{"error": "not found"}')
            # Read the layout and presets on every load, so a reload shows the latest flash and saves.
            try:
                L = km.Layout(km.load_layout(layout_file))
            except (OSError, ValueError):
                L = None
            try:
                presets = leds.load()
            except (OSError, ValueError) as e:
                return self.reply(500, f"<p>Can't read {leds.PRESETS_FILE}: {e}</p>", "text/html")
            self.reply(200, render(page_data(L, presets, editable=True, tab=tab), token), "text/html")

        def do_POST(self):
            # Only the page we served may save: other sites can't read the token.
            if self.path != "/api/presets" or self.headers.get("X-Go60-Token") != token:
                return self.reply(403, '{"error": "forbidden"}')
            try:
                n = int(self.headers.get("Content-Length", 0))
                presets = leds.validate(json.loads(self.rfile.read(n)))
                leds.save(presets)
            except (ValueError, json.JSONDecodeError) as e:
                return self.reply(400, json.dumps({"error": str(e)}))
            print(f"Saved {len(presets)} LED preset(s) to {leds.PRESETS_FILE}")
            self.reply(200, json.dumps({"ok": True, "effects": leds.effect_list(presets)}))

    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{httpd.server_address[1]}/" + ("#lights" if tab == "lights" else "")
    if background:
        STATE_FILE.write_text(json.dumps({"pid": os.getpid(), "port": port, "started": time.time()}))
        signal.signal(signal.SIGTERM, lambda *a: sys.exit(0))
    else:
        print(f"Go60 app: {url}\nLED presets save to {leds.PRESETS_FILE}. Press Ctrl+C here when you're done.")
    if open_it:
        open_in_browser(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nClosed. If you changed the lights, put them on the keyboard with: go60-build")
    finally:
        if background:
            STATE_FILE.unlink(missing_ok=True)


# ------------------------------------------------------------- app mode ---

def _ping(port):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/ping", timeout=1) as r:
            return json.load(r).get("pid")
    except (OSError, ValueError):
        return None


def _code_mtime():
    files = [TEMPLATE, *Path(__file__).parent.glob("*.py"), Path(__file__).parent / "go60-ui"]
    return max(f.stat().st_mtime for f in files if f.exists())


def launch_app():
    """Make sure the background server runs current code, then open or focus the app window."""
    CACHE.mkdir(parents=True, exist_ok=True)
    pid = _ping(APP_PORT)
    try:
        state = json.loads(STATE_FILE.read_text())
    except (OSError, ValueError):
        state = {}
    if pid and state.get("pid") == pid and state.get("started", 0) < _code_mtime():
        os.kill(pid, signal.SIGTERM)          # the app was updated: restart it
        for _ in range(50):
            if not _ping(APP_PORT):
                break
            time.sleep(.1)
        pid = None
    if not pid:
        log = open(CACHE / "ui-server.log", "a")
        subprocess.Popen([sys.executable, str(Path(__file__).parent / "go60-ui"), "--serve-app"],
                         stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
        for _ in range(50):
            if _ping(APP_PORT):
                break
            time.sleep(.1)
        else:
            sys.exit(f"go60-ui: the app server didn't start (port {APP_PORT} busy?). See {CACHE / 'ui-server.log'}")
    url = f"http://127.0.0.1:{APP_PORT}/"
    if shutil.which("omarchy-launch-or-focus-webapp"):
        os.execvp("omarchy-launch-or-focus-webapp", ["omarchy-launch-or-focus-webapp", APP_TITLE, url])
    open_in_browser(url)
