"""The owner's console actions, append-only (owner directive 2026-10-15 PT; PL-071, revised after review-22).

conversations.json (convo.py) keeps only the newest 500 messages, so older history rolls away. This file never
drops or rewrites a line. One JSON object per line:
  {"uid", "at", "ts", "kind", "seat"?, "id"?, ...}
"uid" is unique per action (a random id; "seed-<message id>" for seeded lines), so nothing is ever merged away by
the entity id. Kinds:
- message: a console message, with its id and text;
- card: a Needs-you answer, including the restart cards (the console has no restart button of its own);
- gate: a team gate decision, as saved (filtered choices, verdict, closure, note);
- checkpoint: a research checkpoint, as saved (valid picks, per-niche notes, general note, phase);
- lab: a lab game's pause, resume or stop;
- lounge: the owner's lounge post.

**Free text is kept as the owner typed it**, up to 4000 characters per field, because it is the record. If the
owner pastes a secret into a message or note, it is in here. Tokens, cookies and request headers are never
written.

Where: RIG_HISTORY_DIR (default /var/lib/rig-console-history). The deploy card creates it once:
  sudo install -d -o rigconsole -g <owner> -m 2750 /var/lib/rig-console-history
That makes it readable by the console and the owner's user only (the snapshot logger runs as the owner). Files
are created 0640, and the setgid bit gives them the owner's group. Until that folder exists, lines go to the
private state/conversations.jsonl. On every write while the shared folder is usable, private lines whose uid isn't
in the shared file yet are appended to it, and the private file is then renamed aside (kept, never deleted).

Integrity: one lock serialises this process's writers; the console is a single process. Every write loops until
all its bytes are down, then fsyncs. If a crash left a partial last line, a newline closes it off before the next
write; readers skip lines that aren't valid JSON, one at a time. These are pathname checks, not an OS security
boundary: the files' owner can still truncate them.
Nonfatal: append() and seed() never raise. append() returns "saved", "saved-private" or "failed", which the API
reports, so a lost record is never claimed as saved.
Seeding: at start-up, the buffer's messages not yet in the file are copied in once, oldest first, with their real
ids and times, marked "reconstructed": true. They're deduplicated against the file and within the buffer.
Messages that already rolled out of the buffer aren't invented, and the file doesn't claim to cover them.
"""
import hashlib, json, os, secrets, threading, time
from datetime import datetime

import convo as CV

PUBLIC_DIR = os.environ.get("RIG_HISTORY_DIR", "/var/lib/rig-console-history")
PRIVATE = os.path.join(CV.STATE, "conversations.jsonl")
NAME = "conversations.jsonl"
MAX_TEXT = 4000
_lock = threading.Lock()


def _shared_usable():
    d = PUBLIC_DIR
    return os.path.isdir(d) and not os.path.islink(d) and os.access(d, os.W_OK)


def _write_all(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o640)
    try:
        size = os.fstat(fd).st_size
        if size and os.pread(fd, 1, size - 1) != b"\n":
            data = b"\n" + data          # close off a partial last line left by a crash
        view = memoryview(data)
        while view:
            n = os.write(fd, view)
            if n <= 0:
                raise OSError("short write")
            view = view[n:]
        os.fsync(fd)
    finally:
        os.close(fd)


def _encode(lines):
    return "".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lines).encode("utf-8")


def _read(path):
    """Valid lines only; a damaged line is skipped on its own, never resetting the rest."""
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for l in f:
                try:
                    v = json.loads(l)
                    if isinstance(v, dict):
                        out.append(v)
                except ValueError:
                    pass
    except OSError:
        pass
    return out


def _reconcile_private(shared):
    """Every private line whose uid isn't in the shared file yet goes in; then the private file is set aside."""
    if not os.path.isfile(PRIVATE) or os.path.islink(PRIVATE):
        return
    have = {l.get("uid") for l in _read(shared)}
    pending = []
    for l in _read(PRIVATE):
        if not l.get("uid"):   # a line without a uid gets a stable one from its content, so it's carried once
            l["uid"] = "legacy-" + hashlib.sha256(json.dumps(l, sort_keys=True).encode()).hexdigest()[:16]
        if l["uid"] not in have:
            have.add(l["uid"])
            pending.append(l)
    if pending:
        _write_all(shared, _encode(pending))
    os.replace(PRIVATE, f"{PRIVATE}.carried-{datetime.now().strftime('%Y%m%d%H%M%S')}")


def _clip(v):
    if isinstance(v, str):
        return v[:MAX_TEXT]
    if isinstance(v, dict):
        return {str(k)[:200]: _clip(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_clip(x) for x in v[:200]]
    return v


def append(kind, **fields):
    now = time.time()
    line = {"uid": secrets.token_hex(8), "at": datetime.fromtimestamp(now).astimezone().isoformat(timespec="seconds"),
            "ts": round(now, 3), "kind": kind}
    line.update({k: _clip(v) for k, v in fields.items() if v is not None})
    try:
        data = _encode([line])
        with _lock:
            if _shared_usable():
                shared = os.path.join(PUBLIC_DIR, NAME)
                try:
                    _reconcile_private(shared)
                    _write_all(shared, data)
                    return "saved"
                except Exception as e:   # the shared file failed: keep the line privately rather than lose it
                    print(f"history: shared write failed ({type(e).__name__}); keeping the {kind} line privately", flush=True)
            _write_all(PRIVATE, data)
            return "saved-private"
    except Exception as e:
        print(f"history: couldn't record a {kind} line ({type(e).__name__})", flush=True)
        return "failed"


def seed():
    """Once per start: the buffer's messages not yet recorded, oldest first, marked reconstructed."""
    try:
        with _lock:
            target = os.path.join(PUBLIC_DIR, NAME) if _shared_usable() else PRIVATE
            if target != PRIVATE:
                _reconcile_private(target)
            # A message already recorded, live or seeded, in either file is never seeded again (recheck-22).
            recorded = _read(target) + _read(PRIVATE)
            seen = {l.get("id") for l in recorded if l.get("kind") == "message" and l.get("id")}
            lines = []
            for e in CV._load():
                mid = e.get("id") if isinstance(e, dict) else None
                if not isinstance(mid, str) or mid in seen:
                    continue
                seen.add(mid)
                lines.append({"uid": f"seed-{mid}", "at": e.get("asked_at"), "ts": e.get("asked_ts"), "kind": "message",
                              "seat": e.get("seat"), "id": mid, "text": _clip(str(e.get("question") or "")),
                              "reconstructed": True})
            if lines:
                _write_all(target, _encode(lines))
            return len(lines)
    except Exception as e:
        print(f"history: seeding failed ({type(e).__name__})", flush=True)
        return 0
