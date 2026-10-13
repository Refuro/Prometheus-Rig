#!/usr/bin/env python3
"""Scaffold, verify and web-export one prototype.

Usage (from the job folder):
    python3 tools/build.py <id> --new                 # scaffold protos/<id>/
    python3 tools/build.py <id> --seat build-a        # import, run, smoke test, export
    python3 tools/build.py <id> --seat build-a --no-export

Steps of a build run (stops at the first failure, exit 1):
  1. import       godot --headless --path protos/<id> --import
  2. run          godot --headless --path protos/<id> --quit-after 180
                  (fails on SCRIPT ERROR / Parse Error / non-zero exit)
  3. smoke test   godot --headless --path protos/<id> -s res://tests/smoke.gd
                  (only if the file exists; its exit code is the verdict)
  4. export       godot --headless --path protos/<id> --export-release Web builds/<id>/index.html
  5. text          every string in text.json within its word budget (text-budgets.json),
                   no [TODO] left, and no long player-facing string literals in .gd files
  6. shots         headless Chromium screenshots of the splash and every stage (keys 1-9)
                   into protos/<id>/shots/ (needs studio/setup/install-shots-wsl.sh once)
Then appends a "build" event to events.jsonl. Full output: protos/<id>/build-log.txt.

Godot's user data, config and cache are redirected into .godot/home/ inside the
job folder, so sandboxed seats can run it. Export templates are linked in from
~/.local/share/godot/export_templates (installed once by install-godot-wsl.sh).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

JOB = Path(__file__).resolve().parent.parent
SCAFFOLD = Path(__file__).resolve().parent / "scaffold"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
BAD_OUTPUT = re.compile(r"SCRIPT ERROR|Parse Error|Failed to load script|Invalid call|Cannot open file", re.I)


def godot_bin():
    cand = os.environ.get("GODOT") or shutil.which("godot") or str(Path.home() / ".local/bin/godot")
    if not Path(cand).exists() and not shutil.which(cand):
        sys.exit("godot not found: run studio/setup/install-godot-wsl.sh, or set GODOT=/path/to/godot")
    return cand


def godot_env():
    home = JOB / ".godot" / "home"  # .godot folders are skipped by the Rig Console watcher
    env = dict(os.environ)
    for key, sub in (("XDG_DATA_HOME", "data"), ("XDG_CONFIG_HOME", "config"), ("XDG_CACHE_HOME", "cache")):
        d = home / sub
        d.mkdir(parents=True, exist_ok=True)
        env[key] = str(d)
    real_templates = Path.home() / ".local/share/godot/export_templates"
    link = home / "data/godot/export_templates"
    if real_templates.exists() and not link.exists():
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(real_templates, target_is_directory=True)
    return env


def run(cmd, env, log, label, timeout=600):
    log.write(f"\n===== {label}: {' '.join(cmd)}\n")
    log.flush()
    try:
        p = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        log.write("TIMEOUT\n")
        return False, "timed out"
    out = (p.stdout or "") + (p.stderr or "")
    log.write(out)
    log.write(f"\n[exit {p.returncode}]\n")
    bad = BAD_OUTPUT.search(out)
    if p.returncode != 0:
        return False, f"exit {p.returncode}"
    if bad:
        return False, f"error in output: {bad.group(0)}"
    return True, "ok"


def scaffold(pid):
    dest = JOB / "protos" / pid
    if dest.exists():
        sys.exit(f"protos/{pid} already exists")
    shutil.copytree(SCAFFOLD, dest)
    for name in ("project.godot", "export_presets.cfg"):
        f = dest / name
        f.write_text(f.read_text(encoding="utf-8").replace("__NAME__", pid), encoding="utf-8")
    (dest / "tests").mkdir(exist_ok=True)
    print(f"scaffolded protos/{pid}/ (stage framework main.gd, proto_ui.gd, text.json, text-budgets.json, art/, ABOUT.md, export preset)")
    print("next: read art/STYLE.md, fill text.json and ABOUT.md, build stage 1 around one idea, add tests/smoke.gd, then build.py --seat")



LITERAL = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')


def check_text(proj):
    """Word budgets for text.json, no [TODO], no long player-facing literals in scripts."""
    problems = []
    tj, bj = proj / "text.json", proj / "text-budgets.json"
    if not tj.exists() or not bj.exists():
        return ["text.json or text-budgets.json missing"]
    try:
        strings = json.loads(tj.read_text(encoding="utf-8")).get("strings", [])
        cfg = json.loads(bj.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"invalid JSON: {e}"]
    budgets, banned = cfg["contexts"], [b.lower() for b in cfg.get("banned_phrases", [])]
    for st in strings:
        sid, ctx, txt = st.get("id", "?"), st.get("context", "?"), st.get("text", "")
        n = len(re.findall(r"[A-Za-z0-9'-]+", txt))
        if "[TODO]" in txt:
            problems.append(f"{sid} still [TODO]")
        if ctx not in budgets:
            problems.append(f"{sid}: unknown context {ctx}")
        elif n > budgets[ctx]:
            problems.append(f"{sid}: {n} words > {budgets[ctx]} ({ctx})")
        for b in banned:
            if b in txt.lower():
                problems.append(f"{sid}: banned phrase '{b}'")
        if txt.count("!") > cfg.get("max_exclamations_per_string", 1):
            problems.append(f"{sid}: too many '!'")
    for gd in proj.rglob("*.gd"):
        if "tests" in gd.parts or gd.name == "proto_ui.gd":
            continue
        for i, line in enumerate(gd.read_text(encoding="utf-8").splitlines(), 1):
            code = line.split("#", 1)[0]
            if "print(" in code or "push_error(" in code or "push_warning(" in code:
                continue
            for lit in LITERAL.findall(code):
                if len(lit.split()) >= 4:
                    problems.append(f"{gd.name}:{i} long string literal; player text goes in text.json")
    return problems



def build_info(proj):
    """build-info.json -> the console's build.json (JOBS.md section 5). "auto" fills from text.json."""
    f = proj / "build-info.json"
    if not f.exists():
        return None, ["build-info.json missing (title, pitch, controls, judge, bugs for the Play builds page)"]
    try:
        info = json.loads(f.read_text(encoding="utf-8"))
        strings = {x.get("id"): x.get("text", "") for x in json.loads((proj / "text.json").read_text(encoding="utf-8")).get("strings", [])}
    except (json.JSONDecodeError, OSError) as e:
        return None, [f"build-info.json: {e}"]
    auto = {"title": strings.get("splash.title", ""), "pitch": strings.get("splash.goal", ""),
            "controls": ". ".join(l.strip() for l in strings.get("help.controls", "").splitlines() if l.strip())}
    out, problems = {}, []
    for key in ("title", "pitch", "controls", "judge", "bugs"):
        val = str(info.get(key, "")).strip()
        if val.lower() == "auto":
            val = auto.get(key, "")
        if not val or "[TODO]" in val:
            problems.append(f"build-info.json: fill '{key}'")
        out[key] = val
    return out, problems

def take_shots(pid, proj, out_dir):
    import socket
    import threading
    import http.server
    import functools
    m = re.search(r"STAGE_COUNT\s*:\s*int\s*=\s*(\d+)", (proj / "main.gd").read_text(encoding="utf-8"))
    stages = int(m.group(1)) if m else 1
    node = shutil.which("node")
    if not node:
        return False, "node not found; run studio/setup/install-shots-wsl.sh"
    env = dict(os.environ)
    paths = [str(Path.home() / ".local/share/studio-shots/node_modules")]
    try:
        paths.append(subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, timeout=20).stdout.strip())
    except Exception:
        pass
    env["NODE_PATH"] = os.pathsep.join(p for p in paths if p)
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=str(out_dir))
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    shots_dir = proj / "shots"
    try:
        p = subprocess.run([node, str(Path(__file__).resolve().parent / "shots.cjs"),
                            f"http://127.0.0.1:{port}/index.html", str(shots_dir), str(stages)],
                           env=env, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return False, "timed out"
    finally:
        httpd.shutdown()
    (proj / "build-log.txt").open("a", encoding="utf-8").write("\n===== shots\n" + p.stdout + p.stderr)
    if p.returncode != 0:
        msg = (p.stdout + p.stderr).strip().splitlines()
        tail = msg[-1] if msg else f"exit {p.returncode}"
        if "Cannot find module" in (p.stdout + p.stderr):
            tail = "playwright missing; run studio/setup/install-shots-wsl.sh"
        return False, tail
    return True, "ok"

def event(kind, seat, text, data):
    line = {"kind": kind, "text": text[:300], "data": data, "ts": int(time.time())}
    if seat:
        line["seat"] = seat
    with (JOB / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--new", action="store_true", help="scaffold protos/<id>/")
    ap.add_argument("--seat", default="")
    ap.add_argument("--no-export", action="store_true")
    ap.add_argument("--no-shots", action="store_true")
    args = ap.parse_args()

    if not ID_RE.match(args.id):
        sys.exit("id must be letters, digits, . _ -")
    if args.new:
        scaffold(args.id)
        return 0

    proj = JOB / "protos" / args.id
    if not (proj / "project.godot").exists():
        sys.exit(f"protos/{args.id}/project.godot missing: scaffold with --new first")

    about = proj / "ABOUT.md"
    about_problem = None
    if not about.exists():
        about_problem = "ABOUT.md missing (what the game is, per-stage teaching, open exploits; for the gate)"
    elif "[TODO]" in about.read_text(encoding="utf-8"):
        about_problem = "ABOUT.md still has [TODO] lines"

    gd = godot_bin()
    env = godot_env()
    out_dir = JOB / "builds" / args.id
    results = []
    ok = True
    with (proj / "build-log.txt").open("w", encoding="utf-8") as log:
        steps = [
            ("import", [gd, "--headless", "--path", str(proj), "--import"]),
            ("run", [gd, "--headless", "--path", str(proj), "--quit-after", "180"]),
        ]
        if (proj / "tests" / "smoke.gd").exists():
            steps.append(("smoke", [gd, "--headless", "--path", str(proj), "-s", "res://tests/smoke.gd"]))
        else:
            results.append("smoke: MISSING (tests/smoke.gd is required before hand-back)")
        if not args.no_export:
            out_dir.mkdir(parents=True, exist_ok=True)
            steps.append(("export", [gd, "--headless", "--path", str(proj), "--export-release", "Web",
                                     str(out_dir / "index.html")]))
        for label, cmd in steps:
            good, why = run(cmd, env, log, label)
            results.append(f"{label}: {'ok' if good else 'FAIL (' + why + ')'}")
            if not good:
                ok = False
                break
    if ok and not args.no_export:
        needed = ["index.html", "index.pck", "index.wasm", "index.js"]
        missing = [n for n in needed if not (out_dir / n).exists()]
        if missing:
            ok = False
            results.append("export files missing: " + ", ".join(missing))

    if ok:
        tp = check_text(proj)
        results.append("text: ok" if not tp else "text: FAIL (" + "; ".join(tp[:6]) + (" ..." if len(tp) > 6 else "") + ")")
        ok = not tp
    info = None
    if ok and not args.no_export:
        info, ip = build_info(proj)
        results.append("info: ok (build.json)" if not ip else "info: FAIL (" + "; ".join(ip) + ")")
        ok = not ip
        if info:
            (out_dir / "build.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    if ok and not args.no_export and not args.no_shots:
        good, why = take_shots(args.id, proj, out_dir)
        results.append("shots: ok (protos/%s/shots/)" % args.id if good else "shots: FAIL (" + why + ")")
        ok = good
    if about_problem:
        results.append("about: FAIL (" + about_problem + ")")
    for r in results:
        print(r)
    smoke_missing = any(r.startswith("smoke: MISSING") for r in results)
    ok = ok and not about_problem
    verdict = "GREEN" if ok and not smoke_missing else ("GREEN (no smoke test yet)" if ok else "RED")
    print(f"\n{args.id}: {verdict}. Log: protos/{args.id}/build-log.txt")
    if ok and not args.no_export:
        print(f"Web build: builds/{args.id}/index.html (shows on the console's Play builds page)")
    event("build", args.seat, f"{args.id} build {verdict}", {"id": args.id, "steps": results})
    return 0 if ok and not smoke_missing else 1


if __name__ == "__main__":
    sys.exit(main())
