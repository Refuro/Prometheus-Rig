#!/usr/bin/env python3
"""Check every player-facing string against its word budget.

Strings live in data/text/*.json (any depth) in this shape:
    {"strings": [
        {"id": "hint.magnet", "context": "hint", "text": "Magnets pull anything metal."}
    ]}
Budgets, banned phrases and limits live in text-budgets.json (set by the
brevity editor from the pillars).

Usage:
    python3 tools/check_text.py                    # data/text in this folder
    python3 tools/check_text.py --root /path/to/game/data/text
Exit 0 = all strings within budget. Exit 1 = problems (listed, worst first).
Also usable as a production build step.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def words(text):
    return len(re.findall(r"[A-Za-z0-9'’-]+", text))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(HERE / "data" / "text"))
    ap.add_argument("--budgets", default=str(HERE / "text-budgets.json"))
    args = ap.parse_args()

    cfg = json.loads(Path(args.budgets).read_text(encoding="utf-8"))
    budgets = cfg["contexts"]
    banned = [p.lower() for p in cfg.get("banned_phrases", [])]
    max_bang = cfg.get("max_exclamations_per_string", 1)

    files = sorted(Path(args.root).rglob("*.json"))
    if not files:
        print(f"no text files under {args.root}")
        return 0
    problems, total, seen = [], 0, {}
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            problems.append((999, f"{f.name}: invalid JSON ({e})"))
            continue
        for s in data.get("strings", []):
            total += 1
            sid, ctx, text = s.get("id", "?"), s.get("context", "?"), s.get("text", "")
            where = f"{f.name}:{sid}"
            if sid in seen:
                problems.append((500, f"{where}: duplicate id (also in {seen[sid]})"))
            seen[sid] = f.name
            if ctx not in budgets:
                problems.append((400, f"{where}: unknown context '{ctx}' (add it to text-budgets.json or fix)"))
                continue
            n, cap = words(text), budgets[ctx]
            if n > cap:
                problems.append((n - cap, f"{where}: {n} words, budget {cap} for '{ctx}' -> {text!r}"))
            low = text.lower()
            for p in banned:
                if p in low:
                    problems.append((300, f"{where}: banned phrase '{p}'"))
            if text.count("!") > max_bang:
                problems.append((200, f"{where}: {text.count('!')} exclamation marks (max {max_bang})"))
    problems.sort(key=lambda x: -x[0])
    for _, msg in problems:
        print("FAIL " + msg)
    print(f"\n{total} strings checked, {len(problems)} problems (profile: {cfg.get('profile', '?')})")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
