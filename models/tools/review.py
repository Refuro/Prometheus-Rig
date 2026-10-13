#!/usr/bin/env python3
"""Apply the Model Architect's review decisions to ledger lines.

Reads a JSON file mapping ledger ids to the fields to set, for example
  {"O077": {"attribution": "brief", "status": "reviewed MA-015: ...", "revised": "MA-015"}}
and rewrites models/observations.jsonl in place. Only existing ids are touched; the
line count must stay the same. `id`, `harvest_hash` and `harvested_from` can't be changed.

Usage: python3 models/tools/review.py <updates.json> [--dry-run]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "..", "observations.jsonl")
LOCKED = {"id", "harvest_hash", "harvested_from"}


def main(path, dry):
    updates = json.load(open(path))
    lines = open(LEDGER).read().splitlines()
    out, seen = [], set()
    for line in lines:
        o = json.loads(line)
        u = updates.get(o["id"])
        if u:
            bad = LOCKED & set(u)
            if bad:
                sys.exit(f"{o['id']}: can't change {sorted(bad)}")
            o.update(u)
            seen.add(o["id"])
            line = json.dumps(o, ensure_ascii=False)
        out.append(line)
    unknown = set(updates) - seen
    if unknown:
        sys.exit(f"unknown ids: {sorted(unknown)}")
    assert len(out) == len(lines)
    print(f"{len(seen)} lines updated of {len(lines)}" + (" (dry run)" if dry else ""))
    if not dry:
        with open(LEDGER, "w") as f:
            f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], "--dry-run" in sys.argv[2:])
