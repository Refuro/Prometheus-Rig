"""Your questions to seats, kept with their replies (PL-024, PL-025; owner requests 2026-10-13).

Each message sent from the console gets an id (m-<local time>-<4 hex>) that travels in the delivered text
as "[msg <id>]". Contract: JOBS.md §3e; process: the Rig Architect (scratch/rig/question-reply-process.md).
- Explicit replies (PL-025): a JSON file {"id", "text", "at"?} named <id>.json, or <id>-2.json, <id>-3.json
  for follow-ups (shown in addition, never replacing the first). Where:
    the operator: <RIG_LAUNCHES_DIR>/replies/ (only the operator writes under launches/, SHARED-RULES §1);
    architects:   <architects job>/replies/  (their own job folder; pairs only with questions to them).
  Pairing is by the exact id only: the file name's id, the "id" inside, and a question the console issued to
  a seat allowed to answer from that folder must all agree. Anything else is ignored and logged once.
- Screen fallback (PL-024): the watcher also reads text off the seat's screen once it's idle again. It's
  kept apart ("screen_reply") and always labelled "from the screen (not a confirmed reply)". It never
  counts as the answer.
No extra polling, no agent turns, no notifications. All reply text is agent-written: shown escaped.
"""
import json, os, re, secrets, threading, time
from datetime import datetime

STATE = os.path.expanduser(os.environ.get("RIG_STATE_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")))
LOG = os.path.join(STATE, "conversations.json")
REPLIES = os.path.join(os.path.expanduser(os.environ.get("RIG_LAUNCHES_DIR", "~/openrig/launches")), "replies")
OPERATOR = os.environ.get("RIG_NOTIFY_RECEIPT_TO", "operator-agent@kernel")   # who may reply from REPLIES
ARCHITECTS_RIG = "architects"   # seats <x>@architects may reply from <architects job>/replies/
FILE_RE = re.compile(r"^(m-\d{14}-[0-9a-f]{4})(?:-([2-9]|[1-9]\d))?\.json$")
_ignored = set()   # files already logged as ignored
KEEP = 500                 # newest entries kept
GIVE_UP_S = 4 * 3600       # no screen reply after this: say so (a file reply is still accepted later)
MAX_REPLY = 20000
ID_RE = re.compile(r"^m-\d{14}-[0-9a-f]{4}$")
MARKER = "Message from the owner"
END_RE = re.compile(r"^\s*(?:─\s*)?Worked for \d|^\s*[✻✶✳✢✽·]\s+\w+ed for \d|^\s*│?\s*[❯›>]\s*(Ask Codex|$)")
REPLY_START = re.compile(r"^\s*(?:●|⏺|•)\s")
SKIP_RE = re.compile(r"^\s*(?:[─━╌]{3,}|\? for shortcuts|GPT-|Claude |⏵⏵|Tip:)|⚠ \d+ warning")
_lock = threading.Lock()


def _load():
    try:
        with open(LOG) as f:
            d = json.load(f)
    except (OSError, ValueError):
        return []
    if not isinstance(d, list):
        return []
    for e in d:   # entries from before PL-025: their reply came off the screen, so label it that way
        if "screen_reply" not in e:
            e["screen_reply"], e["screen_reply_at"] = e.pop("reply", None), e.pop("reply_at", None)
            if e.get("status") == "replied":
                e["status"] = "screen"
        e.setdefault("replies", [])
    return d


def _save(d):
    os.makedirs(STATE, exist_ok=True)
    tmp = LOG + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d[-KEEP:], f, indent=1)
    os.replace(tmp, LOG)


def _now_iso(ts):
    return datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")


def new_id(now=None):
    return datetime.fromtimestamp(now or time.time()).strftime("m-%Y%m%d%H%M%S-") + secrets.token_hex(2)


def reply_folder(seat, architects_folder=None):
    """Where this seat writes reply files, or None (it replies on its screen only)."""
    return next((folder for folder, allowed in _reply_sources(architects_folder) if allowed(seat)), None)


def reply_after_marker(lines):
    """The text after the last owner message on screen, up to the seat's end-of-turn footer. None if the
    owner's message isn't on screen (scrolled away) or nothing follows it yet."""
    idx = max((i for i, ln in enumerate(lines) if MARKER in ln), default=None)
    if idx is None:
        return None
    out = []
    for ln in lines[idx + 1:]:
        if END_RE.search(ln):
            break
        if SKIP_RE.search(ln):
            continue
        out.append(ln.rstrip())
    # The owner's message can wrap onto the next lines (Claude shows it in full). If the seat's answer starts
    # with a reply marker (● ⏺ •), start there; otherwise (Codex) the answer follows the message directly.
    first = next((i for i, ln in enumerate(out) if REPLY_START.match(ln)), None)
    if first is not None:
        out = out[first:]
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    text = "\n".join(out).strip()
    return text[:6000] or None


def record(seat, question, mid=None, now=None):
    now = now or time.time()
    mid = mid or new_id(now)
    with _lock:
        d = _load()
        d.append({"id": mid, "seat": seat, "question": question[:4000], "asked_at": _now_iso(now), "asked_ts": now,
                  "replies": [], "screen_reply": None, "screen_reply_at": None, "status": "waiting"})
        _save(d)
    return mid


def _reply_sources(architects_folder):
    """(folder, may this seat answer from it?) pairs."""
    out = [(REPLIES, lambda seat: seat == OPERATOR)]
    if architects_folder:
        out.append((os.path.join(architects_folder, "replies"), lambda seat: seat.endswith("@" + ARCHITECTS_RIG)))
    return out


def _ignore(path, why):
    if path not in _ignored:
        _ignored.add(path)
        print(f"reply file ignored: {os.path.basename(path)}: {why}", flush=True)


def _file_replies(d, architects_folder=None):
    """Explicit replies, paired by exact id only. Returns True if anything changed."""
    by_id = {e.get("id"): e for e in d if e.get("id")}
    changed = False
    for folder, allowed in _reply_sources(architects_folder):
        try:
            names = sorted(os.listdir(folder))
        except OSError:
            continue
        for fn in names:
            p = os.path.join(folder, fn)
            m = FILE_RE.match(fn)
            if not m:
                if fn.endswith(".json"):
                    _ignore(p, "name isn't <id>.json or <id>-<n>.json")
                continue
            mid, n = m.group(1), int(m.group(2) or 1)
            e = by_id.get(mid)
            if not e or not allowed(e["seat"]):
                _ignore(p, "no question with this id to a seat that answers from this folder")
                continue
            try:
                if os.path.islink(p) or not os.path.isfile(p) or os.path.getsize(p) > MAX_REPLY * 2:
                    _ignore(p, "not a plain file, or too big")
                    continue
                mtime = os.path.getmtime(p)
                got = {r["n"]: r for r in e.get("replies") or []}
                if got.get(n, {}).get("mtime") == mtime:
                    continue
                with open(p, encoding="utf-8") as f:
                    r = json.load(f)
            except (OSError, ValueError) as ex:
                _ignore(p, f"unreadable ({type(ex).__name__})")
                continue
            if not isinstance(r, dict) or r.get("id") != mid or not str(r.get("text") or "").strip():
                _ignore(p, 'needs "id" equal to the file name\'s id and a non-empty "text"')
                continue
            got[n] = {"n": n, "text": str(r["text"]).strip()[:MAX_REPLY], "mtime": mtime,
                      "at": str(r.get("at") or "")[:40] or _now_iso(mtime)}
            e["replies"] = [got[k] for k in sorted(got)]
            e["status"] = "replied"
            changed = True
    return changed


def capture(nodes, screen_of, idle_on_screen, architects_folder=None, now=None):
    """Each watcher round: explicit reply files first, then the screen text for idle seats (labelled, never
    the answer). Status: "replied" only from a file; "screen" when only screen text exists; "waiting";
    "missed" when no screen text could be tied to it (a reply file can still arrive)."""
    now = now or time.time()
    by_seat = {n["id"]: n for n in nodes}
    with _lock:
        d = _load()
        changed = _file_replies(d, architects_folder)
        latest = {}
        for i, e in enumerate(d):
            latest[e["seat"]] = i          # only the newest question per seat can still be on screen
        for i, e in enumerate(d):
            if e.get("status") != "waiting" or e.get("screen_reply"):
                continue
            if latest.get(e["seat"]) != i or now - e.get("asked_ts", now) > GIVE_UP_S:
                e["status"], changed = "missed", True
                continue
            n = by_seat.get(e["seat"])
            if not n or (n.get("state") or "").startswith(("working", "needs_input")) or not idle_on_screen(e["seat"]):
                continue
            text = reply_after_marker(screen_of(e["seat"]))
            if text:
                e.update(screen_reply=text, screen_reply_at=_now_iso(now), status="screen")
                changed = True
        if changed:
            _save(d)
        return d


def history(seat=None):
    keys = ("id", "seat", "question", "asked_at", "replies", "screen_reply", "screen_reply_at", "status")
    d = [{k: e.get(k) for k in keys} for e in _load()]
    for e in d:
        e["replies"] = [{k: r.get(k) for k in ("n", "text", "at")} for r in e.get("replies") or []]
    if seat:
        d = [e for e in d if e["seat"] == seat]
    return list(reversed(d))
