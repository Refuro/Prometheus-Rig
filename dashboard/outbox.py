"""The operator's outbox: how the operator notifies the owner (PL-017, owner request 2026-10-13).

The operator writes <RIG_LAUNCHES_DIR>/notify/<id>.json. Only the operator writes under launches/
(SHARED-RULES §1), the same trust the console already gives launch records. Format (JOBS.md §3c):
    {"title": "Bridge production team is ready", "body": "optional detail", "priority": "high"}
Each round the console shows every current note under "Needs you". It pushes each id to the phone once,
ever, and tells the operator what happened with a `rig send` receipt. A note expires 24 h after it was
written. Rewriting an id doesn't send it again: use a new id. Team seats have no route here.
"""
import json, os, re, threading, time

LAUNCHES = os.path.expanduser(os.environ.get("RIG_LAUNCHES_DIR", "~/openrig/launches"))
OUTBOX = os.path.join(LAUNCHES, "notify")
STATE = os.path.expanduser(os.environ.get("RIG_STATE_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")))
SENT = os.path.join(STATE, "notify-sent.json")
RECEIPT_TO = os.environ.get("RIG_NOTIFY_RECEIPT_TO", "operator-agent@kernel")
ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
URL_RE = re.compile(r"^/[A-Za-z0-9._/?=&%-]{0,200}$")   # console pages only, never another site
EXPIRE_S = 24 * 3600
MAX_PER_HOUR = 5
_lock = threading.Lock()


def _sent():
    try:
        with open(SENT) as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _save(d):
    os.makedirs(STATE, exist_ok=True)
    tmp = SENT + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f, indent=1)
    os.replace(tmp, SENT)


def read_notes(now=None):
    """Every note file: (id, note or None, problem or None, mtime). Expired notes are left out."""
    now = now or time.time()
    out = []
    try:
        names = sorted(os.listdir(OUTBOX))
    except OSError:
        return out
    for fn in names:
        if not fn.endswith(".json"):
            continue
        nid, path = fn[:-5], os.path.join(OUTBOX, fn)
        try:
            if not os.path.isfile(path) or os.path.islink(path):
                continue
            mtime = os.path.getmtime(path)
            if now - mtime > EXPIRE_S:
                continue
            if not ID_RE.match(nid):
                out.append((nid[:64], None, "the file name must be letters, numbers, '.', '_' or '-' (64 at most)", mtime))
                continue
            if os.path.getsize(path) > 8000:
                out.append((nid, None, "the file is over 8 KB", mtime))
                continue
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, ValueError) as e:
            out.append((nid, None, f"can't read it as JSON ({type(e).__name__})", 0))
            continue
        title = str(d.get("title") or "").strip() if isinstance(d, dict) else ""
        if not title:
            out.append((nid, None, 'it needs a "title"', mtime))
            continue
        url = str(d.get("url") or "")
        out.append((nid, {
            "title": title[:160],
            "body": str(d.get("body") or "").strip()[:1000],
            "priority": "default" if d.get("priority") == "default" else "high",
            "url": url if URL_RE.match(url) and "//" not in url else "/graph.html",
        }, None, mtime))
    return out


def alerts(now=None):
    """Console alerts for current, valid notes. Kind "operator"; the outbox pushes them itself (nopush)."""
    return [{"kind": "operator", "node": nid, "severity": None if n["priority"] == "high" else "warn",
             "text": n["title"], "detail": n["body"], "url": n["url"], "nopush": True}
            for nid, n, problem, _ in read_notes(now) if n]


def deliver(push, receipt, dismissed=(), now=None):
    """Push each new note once and send the operator one receipt per note.
    push(title, body, priority, url) -> (ok, detail); receipt(text) -> bool."""
    now = now or time.time()
    with _lock:
        sent = _sent()
        recent = [v["at"] for v in sent.values() if v.get("pushed") and now - v.get("at", 0) < 3600]
        changed = False
        for nid, n, problem, mtime in read_notes(now):
            if nid in sent:
                continue
            rec = {"at": now, "pushed": False}
            if problem:
                rec["result"] = f"not shown: {problem}"
            elif f"operator:{nid}" in dismissed:
                rec["result"] = "not pushed: the owner had already dismissed it"
            elif len(recent) >= MAX_PER_HOUR:
                rec["result"] = f"not pushed: over {MAX_PER_HOUR} pushes in the last hour. It is shown under Needs you in the console"
            else:
                ok, detail = push(n["title"], n["body"], n["priority"], n["url"])
                rec["pushed"] = ok
                rec["result"] = ("pushed to the owner's phone (ntfy accepted it; that doesn't prove they read it). "
                                 "Also shown under Needs you" if ok else
                                 f"not pushed: {detail}. It is shown under Needs you in the console")
                if ok:
                    recent.append(now)
            rec["receipt"] = bool(receipt(f"Rig Console receipt for notify/{nid}.json: {rec['result']}. "
                                          "Automatic message; don't reply. To notify again, use a new id."))
            sent[nid] = rec
            changed = True
        if changed:
            _save(sent)
    return sent
