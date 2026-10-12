#!/usr/bin/env python3
"""Draw collision hands from deck.json (one card per suit; suits = the deck's keys).

Usage (from the job folder):
    python3 tools/draw_hands.py --seat a --hands 5 --seed 101
    python3 tools/draw_hands.py --seat c --hands 5 --seed 303 --strange

Prints the hands as markdown and appends them to lead-hands.md.
Same seed + same deck = same hands. No card repeats within one seat's draw.
"""
import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_deck(path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    deck = {}
    for suit, items in raw.items():
        if suit.startswith("_"):
            continue
        cards = []
        for item in items:
            text, strange = (item, False) if isinstance(item, str) else (item["text"], bool(item.get("strange")))
            if "," in text:
                sys.exit(f"deck card contains a comma (breaks card hands): {text!r}")
            cards.append((text, strange))
        deck[suit] = cards
    return deck


def weighted_sample(rng, cards, k, strange):
    pool, picked = list(cards), []
    for _ in range(k):
        weights = [3.0 if (strange and s) else 1.0 for _, s in pool]
        idx = rng.choices(range(len(pool)), weights=weights, k=1)[0]
        picked.append(pool.pop(idx)[0])
    return picked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seat", required=True)
    ap.add_argument("--hands", type=int, default=5)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--strange", action="store_true")
    ap.add_argument("--deck", default=str(ROOT / "deck.json"))
    ap.add_argument("--no-append", action="store_true")
    args = ap.parse_args()

    deck = load_deck(Path(args.deck))
    suits = list(deck)
    for s in suits:
        if len(deck[s]) < args.hands:
            sys.exit(f"deck suit '{s}' has fewer than {args.hands} cards")
    rng = random.Random(args.seed)
    cols = {s: weighted_sample(rng, deck[s], args.hands, args.strange) for s in suits}

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    head = " | ".join(s.replace("_", " ").capitalize() for s in suits)
    lines = [f"## Seat {args.seat}: seed {args.seed}{' (strange)' if args.strange else ''}, drawn {stamp}", "",
             f"| Hand | {head} |", "|---|" + "---|" * len(suits)]
    for i in range(args.hands):
        lines.append(f"| {args.seat}-h{i + 1} | " + " | ".join(cols[s][i] for s in suits) + " |")
    text = "\n".join(lines) + "\n"
    print(text)
    if not args.no_append:
        out = ROOT / "lead-hands.md"
        new = not out.exists()
        with out.open("a", encoding="utf-8") as f:
            if new:
                f.write("# Collision hands\n\n")
            f.write(text + "\n")


if __name__ == "__main__":
    main()
