#!/usr/bin/env python3
"""Make anonymous copies of every valid pitch card for blind judging.

Usage (from the job folder, run by room-lead once all cards are in):
    python3 tools/blind.py --seed 777

Writes blind/x-01.md ... in shuffled order: same body, but the front matter keeps
only title and hook, and the id becomes the blind id. The key that maps blind ids
back to real cards goes to .blind-key.json. The script prints only counts.

Everyone judging (curator, depth critic, scout) works from blind/ only and does
not open .blind-key.json until gate.json has been written.
"""
import argparse
import json
import random
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--round", type=int, default=1, help="round 2+ writes blind-<n>/ and .blind-key-<n>.json")
    args = ap.parse_args()

    check = subprocess.run([sys.executable, str(ROOT / "tools" / "check_pitches.py")], capture_output=True, text=True)
    valid = [line.split()[1].rstrip(":") for line in check.stdout.splitlines() if line.startswith("OK ")]
    seen = set()
    for old in ROOT.glob(".blind-key*.json"):
        seen.update(json.loads(old.read_text(encoding="utf-8")).values())
    valid = [v for v in valid if v[:-3] not in seen]   # only cards new this round
    if not valid:
        sys.exit("no valid cards to blind")
    suffix = "" if args.round == 1 else f"-{args.round}"
    out = ROOT / f"blind{suffix}"
    if out.exists() and any(out.iterdir()):
        sys.exit("blind/ already has files; blinding runs once per round")
    out.mkdir(exist_ok=True)
    rng = random.Random(args.seed)
    rng.shuffle(valid)
    key = {}
    for i, name in enumerate(valid, 1):
        bid = f"x{args.round if args.round > 1 else ''}-{i:02d}"
        text = (ROOT / "pitches" / name).read_text(encoding="utf-8")
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
        front = dict(l.split(":", 1) for l in m.group(1).splitlines() if ":" in l)
        body = re.sub(r"\*\*Hand use:\*\*.*?(?=\n\*\*|\Z)", "", m.group(2), flags=re.S).strip() + "\n"
        (out / f"{bid}.md").write_text(
            f"---\nid: {bid}\ntitle: {front.get('title', '').strip()}\nhook: {front.get('hook', '').strip()}\n---\n{body}",
            encoding="utf-8")
        key[bid] = name[:-3]
    (ROOT / f".blind-key{suffix}.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    skipped = check.stdout.count("FAIL ")
    print(f"blinded {len(valid)} cards into {out.name}/ (skipped {skipped} invalid). Key saved; do not open it before the gate.")


if __name__ == "__main__":
    main()
