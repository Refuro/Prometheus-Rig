"""Lab jobs: the owner's pause/stop control for a running game (R-024, PL-039; Diplomacy, by the Owner's Advisor).

The page reads everything through the sandboxed /job/<job>/ route. The one write is the owner's pause/resume/stop:
<job>/board/control.json is read, only "paused" and "stop" are changed (the clerk owns phase, state and
deadline), and it's replaced atomically so the clerk never reads half a file. Seats can edit the job tree, so
the folder is opened without following links (as lounge.py does) and the file is written relative to it.
Nothing is sent, pushed or counted: the clerk polls the file.
"""
import json, os, re

import gates as G
import lounge as LG

MAX = 64_000


def games():
    """Every lab game that has started (a board/control.json), oldest first, and whether it's over
    (board/final.md). For the Diplomacy page's game list (owner, 2026-10-14). Read-only; links aren't followed."""
    out = []
    for name, j in sorted(G._jobs().items(), key=lambda kv: [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", kv[0])]):
        if j.get("type") != "lab":
            continue
        board = os.path.join(j["folder"], "board")
        if os.path.islink(board) or not os.path.isfile(os.path.join(board, "control.json")) or os.path.islink(os.path.join(board, "control.json")):
            continue
        out.append({"job": name, "title": str(j.get("title") or name)[:80], "over": os.path.isfile(os.path.join(board, "final.md"))})
    return {"games": out}


def control(body):
    job = str(body.get("job") or "")
    if not G.ID_RE.match(job) or job not in G._jobs():
        raise ValueError("Unknown job")
    paused, stop = body.get("paused"), body.get("stop")
    if (paused is None) == (stop is None) or (paused is not None and not isinstance(paused, bool)) or (stop is not None and stop is not True):
        raise ValueError('Send {"paused": true|false} or {"stop": true}')
    try:
        dfd = LG._open_dir(os.path.join(G._jobs()[job]["folder"], "board"))
    except OSError:
        raise ValueError("This game hasn't started: there's no board folder")
    try:
        try:
            fd = os.open("control.json", os.O_RDONLY | os.O_NOFOLLOW, dir_fd=dfd)
        except OSError:
            raise ValueError("This game hasn't started: there's no board/control.json")
        with os.fdopen(fd, "rb") as f:
            cur = json.loads(f.read(MAX + 1)[:MAX] or b"null")
        if not isinstance(cur, dict):
            raise ValueError("board/control.json isn't a JSON object, so it was left alone")
        if paused is not None:
            cur["paused"] = paused
            note = "Paused. The clerk stops the clock on its next look." if paused else "Resumed. The clerk restarts the clock on its next look."
        else:
            cur["stop"] = True
            note = "Stop sent. The clerk ends the game after this phase."
        tmp = f".control.json.{os.getpid()}.tmp"
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=dfd)
        with os.fdopen(fd, "w") as f:
            json.dump(cur, f)
        os.replace(tmp, "control.json", src_dir_fd=dfd, dst_dir_fd=dfd)
        return {"ok": True, "note": note, "control": {k: cur.get(k) for k in ("phase", "state", "paused", "stop")}}
    finally:
        os.close(dfd)
