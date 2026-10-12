#!/usr/bin/env python3
"""Check pitch cards against the brief's card shape.

Usage (from the rig root):
    python3 tools/check_pitches.py                 # all cards in pitches/
    python3 tools/check_pitches.py --seat b        # only b-*.md
    python3 tools/check_pitches.py --file pitches/b-03.md

Exit 0 = every checked card is valid. Exit 1 = at least one problem (listed).
Prints a one-line summary per card either way.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONT_KEYS = ["id", "title", "hand", "hook"]
SECTIONS = [
    "Ten-second clip", "The rule", "Loop", "Minute 100", "Why watch",
    "Hand use", "Prototype question", "Look", "Risk",
]
MAX_BODY_WORDS = 250
MAX_HOOK_WORDS = 20


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        return None, None, ["missing front matter (--- block at top)"]
    front_raw, body = m.group(1), m.group(2)
    front = {}
    for line in front_raw.splitlines():
        line = line.split("#", 1)[0].rstrip() if not line.strip().startswith("hook:") else line.rstrip()
        if ":" in line:
            k, v = line.split(":", 1)
            front[k.strip()] = v.strip()
    return front, body, []


def check(path):
    problems = []
    front, body, errs = parse(path)
    if errs:
        return errs, {}
    for k in FRONT_KEYS:
        if not front.get(k):
            problems.append(f"front matter missing '{k}'")
    expected_id = path.stem
    if front.get("id") and front["id"] != expected_id:
        problems.append(f"id '{front['id']}' does not match file name '{expected_id}'")
    hand = front.get("hand", "")
    if hand and not (hand.startswith("[") and hand.endswith("]")):
        problems.append("hand must be a [list] or [free]")
    else:
        items = [x.strip() for x in hand.strip("[]").split(",") if x.strip()]
        if items != ["free"] and len(items) != 4:
            problems.append("hand must list exactly 4 cards, or be [free]")
    hook_words = len(front.get("hook", "").split())
    if hook_words > MAX_HOOK_WORDS:
        problems.append(f"hook is {hook_words} words (max {MAX_HOOK_WORDS})")
    for s in SECTIONS:
        if not re.search(r"\*\*" + re.escape(s) + r":\*\*\s*\S", body):
            problems.append(f"section '{s}' missing or empty")
    words = len(body.split())
    if words > MAX_BODY_WORDS:
        problems.append(f"body is {words} words (max {MAX_BODY_WORDS})")
    return problems, {"title": front.get("title", "?"), "words": words}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seat")
    ap.add_argument("--file")
    args = ap.parse_args()

    if args.file:
        files = [Path(args.file) if Path(args.file).is_absolute() else ROOT / args.file]
    else:
        d = ROOT / "pitches"
        pattern = f"{args.seat}-*.md" if args.seat else "*.md"
        files = sorted(d.glob(pattern))
    if not files:
        print("no pitch cards found")
        return 1

    bad = 0
    for f in files:
        if not f.exists():
            print(f"FAIL {f.name}: file not found")
            bad += 1
            continue
        problems, info = check(f)
        if problems:
            bad += 1
            print(f"FAIL {f.name}: " + "; ".join(problems))
        else:
            print(f"OK   {f.name}: {info['title']} ({info['words']} words)")
    print(f"\n{len(files) - bad}/{len(files)} valid")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
