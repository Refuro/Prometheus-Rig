#!/usr/bin/env python3
"""Draw collision hands for the pitch room.

Usage (from the rig root):
    python3 tools/draw_hands.py --seat a --hands 5 --seed 101
    python3 tools/draw_hands.py --seat c --hands 5 --seed 303 --strange

Prints the hands as markdown and appends them to lead-hands.md in the job folder.
Same seed + same deck = same hands, so every draw can be reproduced.
No card repeats within one seat's hands for a given suit.
"""
import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUITS = ["verb", "setting", "constraint", "twist_input"]


def load_deck(path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    deck = {}
    for suit in SUITS:
        cards = []
        for item in raw[suit]:
            if isinstance(item, str):
                cards.append((item, False))
            else:
                cards.append((item["text"], bool(item.get("strange"))))
        deck[suit] = cards
    return deck


def weighted_sample(rng, cards, k, strange):
    pool = list(cards)
    picked = []
    for _ in range(k):
        if not pool:
            break
        weights = [3.0 if (strange and is_strange) else 1.0 for _, is_strange in pool]
        idx = rng.choices(range(len(pool)), weights=weights, k=1)[0]
        picked.append(pool.pop(idx)[0])
    return picked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seat", required=True, help="pitcher letter, e.g. a")
    ap.add_argument("--hands", type=int, default=5)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--strange", action="store_true")
    ap.add_argument("--deck", default=str(ROOT / "deck.json"))
    ap.add_argument("--no-append", action="store_true")
    args = ap.parse_args()

    deck = load_deck(Path(args.deck))
    for suit in SUITS:
        if len(deck[suit]) < args.hands:
            sys.exit(f"deck suit '{suit}' has fewer than {args.hands} cards")

    rng = random.Random(args.seed)
    columns = {s: weighted_sample(rng, deck[s], args.hands, args.strange) for s in SUITS}

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"## Seat {args.seat}: seed {args.seed}{' (strange)' if args.strange else ''}, drawn {stamp}",
        "",
        "| Hand | Verb | Setting | Constraint | Twist input |",
        "|---|---|---|---|---|",
    ]
    for i in range(args.hands):
        row = [columns[s][i] for s in SUITS]
        lines.append(f"| {args.seat}-h{i + 1} | " + " | ".join(row) + " |")
    lines.append("")
    text = "\n".join(lines)
    print(text)

    if not args.no_append:
        out = ROOT / "lead-hands.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        new = not out.exists()
        with out.open("a", encoding="utf-8") as f:
            if new:
                f.write("# Collision hands\n\n")
            f.write(text + "\n")


if __name__ == "__main__":
    main()
