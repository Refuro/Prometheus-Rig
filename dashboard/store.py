"""Rig Console event store (SQLite).

One table of events: what changed, when, and who did it. The live feed and the
replay both read from here. The watcher thread in serve.py calls collect() every
10 seconds; nothing else writes.

The database lives in Ubuntu's own filesystem (not OneDrive: syncing a live
database file can corrupt it). Override with RIG_DB.

Event kinds:
  state    seat changed state (text = working | idle | blocked)
  action   a working seat started something new (text = plain-English action)
  handoff  seat sent work to peer (text = tags)
  pickup   seat picked up work from peer
  done     seat closed work from peer (text = done | handed-off | canceled)
  file     seat wrote a file in a job folder (peer = job, text = path in the job folder)
  <any>    jobs can log their own kinds (build, playtest, email_sent...) through events.jsonl

Jobs: any folder under a watched root (jobs.json) is a job: a research run, a validation
campaign, a game prototype, anything. An optional job.json inside it says what it is:
  {"type": "prototype", "rig": "studio-proto-1", "title": "Gravity toy",
   "writers": {"build": "builder-a"}, "watch_depth": 3}
A job can also append its own events, one JSON object per line, to <job>/events.jsonl:
  {"kind": "playtest", "seat": "playtest-bot", "text": "Level 3 solvable in 41 moves", "data": {...}}
"""
import csv, json, os, re, sqlite3, threading, time
from datetime import datetime

DB_PATH = os.path.expanduser(os.environ.get("RIG_DB", "~/.local/share/rig-console/console.db"))
_lock = threading.RLock()
_conn = None

# Schema changes go here as new numbered steps; never edit an old step.
MIGRATIONS = {
    1: [
        """CREATE TABLE events(
             id   INTEGER PRIMARY KEY,
             ts   REAL NOT NULL,          -- unix seconds
             kind TEXT NOT NULL,
             rig  TEXT, seat TEXT, peer TEXT, text TEXT,
             key  TEXT UNIQUE             -- dedupe key, so re-reading the same source is harmless
           )""",
        "CREATE INDEX ev_ts ON events(ts)",
        "CREATE INDEX ev_seat ON events(seat)",
        "CREATE INDEX ev_peer ON events(peer)",
        "CREATE TABLE meta(k TEXT PRIMARY KEY, v TEXT)",
    ],
    2: [
        "ALTER TABLE events ADD COLUMN job TEXT",
        "ALTER TABLE events ADD COLUMN data TEXT",  # optional JSON details
        "CREATE INDEX ev_job ON events(job)",
        """CREATE TABLE jobs(
             name TEXT PRIMARY KEY, type TEXT, rig TEXT, folder TEXT, title TEXT,
             first_seen REAL, last_seen REAL)""",
        "UPDATE events SET job = peer WHERE kind = 'file'",
    ],
}
JOBS_CONFIG = os.path.expanduser(os.environ.get("RIG_JOBS_CONFIG",
                                               os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobs.json")))
DEFAULT_ROOTS = [{"root": "~/openrig/research", "type": "research"},
                 {"root": "~/openrig/jobs", "type": "general"}]
SKIP_DIRS = {"node_modules", "__pycache__", ".godot", ".import", "build", "dist", "venv", ".venv", "target"}
KIND_RE = re.compile(r"^[a-z0-9_-]{1,32}$")
CLOSED = {"done", "handed-off", "canceled"}


def db():
    global _conn
    with _lock:
        if _conn is None:
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            c = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
            c.row_factory = sqlite3.Row
            c.execute("PRAGMA journal_mode=WAL")
            v = c.execute("PRAGMA user_version").fetchone()[0]
            for ver in sorted(MIGRATIONS):
                if ver > v:
                    with c:
                        for sql in MIGRATIONS[ver]:
                            c.execute(sql)
                        c.execute(f"PRAGMA user_version={ver}")
            _conn = c
        return _conn


def _meta(k, v=None):
    with _lock:
        c = db()
        if v is None:
            r = c.execute("SELECT v FROM meta WHERE k=?", (k,)).fetchone()
            return r["v"] if r else None
        with c:
            c.execute("INSERT OR REPLACE INTO meta(k, v) VALUES(?, ?)", (k, str(v)))


def _add_many(rows):
    """rows: (ts, kind, rig, seat, peer, text, key[, job, data]). Duplicate keys are ignored."""
    if not rows:
        return
    rows = [tuple(r) + (None,) * (9 - len(r)) for r in rows]
    with _lock:
        c = db()
        with c:
            c.executemany("INSERT OR IGNORE INTO events(ts, kind, rig, seat, peer, text, key, job, data) VALUES(?,?,?,?,?,?,?,?,?)", rows)


# ---------- Jobs: discovered from folders, described by an optional job.json
def roots():
    try:
        with open(JOBS_CONFIG) as f:
            cfg = json.load(f)
        return cfg.get("roots") or DEFAULT_ROOTS
    except (OSError, ValueError):
        return DEFAULT_ROOTS


def discover_jobs():
    jobs = []
    for r in roots():
        base = os.path.expanduser(r.get("root", ""))
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            folder = os.path.join(base, name)
            if name.startswith((".", "_")) or not os.path.isdir(folder):
                continue
            meta = {}
            try:
                with open(os.path.join(folder, "job.json")) as f:
                    meta = json.load(f) or {}
            except (OSError, ValueError):
                pass
            # The name is always the folder name. job.json is written by seats, so it may not rename a job
            # (it could otherwise pass its gates off as another team's): MA-007 finding 5c.
            jobs.append({"name": name, "type": meta.get("type") or r.get("type") or "general",
                         "rig": meta.get("rig"), "title": meta.get("title") or name, "folder": folder,
                         "writers": meta.get("writers") or {}, "depth": int(meta.get("watch_depth") or 2)})
    return jobs


def duplicate_jobs():
    """Job names that appear under more than one watched root. Only the first is used."""
    seen, dup = set(), set()
    for j in discover_jobs():
        (dup if j["name"] in seen else seen).add(j["name"])
    return sorted(dup)


def jobs_list():
    with _lock:
        return _rows(db().execute("SELECT * FROM jobs ORDER BY last_seen DESC"))


def _iso(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _rig_of(session):
    return session.split("@", 1)[1] if session and "@" in session else None


def simple_state(st):
    st = st or ""
    return "blocked" if st.startswith("needs_input") else "working" if st == "working" else "idle"


# ---------- One-time backfill from the snapshot logger's CSV, so older runs can be replayed.
def backfill_activity(path):
    if _meta("backfill_activity") or not os.path.exists(path):
        return 0
    last, rows = {}, []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            act, sess = (r.get("activity") or ""), r.get("session")
            if not sess or act.startswith("unknown") or not act:
                continue
            st = "blocked" if act.startswith("needs_input") else "working" if act == "working" else "idle"
            if last.get(sess) == st:
                continue
            try:
                ts = time.mktime(time.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S"))  # logger writes local time
            except (KeyError, ValueError):
                continue
            last[sess] = st
            rows.append((ts, "state", r.get("rig") or _rig_of(sess), sess, None, st, f"bf:{sess}:{int(ts)}"))
    _add_many(rows)
    _meta("backfill_activity", int(time.time()))
    return len(rows)


# ---------- The collector: diff each 10-second look at the rig against the last one.
class Collector:
    def __init__(self, data_dir):
        self.data = data_dir
        self.state, self.action = {}, {}
        self.job_rig = {}
        with _lock:
            for r in db().execute("""SELECT seat, text FROM events WHERE id IN
                                     (SELECT MAX(id) FROM events WHERE kind='state' GROUP BY seat)"""):
                self.state[r["seat"]] = r["text"]

    def collect(self, g, queue):
        now, rows = time.time(), []
        nodes = g.get("nodes") or []
        # States and actions
        for n in nodes:
            sid, st = n["id"], simple_state(n.get("state"))
            if self.state.get(sid) != st:
                rows.append((now, "state", n.get("rig"), sid, None, st, None))
                self.state[sid] = st
                if st != "working":
                    self.action.pop(sid, None)
            a = (n.get("action") or "").strip()
            if st == "working" and a and not a.startswith(("Finished:", "Working", "Nothing")) and a != self.action.get(sid):
                rows.append((now, "action", n.get("rig"), sid, None, a[:300], None))
                self.action[sid] = a
        # Handoffs: the queue keeps its history, so the first read backfills old runs too.
        for q in queue:
            qid, s, d = q.get("qitemId"), q.get("sourceSession"), q.get("destinationSession")
            if not qid or not s or not d or s == d:
                continue
            rig = _rig_of(d)
            tags = ", ".join(t for t in (q.get("tags") or []) if t not in (rig, _rig_of(s)))[:200]
            t = _iso(q.get("tsCreated"))
            if t:
                rows.append((t, "handoff", rig, s, d, tags, f"{qid}:sent"))
            t = _iso(q.get("claimedAt"))
            if t:
                rows.append((t, "pickup", rig, d, s, tags, f"{qid}:pick"))
            if q.get("state") in CLOSED:
                t = _iso(q.get("tsUpdated")) or now
                rows.append((t, "done", rig, d, s, q.get("state"), f"{qid}:done"))
        # Files written in job folders. Keyed by minute, so a file edited all afternoon
        # shows once per minute of activity, not once per save.
        rigs = {n.get("rig") for n in nodes if n.get("rig")}
        job_rows = []
        for j in discover_jobs():
            rig = j["rig"] or self.job_rig.get(j["name"]) or next((r for r in rigs if j["name"] in r), None)
            if rig:
                self.job_rig[j["name"]] = rig
            seats = [n for n in nodes if n.get("rig") == rig] if rig else []
            last = self._scan_files(j, rig, seats, rows)
            self._read_jsonl(j, rig, seats, rows)
            job_rows.append((j["name"], j["type"], rig, j["folder"], j["title"], last or now, last or now))
        _add_many(rows)
        if job_rows:
            with _lock:
                c = db()
                with c:
                    c.executemany("""INSERT INTO jobs(name, type, rig, folder, title, first_seen, last_seen) VALUES(?,?,?,?,?,?,?)
                                     ON CONFLICT(name) DO UPDATE SET type=excluded.type, rig=COALESCE(excluded.rig, jobs.rig),
                                     folder=excluded.folder, title=excluded.title,
                                     last_seen=MAX(jobs.last_seen, excluded.last_seen),
                                     first_seen=MIN(jobs.first_seen, excluded.first_seen)""", job_rows)

    def _scan_files(self, j, rig, seats, rows, cap=3000):
        base, newest, seen = j["folder"], None, 0
        for root, dirs, files in os.walk(base):
            depth = os.path.relpath(root, base).count(os.sep) + (0 if root == base else 1)
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in SKIP_DIRS] if depth < j["depth"] - 1 else []
            for fn in files:
                if fn.startswith(".") or fn in ("events.jsonl", "job.json"):
                    continue
                seen += 1
                if seen > cap:
                    return newest
                p = os.path.join(root, fn)
                try:
                    m = os.path.getmtime(p)
                except OSError:
                    continue
                newest = max(newest or 0, m)
                rel = os.path.relpath(p, base)
                rows.append((m, "file", rig, self._writer(rel, seats, j["writers"]), j["name"], rel,
                             f"{j['name']}/{rel}:{int(m // 60)}", j["name"], None))
        return newest

    def _read_jsonl(self, j, rig, seats, rows):
        """Jobs log their own events by appending JSON lines; we remember how far we've read."""
        p = os.path.join(j["folder"], "events.jsonl")
        try:
            size = os.path.getsize(p)
        except OSError:
            return
        k = "jsonl:" + p
        off = int(_meta(k) or 0)
        if size < off:
            off = 0          # file was replaced
        if size == off:
            return
        with open(p, "rb") as f:
            f.seek(off)
            chunk = f.read(min(size - off, 1_000_000))
        end = chunk.rfind(b"\n") + 1   # only whole lines
        if not end:
            return
        names = {n["name"]: n["id"] for n in seats}
        for i, line in enumerate(chunk[:end].splitlines()):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if not isinstance(e, dict):
                continue
            kind = str(e.get("kind") or "").lower()
            if not KIND_RE.match(kind):
                continue
            seat = names.get(e.get("seat"), e.get("seat")) if e.get("seat") else None
            peer = names.get(e.get("peer"), e.get("peer")) if e.get("peer") else None
            ts = e.get("ts") if isinstance(e.get("ts"), (int, float)) else (_iso(e.get("ts")) if isinstance(e.get("ts"), str) else None)
            data = e.get("data")
            data = json.dumps(data)[:4000] if isinstance(data, (dict, list)) else None
            rows.append((ts or time.time(), kind, rig, seat, peer, str(e.get("text") or "")[:300],
                         f"{k}:{off}:{i}", j["name"], data))
        _meta(k, off + end)

    @staticmethod
    def _writer(rel, seats, writers=None):
        """Seats prefix their files (pain-, market-, skeptic-, lead-...); job.json "writers" can map a
        file-name prefix or a top folder ("pitches", "builds") to a seat. Everything else belongs to the lead."""
        fn = os.path.basename(rel)
        pre = fn.split("-", 1)[0].split(".", 1)[0].lower()
        top = rel.split(os.sep, 1)[0].lower() if os.sep in rel else None
        for key in (pre, top):
            if writers and key and key in writers:
                hit = next((n for n in seats if n["name"] == writers[key]), None)
                if hit:
                    return hit["id"]
        for n in seats:
            if pre in n["name"].lower().split("-"):
                return n["id"]
        lead = next((n for n in seats if n["name"].endswith("lead") and not n["name"].startswith("advisor")), None)
        return lead["id"] if lead else None


# ---------- Reads
def _rows(cur):
    return [dict(r) for r in cur]


def events(since=0, limit=60):
    """Newest events after id `since`, oldest first. since=0 returns the latest `limit`."""
    limit = max(1, min(int(limit), 300))
    with _lock:
        c = db()
        if since:
            rs = _rows(c.execute("SELECT * FROM events WHERE id > ? ORDER BY id LIMIT ?", (since, limit)))
        else:
            rs = _rows(c.execute("SELECT * FROM events WHERE ts <= ? ORDER BY ts DESC, id DESC LIMIT ?", (time.time() + 60, limit)))[::-1]
        last = c.execute("SELECT COALESCE(MAX(id), 0) FROM events").fetchone()[0]
    for r in rs:
        r.pop("key", None)
    return {"events": rs, "last_id": last}


def since_summary(ts, until=None):
    """What happened after ts (and before `until`), in epoch seconds, counted: for "Since you last looked" on
    Now and the daily digest (owner, 2026-10-14). Handoffs finished, seats that went to waiting, the busiest
    teams by recorded activity, and teams first seen in the window."""
    # A day window (until given) is [start, end): midnight belongs to the day it starts, as the digest's
    # decisions and to-dos count it (review-1 finding 4). "Since you last looked" is strictly after ts.
    day = until is not None
    ts, until = float(ts), float(until) if day else time.time() + 60
    lo = ">=" if day else ">"
    win = f"ts {lo} ? AND ts < ?"
    with _lock:
        c = db()
        done = c.execute(f"SELECT COUNT(*) FROM events WHERE kind='done' AND {win}", (ts, until)).fetchone()[0]
        waits = c.execute(f"SELECT COUNT(*) FROM events WHERE kind='state' AND text='blocked' AND {win}", (ts, until)).fetchone()[0]
        teams = _rows(c.execute(f"""SELECT rig, COUNT(*) AS n FROM events WHERE {win} AND rig IS NOT NULL AND kind != 'state'
                                   GROUP BY rig ORDER BY n DESC LIMIT 4""", (ts, until)))
        new_jobs = [r["name"] for r in _rows(c.execute(f"SELECT name FROM jobs WHERE first_seen {lo} ? AND first_seen < ? ORDER BY first_seen", (ts, until)))]
    return {"handoffs_done": done, "approval_waits": waits, "busiest": teams, "new_jobs": new_jobs[:10]}


def replay(rig, run=None, max_rows=20000):
    """Everything involving one team, oldest first, for the replay player."""
    like = f"%@{rig}"
    with _lock:
        rs = _rows(db().execute(
            """SELECT ts, kind, rig, seat, peer, text, job, data FROM events
               WHERE seat LIKE ? OR peer LIKE ? OR job = ?
               ORDER BY ts, id LIMIT ?""", (like, like, run or "\x00", max_rows)))
    seats = sorted({x for r in rs for x in (r["seat"], r["peer"] if r["kind"] != "file" else None) if x and "@" in x})
    others = [x for x in seats if not x.endswith("@" + rig)]
    if rs and others:
        # Bring in the states of seats from other teams that traded work with this one (e.g. the operator).
        q = ",".join("?" * len(others))
        with _lock:
            rs += _rows(db().execute(
                f"""SELECT ts, kind, rig, seat, peer, text, job, data FROM events WHERE kind IN ('state','action')
                    AND seat IN ({q}) AND ts BETWEEN ? AND ? ORDER BY ts, id""", (*others, rs[0]["ts"] - 3600, rs[-1]["ts"])))
        rs.sort(key=lambda r: r["ts"])
    return {"rig": rig, "run": run, "events": rs, "seats": seats,
            "start": rs[0]["ts"] if rs else None, "end": rs[-1]["ts"] if rs else None}


def replay_rigs():
    """Teams that have history, newest activity first."""
    with _lock:
        rs = _rows(db().execute(
            """SELECT rig, MIN(ts) AS start, MAX(ts) AS end, COUNT(*) AS n FROM events
               WHERE rig IS NOT NULL AND kind IN ('state','handoff','action') GROUP BY rig ORDER BY end DESC"""))
    return rs
