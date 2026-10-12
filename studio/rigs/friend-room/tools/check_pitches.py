#!/usr/bin/env python3
"""Check pitch cards against card-format.json (sections, word limits, hand size).

Usage (from the job folder):
    python3 tools/check_pitches.py                 # all cards in pitches/
    python3 tools/check_pitches.py --seat b        # only b-*.md
    python3 tools/check_pitches.py --file pitches/b-03.md

Exit 0 = every checked card is valid. Exit 1 = at least one problem (listed).
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FMT = json.loads((ROOT / "card-format.json").read_text(encoding="utf-8"))
FRONT_KEYS = ["id", "title", "hand", "hook"]


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        return None, None
    front = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip() if k == "hook" else re.sub(r"\s+#.*$", "", v).strip()
            front[k] = v
    return front, m.group(2)


def check(path):
    front, body = parse(path)
    if front is None:
        return ["missing front matter (--- block at top)"], {}
    problems = [f"front matter missing '{k}'" for k in FRONT_KEYS if not front.get(k)]
    if front.get("id") and front["id"] != path.stem:
        problems.append(f"id '{front['id']}' does not match file name '{path.stem}'")
    hand = front.get("hand", "")
    items = [x.strip() for x in hand.strip("[]").split(",") if x.strip()]
    allowed = {"free", "revised"}
    if not (hand.startswith("[") and hand.endswith("]")):
        problems.append("hand must be a [list]")
    elif not (len(items) == 1 and items[0] in allowed) and len(items) != FMT["hand_cards"]:
        problems.append(f"hand must list exactly {FMT['hand_cards']} cards, or be [free]")
    hw = len(front.get("hook", "").split())
    if hw > FMT["max_hook_words"]:
        problems.append(f"hook is {hw} words (max {FMT['max_hook_words']})")
    for s in FMT["sections"]:
        if not re.search(r"\*\*" + re.escape(s) + r":\*\*\s*\S", body):
            problems.append(f"section '{s}' missing or empty")
    words = len(body.split())
    if words > FMT["max_body_words"]:
        problems.append(f"body is {words} words (max {FMT['max_body_words']})")
    return problems, {"title": front.get("title", "?"), "words": words}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seat")
    ap.add_argument("--file")
    args = ap.parse_args()
    if args.file:
        files = [Path(args.file) if Path(args.file).is_absolute() else ROOT / args.file]
    else:
        files = sorted((ROOT / "pitches").glob(f"{args.seat}-*.md" if args.seat else "*.md"))
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
