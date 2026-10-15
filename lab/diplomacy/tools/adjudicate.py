#!/usr/bin/env python3
"""Clerk's adjudicator wrapper around the `diplomacy` package (pip install diplomacy).

Draft by the Owner's Advisor, 2026-10-13; repaired by the clerk in the dry run.
State is saved as JSON in clerk/game.json (the package's saved-game format; Game is not picklable).
Run from the clerk/ folder. Relative paths starting board/, powers/ or archive/ resolve against the job folder.

  adjudicate.py init                      new standard game, S1901M
  adjudicate.py state [--json]            current phase, units, centres (JSON for board/<phase>.json)
  adjudicate.py check <POWER> <file>      validate an orders file; prints VALID/INVALID per line
  adjudicate.py submit <POWER> <file>     set that power's valid orders (invalid lines dropped = hold)
                                          Run submits one at a time: each loads and saves game.json, so
                                          parallel submits can overwrite each other.
  adjudicate.py process                   adjudicate the phase; prints results summary
  adjudicate.py legal <POWER>             list legal orders for that power this phase
  adjudicate.py render <out.svg>          draw the current board with the engine's renderer (ownership, units, submitted orders)
                                          The engine draws only orders not yet processed: render board/<phase>-orders.svg
                                          after the submits and before process; after process, render board/<newphase>.svg.
  adjudicate.py archive <PHASE>           copy each power's press/<PHASE>/*.md and orders/<PHASE>.txt into
                                          archive/<PHASE>/ and build archive/<PHASE>/press.jsonl (never intentions)
Power names: AUSTRIA ENGLAND FRANCE GERMANY ITALY RUSSIA TURKEY (case-insensitive).
"""
import json, os, re, shutil, sys

CLERK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOB = os.path.dirname(CLERK)
SAVE = os.path.join(CLERK, "game.json")

def job_path(p):
    # board/, powers/ and archive/ live in the job folder, one level above the clerk's cwd
    if not os.path.isabs(p) and p.split("/", 1)[0] in ("board", "powers", "archive"):
        return os.path.join(JOB, p)
    return p

NATIONS = ["austria", "england", "france", "germany", "italy", "russia", "turkey"]

def _inside(path, root):
    real, root = os.path.realpath(path), os.path.realpath(root)
    return real == root or real.startswith(root + os.sep)

def archive(phase):
    """Copy one phase's press and orders into archive/<phase>/. Only press/<phase>/*.md, orders/<phase>.txt
    and press/sent.jsonl are read; links and anything resolving outside those folders are skipped."""
    if not re.fullmatch(r"[SFW]\d{4}[MRA]", phase):
        print("bad phase", phase); return 2
    dest = os.path.join(JOB, "archive", phase)
    notes, rows, copied = [], [], 0
    for n in NATIONS:
        base = os.path.join(JOB, "powers", n)
        src = os.path.join(base, "press", phase)
        names = set()
        if os.path.isdir(src) and not os.path.islink(src):
            for f in sorted(os.listdir(src)):
                p = os.path.join(src, f)
                if not f.endswith(".md") or os.path.islink(p) or not os.path.isfile(p) or not _inside(p, src):
                    notes.append(f"skipped {n}/press/{phase}/{f}"); continue
                os.makedirs(os.path.join(dest, "press", n), exist_ok=True)
                shutil.copyfile(p, os.path.join(dest, "press", n, f)); copied += 1
                names.add(f[:-3])
        o = os.path.join(base, "orders", phase + ".txt")
        if os.path.isfile(o) and not os.path.islink(o) and _inside(o, os.path.join(base, "orders")):
            os.makedirs(os.path.join(dest, "orders"), exist_ok=True)
            shutil.copyfile(o, os.path.join(dest, "orders", n + ".txt")); copied += 1
        else:
            notes.append(f"no orders file for {n} (hold)")
        log = os.path.join(base, "press", "sent.jsonl")
        logged = set()
        if os.path.isfile(log) and not os.path.islink(log) and _inside(log, os.path.join(base, "press")):
            for i, line in enumerate(open(log, encoding="utf-8"), 1):
                line = line.strip()
                if not line: continue
                try: r = json.loads(line)
                except ValueError: notes.append(f"{n} sent.jsonl line {i}: not JSON"); continue
                if r.get("phase") == phase:
                    rows.append(r); logged.add(f"{str(r.get('to', '')).lower()}-{r.get('n')}")
        for missing in sorted(names - logged): notes.append(f"{n}: press file {missing}.md has no sent.jsonl line")
        for missing in sorted(logged - names): notes.append(f"{n}: sent.jsonl line {missing} has no press file")
    os.makedirs(dest, exist_ok=True)
    rows.sort(key=lambda r: str(r.get("ts", "")))
    with open(os.path.join(dest, "press.jsonl"), "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"archived {phase}: {copied} files, {len(rows)} press.jsonl lines")
    for line in notes: print("NOTE", line)
    return 0

def load():
    from diplomacy.utils.export import from_saved_game_format
    with open(SAVE, encoding="utf-8") as f:
        return from_saved_game_format(json.load(f))

def save(game):
    from diplomacy.utils.export import to_saved_game_format
    tmp = SAVE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(to_saved_game_format(game), f)
    os.replace(tmp, SAVE)

def read_orders(path):
    out = []
    try:
        for line in open(path, encoding="utf-8"):
            s = line.strip()
            if s and not s.startswith("#"):
                out.append(" ".join(s.upper().split()))
    except FileNotFoundError:
        print("NO FILE", os.path.abspath(path), "(all units hold)")
    return out

def state_dict(game):
    st = game.get_state()
    return {
        "phase": game.get_current_phase(),
        "units": st.get("units", {}),
        "centers": st.get("centers", {}),
        "retreats": st.get("retreats", {}),
        "builds": {p: game.get_state()["builds"].get(p) for p in game.powers} if "builds" in st else {},
        "note": game.note if hasattr(game, "note") else "",
    }

def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 0
    cmd = argv[0]
    if cmd == "init":
        from diplomacy import Game
        game = Game()  # standard map, S1901M
        save(game)
        print("initialised", game.get_current_phase()); return 0
    if cmd == "archive":
        if len(argv) != 2:
            print("usage: adjudicate.py archive <PHASE>"); return 2
        return archive(argv[1].upper())
    game = load()
    if cmd == "state":
        d = state_dict(game)
        if "--json" in argv:
            print(json.dumps(d, indent=1, sort_keys=True))
        else:
            print(d["phase"])
            for p in sorted(d["units"]):
                print(f"{p:8s} centres={len(d['centers'].get(p, []))} units={' '.join(d['units'][p])}")
        return 0
    if cmd in ("check", "submit", "legal"):
        power = argv[1].upper()
        if power not in game.powers:
            print("unknown power", power); return 2
        # legal = the engine's possible orders at the locations this power may order this phase
        possible = game.get_all_possible_orders()
        legal = set()
        for loc in game.get_orderable_locations(power):
            legal.update(possible.get(loc, []))
        if cmd == "legal":
            for o in sorted(legal):
                print(o)
            return 0
        orders = read_orders(job_path(argv[2]))
        valid, invalid = [], []
        for o in orders:
            (valid if o in legal else invalid).append(o)
        for o in valid: print("VALID  ", o)
        for o in invalid: print("INVALID", o)
        if cmd == "submit":
            game.set_orders(power, valid)
            save(game)
            print(f"submitted {len(valid)} valid, {len(invalid)} dropped (hold) for {power}")
        return 0 if not invalid else 1
    if cmd == "process":
        before = game.get_current_phase()
        game.process()
        save(game)
        print("processed", before, "->", game.get_current_phase())
        st = game.get_state()
        for p in sorted(st.get("units", {})):
            print(f"{p:8s} centres={len(st['centers'].get(p, []))} units={' '.join(st['units'][p])}")
        if any(st.get("retreats", {}).values()):
            print("retreats needed:", json.dumps(st["retreats"]))
        return 0
    if cmd == "render":
        out = job_path(argv[1])
        game.render(incl_orders=True, incl_abbrev=True, output_format="svg", output_path=out)
        print("rendered", out, os.path.getsize(out), "bytes"); return 0
    print("unknown command", cmd); return 2

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
