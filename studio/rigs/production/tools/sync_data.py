#!/usr/bin/env python3
"""Copy the design job's data into game/data/ (tech lead only), or check the copy.

The design team owns every number and string and edits them in its own job folder.
Production reads a copy, so each team writes only in its own folder (shared rules).

Usage (from the production job folder):
    python3 tools/sync_data.py                  # replace game/data/ with the design data
    python3 tools/sync_data.py --check          # is game/data/ still the synced copy?
    python3 tools/sync_data.py --check --tree work/dev-a

Source: job.json "design_job" (a folder name under ~/openrig/jobs/, or an absolute path):
its data/ folder plus text-budgets.json (copied to game/data/text-budgets.json).
Writes game/data/SYNCED.json: source, time and a sha256 per file. The build fails if any
file differs from it, so nobody edits design data by hand. Then commit: data sync <date>.
"""
import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

JOB = Path(__file__).resolve().parent.parent
MANIFEST = "SYNCED.json"


def design_dir():
    try:
        name = json.loads((JOB / "job.json").read_text(encoding="utf-8")).get("design_job", "")
    except (OSError, json.JSONDecodeError) as e:
        sys.exit(f"job.json: {e}")
    if not name:
        sys.exit('job.json has no "design_job"')
    p = Path(name) if name.startswith("/") else Path.home() / "openrig" / "jobs" / name
    if not (p / "data").is_dir():
        sys.exit(f"no data/ folder in {p}")
    return p


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(data):
    return {p.relative_to(data).as_posix(): digest(p)
            for p in sorted(data.rglob("*")) if p.is_file() and p.name != MANIFEST}


def check(data):
    """Returns a list of problems; empty means game/data matches its manifest."""
    m = data / MANIFEST
    if not m.exists():
        return [f"{MANIFEST} missing: run python3 tools/sync_data.py (tech lead)"]
    try:
        want = json.loads(m.read_text(encoding="utf-8")).get("files", {})
    except json.JSONDecodeError as e:
        return [f"{MANIFEST}: {e}"]
    have = hashes(data)
    problems = [f"changed by hand: {k}" for k in sorted(want) if k in have and have[k] != want[k]]
    problems += [f"missing: {k}" for k in sorted(want) if k not in have]
    problems += [f"not from the design job: {k}" for k in sorted(have) if k not in want]
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--tree", default="game", help="project folder inside the job (default game)")
    args = ap.parse_args()
    data = JOB / args.tree / "data"

    if args.check:
        problems = check(data)
        for p in problems:
            print("FAIL " + p)
        print("data: ok (matches SYNCED.json)" if not problems else f"data: {len(problems)} problems")
        return 1 if problems else 0

    if args.tree != "game":
        sys.exit("sync only into game/ (main); worktrees get data by merging main")
    src = design_dir()
    before = hashes(data) if data.exists() else {}
    if data.exists():
        shutil.rmtree(data)
    shutil.copytree(src / "data", data)
    budgets = src / "text-budgets.json"
    if budgets.exists():
        shutil.copy(budgets, data / "text-budgets.json")
    after = hashes(data)
    (data / MANIFEST).write_text(json.dumps({
        "source": str(src),
        "synced_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "files": after}, indent=1), encoding="utf-8")
    added = [k for k in after if k not in before]
    removed = [k for k in before if k not in after]
    changed = [k for k in after if k in before and before[k] != after[k]]
    print(f"synced {len(after)} files from {src}/data: {len(added)} added, {len(changed)} changed, {len(removed)} removed")
    for label, items in (("added", added), ("changed", changed), ("removed", removed)):
        for k in items[:40]:
            print(f"  {label}: {k}")
    print("next: python3 tools/build.py --seat tech-lead, then commit 'data sync <date>'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
