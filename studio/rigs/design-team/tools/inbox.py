#!/usr/bin/env python3
"""The design team's inbox: discoveries ("this is fun, look") and design questions.

Usage (from the design job folder):
    python3 tools/inbox.py add discovery --title "Rolling a river floods the valley" --by owner --text "Repro: ... Why fun: ..."
    python3 tools/inbox.py add question  --title "Can magnets stack?" --by build-a --body-file q.md
    python3 tools/inbox.py list                  # open items
    python3 tools/inbox.py list --all
    python3 tools/inbox.py set D-003 spike --note "Two-hour spike on branch spike/river-flood"

Statuses:
    discovery: open, adopted, spike, parked, rejected, escalated
    question:  open, answered, escalated
Files: inbox/discoveries/D-NNN.md and inbox/questions/Q-NNN.md (front matter + body).
Only the creative director changes statuses; anyone (or their lead) can add.
"""
import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KINDS = {"discovery": ("D", ROOT / "inbox" / "discoveries",
                       ["open", "adopted", "spike", "parked", "rejected", "escalated"]),
         "question": ("Q", ROOT / "inbox" / "questions", ["open", "answered", "escalated"])}


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def read(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    front = dict(l.split(": ", 1) for l in m.group(1).splitlines() if ": " in l) if m else {}
    return front, (m.group(2) if m else text)


def write(path, front, body):
    head = "\n".join(f"{k}: {v}" for k, v in front.items())
    path.write_text(f"---\n{head}\n---\n{body.rstrip()}\n", encoding="utf-8")


def find(item_id):
    for prefix, folder, statuses in KINDS.values():
        if item_id.startswith(prefix + "-"):
            p = folder / f"{item_id}.md"
            if p.exists():
                return p, statuses
    sys.exit(f"no such item: {item_id}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("kind", choices=list(KINDS))
    a.add_argument("--title", required=True)
    a.add_argument("--by", required=True)
    a.add_argument("--text")
    a.add_argument("--body-file")
    l = sub.add_parser("list")
    l.add_argument("--all", action="store_true")
    s = sub.add_parser("set")
    s.add_argument("id")
    s.add_argument("status")
    s.add_argument("--note", default="")
    args = ap.parse_args()

    if args.cmd == "add":
        prefix, folder, _ = KINDS[args.kind]
        folder.mkdir(parents=True, exist_ok=True)
        nums = [int(p.stem.split("-")[1]) for p in folder.glob(f"{prefix}-*.md")]
        item_id = f"{prefix}-{(max(nums) + 1 if nums else 1):03d}"
        body = Path(args.body_file).read_text(encoding="utf-8") if args.body_file else (args.text or "")
        write(folder / f"{item_id}.md",
              {"id": item_id, "kind": args.kind, "title": args.title, "by": args.by,
               "status": "open", "opened": now()},
              body + "\n\n## Log\n")
        print(item_id)
        return 0

    if args.cmd == "list":
        rows = []
        for kind, (prefix, folder, _) in KINDS.items():
            for p in sorted(folder.glob(f"{prefix}-*.md")):
                f, _b = read(p)
                if args.all or f.get("status") in ("open", "spike", "escalated"):
                    rows.append(f"{f.get('id', p.stem):6} {f.get('status', '?'):10} {f.get('by', '?'):14} {f.get('title', '')}")
        print("\n".join(rows) if rows else "inbox empty")
        return 0

    path, statuses = find(args.id)
    if args.status not in statuses:
        sys.exit(f"status must be one of: {', '.join(statuses)}")
    front, body = read(path)
    front["status"] = args.status
    body = body.rstrip() + f"\n- {now()}: {args.status}" + (f" ({args.note})" if args.note else "") + "\n"
    write(path, front, body)
    print(f"{args.id} -> {args.status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
