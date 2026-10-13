#!/usr/bin/env python3
"""Scaffold, check and export the production game.

Usage (from the production job folder):
    python3 tools/build.py --new --title "A Bridge Goes Walking"   # tech lead, once: game/ + git
    python3 tools/build.py --worktree dev-a                        # tech lead: work/dev-a at main
    python3 tools/build.py --seat dev-a --tree work/dev-a          # a dev's check before hand-back
    python3 tools/build.py --seat review-code --tree work/dev-a    # the reviewer re-runs it
    python3 tools/build.py --seat tech-lead                        # main
    python3 tools/build.py --seat tech-lead --milestone m1 [--linux]   # milestone build, main only

Check steps (stop at the first failure, exit 1):
  1. data     game data matches data/SYNCED.json (nobody edits design data by hand)
  2. import   godot --headless --import
  3. run      boots the main scene headless for 120 frames (fails on script errors)
  4. tests    res://tests/run.tscn: every tests/test_*.gd; prints TESTS passed=N failed=M
  5. text     tools/check_text.py on data/text (budgets, banned phrases) and no player text
              in scripts (string literals of 4+ words outside tests/ and dev/)
--milestone <m> adds (main only, clean tree):
  6. export   Windows zip + download page in builds/<m>/ (and Linux zip with --linux)
  7. web      web build with dev tools in builds/<m>-web/, build.json for the Play builds page
  8. shots    every shot in shots.json into milestones/<m>/shots/
  then builds/<m>/build-meta.json, the milestone's "tests" and "build" in milestones.json, and a
  copy of game/assets/manifest.json (if any) at <job>/assets/manifest.json for the console.
Every run appends a "build" event to events.jsonl. Log: <tree>/build-log.txt.
"""
import argparse
import functools
import http.server
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
JOB = TOOLS.parent
SCAFFOLD = TOOLS / "scaffold"
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
BAD_OUTPUT = re.compile(r"SCRIPT ERROR|Parse Error|Failed to load script|Invalid call|Cannot open file", re.I)
LITERAL = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')
SKIP_CALLS = ("print(", "push_error(", "push_warning(", "assert(", "print_debug(")

sys.path.insert(0, str(TOOLS))
import sync_data  # noqa: E402


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
    real = Path.home() / ".local/share/godot/export_templates"
    link = home / "data/godot/export_templates"
    if real.exists() and not link.exists():
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(real, target_is_directory=True)
    return env


def git(*args, cwd=JOB / "game", check=True):
    p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and p.returncode != 0:
        sys.exit(f"git {' '.join(args)}: {(p.stderr or p.stdout).strip()}")
    return p.stdout.strip()


def run(cmd, env, log, label, timeout=900):
    log.write(f"\n===== {label}: {' '.join(cmd)}\n")
    log.flush()
    try:
        p = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        log.write("TIMEOUT\n")
        return False, "timed out", ""
    out = (p.stdout or "") + (p.stderr or "")
    log.write(out + f"\n[exit {p.returncode}]\n")
    if p.returncode != 0:
        return False, f"exit {p.returncode}", out
    bad = BAD_OUTPUT.search(out)
    if bad:
        return False, f"error in output: {bad.group(0)}", out
    return True, "ok", out


# ---------- one-off setup ----------

def new_project(title):
    dest = JOB / "game"
    if dest.exists():
        sys.exit("game/ already exists")
    shutil.copytree(SCAFFOLD, dest)
    f = dest / "project.godot"
    f.write_text(f.read_text(encoding="utf-8").replace("__NAME__", title.replace('"', "'")), encoding="utf-8")
    (dest / "data").mkdir(exist_ok=True)
    git("init", "-q", "-b", "main")
    git("config", "user.name", JOB.name)
    git("config", "user.email", f"{JOB.name}@studio.local")
    git("add", "-A")
    git("commit", "-q", "-m", "scaffold")
    print(f"game/ scaffolded and committed for {title!r}.")
    print("next: python3 tools/sync_data.py, build, commit 'data sync', then write docs/architecture.md")


def new_worktree(seat):
    if not NAME_RE.match(seat):
        sys.exit("seat must be letters, digits, . _ -")
    dest = JOB / "work" / seat
    if dest.exists():
        sys.exit(f"work/{seat} already exists")
    dest.parent.mkdir(exist_ok=True)
    git("worktree", "add", "-q", "--detach", str(dest), "main")
    print(f"work/{seat} is a worktree at main. Per task: git -C work/{seat} switch -c {seat}/T-nnn main")


# ---------- checks ----------

def check_scripts(proj):
    problems = []
    for gd in sorted(proj.rglob("*.gd")):
        rel = gd.relative_to(proj)
        if rel.parts[0] in ("tests", "dev", ".godot", "addons"):
            continue
        for i, line in enumerate(gd.read_text(encoding="utf-8").splitlines(), 1):
            code = line.split("#", 1)[0]
            if any(c in code for c in SKIP_CALLS):
                continue
            for lit in LITERAL.findall(code):
                if len(lit.split()) >= 4:
                    problems.append(f"{rel}:{i} player text in a script; it belongs in data/text")
    return problems


def check_text(proj, log):
    root, budgets = proj / "data" / "text", proj / "data" / "text-budgets.json"
    problems = check_scripts(proj)
    if root.exists() and any(root.rglob("*.json")):
        if not budgets.exists():
            problems.append("data/text-budgets.json missing (sync_data.py copies it from the design job)")
        else:
            p = subprocess.run([sys.executable, str(TOOLS / "check_text.py"), "--root", str(root),
                                "--budgets", str(budgets)], capture_output=True, text=True)
            log.write("\n===== text\n" + p.stdout + p.stderr)
            if p.returncode != 0:
                problems += [l[5:] for l in p.stdout.splitlines() if l.startswith("FAIL ")]
    return problems


# ---------- milestone outputs ----------

def build_info(proj):
    f = proj / "build-info.json"
    try:
        info = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return None, [f"build-info.json: {e}"]
    title_auto = title_of(proj)
    out, problems = {}, []
    for key in ("title", "pitch", "controls", "judge", "bugs"):
        val = str(info.get(key, "")).strip()
        if key == "title" and val.lower() == "auto":
            val = title_auto
        if not val or "[TODO]" in val:
            problems.append(f"build-info.json: fill '{key}'")
        out[key] = val
    return out, problems


def title_of(proj):
    m = re.search(r'config/name="([^"]*)"', (proj / "project.godot").read_text(encoding="utf-8"))
    return m.group(1) if m else proj.name


def slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "game"


def download_page(out_dir, title, milestone, info, zips):
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    links = "".join(f'<p><a class="dl" href="{z.name}" download>Download {label} ({z.stat().st_size / 1e6:.0f} MB)</a></p>'
                    for label, z in zips)
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} {milestone}</title>
<style>body{{font:16px/1.5 system-ui,sans-serif;max-width:680px;margin:24px auto;padding:0 16px}}
a.dl{{display:inline-block;background:#f0b23c;color:#111;font-weight:700;padding:12px 18px;border-radius:10px;text-decoration:none}}</style></head><body>
<h1>{esc(title)}: {milestone}</h1>{links}
<p>Unzip and run the .exe. Windows may warn about an unknown publisher: More info, Run anyway.</p>
<h2>What to judge</h2><p>{esc(info.get('judge', ''))}</p>
<h2>Controls</h2><p>{esc(info.get('controls', ''))}</p>
<h2>Known bugs</h2><p>{esc(info.get('bugs', ''))}</p>
<p>The milestone packet (milestones/{milestone}/packet.md) has the checklist and test results.</p></body></html>"""
    (out_dir / "index.html").write_text(page, encoding="utf-8")


def take_shots(proj, web_dir, shots_dir):
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
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Quiet, directory=str(web_dir)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        p = subprocess.run([node, str(TOOLS / "shots.cjs"), f"http://127.0.0.1:{port}/index.html",
                            str(shots_dir), str(proj / "shots.json")], env=env, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        return False, "timed out"
    finally:
        httpd.shutdown()
    with (proj / "build-log.txt").open("a", encoding="utf-8") as log:
        log.write("\n===== shots\n" + p.stdout + p.stderr)
    out = (p.stdout + p.stderr).strip().splitlines()
    if p.returncode != 0:
        if "Cannot find module" in (p.stdout + p.stderr):
            return False, "playwright missing; run studio/setup/install-shots-wsl.sh"
        return False, out[-1] if out else f"exit {p.returncode}"
    return True, out[-1] if out else "ok"


def update_milestones(milestone, tests, build_dir):
    f = JOB / "milestones.json"
    if not f.exists():
        return "milestones.json missing (the tech lead creates it from brief section 9)"
    try:
        doc = json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return f"milestones.json: {e}"
    for m in doc.get("milestones", []):
        if m.get("id") == milestone:
            m["tests"] = tests
            m["build"] = build_dir
            f.write_text(json.dumps(doc, indent=1), encoding="utf-8")
            return None
    return f"milestones.json has no milestone {milestone!r}"


def event(seat, text, data):
    line = {"kind": "build", "text": text[:300], "data": data, "ts": int(time.time())}
    if seat:
        line["seat"] = seat
    with (JOB / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", action="store_true")
    ap.add_argument("--title", default="")
    ap.add_argument("--worktree", default="")
    ap.add_argument("--seat", default="")
    ap.add_argument("--tree", default="game")
    ap.add_argument("--only", default="", help="run only tests whose file or method contains this")
    ap.add_argument("--milestone", default="")
    ap.add_argument("--linux", action="store_true")
    ap.add_argument("--no-shots", action="store_true")
    args = ap.parse_args()

    if args.new:
        if not args.title:
            sys.exit('--new needs --title "Game Title"')
        new_project(args.title)
        return 0
    if args.worktree:
        new_worktree(args.worktree)
        return 0

    proj = (JOB / args.tree).resolve()
    if JOB not in proj.parents or not (proj / "project.godot").exists():
        sys.exit(f"{args.tree}/project.godot missing (scaffold with --new, or --worktree <seat>)")
    if args.milestone:
        if not NAME_RE.match(args.milestone):
            sys.exit("milestone must be letters, digits, . _ -")
        if args.tree != "game":
            sys.exit("milestone builds come from main (game/), not a worktree")
        if git("rev-parse", "--abbrev-ref", "HEAD", cwd=proj) != "main":
            sys.exit("game/ is not on main")
        if git("status", "--porcelain", cwd=proj):
            sys.exit("game/ has uncommitted changes; a milestone build must match a commit")

    gd, env = godot_bin(), godot_env()
    results, ok, tests = [], True, {"passed": 0, "failed": 0, "at": None}
    with (proj / "build-log.txt").open("w", encoding="utf-8") as log:
        dp = sync_data.check(proj / "data")
        results.append("data: ok" if not dp else "data: FAIL (" + "; ".join(dp[:4]) + ")")
        ok = not dp
        steps = [("import", [gd, "--headless", "--path", str(proj), "--import"]),
                 ("run", [gd, "--headless", "--path", str(proj), "--quit-after", "120"])]
        test_cmd = [gd, "--headless", "--path", str(proj), "res://tests/run.tscn"]
        if args.only:
            test_cmd += ["--", f"--only={args.only}"]
        steps.append(("tests", test_cmd))
        for label, cmd in steps:
            if not ok:
                break
            good, why, out = run(cmd, env, log, label)
            if label == "tests":
                m = re.search(r"TESTS passed=(\d+) failed=(\d+)", out)
                if m:
                    tests = {"passed": int(m.group(1)), "failed": int(m.group(2)),
                             "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                fails = [l for l in out.splitlines() if l.startswith("FAIL ")]
                why = f"{tests['failed']} failed: " + "; ".join(fails[:3]) if fails else why
                results.append(f"tests: {'ok' if good else 'FAIL'} ({tests['passed']} passed, {tests['failed']} failed)"
                               + ("" if good else " " + why))
            else:
                results.append(f"{label}: {'ok' if good else 'FAIL (' + why + ')'}")
            ok = good
        if ok:
            tp = check_text(proj, log)
            results.append("text: ok" if not tp else "text: FAIL (" + "; ".join(tp[:6]) + (" ..." if len(tp) > 6 else "") + ")")
            ok = not tp

    if ok and args.milestone:
        m = args.milestone
        title = title_of(proj)
        info, ip = build_info(proj)
        if ip:
            results.append("info: FAIL (" + "; ".join(ip) + ")")
            ok = False
        out_dir, web_dir = JOB / "builds" / m, JOB / "builds" / f"{m}-web"
        presets = [("Windows Desktop", "windows", ".exe")] + ([("Linux", "linux", ".x86_64")] if args.linux else [])
        zips = []
        with (proj / "build-log.txt").open("a", encoding="utf-8") as log:
            for preset, plat, ext in presets:
                if not ok:
                    break
                tmp = out_dir / f"_{plat}"
                if tmp.exists():
                    shutil.rmtree(tmp)
                tmp.mkdir(parents=True)
                good, why, _ = run([gd, "--headless", "--path", str(proj), "--export-release", preset,
                                    str(tmp / (slug(title) + ext))], env, log, f"export-{plat}")
                if good and not any(tmp.iterdir()):
                    good, why = False, "no executable produced"
                results.append(f"export-{plat}: {'ok' if good else 'FAIL (' + why + ')'}")
                ok = good
                if good:
                    z = Path(shutil.make_archive(str(out_dir / f"{slug(title)}-{plat}"), "zip", tmp))
                    zips.append(({"windows": "Windows build", "linux": "Linux / Steam Deck build"}[plat], z))
                shutil.rmtree(tmp, ignore_errors=True)
            if ok:
                if web_dir.exists():
                    shutil.rmtree(web_dir)
                web_dir.mkdir(parents=True)
                good, why, _ = run([gd, "--headless", "--path", str(proj), "--export-release", "Web",
                                    str(web_dir / "index.html")], env, log, "export-web")
                results.append(f"export-web: {'ok' if good else 'FAIL (' + why + ')'}")
                ok = good
        if ok:
            download_page(out_dir, title, m, info, zips)
            (out_dir / "build.json").write_text(json.dumps(dict(info, title=f"{info['title']} ({m})"), indent=1), encoding="utf-8")
            (web_dir / "build.json").write_text(json.dumps(dict(info, title=f"{info['title']} ({m}, web look)",
                judge="A quick look only; play the Windows build for feel and performance."), indent=1), encoding="utf-8")
        if ok and not args.no_shots:
            shots_dir = JOB / "milestones" / m / "shots"
            if shots_dir.exists():
                shutil.rmtree(shots_dir)
            good, why = take_shots(proj, web_dir, shots_dir)
            results.append(f"shots: {'ok' if good else 'FAIL'} ({why})")
            ok = good
        if ok:
            commit = git("rev-parse", "--short", "HEAD", cwd=proj)
            (out_dir / "build-meta.json").write_text(json.dumps(
                {"milestone": m, "commit": commit, "tests": tests, "steps": results,
                 "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1), encoding="utf-8")
            warn = update_milestones(m, tests, f"builds/{m}")
            results.append("milestones.json: updated" if not warn else f"milestones.json: WARN ({warn})")
            manifest = proj / "assets" / "manifest.json"
            if manifest.exists():  # the console's Assets tab reads <job>/assets/manifest.json
                (JOB / "assets").mkdir(exist_ok=True)
                shutil.copy(manifest, JOB / "assets" / "manifest.json")
                results.append("assets: manifest copied to assets/manifest.json")

    for r in results:
        print(r)
    verdict = "GREEN" if ok else "RED"
    where = args.tree + (f" {args.milestone}" if args.milestone else "")
    print(f"\n{where}: {verdict}. Log: {args.tree}/build-log.txt")
    if ok and args.milestone:
        print(f"Download page: builds/{args.milestone}/ (Play builds page). Web look: builds/{args.milestone}-web/. "
              f"Shots: milestones/{args.milestone}/shots/")
    event(args.seat, f"{where} build {verdict}", {"tree": args.tree, "milestone": args.milestone or None,
                                                 "tests": tests, "steps": results})
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
