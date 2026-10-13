#!/usr/bin/env python3
"""Check harvested ledger lines against the live job folders (read-only).

For each observation in the id range, finds the files its `evidence` names under
~/openrig/jobs/<rig>/ (or ~/openrig/research/<rig>/) and checks that quoted snippets
appear in them. Lines marked "!!" need a manual look; queue-row quotes can be checked
with `rig queue show <id> --full`.

Usage: python3 models/tools/verify_evidence.py 77 125
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "..", "observations.jsonl")
JOBS = os.path.expanduser("~/openrig/jobs")
RESEARCH = os.path.expanduser("~/openrig/research")


def norm(s):
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("—", "-"), ("–", "-"), ("→", "->")):
        s = s.replace(a, b)
    return re.sub(r"[\s*`|]+", " ", s).strip().lower()


def find_files(base, ev):
    found, missing = [], []
    for t in re.findall(r"[A-Za-z0-9_./-]+\.(?:md|gd|csv|json|jsonl|py|txt)", ev):
        t = re.sub(r"^(jobs|research)-mirror/[^/]+/", "", t)
        for cand in (os.path.join(base, t), os.path.join(base, "reviews", t), os.path.join(base, "depth", t)):
            if os.path.isfile(cand):
                found.append(cand)
                break
        else:
            hits = glob.glob(os.path.join(base, "**", os.path.basename(t)), recursive=True)
            (found.append(hits[0]) if hits else missing.append(t))
    return found, missing


def main(lo, hi):
    for line in open(LEDGER):
        o = json.loads(line)
        if not lo <= int(o["id"][1:]) <= hi:
            continue
        ev = o.get("evidence", "")
        base = os.path.join(JOBS, o["rig"])
        if not os.path.isdir(base):
            base = os.path.join(RESEARCH, o["rig"])
        files, missing = find_files(base, ev)
        text = "".join(norm(open(f, errors="replace").read()) for f in files)
        quotes = [a or b for a, b in re.findall(r"\"([^\"]{8,})\"|'([^']{8,})'", ev)]
        if not quotes and ":" in ev:
            tail = ev.split(":", 1)[1].strip()
            if len(tail) > 12 and not tail.startswith("/"):
                quotes = [tail[:60]]
        res = []
        for q in quotes:
            parts = [p for p in re.split(r"\.\.\.|…", q) if p.strip()]
            ok = all(norm(p)[:50] in text for p in parts)
            res.append(("OK " if ok else "NOQUOTE ") + q[:50])
        bad = missing or not files or any(r.startswith("NOQUOTE") for r in res)
        print("!!" if bad else "  ", o["id"], o["rig"], o["seat"], "| files:", len(files),
              "missing:", missing, "|", "; ".join(res) or "(no quote)")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
