#!/usr/bin/env python3
"""Scaffold, verify, sync-test and Windows-export one co-op prototype.

Usage (from the job folder):
    python3 tools/build.py <id> --new                 # scaffold protos/<id>/
    python3 tools/build.py <id> --seat build-a        # import, run, smoke, net test, export
    python3 tools/build.py <id> --seat build-a --no-export --no-net   # quick check while iterating

Steps of a build run (stops at the first failure, exit 1):
  1. import       godot --headless --path protos/<id> --import
  2. run          godot --headless --path protos/<id> --quit-after 180
                  (fails on SCRIPT ERROR / Parse Error / non-zero exit)
  3. smoke test   godot --headless --path protos/<id> -s res://tests/smoke.gd
                  (only if the file exists; its exit code is the verdict)
  4. net test     tools/net_test.py <id>: headless host + 2 bot clients must stay in sync
  5. export       Windows Desktop build, zipped to builds/<id>/<id>-windows.zip, plus
                  builds/<id>/index.html: a download page with host/join steps
                  (shows on the console's Play builds page; download it there and
                  share the zip with friends)
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
    print(f"scaffolded protos/{pid}/ (project.godot, main.tscn, main.gd with host/join networking, proto_ui.gd, ABOUT.txt, export_presets.cfg)")
    print("next: fill ABOUT.txt, build the core rule in main.gd, add tests/smoke.gd, then run build.py with --seat")


def write_download_page(pid, proj, out_dir):
    how = ""
    if (proj / "HOW-TO-PLAY.md").exists():
        how = (proj / "HOW-TO-PLAY.md").read_text(encoding="utf-8")
    esc = how.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    size = (out_dir / f"{pid}-windows.zip").stat().st_size / 1e6
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{pid} (co-op prototype)</title>
<style>body{{font:16px/1.5 system-ui,sans-serif;max-width:680px;margin:24px auto;padding:0 16px}}
a.dl{{display:inline-block;background:#f0b23c;color:#111;font-weight:700;padding:12px 18px;border-radius:10px;text-decoration:none}}
pre{{white-space:pre-wrap;background:#f3f4f6;padding:12px;border-radius:8px}}</style></head><body>
<h1>{pid}</h1><p><a class="dl" href="{pid}-windows.zip" download>Download Windows build ({size:.0f} MB)</a></p>
<h2>How to play together</h2><ol>
<li>Everyone installs <b>Tailscale</b> (free) and accepts the host's share invite.</li>
<li>Everyone unzips the build and runs <code>{pid}.exe</code> (Windows may warn about an unknown publisher: More info, Run anyway).</li>
<li>The host clicks <b>Host</b>. Everyone else types the host's Tailscale address (100.x.y.z or the machine name) and clicks <b>Join</b>.</li>
</ol><h2>About this prototype</h2><pre>{esc}</pre></body></html>"""
    (out_dir / "index.html").write_text(page, encoding="utf-8")


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
    ap.add_argument("--no-net", action="store_true")
    args = ap.parse_args()

    if not ID_RE.match(args.id):
        sys.exit("id must be letters, digits, . _ -")
    if args.new:
        scaffold(args.id)
        return 0

    proj = JOB / "protos" / args.id
    if not (proj / "project.godot").exists():
        sys.exit(f"protos/{args.id}/project.godot missing: scaffold with --new first")

    about = proj / "ABOUT.txt"
    about_problem = None
    if not about.exists():
        about_problem = "ABOUT.txt missing (the title card text)"
    elif "[TODO]" in about.read_text(encoding="utf-8"):
        about_problem = "ABOUT.txt still has [TODO] lines (fill in what the game is, the goal, every object)"

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
        if not args.no_net:
            steps.append(("net", [sys.executable, str(Path(__file__).resolve().parent / "net_test.py"), args.id]))
        win_dir = out_dir / "_win"
        if not args.no_export:
            if win_dir.exists():
                shutil.rmtree(win_dir)
            win_dir.mkdir(parents=True, exist_ok=True)
            steps.append(("export", [gd, "--headless", "--path", str(proj), "--export-release", "Windows Desktop",
                                     str(win_dir / f"{args.id}.exe")]))
        for label, cmd in steps:
            good, why = run(cmd, env, log, label)
            results.append(f"{label}: {'ok' if good else 'FAIL (' + why + ')'}")
            if not good:
                ok = False
                break
    if ok and not args.no_export:
        exe = win_dir / f"{args.id}.exe"
        if not exe.exists():
            ok = False
            results.append("export: FAIL (no .exe produced)")
        else:
            for name in ("ABOUT.txt", "HOW-TO-PLAY.md"):
                if (proj / name).exists():
                    shutil.copy(proj / name, win_dir / name)
            zip_base = out_dir / f"{args.id}-windows"
            shutil.make_archive(str(zip_base), "zip", win_dir)
            shutil.rmtree(win_dir)
            write_download_page(args.id, proj, out_dir)

    if about_problem:
        results.append("about: FAIL (" + about_problem + ")")
    for r in results:
        print(r)
    smoke_missing = any(r.startswith("smoke: MISSING") for r in results)
    ok = ok and not about_problem
    verdict = "GREEN" if ok and not smoke_missing else ("GREEN (no smoke test yet)" if ok else "RED")
    print(f"\n{args.id}: {verdict}. Log: protos/{args.id}/build-log.txt")
    if ok and not args.no_export:
        print(f"Windows build: builds/{args.id}/{args.id}-windows.zip (download page on the console's Play builds page)")
    event("build", args.seat, f"{args.id} build {verdict}", {"id": args.id, "steps": results})
    return 0 if ok and not smoke_missing else 1


if __name__ == "__main__":
    sys.exit(main())
