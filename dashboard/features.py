"""Rig Console features: run timeline, usage log, evidence checker, health.
Imported by serve.py. Reads OpenRig mirrors; writes only to dashboard/state/."""
import csv, json, os, re, shutil, threading, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

DASH = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.expanduser(os.environ.get("RIG_STATE_DIR", os.path.join(DASH, "state")))
SNAP = os.path.expanduser(os.environ.get("RIG_SNAPSHOTS", os.path.join(DASH, "..", "snapshots")))
os.makedirs(STATE, exist_ok=True)
ACTIVITY = os.path.join(SNAP, "activity-log.csv")
os.makedirs(STATE, exist_ok=True)
_lock = threading.Lock()
RUN_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def _now():
    return datetime.now().astimezone()


def _parse_local(ts):
    return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").astimezone()


def _parse_iso(ts):
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00")).astimezone()
    except Exception:
        return None


# ---------- Phase history (recorded whenever a run's phase changes)
PHASES = os.path.join(STATE, "phases.csv")
_last_phase = {}


def record_phases(runs):
    with _lock:
        if not _last_phase and os.path.isfile(PHASES):
            for r in csv.reader(open(PHASES)):
                if len(r) == 3:
                    _last_phase[r[1]] = r[2]
        new = [(r["run"], r.get("phase")) for r in runs if r.get("phase") and _last_phase.get(r["run"]) != r.get("phase")]
        if new:
            with open(PHASES, "a", newline="") as f:
                w = csv.writer(f)
                for run, ph in new:
                    w.writerow([_now().isoformat(timespec="seconds"), run, ph])
                    _last_phase[run] = ph


def phases(run):
    if not os.path.isfile(PHASES):
        return []
    return [{"ts": r[0], "phase": r[2]} for r in csv.reader(open(PHASES)) if len(r) == 3 and r[1] == run]


# ---------- Timeline: one lane per agent over the life of a team
def _state_code(s):
    return "b" if s.startswith("needs_input") else "w" if s in ("working", "running") else "i"


def timeline(rig, run=None, queue=None):
    lanes, t0, t1 = {}, None, None
    if os.path.isfile(ACTIVITY):
        with open(ACTIVITY, newline="") as f:
            for r in csv.reader(f):
                if len(r) < 6 or r[1] != rig or r[0][:2] != "20":
                    continue
                try:
                    t = _parse_local(r[0])
                except ValueError:
                    continue
                t0 = t0 or t
                t1 = t
                code = _state_code(r[4])
                segs = lanes.setdefault(r[2], [])
                if segs and segs[-1][2] == code and (t - segs[-1][1]).total_seconds() <= 60:
                    segs[-1][1] = t
                else:
                    if segs and (t - segs[-1][1]).total_seconds() <= 60:
                        segs[-1][1] = t  # close the previous segment where this one starts
                    segs.append([t, t, code])
    out, stats = [], {}
    for sess, segs in sorted(lanes.items()):
        tot = {"w": 0.0, "i": 0.0, "b": 0.0}
        for a, b, c in segs:
            tot[c] += max(10.0, (b - a).total_seconds())
        stats[sess] = {k: round(v / 60, 1) for k, v in tot.items()}
        out.append({"session": sess, "segments": [[a.isoformat(timespec="seconds"), b.isoformat(timespec="seconds"), c] for a, b, c in segs]})
    events = []
    for q in queue or []:
        src, dst = q.get("sourceSession") or "", q.get("destinationSession") or ""
        if not (src.endswith("@" + rig) or dst.endswith("@" + rig)):
            continue
        for key, kind in (("tsCreated", "sent"), ("claimedAt", "picked up")):
            t = _parse_iso(q.get(key))
            if t:
                events.append({"ts": t.isoformat(timespec="seconds"), "kind": kind, "from": src, "to": dst,
                               "state": q.get("state"), "tags": q.get("tags") or []})
    events.sort(key=lambda e: e["ts"])
    return {"rig": rig, "start": t0.isoformat(timespec="seconds") if t0 else None,
            "end": t1.isoformat(timespec="seconds") if t1 else None,
            "lanes": out, "stats": stats, "events": events, "phases": phases(run) if run else []}


# ---------- Usage log (entered by hand from the Claude and ChatGPT usage pages)
USAGE = os.path.join(STATE, "usage.csv")
USAGE_FIELDS = ["ts", "provider", "meter", "percent_used", "run", "note"]
METERS = {("claude", "session"), ("claude", "weekly"), ("codex", "weekly")}


def _seed_usage():
    if os.path.isfile(USAGE):
        return
    with open(USAGE, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(USAGE_FIELDS)
        w.writerow(["2026-10-11T15:11:00-07:00", "claude", "session", "13", "run-1", "Before launching the research team"])
        w.writerow(["2026-10-11T15:13:00-07:00", "codex", "weekly", "0", "run-1", "Before launching the research team"])


def usage_list():
    _seed_usage()
    with open(USAGE, newline="") as f:
        return list(csv.DictReader(f))


def usage_add(body):
    provider, meter = str(body.get("provider", "")).lower(), str(body.get("meter", "")).lower()
    if (provider, meter) not in METERS:
        raise ValueError("Unknown meter")
    pct = float(body.get("percent_used"))
    if not 0 <= pct <= 100:
        raise ValueError("Percent must be 0-100")
    run = str(body.get("run") or "")
    if run and not RUN_RE.match(run):
        raise ValueError("Bad run")
    _seed_usage()
    row = [_now().isoformat(timespec="seconds"), provider, meter, f"{pct:g}", run, str(body.get("note") or "")[:200]]
    with _lock, open(USAGE, "a", newline="") as f:
        csv.writer(f).writerow(row)
    return dict(zip(USAGE_FIELDS, row))


# ---------- Evidence checker: are the team's source links real and reachable?
URL_RE = re.compile(r"https?://[^\s)<>\]\"'`]+")
_jobs = {}
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36"


def _check(url):
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
            with urllib.request.urlopen(req, timeout=12) as r:
                return {"url": url, "status": r.status, "final": r.geturl(), "verdict": "ok"}
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 429, 501):
                continue  # many sites refuse HEAD; retry with GET
            v = "dead" if e.code in (404, 410) else "blocked" if e.code in (401, 403, 429, 451, 999) else "error"
            return {"url": url, "status": e.code, "final": url, "verdict": v}
        except Exception as e:
            if method == "HEAD":
                continue
            return {"url": url, "status": None, "final": url, "verdict": "unreachable", "detail": type(e).__name__}
    return {"url": url, "status": None, "final": url, "verdict": "unreachable"}


def evidence_start(run, research_dir):
    if not RUN_RE.match(run or ""):
        raise ValueError("Unknown run")
    if _jobs.get(run, {}).get("running"):
        return {"started": False, "running": True}
    run_dir = os.path.join(research_dir, run)
    tracker = json.load(open(os.path.join(run_dir, "niches.json")))
    cites, unsupported = {}, []
    for n in tracker.get("niches") or []:
        ev = [u for u in n.get("evidence") or [] if URL_RE.match(str(u))]
        if not ev and n.get("stage") != "cut":
            unsupported.append({"id": n.get("id"), "name": n.get("name")})
        for u in ev:
            cites.setdefault(u.rstrip(".,;"), []).append(n.get("id"))
    for p in [os.path.join(run_dir, "sources.md")]:
        if os.path.isfile(p):
            for u in URL_RE.findall(open(p, encoding="utf-8", errors="replace").read()):
                cites.setdefault(u.rstrip(".,;"), [])
    urls = sorted(cites)
    job = {"running": True, "started": _now().isoformat(timespec="seconds"), "total": len(urls), "done": 0,
           "results": [], "unsupported": unsupported}
    _jobs[run] = job

    def work():
        with ThreadPoolExecutor(max_workers=8) as pool:
            for res in pool.map(_check, urls):
                res["niches"] = cites.get(res["url"], [])
                job["results"].append(res)
                job["done"] += 1
        job["running"] = False
        job["finished"] = _now().isoformat(timespec="seconds")
        with open(os.path.join(STATE, f"evidence-{run}.json"), "w") as f:
            json.dump(job, f, indent=1)

    threading.Thread(target=work, daemon=True).start()
    return {"started": True, "total": len(urls)}


def evidence_status(run):
    if not RUN_RE.match(run or ""):
        raise ValueError("Unknown run")
    if run in _jobs:
        return _jobs[run]
    p = os.path.join(STATE, f"evidence-{run}.json")
    return json.load(open(p)) if os.path.isfile(p) else {"running": False, "total": 0, "results": []}


# ---------- Health: is the plumbing up?
def health():
    out = {}
    try:
        last = None
        with open(ACTIVITY, "rb") as f:
            f.seek(max(0, os.path.getsize(ACTIVITY) - 400))
            last = f.read().decode("utf-8", "replace").strip().splitlines()[-1].split(",")[0]
        age = (_now() - _parse_local(last)).total_seconds()
        when = f"{int(age)} s" if age < 120 else f"{int(age // 60)} min" if age < 7200 else f"{int(age // 3600)} h"
        out["logger"] = {"ok": age < 60, "detail": f"last write {when} ago", "age_s": int(age)}
    except Exception:
        out["logger"] = {"ok": False, "detail": "no activity log"}
    try:
        st = open(os.path.join(SNAP, "_status.txt")).read()
        out["daemon"] = {"ok": "Daemon running" in st, "detail": "running" if "Daemon running" in st else "not running"}
    except Exception:
        out["daemon"] = {"ok": False, "detail": "unknown"}
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434", timeout=1.5) as r:
            out["ollama"] = {"ok": r.status == 200, "detail": "reachable", "level": "optional"}
    except Exception:
        out["ollama"] = {"ok": False, "detail": "off (only the local model tests use it)", "level": "optional"}
    try:
        du = shutil.disk_usage(os.path.expanduser("~"))
        free = du.free / 2**30
        out["disk"] = {"ok": free > 10, "detail": f"{free:.0f} GB free"}
    except Exception:
        out["disk"] = {"ok": True, "detail": "unknown"}
    ka = keepalive_running()
    out["keepalive"] = {"ok": ka, "level": "advisory",
                        "detail": "Windows keep-alive is holding Ubuntu open" if ka else "not running: closing every terminal may stop Ubuntu and the agents"}
    try:
        up = float(open("/proc/uptime").read().split()[0])
        out["ubuntu"] = {"ok": True, "detail": f"up {int(up // 3600)} h {int(up % 3600 // 60)} min"}
    except Exception:
        out["ubuntu"] = {"ok": True, "detail": "unknown"}
    return out


# ---------- Approvals log: every approval prompt, how long it waited, what it asked
APPROVALS = os.path.join(STATE, "approvals.csv")
APPROVAL_FIELDS = ["start", "end", "rig", "seat", "request", "wait_s"]
_open_prompts = {}  # seat -> {"start", "rig", "request"}


def track_approvals(nodes):
    """Called every few seconds with the current agents. Writes one row per prompt once it clears."""
    now = _now()
    blocked = {n["id"]: n for n in nodes if n["state"].startswith("needs_input")}
    for seat, n in blocked.items():
        cur = _open_prompts.setdefault(seat, {"start": now, "rig": n.get("rig"), "request": n.get("action") or ""})
        if n.get("action") and len(n["action"]) > len(cur["request"]):
            cur["request"] = n["action"]
    for seat in [s for s in _open_prompts if s not in blocked]:
        p = _open_prompts.pop(seat)
        row = [p["start"].isoformat(timespec="seconds"), now.isoformat(timespec="seconds"), p["rig"], seat,
               p["request"][:300], str(int((now - p["start"]).total_seconds()))]
        new = not os.path.isfile(APPROVALS)
        with _lock, open(APPROVALS, "a", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(APPROVAL_FIELDS)
            w.writerow(row)


def _kind(req):
    """Group similar prompts so repeat offenders stand out."""
    r = (req or "").lower()
    for key, label in (("handoff", "Hand work back through the queue"), ("hand ", "Hand work back through the queue"),
                       ("queue", "Queue commands"), ("validate", "Run a validation script"), ("python", "Run a script"),
                       ("script", "Run a script"), ("fetch", "Read a web page"), ("web", "Web search or page"),
                       ("edit", "Edit a file"), ("write", "Write a file"), ("rig ", "OpenRig command")):
        if key in r:
            return label
    return "Other"


def approvals(rig=None):
    rows = []
    if os.path.isfile(APPROVALS):
        with open(APPROVALS, newline="") as f:
            rows = [r for r in csv.DictReader(f) if not rig or r["rig"] == rig]
    for seat, p in _open_prompts.items():
        if not rig or p["rig"] == rig:
            rows.append({"start": p["start"].isoformat(timespec="seconds"), "end": "", "rig": p["rig"], "seat": seat,
                         "request": p["request"], "wait_s": str(int((_now() - p["start"]).total_seconds())), "open": True})
    groups = {}
    for r in rows:
        g = groups.setdefault(_kind(r["request"]), {"kind": _kind(r["request"]), "count": 0, "wait_s": 0, "longest_s": 0, "example": r["request"]})
        w = int(r["wait_s"] or 0)
        g["count"] += 1; g["wait_s"] += w; g["longest_s"] = max(g["longest_s"], w)
    return {"rows": rows[::-1], "groups": sorted(groups.values(), key=lambda g: -g["wait_s"])}


# ---------- Decision log: every checkpoint call across runs
def decisions(research_dir):
    out = []
    if not os.path.isdir(research_dir):
        return out
    for run in sorted(os.listdir(research_dir)):
        p = os.path.join(research_dir, run, "decision.json")
        if not os.path.isfile(p):
            continue
        try:
            d = json.load(open(p))
            tracker = json.load(open(os.path.join(research_dir, run, "niches.json")))
        except Exception:
            continue
        by_id = {n.get("id"): n for n in tracker.get("niches") or []}
        d["outcomes"] = [{"id": i, "name": by_id.get(i, {}).get("name", i), "stage": by_id.get(i, {}).get("stage"),
                          "reason": by_id.get(i, {}).get("reason")} for i in d.get("deep_dive") or []]
        out.append(d)
    return sorted(out, key=lambda d: d.get("decided_at") or "", reverse=True)


# ---------- Cross-run comparison
def runs_summary(research_dir, rigs, queue):
    out = []
    usage = usage_list()
    for run in sorted(os.listdir(research_dir)) if os.path.isdir(research_dir) else []:
        tp = os.path.join(research_dir, run, "niches.json")
        if not os.path.isfile(tp):
            continue
        try:
            tr = json.load(open(tp))
        except Exception:
            continue
        n = tr.get("niches") or []
        rig = next((r for r in rigs if r.endswith(run)), None) or next((r for r in rigs if run in r), None)
        tl = timeline(rig, run, queue) if rig else {"stats": {}, "start": None, "end": None, "events": []}
        st = tl["stats"].values()
        dur = None
        if tl["start"] and tl["end"]:
            dur = round((_parse_iso(tl["end"]) - _parse_iso(tl["start"])).total_seconds() / 60)
        cost = {}
        for r in usage:
            if r["run"] != run:
                continue
            k = f"{r['provider']} {r['meter']}"
            cost.setdefault(k, []).append(float(r["percent_used"]))
        ev = None
        ep = os.path.join(STATE, f"evidence-{run}.json")
        if os.path.isfile(ep):
            e = json.load(open(ep))
            res = e.get("results") or []
            ev = {"links": len(res), "dead": sum(1 for x in res if x["verdict"] == "dead"),
                  "unsupported": len(e.get("unsupported") or [])}
        out.append({
            "run": run, "rig": rig, "phase": tr.get("phase"), "minutes": dur,
            "working_min": round(sum(s["w"] for s in st)), "waiting_min": round(sum(s["b"] for s in st)),
            "handoffs": sum(1 for e in tl["events"] if e["kind"] == "sent"),
            "longlist": len(n), "screened": max(sum(1 for x in n if x.get("stage") in ("screened", "shortlisted", "finalist")),
                                                (json.load(open(FUNNEL)).get(run, {}) if os.path.isfile(FUNNEL) else {}).get("screened", 0)),
            "shortlisted": sum(1 for x in n if x.get("stage") in ("shortlisted", "finalist")),
            "cost": {k: round(v[-1] - v[0]) for k, v in cost.items() if len(v) > 1},
            "evidence": ev,
        })
    return out


# ---------- Keep-alive check (the Windows task runs `sleep infinity` inside Ubuntu)
def keepalive_running():
    try:
        for pid in os.listdir("/proc"):
            if pid.isdigit():
                try:
                    cmd = open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ").strip()
                except Exception:
                    continue
                if cmd == b"sleep infinity":
                    return True
    except Exception:
        pass
    return False


# ---------- Optional phone push via ntfy (set NTFY_TOPIC to enable; sends alert text to ntfy.sh)
_pushed = {}     # alert key -> when we last pushed it
PUSH = {"last_ok": None, "error": None, "error_at": None}   # last push outcome, for /api/health
_pending = {}    # alert key -> when we first saw it (not pushed yet)
PUSH_AFTER_S = 25          # must persist across two checks: ignores one-tick blips
REPUSH_AFTER_S = 6 * 3600  # an alert that flaps off and on again is only re-sent after 6 hours


def push_alerts(alerts):
    """Phone pushes for alerts the console marked `notify` (serve.NOTIFY). Each alert is pushed once while it
    lasts, and not again if it clears and comes back within 6 hours. Several due in one round go as one
    summary push."""
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        return
    now = time.time()
    live = {a["key"] for a in alerts if not a.get("dismissed")}
    for k in list(_pending):
        if k not in live:
            del _pending[k]
    due = []
    for a in alerts:
        k = a["key"]
        if k in _pushed and k in live:
            _pushed[k] = now   # still there: never repeat it
        # nopush: the operator's outbox pushes its own notes (outbox.py)
        if a.get("dismissed") or a.get("nopush") or not a.get("notify") or k in _pushed:
            continue
        if now - _pending.setdefault(k, now) < PUSH_AFTER_S:
            continue
        _pushed[k] = now
        due.append(a)
    if len(due) == 1:
        a = due[0]
        push_now(a["text"], a["notify"], "high" if a.get("severity") != "warn" else "default", a.get("url"))
    elif due:
        push_now("\n".join(f"- {a['notify']}: {a['text']}" for a in due[:8]) + (f"\n…and {len(due) - 8} more" if len(due) > 8 else ""),
                 f"{len(due)} things need you", "high" if any(a.get("severity") != "warn" for a in due) else "default", "/m.html")
    for k in [k for k, t in _pushed.items() if now - t > REPUSH_AFTER_S]:
        del _pushed[k]


def push_now(text, title="Rig Console", priority="high", url=None):
    """One ntfy push. Returns (ok, detail); the detail never includes the topic."""
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        return False, "phone push isn't set up on the console (NTFY_TOPIC)"
    now = time.time()
    try:
        headers = {"Title": title.encode("ascii", "replace").decode(), "Priority": priority}
        base = os.environ.get("NTFY_CLICK", "").rstrip("/")
        if base:   # tapping the notification opens the console (or the decision page for gates)
            headers["Click"] = base + (url or "/m.html")
        req = urllib.request.Request(f"https://ntfy.sh/{topic}", data=text.encode(), method="POST", headers=headers)
        urllib.request.urlopen(req, timeout=5).close()
        PUSH["last_ok"], PUSH["error"] = now, None
        return True, "sent"
    except Exception as e:
        # Remember the failure so /api/health can show it; a silent push failure means a silent phone.
        PUSH["error"], PUSH["error_at"] = f"{type(e).__name__}: {e}"[:200], now
        print("ntfy push failed:", PUSH["error"], flush=True)
        return False, f"the push service refused or didn't answer ({type(e).__name__})"


# ---------- Funnel peaks: how many niches each stage ever held (cuts later don't shrink it)
FUNNEL = os.path.join(STATE, "funnel.json")


def record_funnel(run, tracker):
    n = tracker.get("niches") or []
    now = {"longlist": len(n),
           "screened": sum(1 for x in n if x.get("stage") in ("screened", "shortlisted", "finalist")),
           "shortlist": sum(1 for x in n if x.get("stage") in ("shortlisted", "finalist"))}
    if tracker.get("phase") in ("deep-dive", "shortlist", "done"):
        now["deep_dive"] = now["screened"]
    with _lock:
        try:
            data = json.load(open(FUNNEL))
        except Exception:
            data = {}
        peak = data.setdefault(run, {})
        changed = False
        for k, v in now.items():
            if v > peak.get(k, 0):
                peak[k] = v
                changed = True
        if changed:
            json.dump(data, open(FUNNEL, "w"), indent=1)
    out = dict(peak)
    out.update({f"{k}_now": v for k, v in now.items()})
    # A tracker can state its own funnel; trust it over our observations.
    for k, v in (tracker.get("funnel") or {}).items():
        if isinstance(v, int):
            out[k] = v
    return out
