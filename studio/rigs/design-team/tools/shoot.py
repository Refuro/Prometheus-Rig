#!/usr/bin/env python3
"""Screenshot a prototype's web build so the team can see it.

Usage (from the job folder):
    python3 tools/shoot.py <build-folder> <out-folder> [stages]
e.g. python3 tools/shoot.py inputs/build inputs/shots 3

Serves the folder on a free local port, opens index.html in headless
Chromium, saves 00-splash.png, then stage-1..N (debug keys 2..N). Needs
studio/setup/install-shots-wsl.sh once. Best effort: older prototypes may not
close their title card on a click, so check the images.
"""
import functools
import http.server
import os
import shutil
import socket
import subprocess
import sys
import threading
from pathlib import Path


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    build, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    stages = sys.argv[3] if len(sys.argv) > 3 else "3"
    if not (build / "index.html").exists():
        sys.exit(f"{build}/index.html not found")
    node = shutil.which("node")
    if not node:
        sys.exit("node not found; run studio/setup/install-shots-wsl.sh")
    env = dict(os.environ)
    paths = [str(Path.home() / ".local/share/studio-shots/node_modules"), env.get("NODE_PATH", "")]
    try:
        paths.append(subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, timeout=20).stdout.strip())
    except Exception:
        pass
    env["NODE_PATH"] = os.pathsep.join(p for p in paths if p)

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Quiet, directory=str(build)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        p = subprocess.run([node, str(Path(__file__).resolve().parent / "shots.cjs"),
                            f"http://127.0.0.1:{port}/index.html", str(out), stages],
                           env=env, capture_output=True, text=True, timeout=180)
    finally:
        httpd.shutdown()
    print((p.stdout + p.stderr).strip())
    print(f"shots in {out}" if p.returncode == 0 else "shots FAILED")
    return p.returncode


if __name__ == "__main__":
    sys.exit(main())
