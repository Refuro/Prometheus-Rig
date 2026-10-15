#!/usr/bin/env python3
"""Rig dashboard. Run in Ubuntu:
    python3 <repo>/dashboard/serve.py
then open http://localhost:8800 in your Windows browser.

Reads (never writes):
  ~/openrig/research/<run>/niches.json          one tracker per research run
  ../snapshots/activity-log.csv                 written by rig-snapshots.sh
"""
import traceback
import csv, glob, hmac, html, http.cookies, http.server, io, json, os, posixpath, re, shutil, subprocess, threading, time, urllib.parse
from datetime import datetime
import features as F
import store as S
import gates as G
import models as MD
import outbox as OB
import lounge as LG
import oplog as OL
import jobpage as JP
import lab as LAB
import escalate as EP
import convo as CV
import seatprofile as PR
import digest as DG

DASH = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.expanduser(os.environ.get("RIG_RESEARCH_DIR", "~/openrig/research"))
SNAP = os.path.expanduser(os.environ.get("RIG_SNAPSHOTS", os.path.join(DASH, "..", "snapshots")))
ACTIVITY = F.ACTIVITY   # today's file; earlier days via F.activity_files (R-011)
PORT = int(os.environ.get("PORT", "8800"))
SNAP_STALE_S = int(os.environ.get("RIG_SNAP_STALE_S", "60"))   # the logger writes every ~10 s
BRIEFS = os.path.expanduser(os.environ.get("RIG_BRIEFS_DIR", "~/openrig/briefs"))


def list_runs():
    runs = []
    if not os.path.isdir(DATA):
        return runs
    for name in sorted(os.listdir(DATA)):
        path = os.path.join(DATA, name, "niches.json")
        if not os.path.isfile(path):
            continue
        try:
            with open(path) as f:
                d = json.load(f)
        except Exception as e:  # half-written or invalid file
            runs.append({"run": name, "error": f"Can't read niches.json: {e}"})
            continue
        n = d.get("niches") or []
        try:
            funnel = F.record_funnel(name, d)
        except Exception:
            funnel = {}
        j = G._jobs().get(name)
        team = G.team_of(j) if j else {}
        runs.append({
            "run": name,
            # The team from the operator's launch record (or the pin), not guessed from names (run-report review).
            "rig": team.get("rig") if team.get("source") in ("launch record", "first seen") else None,
            "funnel": funnel,
            "phase": d.get("phase"),
            "updated": d.get("updated"),
            "total": len(n),
            "alive": sum(1 for x in n if x.get("stage") != "cut"),
        })
    try:
        F.record_phases(runs)
    except Exception:
        pass
    return runs


def team():
    """Latest state per seat, how long it has held that state, and its share
    of time spent working over the logged window."""
    if not os.path.isfile(ACTIVITY):
        return {"logger": "missing", "seats": []}
    rows = list(csv.reader(io.StringIO("\n".join(F.activity_tail()))))
    rows = [r for r in rows if len(r) >= 6 and r[0][:2] == "20"]
    if not rows:
        return {"logger": "empty", "seats": []}
    latest_ts = rows[-1][0]
    current = [r for r in rows if r[0] == latest_ts]
    by_seat = {}
    for r in rows:
        by_seat.setdefault(r[2], []).append(r)
    seats = []
    for r in current:
        hist = by_seat[r[2]]
        since = hist[-1][0]
        for h in reversed(hist):
            if h[4] != r[4]:
                break
            since = h[0]
        working = sum(1 for h in hist if h[4] == "working")
        seats.append({
            "rig": r[1], "session": r[2], "lifecycle": r[3], "activity": r[4],
            "since": since, "work_share": round(working / len(hist), 3),
            "window_start": hist[0][0],
        })
    age = (datetime.now() - datetime.strptime(latest_ts, "%Y-%m-%d %H:%M:%S")).total_seconds()
    return {"logger": "ok" if age < 90 else "stale", "latest": latest_ts,
            "age_seconds": int(age), "seats": seats}


_screen_seen = {}  # session -> (hash, last_change_epoch)
_watch_start = {}  # session -> when this server first saw it
ACTION_RE = re.compile(r"^\s*(?:•|●|⏺)\s+(.*\S)")
WORKING_RE = re.compile(r"^\s*[•◦]\s+Working \(([^)]*)\)")
GENERIC_RE = re.compile(r"^(Working \(|Explored$|Exploring$|How is Claude doing)")
SPIN_RE = re.compile(r"^\s*[✻✶✳✢✽·*]\s+(\S.*?)(?:…|\.\.\.)?\s*\((\d[^)·]*)")
ACTIVE_Q = {"pending", "in-progress", "blocked"}


def _load(name):
    try:
        with open(os.path.join(SNAP, name)) as f:
            d = json.load(f)
        if isinstance(d, dict):
            d = d.get("items") or d.get("rows") or []
        return d if isinstance(d, list) else []
    except Exception:
        return []


def _iso_age(ts):
    try:
        t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return (datetime.now(t.tzinfo) - t).total_seconds()
    except Exception:
        return None


def _screen(session, state):
    """Current or last action from the agent's mirrored screen, plus how long
    the screen has been unchanged."""
    path = os.path.join(SNAP, session.replace(":", "_").replace("/", "_") + ".txt")
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()[1:]
    except Exception:
        return {"action": None, "elapsed": None, "unchanged_s": None}
    h = hash("\n".join(lines))
    now = time.time()
    prev = _screen_seen.get(session)
    _watch_start.setdefault(session, now)
    if not prev:
        # First sight: we don't know when it last changed, so assume "a while ago"
        # rather than claiming it is active.
        _screen_seen[session] = (h, now - 3600)
    elif prev[0] != h:
        _screen_seen[session] = (h, now)
    unchanged = now - _screen_seen[session][1]
    action, elapsed = None, None
    if state.startswith("needs_input"):
        tail = [ln.strip() for ln in lines[-160:]]  # long commands push the header far up
        for ln in reversed(tail):  # Codex: "Reason: ..."
            if ln.startswith("Reason:"):
                action = "Asking approval: " + ln[7:].strip()
                break
        if not action:  # Claude Code: a tool header, an optional tip, a description, then a dashed box
            for i in range(len(tail) - 1, -1, -1):  # the most recent prompt header
                ln = tail[i]
                if ln in ("Bash command", "Fetch", "Web Search", "Edit file", "Write", "Create file", "Read file"):
                    rest = tail[i + 1:]
                    stop = next((j for j, x in enumerate(rest) if x.startswith("╌") or x.startswith("│") or x.startswith("Do you want")), len(rest))
                    desc = next((x for x in reversed(rest[:stop]) if x), "")
                    if desc.startswith("Tip:") or "switch to auto mode" in desc:
                        desc = ""
                    cmd = next((x.lstrip("│ ").strip() for x in rest[stop:stop + 4] if x.startswith("│")), "")
                    action = f"Asking approval ({ln.lower()}): {desc or cmd}" if (desc or cmd) else f"Asking approval: {ln}"
                    break
        action = action or "Waiting at a prompt"
    else:
        if state == "working":
            for ln in reversed(lines[-25:]):
                m = WORKING_RE.match(ln) or SPIN_RE.match(ln)
                if m:
                    elapsed = re.sub(r"\s*[•·].*$", "", m.group(m.lastindex)).strip()
                    break
        for idx in range(len(lines) - 1, -1, -1):
            m = ACTION_RE.match(lines[idx])
            if m and not GENERIC_RE.match(m.group(1)):
                # Keep the wrapped continuation lines too, so long messages aren't cut.
                parts = [m.group(1)]
                for nxt in lines[idx + 1: idx + 12]:
                    t = nxt.strip()
                    if not t or not nxt.startswith(" ") or ACTION_RE.match(nxt) or t[0] in "⎿└─╌│❯›✻✶✳✢✽◦":
                        break
                    parts.append(t)
                action = re.sub(r"\s+", " ", " ".join(parts)).rstrip("…").strip()
                break
    if not action and state != "working":
        # Finished agents often end with plain text, not a "•" action line: use their last message.
        chrome = re.compile(r"^(›|❯|>|\?|GPT-|Tip:|─|╌|│|⏵|Worked for|✻|updated |How is Claude doing)")
        block = []
        for ln in reversed(lines):
            t = ln.strip()
            if not t:
                if block:
                    break
                continue
            if chrome.match(t):
                if block:
                    break
                continue
            block.insert(0, t)
            if len(block) >= 6:
                break
        if block:
            action = "Finished: " + re.sub(r"\s+", " ", " ".join(block)).strip()
    if action and len(action) > 600:
        action = action[:597] + "…"
    since_start = _screen_seen[session][1] < _watch_start[session]
    return {"action": action, "elapsed": elapsed, "unchanged_s": int(unchanged),
            "since_start": since_start, "watched_s": int(now - _watch_start[session])}


QITEM_RE = re.compile(r"qitem-[0-9a-f-]{6,}", re.I)
CMD_PLAIN = [
    (r"^rig queue show", "Reading a handoff"), (r"^rig queue handoff", "Handing off work"),
    (r"^rig queue claim", "Picking up work"), (r"^rig queue update", "Updating a task"),
    (r"^rig queue create", "Assigning work"), (r"^rig queue list", "Checking the queue"),
    (r"^rig send\s+(\S+)", "Messaging {1}"), (r"^rig (ps|status|whoami)", "Checking the team"),
    (r"^rig ", "Running an OpenRig command"),
    (r"^(python3?|node)\b", "Running a script"), (r"^(cat|head|tail|less|sed -n|grep|rg|ls|find|wc)\b", "Reading files"),
    (r"^git\b", "Using git"), (r"^(curl|wget)\b", "Fetching a page"), (r"^(mkdir|cp|mv|touch)\b", "Organizing files"),
]


def _plain_cmd(cmd):
    cmd = cmd.strip().strip("`")
    for pat, text in CMD_PLAIN:
        m = re.match(pat, cmd)
        if m:
            if "{1}" in text:
                return text.replace("{1}", m.group(1).split("@")[0].strip("'\""))
            return text
    return "Running a command"


def plain(action):
    """Turn a raw screen line into something a person can read at a glance."""
    if not action:
        return action
    a = action
    m = re.match(r"^Thinking \(([^)]*)\)(?::\s*after\s+(.*))?$", a)
    if m:
        return f"Thinking ({m.group(1).strip()})"
    m = re.match(r"^Working \(([^)]*)\)", a)
    if m:
        return f"Working ({m.group(1).strip()})"
    if a.startswith("Asking approval"):
        m = re.match(r"^Asking approval(?: \(([^)]*)\))?: (.*)$", a)
        if m:
            what = m.group(2)
            for lead in ("May I ", "Can I ", "Allow "):
                if what.startswith(lead):
                    what = what[len(lead):].rstrip("?")
                    what = what[:1].upper() + what[1:]
            return "Needs your OK: " + QITEM_RE.sub("a task", what)
        return "Needs your OK"
    m = re.match(r"^(?:Ran|Running)\s+(.*)$", a)
    if m:
        return _plain_cmd(m.group(1))
    m = re.match(r"^Bash\((.*)", a)
    if m:
        return _plain_cmd(m.group(1))
    m = re.match(r"^Searched (?:the web )?(?:for )?\"?(.+?)\"?$", a) or re.match(r"^Web ?Search\(\s*\"?([^\")]*)", a)
    if m and m.group(1).strip():
        q = re.sub(r'["“”]+', " ", m.group(1)).strip()
        q = re.sub(r"\s+", " ", q)
        return "Searching the web" if q.lower() in ("the web", "web") else f"Searching the web: {q[:80]}"
    if re.match(r"^Searching(?: the web)?\b", a):
        return "Searching the web"
    m = re.match(r"^(?:Fetch\(|Opened |Fetched |Visited )(https?://[^/)\s]+)", a)
    if m:
        return "Reading " + re.sub(r"^https?://(www\.)?", "", m.group(1))
    m = re.match(r"^(Read|Write|Edit|Update|Create)\(([^)]*)\)", a)
    if m:
        verb = {"Read": "Reading", "Write": "Writing", "Edit": "Editing", "Update": "Editing", "Create": "Creating"}[m.group(1)]
        return f"{verb} {os.path.basename(m.group(2).strip())}"
    m = re.match(r"^(Explored|Read \d+ files?|Searched)", a)
    if m:
        return "Reading files"
    return QITEM_RE.sub("a task", a)


def _logged_rigs(tail_bytes):
    """Every team with recorded history: SQLite's (all of it, since the activity log rotates daily, R-011),
    plus the recent log in case the collector hasn't caught up."""
    rigs = {r["rig"] for r in S.replay_rigs() if r.get("rig")}
    rigs |= {row[1] for row in csv.reader(io.StringIO("\n".join(F.activity_tail(tail_bytes)))) if len(row) > 2 and row[0][:2] == "20"}
    return rigs


def history(minutes=30):
    """Per seat, one state per minute for the last N minutes: w(orking), b(locked), i(dle), or ''."""
    out = {}
    if not os.path.isfile(ACTIVITY):
        return out
    now = datetime.now()
    rows = list(csv.reader(io.StringIO("\n".join(F.activity_tail(600_000)))))
    for r in rows:
        if len(r) < 6 or r[0][:2] != "20":
            continue
        try:
            age = (now - datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S")).total_seconds()
        except ValueError:
            continue
        b = int(age // 60)
        if b >= minutes or b < 0:
            continue
        st = "b" if r[4].startswith("needs_input") else "w" if r[4] in ("working", "running") else "i"
        cell = out.setdefault(r[2], [dict() for _ in range(minutes)])[minutes - 1 - b]
        cell[st] = cell.get(st, 0) + 1
    return {k: ["b" if c.get("b") else max(c, key=c.get) if c else "" for c in v] for k, v in out.items()}


def _screen_tail(session, n):
    try:
        with open(os.path.join(SNAP, session + ".txt"), encoding="utf-8", errors="replace") as f:
            return f.read().splitlines()[-n:]
    except Exception:
        return []


# What a seat's screen shows at the bottom: a choice it's waiting on ("menu"), an empty input box ("idle"),
# or neither ("unknown"). OpenRig sometimes reports an idle Claude seat as "at a prompt" and then refuses
# messages (2026-10-12); the screen settles it. Anything unclear counts as a prompt.
MENU_RE = re.compile(r"^\s*[❯›>]\s*\d+\.\s|\b1\.\s+Yes\b|Do you want to|Would you like to|Esc to cancel|Press enter to confirm|\(y/n\)|\[y/N\]", re.I)
INPUT_RE = re.compile(r"^\s*│?\s*[❯›>](\s.*)?$")
REPLY_RE = re.compile(r"^(?:●|⏺|•)\s+(.*)")
# Codex's slow-model notice: a menu, but nothing to approve ("No action is required; Codex will keep waiting").
SLOW_RE = re.compile(r"No action is required|Dismiss and keep waiting|Giving this request a little extra thought", re.I)
TOOL_RE = re.compile(r"^(?:●|⏺|•)\s+(?:[A-Z][A-Za-z]*\(|Ran |Read |Edited |Explored|Waiting|Working)")


def screen_prompt(session, max_age_s=None):
    """("menu" | "idle" | "unknown", age in seconds or None, the last 15 lines)."""
    try:
        p = os.path.join(SNAP, session + ".txt")
        age = time.time() - os.path.getmtime(p)
        with open(p, encoding="utf-8", errors="replace") as f:
            tail = [l.rstrip() for l in f.read().splitlines()[-15:]]
    except OSError:
        return "unknown", None, []
    if max_age_s is not None and age > max_age_s:
        return "unknown", age, tail
    if any(MENU_RE.search(l) for l in tail):
        return "menu", age, tail
    if any(INPUT_RE.match(l) for l in tail[-8:]):
        return "idle", age, tail
    return "unknown", age, tail


def last_reply(lines, limit=1500):
    """The seat's most recent answer on screen: its last text block that isn't a tool call."""
    start = None
    for i in range(len(lines) - 1, -1, -1):
        if REPLY_RE.match(lines[i]) and not TOOL_RE.match(lines[i]):
            start = i
            break
    if start is None:
        return ""
    out = [REPLY_RE.match(lines[start]).group(1)]
    for l in lines[start + 1:]:
        if REPLY_RE.match(l) or INPUT_RE.match(l) or l.lstrip().startswith(("─", "╭", "╰", "✻", "✶", "✳")):
            break
        out.append(l.strip())
    return "\n".join(out).strip()[:limit]


# Which alerts may notify the owner (phone push and desktop), and under what name (PL-017, owner request
# 2026-10-13: too many notifications, mostly "screen unchanged"). Everything else stays in the console:
# screen unchanged, busy for long, context, handoffs and duplicate folder names are diagnostics, not news.
# kind -> (notification title, seconds the alert must last first)
NOTIFY = {
    "gate": ("Decision needed", 0),
    "operator": ("From the operator", 0),
    "limit": ("Stopped: usage limit", 0),
    "snapshots": ("Console can't see the agents", 0),   # already 60 s stale before it exists
    "decision": ("Check a decision", 0),
    "jobrig": ("Team routing changed", 0),
    "approval": ("Waiting for approval", 600),   # most clear within minutes; only a long wait is news
    "task": ("To do", 0),                        # owner tasks (R-018) notify only when marked urgent
}
# "Needs you" sections (R-018): Decide (choices), Do (hands-on, stays until answered), FYI (operator notes).
# Alerts not in NOTIFY go under "Other signals", collapsed: diagnostics, nothing to do.
SECTION = {"gate": "decide", "decision": "decide", "operator": "fyi"}   # other NOTIFY kinds: "do"
# Which NOTIFY kinds stay off the phone (R-030, owner approved 2026-10-14): the operator judges them and pushes
# through JOBS.md 3c if needed. NOTIFY itself, Needs you's "must act" list and desktop notices don't change.
# An alert with "push": True (the operator's own seat at a limit) still pushes.
NO_PUSH = {"limit", "jobrig"}
PROVIDER = {"claude-code": "Claude", "claude": "Claude", "codex": "Codex"}
_limit_since = {}   # seat -> when this server first saw it at a usage limit
_alert_seen = {}   # alert key -> when this server first saw it, while it lasts


def _label(al):
    if al["kind"] not in NOTIFY:
        return None
    if al["node"] == "console" and al["kind"] != "snapshots":
        return "Console problem"   # a broken check, not the event itself
    return NOTIFY[al["kind"]][0]


def _notify_title(al, age_s):
    if al["kind"] not in NOTIFY or age_s < NOTIFY[al["kind"]][1] or (al["kind"] == "task" and not al.get("urgent")):
        return None
    return _label(al)


# A short cache for the slow read-only answers every page polls (graph, gates, docket, digest, seat; owner approved
# 2026-10-14, measurements in jobs/architects/ops/console-speed-assessment.md). An answer is reused for CACHE_S
# seconds, below the logger's 10 s write interval. Identical requests that arrive while one is being computed wait
# for it instead of computing again. Any POST clears the cache before and after it runs, so the owner's own
# changes show at once. Errors are never cached. Cached values are shared, so callers must not change them.
CACHE_S = float(os.environ.get("RIG_CACHE_S", "5"))
CACHE_MAX = 64   # keys include a day or a seat, so entries are capped: expired ones go first, then the oldest
_CACHE, _CACHE_LOCK, _CACHE_GEN = {}, threading.Lock(), [0]


class _Entry:
    __slots__ = ("gen", "t", "value", "err", "ready")

    def __init__(self, gen):
        self.gen, self.t, self.value, self.err, self.ready = gen, time.monotonic(), None, None, threading.Event()


def cached(key, fn):
    if CACHE_S <= 0:
        return fn()
    with _CACHE_LOCK:
        e = _CACHE.get(key)
        now = time.monotonic()
        reuse = e is not None and e.gen == _CACHE_GEN[0] and (not e.ready.is_set() or now - e.t < CACHE_S)
        if not reuse:
            if len(_CACHE) >= CACHE_MAX:
                for k in [k for k, x in _CACHE.items() if x.ready.is_set() and now - x.t >= CACHE_S]:
                    del _CACHE[k]
                done = sorted((x.t, k) for k, x in _CACHE.items() if x.ready.is_set())
                for _, k in done[:max(0, len(_CACHE) - CACHE_MAX + 1)]:
                    del _CACHE[k]
            if len(_CACHE) >= CACHE_MAX:
                e = None   # still full: every entry is mid-computation, so this one isn't kept (recheck-8)
            else:
                e = _CACHE[key] = _Entry(_CACHE_GEN[0])
    if e is None:
        return fn()
    if reuse:
        # Use the shared answer only if it finished, didn't fail, and no write cleared the cache while we waited.
        if e.ready.wait(60) and e.err is None and e.gen == _CACHE_GEN[0]:
            return e.value
        return fn()   # failed, cleared meanwhile, or over a minute: compute for this request, uncached
    try:
        e.value = fn()
    except BaseException as x:
        e.err = x
        with _CACHE_LOCK:
            if _CACHE.get(key) is e:
                del _CACHE[key]
        raise
    finally:
        e.t = time.monotonic()
        e.ready.set()
    return e.value


def _docket():
    qa = os.path.join(SNAP, "_queue_active.json")
    full = _load("_queue_active.json") if os.path.isfile(qa) else None
    qp = qa if full is not None else os.path.join(SNAP, "_queue.json")
    return JP.docket(_load("_ps.json"), full, _load("_queue.json"), os.path.getmtime(qp) if os.path.isfile(qp) else None,
                     [t for t in G.list_tasks() if not t.get("error")])


def invalidate_cache():
    with _CACHE_LOCK:
        _CACHE_GEN[0] += 1
        _CACHE.clear()


def graph():
    ps = _load("_ps.json")
    queue = _load("_queue.json")
    runs = {r["run"]: r for r in list_runs() if "error" not in r}
    nodes, alerts = [], []
    limited = {}   # runtime -> [(seat, rig, stopped since)] (R-030)
    hist = history()
    ctx = {}
    for c in _load("_ctx.json"):
        cu = c.get("contextUsage") or {}
        if isinstance(cu, dict) and cu.get("percent") is not None:
            ctx[c.get("canonicalSessionName")] = {"percent": cu.get("percent"), "state": cu.get("state")}
    active_by_dest = {}
    for q in queue:
        if q.get("state") in ACTIVE_Q:
            active_by_dest.setdefault(q.get("destinationSession"), []).append(q)
    for r in ps:
        if r.get("runtime") == "terminal" or r.get("sessionStatus") not in (None, "running"):
            continue
        a = r.get("agentActivity") or {}
        st = a.get("state", "unknown")
        st = "working" if st == "running" else st
        if a.get("reason"):
            st = f"{st}:{a['reason']}"
        sess = r.get("canonicalSessionName")
        scr = _screen(sess, st)
        inferred = False
        if st == "unknown" and scr["unchanged_s"] is not None:
            # OpenRig has no signal for this seat (common for idle Claude seats):
            # infer from whether its screen is still changing.
            st, inferred = ("working" if scr["unchanged_s"] < 45 else "idle"), True
        slow = st.startswith("needs_input") and SLOW_RE.search("\n".join(_screen_tail(sess, 25)))
        if slow:
            # Codex's "Giving this request a little extra thought" menu: the model is slow and Codex keeps
            # waiting by itself. OpenRig calls it a prompt, but it isn't an approval (operator, 17:44Z).
            st, inferred = "working", True
        if st == "working" and not inferred and (scr["unchanged_s"] or 0) > 300:
            # OpenRig sometimes reports "running" for a seat that is sitting at its prompt (e.g. text typed
            # into the input box). A working agent shows a live spinner/timer that changes the screen; with no
            # spinner and nothing changing for 5+ minutes, it's idle, not frozen.
            tail25 = _screen_tail(sess, 25)
            if not any(WORKING_RE.match(ln) or SPIN_RE.match(ln) for ln in tail25):
                st, inferred = "idle", True
        work = active_by_dest.get(sess, [])
        node = {
            "id": sess, "rig": r.get("rigName"), "name": sess.split("@")[0],
            "runtime": r.get("runtime"), "model": r.get("model"), "state": st,
            "lifecycle": r.get("lifecycleState"), "raw": scr["action"],
            "action": "Model is slow to answer; it keeps waiting (nothing to approve)" if slow else plain(scr["action"]),
            "elapsed": scr["elapsed"], "ctx": ctx.get(sess), "since_start": scr.get("since_start"), "watched_s": scr.get("watched_s"),
            "inferred": inferred, "history": hist.get(sess, []),
            "unchanged_s": scr["unchanged_s"], "work": [
                {"id": q.get("qitemId"), "from": q.get("sourceSession"), "state": q.get("state"),
                 "tags": q.get("tags") or [], "age_s": _iso_age(q.get("tsCreated") or "")}
                for q in work],
        }
        tail_txt = "\n".join(_screen_tail(sess, 25))
        if re.search(r"usage limit reached|rate limit reached|You've hit your (usage )?limit|out of (usage|credits)", tail_txt, re.I):
            node["alert"] = "limit"
            node["action"] = "Hit its usage limit and stopped"
            # One alert per provider, not per seat (R-030): collected here, added after the loop.
            limited.setdefault(node.get("runtime") or "unknown", []).append((sess, node.get("rig"), _limit_since.setdefault(sess, time.time())))
        elif st.startswith("needs_input"):
            node["alert"] = "approval"
            alerts.append({"kind": "approval", "node": sess,
                           "text": f"{node['name']} is waiting for approval", "detail": scr["action"]})
        elif st == "working" and (scr["unchanged_s"] or 0) > 300 and time.time() - _watch_start.get(sess, time.time()) > 300:
            node["alert"] = "frozen"
            alerts.append({"kind": "frozen", "node": sess,
                           "text": f"{node['name']} screen unchanged for {scr['unchanged_s']//60} min while working"})
        streak = 0
        for c in reversed(node["history"]):
            if c != "w":
                break
            streak += 1
        node["busy_streak_min"] = streak
        if not node.get("alert") and st == "working" and streak >= 15:
            node["alert"] = "long"
            alerts.append({"kind": "long", "severity": "warn", "node": sess,
                           "text": f"{node['name']} has been busy for {streak}+ min straight",
                           "detail": "Fine for real work. If it's just monitoring or polling, it's spending usage for nothing."})
        nodes.append(node)
    # Usage limits, one alert per provider (R-030): "Claude usage limit: 6 seats stopped since 01:20". Each
    # seat still shows its own badge on the graph. It doesn't push to the phone; the operator gets one queue
    # item per outage (escalate.track_outages) and decides. If the operator's own seat (kernel) is stopped,
    # nobody else can judge, so that alert still pushes.
    for s in [s for s in _limit_since if not any(s == x[0] for xs in limited.values() for x in xs)]:
        del _limit_since[s]
    for runtime, xs in sorted(limited.items()):
        since = min(t for _, _, t in xs)
        names = ", ".join(sorted(s.split("@")[0] for s, _, _ in xs))
        alerts.append({"kind": "limit", "node": f"provider:{runtime}",
                       "text": f"{PROVIDER.get(runtime, runtime)} usage limit: {len(xs)} seat{'s' if len(xs) != 1 else ''} stopped since {datetime.fromtimestamp(since).strftime('%H:%M')}",
                       "detail": f"Stopped: {names}. They continue when the limit resets. The operator decides what to tell you.",
                       "runtime": runtime, "seats": [s for s, _, _ in xs], "since": since,
                       "push": any(rig in EP.SKIP_RIGS for _, rig, _ in xs)})
    # Fill in each seat's model from the operator's launch record when OpenRig doesn't report one (MA-010).
    try:
        launched = G.launched_seats()
        for n in nodes:
            info = (launched.get(n["rig"]) or {}).get(n["name"])
            if info and info.get("model"):
                if not n.get("model"):
                    n["model"] = info["model"] + (f" {info['version']}" if info.get("version") else "")
                n["model_source"] = "launch record"
    except Exception:
        pass
    by_id = {q.get("qitemId"): q for q in queue}
    edges = {}
    for q in queue:
        s, d = q.get("sourceSession"), q.get("destinationSession")
        if not s or not d or s == d:
            continue
        a_, b_ = sorted((s, d))
        e = edges.setdefault((a_, b_), {"a": a_, "b": b_, "from": s, "to": d, "total": 0, "a_to_b": 0, "b_to_a": 0,
                                        "active": 0, "active_to": None, "stuck": 0, "last": None})
        e["total"] += 1
        e["a_to_b" if s == a_ else "b_to_a"] += 1
        ts = q.get("tsUpdated") or q.get("tsCreated")
        if ts and (e["last"] is None or ts > e["last"]):
            e["last"] = ts
        if q.get("state") in ACTIVE_Q:
            e["active"] += 1
            e["active_to"] = d
            age = _iso_age(q.get("tsCreated") or "") or 0
            dep = by_id.get(q.get("blockedOn") or "")
            # "blocked" on a sub-task that is still being worked is a normal dependency, not a stall.
            waiting_on_live_dep = q.get("state") == "blocked" and dep is not None and dep.get("state") in ACTIVE_Q
            if (q.get("state") == "pending" and not q.get("claimedAt") and age > 600) or \
                    (q.get("state") == "blocked" and not waiting_on_live_dep):
                e["stuck"] += 1
                alerts.append({"kind": "handoff", "node": d,
                               "text": f"Handoff to {d.split('@')[0]} {'blocked' if q.get('state')=='blocked' else 'unclaimed for ' + str(int(age//60)) + ' min'}"})
    for e in edges.values():
        age = _iso_age(e["last"] or "")
        e["recent"] = age is not None and age < 1800
    rigs = {}
    for n in nodes:
        rg = rigs.setdefault(n["rig"], {"name": n["rig"], "phase": None, "run": None})
        for run, info in runs.items():
            if run in (n["rig"] or ""):
                rg["phase"], rg["run"] = info.get("phase"), run
    # Context meters: warn when an agent's memory is nearly full.
    for n in nodes:
        c = n.get("ctx") or {}
        if (c.get("percent") or 0) >= 80:
            alerts.append({"kind": "context", "severity": "warn", "node": n["id"],
                           "text": f"{n['name']} is {c['percent']:.0f}% through its context window",
                           "detail": "Near the limit it starts dropping earlier details. Consider a handoff or fresh session."})
    # Stale snapshots: everything above is built from them, so a stuck logger silently freezes every state
    # and alert (2026-10-12, a hung copy). _status.txt is rewritten every round, even when `rig` fails.
    try:
        age = time.time() - os.path.getmtime(os.path.join(SNAP, "_status.txt"))
    except OSError:
        age = None
    if age is None or age > SNAP_STALE_S:
        when = "never" if age is None else f"{int(age)} s ago" if age < 120 else f"{int(age // 60)} min ago"
        alerts.append({"kind": "snapshots", "node": "console",
                       "text": f"Agent snapshots stopped updating (last {when}): states and alerts here are out of date",
                       "detail": "The snapshot logger is stuck or stopped. Check it with: systemctl status rig-snapshots. "
                                 "Restarting it (sudo systemctl restart rig-snapshots) is safe.",
                       "url": "/system.html"})
    # The operator's notes to you (outbox.py, JOBS.md §3c).
    try:
        alerts.extend(OB.alerts())
    except Exception as e:
        alerts.append({"kind": "outbox", "severity": "warn", "node": "console", "text": "Couldn't read the operator's notes",
                       "detail": f"{type(e).__name__}: {e}"[:200]})
    # Hands-on tasks the architects have asked of you (R-018).
    try:
        for t in G.list_tasks():
            if t.get("error"):
                alerts.append({"kind": "taskfile", "severity": "warn", "node": t["id"], "text": "A task card can't be read",
                               "detail": t["error"]})
                continue
            alerts.append({"kind": "task", "severity": None if t["urgent"] else "warn", "node": t["id"],
                           "text": t["title"], "detail": t["action"], "urgent": t["urgent"], "url": "/needs.html"})
    except Exception as e:
        alerts.append({"kind": "tasks", "severity": "warn", "node": "console", "text": "Couldn't read the task cards",
                       "detail": f"{type(e).__name__}: {e}"[:200]})
    # Decision gates any job has opened for you.
    try:
        for gt in G.list_gates(0)["open"]:
            alerts.append({"kind": "gate", "severity": "warn", "node": f"{gt['job']}.{gt['id']}",
                           "text": f"{gt['job']}: {gt['title']}", "detail": gt["question"] or "A team is waiting for your decision.",
                           "url": f"/decide.html?job={gt['job']}&gate={gt['id']}"})
    except Exception as e:
        # Don't hide this: a broken gates folder would otherwise silently drop every "decide this" alert.
        alerts.append({"kind": "gates", "severity": "warn", "node": "console",
                       "text": "Couldn't check for open decisions", "detail": f"{type(e).__name__}: {e}"[:200], "url": "/decide.html"})
    for name in S.duplicate_jobs():
        alerts.append({"kind": "jobname", "severity": "warn", "node": name,
                       "text": f"Two job folders are both named {name}",
                       "detail": "Only the first is shown. Rename one so gates and files can't be mixed up."})
    try:
        for m in G.team_mismatches():
            alerts.append({"kind": "jobrig", "node": m["job"],
                           "text": f"{m['job']} now says it belongs to team {m['claimed']}",
                           "detail": f"The console keeps sending its decisions to {m['rig']} ({m['source']}). If the team really changed, ask the operator to update the launch record."})
    except Exception as e:
        alerts.append({"kind": "jobrig", "severity": "warn", "node": "console", "text": "Couldn't check which team owns each job", "detail": f"{type(e).__name__}: {e}"[:200]})
    # Decision files the console didn't write (R-005 step 1).
    try:
        for u in G.unverified_decisions():
            what = "changed after you decided it" if u["changed"] else "was written outside the console"
            if u["closed"] and not u["changed"]:
                alerts.append({"kind": "decision", "severity": "warn", "node": f"{u['job']}.{u['gate']}",
                               "text": f"{u['job']}: gate “{u['gate']}” was closed outside the console",
                               "detail": "Usually the operator closing a gate you decided in chat. If you didn't, check it.",
                               "url": f"/decide.html?job={u['job']}&gate={u['gate']}"})
            else:
                alerts.append({"kind": "decision", "node": f"{u['job']}.{u['gate']}",
                               "text": f"{u['job']}: the decision for “{u['gate']}” {what}",
                               "detail": "You didn't make this in the console. Check it before the team acts on it. (This check catches mistakes; it can't prove a decision is genuine.)",
                               "url": f"/decide.html?job={u['job']}&gate={u['gate']}"})
    except Exception as e:
        alerts.append({"kind": "decision", "severity": "warn", "node": "console",
                       "text": "Couldn't check decision files", "detail": f"{type(e).__name__}: {e}"[:200]})
    # Dismissals last only as long as the condition: once an alert clears, its dismissal is forgotten.
    dis = _dismissed()
    keys = set()
    now = time.time()
    for al in alerts:
        al["key"] = f"{al['kind']}:{al['node']}"
        keys.add(al["key"])
        al["dismissed"] = al["key"] in dis
        al["notify"] = _notify_title(al, now - _alert_seen.setdefault(al["key"], now))
        if al["kind"] in NO_PUSH and not al.get("push"):
            al["nopush"] = True    # still on the dashboard and desktop; the phone push is the operator's call (R-030)
        # Task cards live on their own page (needs.html, R-018 08:10Z correction). Their alert exists only so an
        # urgent card can push once; the graph and phone panels leave section "inbox" out.
        al["act"] = al["kind"] in NOTIFY and al["kind"] != "task"   # the panel's "must act" list; the rest are "Other signals"
        al["label"] = _label(al)           # e.g. "Decision needed"; None for other signals
        al["section"] = "inbox" if al["kind"] == "task" else SECTION.get(al["kind"], "do") if al["act"] else "other"
    for k in [k for k in _alert_seen if k not in keys]:
        del _alert_seen[k]
    if set(dis) - keys:
        _save_dismissed({k: v for k, v in dis.items() if k in keys})
    return {"generated": datetime.now().isoformat(timespec="seconds"),
            "rigs": list(rigs.values()), "nodes": nodes, "edges": list(edges.values()),
            "alerts": alerts, "queue_seen": len(queue)}


RUN_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
DISMISSED = os.path.join(F.STATE, "dismissed.json")


def _dismissed():
    try:
        with open(DISMISSED) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_dismissed(d):
    os.makedirs(os.path.dirname(DISMISSED), exist_ok=True)
    tmp = DISMISSED + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f)
    os.replace(tmp, DISMISSED)


def _rig_bin():
    if "RIG_BIN" in os.environ:          # tests set RIG_BIN="" so nothing is ever sent to a real rig
        return os.environ["RIG_BIN"] or None
    found = shutil.which("rig")
    if found:
        return found
    cands = sorted(glob.glob(os.path.expanduser("~/.nvm/versions/node/*/bin/rig")))
    return cands[-1] if cands else None


def _lead_for(run):
    for r in _load("_ps.json"):
        if run in (r.get("rigName") or "") and "lead" in (r.get("logicalId") or "") \
                and r.get("runtime") != "terminal":
            return r.get("canonicalSessionName")
    return None


def save_decision(run, body):
    """Write the user's checkpoint decision where the lead can read it, then
    tell the lead. Only ids that exist in the run's tracker are accepted."""
    if not RUN_RE.match(run or ""):
        raise ValueError("Unknown run")
    run_dir = os.path.join(DATA, run)
    with open(os.path.join(run_dir, "niches.json")) as f:
        tracker = json.load(f)
    by_id = {n.get("id"): n for n in tracker.get("niches") or []}
    picks = [i for i in body.get("deep_dive") or [] if i in by_id]
    if not picks:
        raise ValueError("Select at least one niche")
    notes = {k: str(v)[:2000] for k, v in (body.get("notes") or {}).items() if k in by_id and str(v).strip()}
    general = str(body.get("general_note") or "")[:4000].strip()
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    record = {"run": run, "decided_at": stamp, "checkpoint": tracker.get("phase"),
              "deep_dive": picks, "notes": notes, "general_note": general}
    tmp = os.path.join(run_dir, ".decision.tmp")
    with open(tmp, "w") as f:
        json.dump(record, f, indent=2)
    os.replace(tmp, os.path.join(run_dir, "decision.json"))
    lines = [f"# Checkpoint decision: {run}", "", f"Decided {stamp} by the user in Rig Console.", "",
             "## Deep dive these niches, in this order"]
    for i, pid in enumerate(picks, 1):
        lines.append(f"{i}. **{by_id[pid].get('name')}** (`{pid}`)")
        if pid in notes:
            lines.append(f"   - Note: {notes[pid]}")
    skipped = [n for n in by_id.values() if n.get("stage") == "screened" and n.get("id") not in picks]
    if skipped:
        lines += ["", "## Not selected (do not deep dive)"] + [f"- {n.get('name')} (`{n.get('id')}`)" for n in skipped]
    if general:
        lines += ["", "## General notes", general]
    with open(os.path.join(run_dir, "decision.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    lead, sent = _lead_for(run), False
    rig = _rig_bin()
    if lead and rig:
        msg = (f"Checkpoint decision from the user for {run} is ready: "
               f"{os.path.join(run_dir, 'decision.md')} (also decision.json). Read it, deep dive only "
               f"the selected niches in that order, apply the notes, and keep niches.json updated.")
        try:
            r = subprocess.run(G.rig_cmd(rig, "send", lead, msg), capture_output=True, text=True, timeout=30)
            sent = r.returncode == 0
        except Exception:
            sent = False
    return {"saved": True, "decided_at": stamp, "count": len(picks), "lead": lead, "lead_notified": sent}



OWNER_SENDER = "owner@rig-console"   # the From line seats see; OpenRig takes it from OPENRIG_SESSION_NAME
CONSOLE_SENDER = "console@rig-console"   # automatic messages (receipts): not the owner speaking
FORCE_REASON = "Owner chose Send anyway in Rig Console: the seat's screen shows an empty input box, not a prompt"
FORCE_MAX_AGE_S = 30


def _rig_send(rig, seat, text, *extra):
    env = {**os.environ, "OPENRIG_SESSION_NAME": OWNER_SENDER}
    return subprocess.run(G.rig_cmd(rig, "send", seat, text, *extra), capture_output=True, text=True, timeout=30, env=env)


def _console_send(seat, text):
    """An automatic message from the console itself (receipts), labeled as the console, not the owner.
    Under option A the rig-owner helper's "receipt" verb applies that label, since sudo drops the env."""
    rig = _rig_bin()
    if not rig:
        return False
    cmd = G.rig_cmd(rig)
    via_helper = os.path.basename(cmd[-1]) == "rig-owner"
    cmd += ["receipt" if via_helper else "send", seat, text]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                           env={**os.environ, "OPENRIG_SESSION_NAME": CONSOLE_SENDER})
        return r.returncode == 0
    except Exception:
        return False


SESSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}@[A-Za-z0-9._-]{1,64}$")   # seat@rig; within what setup/rig-owner accepts


def deploy_status():
    """Which reviewed commit is live (written by rig-console-deploy), and whether the repo has a newer one.
    Plain file reads only: the console never runs git in the agents' repo."""
    mark = os.environ.get("RIG_DEPLOYED_MARK", "/var/lib/rig-console/deployed")
    out = {"commit": None}
    try:
        with open(mark + ".json") as f:
            d = json.load(f)
        if isinstance(d, dict):
            out.update({k: str(d.get(k) or "")[:160] for k in ("commit", "subject", "at", "smoke")})
    except (OSError, ValueError):
        try:
            with open(mark) as f:
                out["commit"] = f.read().strip()[:40] or None
        except OSError:
            pass
    head = None
    try:   # the repo's HEAD commit: .git/HEAD -> a ref file, or packed-refs
        git = os.path.join(PR.REPO, ".git")
        with open(os.path.join(git, "HEAD")) as f:
            h = f.read().strip()
        if h.startswith("ref: "):
            ref = h[5:]
            if re.fullmatch(r"refs/heads/[A-Za-z0-9._/-]{1,100}", ref) and ".." not in ref:
                try:
                    with open(os.path.join(git, ref)) as f:
                        head = f.read().strip()
                except OSError:
                    with open(os.path.join(git, "packed-refs")) as f:
                        head = next((ln.split()[0] for ln in f if ln.strip().endswith(" " + ref)), None)
        else:
            head = h
    except OSError:
        pass
    head = head if head and re.fullmatch(r"[0-9a-f]{40}", head) else None
    out["repo_head"] = head
    out["newer_in_repo"] = bool(head and out["commit"] and head != out["commit"])
    return out


PAGE_VIEWS = os.path.join(G.STATE_DIR, "page-views.json")
PAGE_RE = re.compile(r"^/(?:[a-z0-9-]+\.html)?$")
_views_lock = threading.Lock()


def _count_page(path, today=None):
    """Which pages get opened, for phase 2 of the reorganisation (R-027): page and day only. No addresses, no
    times, no query strings. Only the console's own pages count; 60 days are kept. Never fails a request."""
    if not PAGE_RE.match(path) or not os.path.isfile(os.path.join(DASH, path.lstrip("/") or "graph.html")):
        return
    day = today or datetime.now().strftime("%Y-%m-%d")
    try:
        with _views_lock:
            try:
                with open(PAGE_VIEWS) as f:
                    d = json.load(f)
                d = d if isinstance(d, dict) else {}
            except (OSError, ValueError):
                d = {}
            page = d.setdefault(day, {})
            page[path or "/"] = page.get(path or "/", 0) + 1
            for k in sorted(d)[:-60]:
                del d[k]
            os.makedirs(G.STATE_DIR, exist_ok=True)
            tmp = PAGE_VIEWS + ".tmp"
            with open(tmp, "w") as f:
                json.dump(d, f)
            os.replace(tmp, PAGE_VIEWS)
    except Exception:
        pass


def _clerk_for(job):
    """The running clerk seat of a lab game, from the trusted team record (not the seat-written job.json)."""
    j = G._jobs().get(job)
    rig = G.team_of(j).get("rig") if j else None
    for r in _load("_ps.json") if rig else []:
        if r.get("rigName") == rig and r.get("logicalId") == "clerk.clerk" and r.get("runtime") != "terminal":
            name = str(r.get("canonicalSessionName") or "")
            return name if SESSION_RE.match(name) else None
    return None


def _lab_control(body):
    """Write the owner's pause/resume/stop, then wake the clerk so it acts now rather than on its next timer
    (PL-045: after a resume the clerk slept up to 5 minutes and the page read the old deadline as "adjudicating").
    The message is a fixed sentence: no owner or agent text goes into it."""
    res = LAB.control(body)
    clerk = _clerk_for(str(body.get("job") or ""))
    what = "stopped" if body.get("stop") is True else ("paused" if body.get("paused") else "resumed")
    told = bool(clerk) and _console_send(clerk, f"The owner {what} the game in Rig Console. Re-read board/control.json now and act on it.")
    res["clerk_told"] = told
    res["note"] = {"paused": "Paused.", "resumed": "Resumed.", "stopped": "Stop sent."}[what] + (
        " The clerk was told and acts now." if told else " The clerk acts on its next look (it couldn't be messaged).")
    return res


NEEDS = {"count": None}   # open cards on the Needs you page, from the watcher's last round (the nav badge reads it)


def _approval_item(qid, summary, text):
    """One durable queue item for the operator about an approval wait (R-020). The body goes in on stdin.
    Under option A the rig-owner helper's "approval-item" verb fixes the destination to the operator."""
    rig = _rig_bin()
    if not rig:
        return False
    cmd = G.rig_cmd(rig)
    if os.path.basename(cmd[-1]) == "rig-owner":
        cmd += ["approval-item", qid, summary]
    else:
        cmd += ["queue", "create", "--source", CONSOLE_SENDER, "--destination", EP.OPERATOR, "--id", qid,
                "--summary", summary, "--body", "-"]
    try:
        r = subprocess.run(cmd, input=text, capture_output=True, text=True, timeout=30,
                           env={**os.environ, "OPENRIG_SESSION_NAME": CONSOLE_SENDER})
        if r.returncode != 0:
            print("approval item failed:", (r.stderr or r.stdout or "").strip()[:200], flush=True)
        return r.returncode == 0
    except Exception as e:
        print("approval item failed:", f"{type(e).__name__}: {e}"[:200], flush=True)
        return False


def _blocked_reply(seat, why):
    """Refusal for a seat OpenRig says is at a prompt. Its screen decides whether to offer Send anyway."""
    kind, age, tail = screen_prompt(seat)
    if kind == "menu":
        return {"error": "It's waiting at a prompt on its screen. Answer that in its terminal first: a message now could answer it by accident.",
                "screen": tail}
    if kind == "idle" and age is not None and age <= FORCE_MAX_AGE_S:
        return {"error": f"{why}, but its screen ({int(age)} s ago) shows an empty input box. OpenRig sometimes misreads idle seats. "
                         "Check the screen below; if it's idle, use Send anyway.",
                "can_force": True, "screen": tail}
    return {"error": f"{why}. Its screen doesn't show clearly, so sending stays off. Look at its terminal.", "screen": tail}


def _delivered(seat, mid, msg):
    """The text a seat gets: the message id, then the message, then how to answer (JOBS.md §3e, PL-025).
    One line, so it also works with --dangerously-interact."""
    head = f"Message from the owner [msg {mid}] (via Rig Console): {msg}"
    folder = CV.reply_folder(seat, G.folder_of_rig(CV.ARCHITECTS_RIG))
    if not folder:
        return head + " -- Reply on your screen; the owner reads it there."
    return (head + f' -- Reply by writing {os.path.join(folder, mid)}.json as {{"id": "{mid}", "text": "<your reply>", '
            '"at": "<ISO time>"}; the owner reads it on the Messages page. Your screen text is not the record.')


def send_message(body):
    """Deliver a message from the owner to one agent with `rig send`. Refuses when the agent is at a prompt,
    where typed text could answer it. When OpenRig says "prompt" but the screen shows an empty input box,
    the owner may choose Send anyway, which re-checks the screen first."""
    seat = str(body.get("seat") or "")
    msg = str(body.get("message") or "").strip()
    if not msg or len(msg) > 4000:
        raise ValueError("Write a message (up to 4000 characters)")
    node = next((r for r in _load("_ps.json") if r.get("canonicalSessionName") == seat and r.get("runtime") != "terminal"), None)
    if not node:
        raise ValueError("Unknown agent")
    force = body.get("force") is True
    if not force and ((node.get("agentActivity") or {}).get("state") or "").startswith("needs_input"):
        return _blocked_reply(seat, "OpenRig says it's waiting at a prompt")
    if force:
        kind, age, tail = screen_prompt(seat, FORCE_MAX_AGE_S)
        if kind != "idle":
            return {"error": "Not sent: its screen no longer shows an empty input box (or is too old to tell).", "screen": tail}
    rig = _rig_bin()
    if not rig:
        raise ValueError("Couldn't find the rig command on this machine")
    sent = {"sent": True, "at": datetime.now().astimezone().isoformat(timespec="seconds")}
    mid = CV.new_id()   # travels in the text; a reply file must name it exactly (PL-025)
    if force:
        # --dangerously-interact types keystrokes without OpenRig's From/To envelope, and Enter would submit
        # early, so the text is one line and carries its own label.
        r = _rig_send(rig, seat, _delivered(seat, mid, " ".join(msg.split())),
                      "--dangerously-interact", "--reason", FORCE_REASON)
        if r.returncode != 0:
            raise ValueError((r.stderr or r.stdout or "rig send failed").strip()[:300])
        CV.record(seat, msg, mid)
        return {**sent, "id": mid, "forced": True, "note": (r.stdout or "").strip()[:300]}
    r = _rig_send(rig, seat, _delivered(seat, mid, msg))
    if r.returncode != 0:
        out = (r.stderr or r.stdout or "rig send failed").strip()
        if "interactive prompt" in out:
            return _blocked_reply(seat, "OpenRig refused: it says the seat is at a prompt")
        raise ValueError(out[:300])
    CV.record(seat, msg, mid)   # kept with its reply on the Messages page (PL-024, PL-025)
    return {**sent, "id": mid, "note": (r.stdout or "").strip()[:300]}

TOKEN = os.environ.get("RIG_CONSOLE_TOKEN", "")
# Builds are agent-written JavaScript, so they get their own port (R-006): a different origin from the
# console, with no pages, no API and no sign-in. The phone reaches it through Tailscale Serve on
# RIG_PLAY_PUBLIC_PORT (default 8443).
PLAY_PORT = int(os.environ.get("PLAY_PORT") or (int(os.environ.get("PORT", "8800")) + 1))
PLAY_PUBLIC_PORT = int(os.environ.get("RIG_PLAY_PUBLIC_PORT") or 8443)
EXTRA_HOSTS = {h.strip().lower() for h in os.environ.get("RIG_CONSOLE_HOSTS", "").split(",") if h.strip()}
# Once your Tailscale name is in RIG_CONSOLE_HOSTS, only that name is accepted; until then any *.ts.net
# name is, and /api/health asks you to pin it (MA-013).
TS_PINNED = any(h.endswith(".ts.net") for h in EXTRA_HOSTS)


def _host_name(host):
    host = (host or "").strip().lower()
    return host[1:host.index("]")] if host.startswith("[") and "]" in host else host.rsplit(":", 1)[0] if host.count(":") == 1 else host


def _name_ok(name):
    return bool(name) and (name in ("localhost", "127.0.0.1", "::1") or name in EXTRA_HOSTS
                           or (not TS_PINNED and name.endswith(".ts.net")))
HOST = os.environ.get("HOST", "127.0.0.1")


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".wasm": "application/wasm", ".pck": "application/octet-stream",
                      ".md": "text/plain; charset=utf-8", ".json": "application/json", ".webmanifest": "application/manifest+json"}
    PUBLIC = ("/manifest.json", "/icon.svg")   # the browser fetches these without cookies when installing

    def _signed_in(self):
        """True when this browser holds the console cookie, or brings the token in ?token= (which then
        sets the cookie). Works for local and remote requests alike."""
        if not TOKEN:
            return False
        q = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
        if hmac.compare_digest((q.get("token") or [""])[0], TOKEN):
            self._set_cookie = self._token_login = True
            return True
        jar = http.cookies.SimpleCookie()
        try:
            jar.load(self.headers.get("Cookie") or "")
        except http.cookies.CookieError:
            return False
        ok = "rc_token" in jar and hmac.compare_digest(jar["rc_token"].value, TOKEN)
        if ok:
            self._set_cookie = True   # refresh it, so older cookies pick up the current settings
        return ok

    def _local(self):
        proxied = any(self.headers.get(h) for h in ("X-Forwarded-For", "Tailscale-User-Login", "Forwarded"))
        return self.client_address[0] in ("127.0.0.1", "::1") and not proxied

    def _to_play(self, path):
        """Send the browser to the same build on the builds port: http://localhost:<PLAY_PORT> on this PC,
        or https://<tailscale name>:<PLAY_PUBLIC_PORT> through Tailscale Serve."""
        if not re.match(r"^/play/[A-Za-z0-9._-]{1,64}/[A-Za-z0-9._/%-]{1,512}$", path) or ".." in path:
            self.send_error(404)
            return
        fwd = (self.headers.get("X-Forwarded-Host") or "").split(",")[0].strip()
        host = fwd if fwd and _name_ok(_host_name(fwd)) else (self.headers.get("Host") or "localhost").strip()   # MA-013
        name = host[: host.index("]") + 1] if host.startswith("[") else host.rsplit(":", 1)[0]
        origin = f"https://{name}:{PLAY_PUBLIC_PORT}" if not self._local() else f"http://{name}:{PLAY_PORT}"
        self.send_response(302)
        self.send_header("Location", origin + path)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _host_ok(self):
        """DNS rebinding guard (MA-007 finding 3): a web page can point its own domain at 127.0.0.1 and
        become same-origin with the console. Browsers still send that domain as Host, so only answer
        to names that are really this console: localhost, the Tailscale name (*.ts.net), and any extra
        names in RIG_CONSOLE_HOSTS (comma-separated)."""
        host = (self.headers.get("Host") or "").strip().lower()
        name = _host_name(host)
        return _name_ok(name)

    def _refuse_host(self):
        body = b"Unknown host name. Open the console at localhost or its Tailscale address (or add the name to RIG_CONSOLE_HOSTS)."
        self.send_response(421)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_HEAD(self):
        if not self._host_ok():
            return self._refuse_host()
        if not self._allowed():
            self.send_error(403)
            return
        return super().do_HEAD()

    def _allowed(self):
        """Who may look. Local requests may always read. Remote ones (laptop/phone over Tailscale)
        need the token once via ?token=..., after which a cookie remembers it.
        Who may *change* things is stricter: see do_POST."""
        if self.path.split("?", 1)[0] in self.PUBLIC:
            return True
        signed = self._signed_in()
        if self._local():
            return True
        # Requests relayed by a proxy on this PC (e.g. Tailscale Serve) come from 127.0.0.1 too,
        # but they're really from another device, so they need the token like any remote request.
        return signed

    def _login_page(self, local=False):
        """Friendly sign-in instead of a bare 403: type the token once, the cookie remembers it.
        /signin shows the same form on this PC, where it's needed before making changes (R-005)."""
        path, _, query = self.path.partition("?")
        if local:
            nxt = (urllib.parse.parse_qs(query).get("next") or ["/"])[0]
            path, query = (nxt if nxt.startswith("/") and not nxt.startswith("//") else "/"), ""
        keep = "".join(f'<input type="hidden" name="{html.escape(k)}" value="{html.escape(v)}">'
                       for k, vs in urllib.parse.parse_qs(query).items() if k != "token" for v in vs)
        body = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sign in · Rig Console</title><style>
body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#0a0f17;color:#e3e8ef;font:16px/1.5 system-ui,sans-serif;padding:20px}}
form{{width:min(380px,100%);background:#0f1621;border:1px solid #212c3c;border-radius:16px;padding:22px}}
h1{{margin:0 0 6px;font-size:20px}} p{{margin:0 0 16px;color:#8e9aac;font-size:14px}}
input[type=password]{{width:100%;box-sizing:border-box;padding:12px;border-radius:10px;border:1px solid #212c3c;background:#141d2a;color:#e3e8ef;font-size:16px}}
button{{margin-top:12px;width:100%;padding:12px;border:0;border-radius:10px;background:#f0b23c;color:#111;font-weight:800;font-size:16px}}
</style></head><body><form method="get" action="{html.escape(path)}"><h1>Rig Console</h1>
<p>Enter your console token. This device will remember it{" and can then make decisions" if local else ""}.</p>{keep}
<input type="password" name="token" autocomplete="current-password" placeholder="Token" required autofocus>
<button type="submit">Sign in</button></form></body></html>""".encode()
        self.send_response(401)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self._host_ok():
            return self._refuse_host()
        if not self._allowed():
            p = self.path.split("?", 1)[0]
            if p.startswith("/api/") or not TOKEN:
                self.send_error(403, "Not signed in")
            else:
                self._login_page()
            return
        path = self.path.split("?", 1)[0]
        if path.startswith("/go/play/") and not getattr(self, "_token_login", False):
            return self._to_play(path[len("/go"):])
        if path.startswith("/play/"):
            self.send_error(404, "Builds are served on their own port now; open them from the Builds page.")
            return
        if path == "/signin" and not getattr(self, "_token_login", False):
            return self._login_page(local=True)
        if getattr(self, "_token_login", False):
            # Signed in with ?token=: set the cookie and reload without the token in the address bar or history.
            rest = [(k, v) for k, vs in urllib.parse.parse_qs(self.path.partition("?")[2]).items() if k != "token" for v in vs]
            self.send_response(303)
            self.send_header("Location", path + ("?" + urllib.parse.urlencode(rest) if rest else ""))
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        try:
            if path == "/api/session":
                return self.send_json({"signed_in": self._signed_in(), "token_set": bool(TOKEN)})
            if path == "/api/runs":
                return self.send_json(list_runs())
            if path == "/api/team":
                return self.send_json(team())
            if path == "/api/graph":
                return self.send_json(cached("graph", graph))
            q = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
            arg = lambda k: (q.get(k) or [""])[0]
            if path == "/api/events":
                num = lambda k, d: int(arg(k)) if arg(k).isdigit() else d
                return self.send_json(S.events(num("since", 0), num("limit", 60)))
            if path == "/api/replay":
                rig, run = arg("rig"), arg("run")
                if not RUN_RE.match(rig) or (run and not RUN_RE.match(run)):
                    return self.send_json({"error": "bad rig"})
                return self.send_json(S.replay(rig, run or None))
            if path == "/api/gates":
                return self.send_json(cached("gates", G.list_gates))
            if path == "/api/builds":
                return self.send_json(G.list_builds())
            if path == "/api/models":
                return self.send_json(MD.load())
            if path == "/api/since":   # "Since you last looked" on Now: counts after ?ts= (epoch s), read-only
                ts = float(arg("ts") or 0)
                if not (0 < ts <= time.time() + 60):
                    raise ValueError("ts must be a past time in epoch seconds")
                gates_new = [g for g in G.list_gates(0)["open"] if g.get("created", 0) > ts]
                cards_new = [t for t in G.list_tasks() if not t.get("error") and t.get("created", 0) > ts]
                return self.send_json({**S.since_summary(ts),
                                       "decisions_new": [{"title": str(g.get("title") or "")[:120], "url": f"/decide.html?job={g['job']}&gate={g['id']}"} for g in gates_new][:5],
                                       "decisions_new_n": len(gates_new),
                                       "cards_new": [str(t.get("title") or "")[:100] for t in cards_new][:5], "cards_new_n": len(cards_new)})
            if path == "/api/digest":   # the daily digest (R-026), read-only; ?day=YYYY-MM-DD (UTC), default today
                day = arg("day") or None
                return self.send_json(cached(f"digest:{day}", lambda: DG.build(day)))
            if path == "/api/lab/games":   # the Diplomacy games, for the page's game list
                return self.send_json(LAB.games())
            if path == "/api/deploy":   # which commit is live, and whether a newer one waits in the repo
                return self.send_json(deploy_status())
            if path == "/api/models/review":   # one review's report.md, read-only (Diplomacy postgame, 2026-10-14)
                return self.send_json(MD.review(arg("id")))
            if path == "/api/jobs":
                return self.send_json(S.jobs_list())
            if path == "/api/replay_rigs":
                return self.send_json(S.replay_rigs())
            if path == "/api/health":
                return self.send_json(health())
            if path == "/api/usage":
                return self.send_json(F.usage_list())
            if path == "/api/evidence":
                return self.send_json(F.evidence_status(arg("run")))
            if path == "/api/timeline":
                rig = arg("rig")
                if not re.match(r"^[A-Za-z0-9._-]{1,64}$", rig):
                    return self.send_json({"error": "bad rig"})
                # Only the daily activity files this team's run can touch (R-011), from its span in SQLite.
                span = next((r for r in S.replay_rigs() if r["rig"] == rig), None)
                since, until = ((datetime.fromtimestamp(span["start"] - 3600).astimezone(),
                                 datetime.fromtimestamp(span["end"] + 3600).astimezone()) if span else (None, None))
                return self.send_json(F.timeline(rig, arg("run") or None, _load("_queue.json"), since, until))
            if path == "/api/approvals":
                rig = arg("rig")
                return self.send_json(F.approvals(rig if re.match(r"^[A-Za-z0-9._-]{1,64}$", rig or "") else None))
            if path == "/api/decisions":
                return self.send_json(F.decisions(DATA))
            if path == "/api/runs_summary":
                return self.send_json(F.runs_summary(DATA, sorted(_logged_rigs(5_000_000)), _load("_queue.json")))
            if path == "/api/briefs":
                bdir = BRIEFS
                items = []
                if os.path.isdir(bdir):
                    for fn in sorted(os.listdir(bdir)):
                        if fn.endswith(".md"):
                            items.append({"name": fn, "text": open(os.path.join(bdir, fn), encoding="utf-8", errors="replace").read()[:60000]})
                return self.send_json(items)
            if path == "/api/rigs":
                return self.send_json(sorted({r.get("rigName") for r in _load("_ps.json") if r.get("rigName")} | _logged_rigs(2_000_000)))
            if path == "/api/needs":    # the nav badge: open cards on the Needs you page; cheap, from the watcher
                return self.send_json(NEEDS)
            if path == "/api/tasks":    # the Needs you page (R-018): open cards and the last 14 days' answers
                return self.send_json({"open": [t for t in G.list_tasks() if not t.get("error")],
                                       "unreadable": [t for t in G.list_tasks() if t.get("error")],
                                       "resolved": G.resolved_tasks()})
            if path == "/api/messages":   # your questions to seats with their replies (PL-024)
                q = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
                seat = (q.get("seat") or [""])[0]
                return self.send_json(CV.history(seat if re.match(r"^[A-Za-z0-9._@-]{1,128}$", seat) else None))
            if path == "/api/lounge":   # read-only, never notifies (R-019)
                return self.send_json(LG.posts())
            if path in ("/api/job", "/api/job/docs", "/api/job/assets"):   # one page per job (PL-034), read-only
                name = arg("job") or ""
                if not G.ID_RE.match(name):
                    raise ValueError("Unknown job")
                fn = {"/api/job": JP.overview, "/api/job/docs": JP.docs, "/api/job/assets": JP.assets}[path]
                return self.send_json(fn(name))
            if path == "/api/docket":   # each architect's work (R-023), from queue rows, gates and cards only
                return self.send_json(cached("docket", _docket))
            if path == "/api/seat":     # an architect's profile (R-027), read-only, from existing sources
                seat = arg("seat") or ""
                if not PR.SEAT_RE.match(seat):
                    raise ValueError("Unknown seat")

                # Not cached itself: a second cache layer on top of graph and docket would add a second window of
                # staleness (review-8). Those two are the expensive part, and they're cached.
                dk = cached("docket", _docket)
                node = next((n for n in cached("graph", graph)["nodes"] if n.get("id") == seat), None)
                return self.send_json(PR.profile(seat, node, next((s for s in dk.get("seats", []) if s["seat"] == seat), None),
                                                 LG.posts(), CV.history(seat)))
            if path == "/api/oplog":    # the operator's log, read-only (R-022)
                q = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
                return self.send_json(OL.read((q.get("month") or [""])[0]))
            if path == "/api/screen":
                q = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
                seat = (q.get("seat") or [""])[0]
                if not re.match(r"^[A-Za-z0-9._@-]{1,128}$", seat):
                    return self.send_json({"error": "bad seat"})
                p = os.path.join(SNAP, seat + ".txt")
                if not os.path.isfile(p):
                    return self.send_json({"error": "no screen yet"})
                with open(p, encoding="utf-8", errors="replace") as f:
                    lines = f.read().splitlines()
                kind, _, _ = screen_prompt(seat)
                return self.send_json({"updated": lines[0] if lines else "", "lines": [l.rstrip() for l in lines[1:]][-80:],
                                       "prompt": kind, "reply": last_reply(lines[-200:])})
        except Exception as e:
            return self.send_json({"error": str(e)})
        _count_page(path)
        return super().do_GET()

    def do_POST(self):
        # Every change clears the read cache, before (so nothing computed from the old state is reused) and after (so
        # nothing computed during the change survives it).
        invalidate_cache()
        try:
            return self._do_post()
        finally:
            invalidate_cache()

    def _do_post(self):
        if not self._host_ok():
            return self._refuse_host()
        if not self._allowed():
            self.send_error(403)
            return
        path = self.path.split("?", 1)[0]
        # Every change needs the signed-in cookie, even from this PC (R-005). Agents run on this PC as the
        # same user, so "local" can't mean "the owner"; only the owner's browser holds the cookie.
        # Without a token configured there's nothing to check, and /api/health says so.
        if not TOKEN:
            body = json.dumps({"error": "Set RIG_CONSOLE_TOKEN before making changes: without it the console can't tell you from an agent."}).encode()
            self.send_response(403)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if not self._signed_in():
            body = json.dumps({"error": "Sign in on this device to make changes.", "signin": True}).encode()
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        # Reject cross-site requests: browsers can't send this header cross-origin
        # without a CORS preflight, which this server never approves.
        if self.headers.get("X-Rig-Console") != "1" or "application/json" not in (self.headers.get("Content-Type") or ""):
            self.send_error(403)
            return
        try:
            length = min(int(self.headers.get("Content-Length") or 0), 200_000)
            body = json.loads(self.rfile.read(length) or b"{}")
            if path == "/api/usage":
                return self.send_json(F.usage_add(body))
            if path == "/api/send":
                return self.send_json(send_message(body))
            if path == "/api/task":
                tid = str(body.get("id") or "")
                if not G.ID_RE.match(tid):
                    raise ValueError("Unknown task")
                record, asker, rec_path = G.answer_task(tid, body)
                said = {"done": "Done", "wont": "Won’t do", "answered": "answered", "skipped": "skipped"}[record["result"]]
                told = bool(asker) and _console_send(asker, f"The owner answered your card '{record['title']}': {said}. "
                                                            f"Read {rec_path}, act on it, then remove the task file.")
                return self.send_json({"saved": True, "result": record["result"], "asker_told": told})
            if path == "/api/lab/control":   # pause, resume or stop a lab game (R-024): one file, then wake the clerk (PL-045)
                return self.send_json(_lab_control(body))
            if path == "/api/lounge":   # the owner's post or reply (R-021): quiet, no notification or message
                return self.send_json(LG.post(body.get("text"), body.get("reply_to")))
            if path == "/api/dismiss":
                key = str(body.get("key") or "")
                if not re.match(r"^[a-z]+:[A-Za-z0-9._@-]{1,128}$", key):
                    raise ValueError("bad key")
                d = _dismissed()
                if body.get("undo"):
                    d.pop(key, None)
                else:
                    d[key] = datetime.now().astimezone().isoformat(timespec="seconds")
                _save_dismissed(d)
                return self.send_json({"ok": True})
            if path == "/api/evidence":
                q = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
                return self.send_json(F.evidence_start((q.get("run") or [""])[0], DATA))
            if path == "/api/gate":
                q = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
                return self.send_json(G.decide((q.get("job") or [""])[0], (q.get("gate") or [""])[0], body, _rig_bin()))
            if path == "/api/decision":
                q = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
                return self.send_json(save_decision((q.get("run") or [""])[0], body))
        except Exception as e:
            return self.send_json({"error": str(e)})
        self.send_error(404)

    def translate_path(self, path):
        path = posixpath.normpath(urllib.parse.unquote(path.split("?", 1)[0]))
        m = re.match(r"^/(job)/([A-Za-z0-9._-]{1,64})/(.+)$", path)
        if m:
            full = G.safe_path(m.group(2), m.group(3))
            return full or os.path.join(DASH, "__forbidden__")
        if path.startswith("/data/"):
            root, rel = DATA, path[len("/data/"):]
        else:
            root, rel = DASH, path.lstrip("/") or "graph.html"   # home is the live graph
        full = os.path.realpath(os.path.join(root, rel))
        if not full.startswith(os.path.realpath(root) + os.sep):
            return os.path.join(DASH, "__forbidden__")
        return full

    def end_headers(self):
        if getattr(self, "_set_cookie", False):
            self.send_header("Set-Cookie", f"rc_token={TOKEN}; Path=/; HttpOnly; SameSite=Lax; Secure; Max-Age=31536000")
        p = self.path.split("?", 1)[0]
        if p.startswith(("/job/", "/data/")):
            # Files agents wrote: show them, but never let them run scripts as the console.
            self.send_header("Content-Security-Policy", "sandbox")
            self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


# The watcher's own heartbeat. Before this, any error in the loop was swallowed and phone alerts could
# stop with no sign (PL-006). Now each round records its outcome, errors go to the service log, and
# /api/health shows "Alerts" red once the loop hasn't finished a round for a minute.
WATCH = {"started": time.time(), "last_ok": None, "error": None, "error_at": None, "rounds": 0}


def health():
    out = F.health()
    now, w = time.time(), WATCH
    if w["last_ok"] and now - w["last_ok"] < 60:
        out["alerts"] = {"ok": True, "detail": f"checked {int(now - w['last_ok'])} s ago"}
    elif not w["last_ok"] and now - w["started"] < 90:
        out["alerts"] = {"ok": True, "detail": "starting"}
    else:
        last = f"last good check {int((now - w['last_ok']) // 60)} min ago" if w["last_ok"] else "no good check since start"
        out["alerts"] = {"ok": False, "detail": f"stopped: {last}" + (f" ({w['error']})" if w["error"] else "") + ". Phone alerts won't arrive."}
    # R-005 step 3 (option A): is the console out of the agents' reach yet?
    try:
        agents_uid = os.stat(G.LAUNCHES if os.path.isdir(G.LAUNCHES) else os.path.expanduser("~")).st_uid
        problems = []
        if os.getuid() == agents_uid:
            problems.append("runs as the agents' user, so they can read its token")
        if os.path.realpath(DASH).startswith("/mnt/"):
            problems.append("runs from /mnt/c, where agents can edit its code")
        try:   # which reviewed commit deploy-console.sh put live (MA-014 finding 1)
            with open(os.environ.get("RIG_DEPLOYED_MARK", "/var/lib/rig-console/deployed")) as f:
                deployed = f.read().strip()[:12]
        except OSError:
            deployed = ""
        out["isolation"] = {"ok": not problems, "level": "advisory",
                            "detail": ("runs as its own user, from code agents can't edit"
                                       + (f"; deployed commit {deployed[:7]}" if deployed else "")) if not problems
                            else "Console " + " and ".join(problems) + " (R-005 step 3)."}
    except OSError:
        pass
    if not TOKEN:
        out["token"] = {"ok": False, "detail": "No console token set, so changes are switched off. Set RIG_CONSOLE_TOKEN."}
    if TOKEN and not TS_PINNED:
        out["hostname"] = {"ok": False, "level": "advisory",
                           "detail": "Your Tailscale name isn't pinned: add it to RIG_CONSOLE_HOSTS (e.g. prometheus.tail1234.ts.net)."}
    if os.environ.get("NTFY_TOPIC"):
        p = F.PUSH
        failed = p["error"] and (not p["last_ok"] or p["error_at"] > p["last_ok"])
        out["push"] = {"ok": not failed, "detail": f"last push failed: {p['error']}" if failed else "working"}
    return out


class PlayHandler(http.server.SimpleHTTPRequestHandler):
    """The builds port (R-006). It serves only /play/<job>/<file> from inside the job's build folder, with
    the cross-origin isolation headers Godot needs. No pages, no /api/, no sign-in, no ?token=, and it
    never sets a cookie: a build running here is a different origin and can't act as the console.
    The console cookie still reaches this port (cookies ignore ports), so remote requests are allowed only
    with it, like the console itself; it's HttpOnly, so a build's script can't read it."""
    extensions_map = Handler.extensions_map

    def _ok(self):
        if not Handler._host_ok(self):
            Handler._refuse_host(self)
            return None
        path = posixpath.normpath(urllib.parse.unquote(self.path.split("?", 1)[0]))
        m = re.match(r"^/play/([A-Za-z0-9._-]{1,64})/(.+)$", path)
        full = G.build_file(m.group(1), m.group(2)) if m else None   # build folders only (MA-013)
        if not full or not os.path.isfile(full):
            self.send_error(404)
            return None
        if not Handler._local(self):
            jar = http.cookies.SimpleCookie()
            try:
                jar.load(self.headers.get("Cookie") or "")
            except http.cookies.CookieError:
                pass
            if not (TOKEN and "rc_token" in jar and hmac.compare_digest(jar["rc_token"].value, TOKEN)):
                self.send_error(403, "Open the console once on this device to sign in, then play from the Builds page.")
                return None
        return full

    def do_GET(self):
        if self._ok():
            super().do_GET()

    def do_HEAD(self):
        if self._ok():
            super().do_HEAD()

    def translate_path(self, path):
        path = posixpath.normpath(urllib.parse.unquote(path.split("?", 1)[0]))
        m = re.match(r"^/play/([A-Za-z0-9._-]{1,64})/(.+)$", path)
        return (G.build_file(m.group(1), m.group(2)) if m else None) or os.path.join(DASH, "__forbidden__")

    def end_headers(self):
        # Godot 4 web builds need cross-origin isolation; big .wasm/.pck files may be cached but rechecked.
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_message(self, *a):
        pass


def _open_qitem_ids(max_age_s=90):
    """Ids of the queue items still open, from the logger's active-queue snapshot, or None when that snapshot
    is missing, stale or possibly cut off at its 300-row limit (then nobody is re-alerted on a guess)."""
    qa = os.path.join(SNAP, "_queue_active.json")
    try:
        if time.time() - os.path.getmtime(qa) > max_age_s:
            return None
    except OSError:
        return None
    rows = _load("_queue_active.json")
    if len(rows) >= 300:
        return None
    return {str(r.get("qitemId")) for r in rows if isinstance(r, dict) and r.get("qitemId")}


def _watch():
    try:
        S.backfill_activity(ACTIVITY)
    except Exception as e:
        print("activity backfill failed:", e)
    col = S.Collector(DATA)
    while True:
        try:
            g = graph()
            try:
                col.collect(g, _load("_queue.json"))
            except Exception as e:
                print("event collector:", e)
            F.track_approvals(g["nodes"])
            F.push_alerts(g["alerts"])
            OB.deliver(lambda title, body, pr, url: F.push_now(f"{title}\n{body}".strip(), "From the operator", pr, url),
                       lambda text: _console_send(OB.RECEIPT_TO, text), set(_dismissed()))
            EP.track(g["nodes"], lambda s: screen_prompt(s)[2], _approval_item,
                     idle_on_screen=lambda s: screen_prompt(s)[0] == "idle", open_ids=_open_qitem_ids())
            EP.track_outages(g["alerts"], _approval_item)   # one operator item per provider usage-limit outage (R-030)
            CV.capture(g["nodes"], lambda s: _screen_tail(s, 400), lambda s: screen_prompt(s)[0] == "idle",
                       G.folder_of_rig(CV.ARCHITECTS_RIG))
            NEEDS["count"] = sum(1 for a in g["alerts"] if a["kind"] == "task")   # open cards on the Needs you page
            WATCH["last_ok"], WATCH["error"] = time.time(), None
        except Exception as e:
            WATCH["error"], WATCH["error_at"] = f"{type(e).__name__}: {e}"[:200], time.time()
            print("watcher round failed:", WATCH["error"], flush=True)
            traceback.print_exc()
        WATCH["rounds"] += 1
        time.sleep(10)


if __name__ == "__main__":
    import threading
    if HOST not in ("127.0.0.1", "localhost") and not TOKEN:
        raise SystemExit("Refusing to listen beyond localhost without RIG_CONSOLE_TOKEN set.")
    threading.Thread(target=_watch, daemon=True).start()
    if PLAY_PORT:
        threading.Thread(target=http.server.ThreadingHTTPServer((HOST, PLAY_PORT), PlayHandler).serve_forever, daemon=True).start()
        print(f"Builds on http://{HOST}:{PLAY_PORT}")
    print(f"Dashboard on http://{HOST}:{PORT}  (Ctrl+C to stop)")
    http.server.ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
