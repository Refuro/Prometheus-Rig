#!/usr/bin/env python3
"""Multi-instance sync test: one headless host plus N headless clients on this machine.

Usage (from the job folder):
    python3 tools/net_test.py <id>                 # host + 2 clients, 12 seconds
    python3 tools/net_test.py <id> --clients 3 --seconds 20

Every instance runs the prototype with bots (random inputs). Each writes a JSON
report on quit (see main.gd: --report). The test passes when:
  - every client connected and the host saw every client;
  - every peer ends with the same set of players;
  - every client's final player positions match the host's (within tolerance);
  - no instance printed a script error.
Exit 0 = pass. Reports and logs: protos/<id>/net-test/.
"""
import argparse
import json
import math
import socket
import os
import subprocess
import sys
import time
from pathlib import Path

JOB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import godot_bin, godot_env, BAD_OUTPUT  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--clients", type=int, default=2)
    ap.add_argument("--seconds", type=float, default=12.0)
    ap.add_argument("--tolerance", type=float, default=0.05)
    args = ap.parse_args()

    proj = JOB / "protos" / args.id
    out = proj / "net-test"
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*"):
        f.unlink(missing_ok=True)
    gd, env = godot_bin(), godot_env()
    S = args.seconds
    procs = []
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:  # free UDP port, so tests can run in parallel
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    start = time.time() + 2.0  # shared clock: every instance counts from here

    def launch(name, extra):
        log = open(out / f"{name}.log", "w", encoding="utf-8")
        cmd = [gd, "--headless", "--path", str(proj), "--", *extra, "--bot", f"--clock={start:.3f}", f"--port={port}",
               f"--freeze={S - 3}", f"--report-at={S}", f"--report={out / (name + '.json')}"]
        procs.append((name, subprocess.Popen(cmd, env=env, stdout=log, stderr=subprocess.STDOUT), log))

    # Everyone reports at the same moment while connected; clients quit 1 s later, the host 3 s later.
    launch("host", ["--host", f"--seconds={S + 3}"])
    time.sleep(1.0)
    for i in range(args.clients):
        launch(f"client{i + 1}", ["--join=127.0.0.1", f"--seconds={S + 1}"])

    deadline = time.time() + S + 30
    for name, p, log in procs:
        try:
            p.wait(timeout=max(1, deadline - time.time()))
        except subprocess.TimeoutExpired:
            p.kill()
        log.close()

    problems = []
    reports = {}
    for name, p, _ in procs:
        text = (out / f"{name}.log").read_text(encoding="utf-8", errors="replace")
        bad = BAD_OUTPUT.search(text)
        if bad:
            problems.append(f"{name}: error in output ({bad.group(0)}), see net-test/{name}.log")
        rp = out / f"{name}.json"
        if not rp.exists():
            problems.append(f"{name}: no report (crashed or never quit), see net-test/{name}.log")
            continue
        reports[name] = json.loads(rp.read_text(encoding="utf-8"))

    host = reports.get("host")
    if host:
        if host["role"] != "host":
            problems.append("host: did not start hosting")
        if len(host["peers"]) != args.clients:
            problems.append(f"host: saw {len(host['peers'])} peers, expected {args.clients}")
        for name, r in reports.items():
            if name == "host":
                continue
            if r["role"] != "client":
                problems.append(f"{name}: not connected at the end")
                continue
            if set(r["state"]) != set(host["state"]):
                problems.append(f"{name}: players {sorted(r['state'])} differ from host {sorted(host['state'])}")
                continue
            worst = max((math.dist(r["state"][k], host["state"][k]) for k in host["state"]), default=0.0)
            if worst > args.tolerance:
                problems.append(f"{name}: positions drift from host by {worst:.3f} (tolerance {args.tolerance})")
        if host.get("ticks", 0) < 30:
            problems.append(f"host: only {host.get('ticks', 0)} ticks simulated")

    for p in problems:
        print("FAIL " + p)
    verdict = "PASS" if not problems else "FAIL"
    print(f"\nnet test {args.id}: {verdict} (host + {args.clients} clients, {S:.0f}s). Logs: protos/{args.id}/net-test/")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
