#!/usr/bin/env python3
"""Rig dashboard. Run in Ubuntu:
    python3 /mnt/c/Users/you/OneDrive/Documents/Projects/OpenRig/dashboard/serve.py
then open http://localhost:8800 in your Windows browser.

Reads (never writes):
  ~/openrig/research/<run>/niches.json          one tracker per research run
  ../snapshots/activity-log.csv                 written by rig-snapshots.sh
"""
import csv, glob, hmac, html, http.cookies, http.server, io, json, os, posixpath, re, shutil, subprocess, time, urllib.parse
from datetime import datetime
import features as F
import store as S
import gates as G

DASH = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.expanduser(os.environ.get("RIG_RESEARCH_DIR", "~/openrig/research"))
ACTIVITY = os.environ.get("RIG_ACTIVITY_LOG",
                          os.path.join(DASH, "..", "snapshots", "activity-log.csv"))
PORT = int(os.environ.get("PORT", "8800"))


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
        runs.append({
            "run": name,
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


def tail_lines(path, max_bytes=256_000):
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - max_bytes))
        data = f.read().decode("utf-8", "replace")
    lines = data.splitlines()
    return lines[1:] if size > max_bytes else lines[1:]  # drop partial line or header


def team():
    """Latest state per seat, how long it has held that state, and its share
    of time spent working over the logged window."""
    if not os.path.isfile(ACTIVITY):
        return {"logger": "missing", "seats": []}
    rows = list(csv.reader(io.StringIO("\n".join(tail_lines(ACTIVITY)))))
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


SNAP = os.path.join(DASH, "..", "snapshots")
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


def history(minutes=30):
    """Per seat, one state per minute for the last N minutes: w(orking), b(locked), i(dle), or ''."""
    out = {}
    if not os.path.isfile(ACTIVITY):
        return out
    now = datetime.now()
    rows = list(csv.reader(io.StringIO("\n".join(tail_lines(ACTIVITY, 600_000)))))
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


def graph():
    ps = _load("_ps.json")
    queue = _load("_queue.json")
    runs = {r["run"]: r for r in list_runs() if "error" not in r}
    nodes, alerts = [], []
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
            "lifecycle": r.get("lifecycleState"), "action": plain(scr["action"]), "raw": scr["action"],
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
            alerts.append({"kind": "limit", "node": sess, "text": f"{node['name']} hit its usage limit and stopped",
                           "detail": "It won't continue until the limit resets. Consider pausing the team."})
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
    # Decision gates any job has opened for you.
    try:
        for gt in G.list_gates(0)["open"]:
            alerts.append({"kind": "gate", "severity": "warn", "node": f"{gt['job']}.{gt['id']}",
                           "text": f"{gt['job']}: {gt['title']}", "detail": gt["question"] or "A team is waiting for your decision.",
                           "url": f"/decide.html?job={gt['job']}&gate={gt['id']}"})
    except Exception:
        pass
    # Dismissals last only as long as the condition: once an alert clears, its dismissal is forgotten.
    dis = _dismissed()
    keys = set()
    for al in alerts:
        al["key"] = f"{al['kind']}:{al['node']}"
        keys.add(al["key"])
        al["dismissed"] = al["key"] in dis
    if set(dis) - keys:
        _save_dismissed({k: v for k, v in dis.items() if k in keys})
    return {"generated": datetime.now().isoformat(timespec="seconds"),
            "rigs": list(rigs.values()), "nodes": nodes, "edges": list(edges.values()),
            "alerts": alerts, "queue_seen": len(queue)}


RUN_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
DISMISSED = os.path.join(DASH, "state", "dismissed.json")


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
            r = subprocess.run([rig, "send", lead, msg], capture_output=True, text=True, timeout=30)
            sent = r.returncode == 0
        except Exception:
            sent = False
    return {"saved": True, "decided_at": stamp, "count": len(picks), "lead": lead, "lead_notified": sent}



def send_message(body):
    """Deliver a message from the user to one agent with `rig send`. Refuses when the
    agent is sitting at an approval prompt, where typed text could answer the prompt."""
    seat = str(body.get("seat") or "")
    msg = str(body.get("message") or "").strip()
    if not msg or len(msg) > 4000:
        raise ValueError("Write a message (up to 4000 characters)")
    node = next((r for r in _load("_ps.json") if r.get("canonicalSessionName") == seat and r.get("runtime") != "terminal"), None)
    if not node:
        raise ValueError("Unknown agent")
    if ((node.get("agentActivity") or {}).get("state") or "").startswith("needs_input"):
        raise ValueError("It's waiting at an approval prompt. Answer that in its terminal first; a message now could answer the prompt by accident.")
    rig = _rig_bin()
    if not rig:
        raise ValueError("Couldn't find the rig command on this machine")
    r = subprocess.run([rig, "send", seat, f"Message from the user (via Rig Console): {msg}"],
                       capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise ValueError((r.stderr or r.stdout or "rig send failed").strip()[:300])
    return {"sent": True, "at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "note": (r.stdout or "").strip()[:300]}

TOKEN = os.environ.get("RIG_CONSOLE_TOKEN", "")
HOST = os.environ.get("HOST", "127.0.0.1")


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".wasm": "application/wasm", ".pck": "application/octet-stream",
                      ".md": "text/plain; charset=utf-8", ".json": "application/json", ".webmanifest": "application/manifest+json"}
    PUBLIC = ("/manifest.json", "/icon.svg")   # the browser fetches these without cookies when installing

    def _allowed(self):
        """Local requests are always allowed. Remote ones (laptop/phone over Tailscale)
        need the token once via ?token=..., after which a cookie remembers it."""
        if self.path.split("?", 1)[0] in self.PUBLIC:
            return True
        proxied = any(self.headers.get(h) for h in ("X-Forwarded-For", "Tailscale-User-Login", "Forwarded"))
        if self.client_address[0] in ("127.0.0.1", "::1") and not proxied:
            return True
        # Requests relayed by a proxy on this PC (e.g. Tailscale Serve) come from 127.0.0.1 too,
        # but they're really from another device, so they need the token like any remote request.
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

    def _login_page(self):
        """Friendly sign-in instead of a bare 403: type the token once, the cookie remembers it."""
        path, _, query = self.path.partition("?")
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
<p>Enter your console token. This device will remember it.</p>{keep}
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
        if not self._allowed():
            p = self.path.split("?", 1)[0]
            if p.startswith("/api/") or not TOKEN:
                self.send_error(403, "Not signed in")
            else:
                self._login_page()
            return
        path = self.path.split("?", 1)[0]
        if getattr(self, "_token_login", False):
            # Signed in with ?token=: set the cookie and reload without the token in the address bar or history.
            rest = [(k, v) for k, vs in urllib.parse.parse_qs(self.path.partition("?")[2]).items() if k != "token" for v in vs]
            self.send_response(303)
            self.send_header("Location", path + ("?" + urllib.parse.urlencode(rest) if rest else ""))
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        try:
            if path == "/api/runs":
                return self.send_json(list_runs())
            if path == "/api/team":
                return self.send_json(team())
            if path == "/api/graph":
                return self.send_json(graph())
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
                return self.send_json(G.list_gates())
            if path == "/api/builds":
                return self.send_json(G.list_builds())
            if path == "/api/jobs":
                return self.send_json(S.jobs_list())
            if path == "/api/replay_rigs":
                return self.send_json(S.replay_rigs())
            if path == "/api/health":
                return self.send_json(F.health())
            if path == "/api/usage":
                return self.send_json(F.usage_list())
            if path == "/api/evidence":
                return self.send_json(F.evidence_status(arg("run")))
            if path == "/api/timeline":
                rig = arg("rig")
                if not re.match(r"^[A-Za-z0-9._-]{1,64}$", rig):
                    return self.send_json({"error": "bad rig"})
                return self.send_json(F.timeline(rig, arg("run") or None, _load("_queue.json")))
            if path == "/api/approvals":
                rig = arg("rig")
                return self.send_json(F.approvals(rig if re.match(r"^[A-Za-z0-9._-]{1,64}$", rig or "") else None))
            if path == "/api/decisions":
                return self.send_json(F.decisions(DATA))
            if path == "/api/runs_summary":
                rigs = sorted({row[1] for row in csv.reader(io.StringIO("\n".join(tail_lines(ACTIVITY, 5_000_000)))) if len(row) > 2 and row[0][:2] == "20"})
                return self.send_json(F.runs_summary(DATA, rigs, _load("_queue.json")))
            if path == "/api/briefs":
                bdir = os.path.expanduser("~/openrig/briefs")
                items = []
                if os.path.isdir(bdir):
                    for fn in sorted(os.listdir(bdir)):
                        if fn.endswith(".md"):
                            items.append({"name": fn, "text": open(os.path.join(bdir, fn), encoding="utf-8", errors="replace").read()[:60000]})
                return self.send_json(items)
            if path == "/api/rigs":
                return self.send_json(sorted({r.get("rigName") for r in _load("_ps.json") if r.get("rigName")} |
                                             {row[1] for row in csv.reader(io.StringIO("\n".join(tail_lines(ACTIVITY, 2_000_000)))) if len(row) > 2 and row[0][:2] == "20"}))
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
                return self.send_json({"updated": lines[0] if lines else "", "lines": [l.rstrip() for l in lines[1:]][-80:]})
        except Exception as e:
            return self.send_json({"error": str(e)})
        return super().do_GET()

    def do_POST(self):
        if not self._allowed():
            self.send_error(403)
            return
        path = self.path.split("?", 1)[0]
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
        m = re.match(r"^/(job|play)/([A-Za-z0-9._-]{1,64})/(.+)$", path)
        if m:
            full = G.safe_path(m.group(2), m.group(3))
            return full or os.path.join(DASH, "__forbidden__")
        if path.startswith("/data/"):
            root, rel = DATA, path[len("/data/"):]
        else:
            root, rel = DASH, path.lstrip("/") or "index.html"
        full = os.path.realpath(os.path.join(root, rel))
        if not full.startswith(os.path.realpath(root) + os.sep):
            return os.path.join(DASH, "__forbidden__")
        return full

    def end_headers(self):
        if getattr(self, "_set_cookie", False):
            self.send_header("Set-Cookie", f"rc_token={TOKEN}; Path=/; HttpOnly; SameSite=Lax; Secure; Max-Age=31536000")
        p = self.path.split("?", 1)[0]
        if p.startswith("/play/"):
            # Godot 4 web builds need cross-origin isolation; big .wasm/.pck files may be cached but rechecked.
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
            self.send_header("Cache-Control", "no-cache")
        else:
            if p.startswith("/job/"):
                # Files agents wrote: show them, but never let them run scripts as the console.
                self.send_header("Content-Security-Policy", "sandbox")
                self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


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
        except Exception:
            pass
        time.sleep(10)


if __name__ == "__main__":
    import threading
    if HOST not in ("127.0.0.1", "localhost") and not TOKEN:
        raise SystemExit("Refusing to listen beyond localhost without RIG_CONSOLE_TOKEN set.")
    threading.Thread(target=_watch, daemon=True).start()
    print(f"Dashboard on http://{HOST}:{PORT}  (Ctrl+C to stop)")
    http.server.ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
