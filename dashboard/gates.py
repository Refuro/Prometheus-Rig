"""Decision gates and playable builds, for any kind of job.

GATES: a team asks you to decide something by writing a JSON file in its job folder:
  <job>/gate.json            one gate, or
  <job>/gates/<id>.json      several
  {
    "title": "Pick 3 pitches",
    "question": "Which three should we prototype?",
    "kind": "choose",            # "choose" (pick options) or "approve" (approve / send back)
    "pick": 3,                   # exact count; or "min"/"max"
    "lead": "room-lead",         # seat to tell when you decide (default: the team's lead)
    "options": [{"id": "p01", "title": "Gravity Gardener", "summary": "One paragraph...",
                 "image": "art/p01.png", "file": "pitches/p01.md", "play": "builds/p01"}]
  }
Your answer goes to <job>/decisions/<id>.json and .md, and the lead gets a message.
A gate is open until its decision file exists.

BUILDS: any folder with an index.html under <job>/builds/ (or the folder named by
"builds" in job.json) is playable at /play/<job>/<build>/ on the builds port (R-006). Godot web exports work as-is:
the server sends the isolation headers Godot 4 needs.
"""
import hashlib, json, os, re, shlex, subprocess, threading
from datetime import datetime

import store as S

ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
SEAT_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def _jobs():
    out = {}
    for j in S.discover_jobs():
        if ID_RE.match(j["name"]) and j["name"] not in out:   # first folder wins; duplicates are flagged
            out[j["name"]] = j
    return out


def safe_path(job, rel):
    """Absolute path of rel inside the job folder, or None if it escapes it."""
    j = _jobs().get(job)
    if not j or not rel:
        return None
    base = os.path.realpath(j["folder"])
    full = os.path.realpath(os.path.join(base, rel))
    return full if full.startswith(base + os.sep) else None


def _url(job, rel, kind="job"):
    if not isinstance(rel, str) or not rel:
        return None
    full = safe_path(job, rel)
    prefix = "/go/play" if kind == "play" else f"/{kind}"   # builds live on their own port; /go/ redirects there (R-006)
    return f"{prefix}/{job}/{rel.lstrip('/')}" if full and os.path.exists(full) else None


# ---------- Which team a job belongs to (MA-007 finding 5c)
# job.json is written by seats, so its "rig" can't be trusted to route your decisions. In order:
#   1. The operator's launch record: <RIG_LAUNCHES_DIR>/<job>.json, written when the team is started:
#        {"job": "proto-2", "folder": "/home/<you>/openrig/jobs/proto-2", "rig": "proto-2", "lead": "proto-lead"}
#      Used only if its "folder" is this job's folder. Format in JOBS.md.
#   2. Otherwise the rig the console first saw for this job (pinned in state/job-pins.json). If job.json later
#      claims another rig, the pin wins and an alert says so.
LAUNCHES = os.path.expanduser(os.environ.get("RIG_LAUNCHES_DIR", "~/openrig/launches"))
PINS = os.path.join(STATE_DIR := os.path.expanduser(os.environ.get("RIG_STATE_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "state"))), "job-pins.json")
_pin_lock = threading.Lock()


def _launch(j):
    try:
        with open(os.path.join(LAUNCHES, j["name"] + ".json")) as f:
            rec = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(rec, dict) or not rec.get("rig") or not ID_RE.match(str(rec["rig"])):
        return None
    if os.path.realpath(os.path.expanduser(str(rec.get("folder") or ""))) != os.path.realpath(j["folder"]):
        return None
    lead = str(rec.get("lead") or "")
    seats = {}
    for seat, v in (rec.get("seats") or {}).items() if isinstance(rec.get("seats"), dict) else []:
        if SEAT_RE.match(str(seat)) and isinstance(v, dict):
            seats[str(seat)] = {k: str(v.get(k) or "")[:80] for k in ("runtime", "model", "version") if v.get(k)}
    return {"rig": str(rec["rig"]), "lead": lead if SEAT_RE.match(lead) else None, "seats": seats}


def _pins():
    try:
        with open(PINS) as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def team_of(j):
    """{"rig", "lead", "source", "claimed"}: who works on this job, and how sure the console is."""
    rec = _launch(j)
    claimed = j.get("rig") if j.get("rig") and ID_RE.match(str(j.get("rig"))) else None
    if rec:
        return {**rec, "source": "launch record", "claimed": claimed}
    with _pin_lock:
        pins = _pins()
        key = os.path.realpath(j["folder"])
        if key not in pins and claimed:
            pins[key] = claimed
            os.makedirs(STATE_DIR, exist_ok=True)
            tmp = PINS + ".tmp"
            with open(tmp, "w") as f:
                json.dump(pins, f, indent=1)
            os.replace(tmp, PINS)
        pinned = pins.get(key)
    if not pinned:
        for r in S.jobs_list():
            if r["name"] == j["name"] and r.get("rig"):
                return {"rig": r["rig"], "lead": None, "source": "guessed from the folder name", "claimed": claimed}
        return {"rig": None, "lead": None, "source": "unknown", "claimed": claimed}
    return {"rig": pinned, "lead": None, "source": "first seen", "claimed": claimed}


def team_mismatches():
    """Jobs whose job.json now claims a different rig than the trusted one."""
    out = []
    for j in _jobs().values():
        t = team_of(j)
        if t["claimed"] and t["rig"] and t["claimed"] != t["rig"]:
            out.append({"job": j["name"], "rig": t["rig"], "claimed": t["claimed"], "source": t["source"]})
    return out


def launched_seats():
    """{rig: {seat: {"runtime", "model", "version"}}} from launch records (MA-010): which model the operator
    put in each seat. OpenRig's own snapshot has no model for most seats."""
    out = {}
    for j in _jobs().values():
        rec = _launch(j)
        if rec and rec.get("seats"):
            out.setdefault(rec["rig"], {}).update(rec["seats"])
    return out


def folder_of_rig(rig):
    """The job folder the operator's launch record ties to this rig, or None (PL-025: architects' reply files)."""
    for j in _jobs().values():
        rec = _launch(j)
        if rec and rec["rig"] == rig:
            return j["folder"]
    return None


def _rig_for(j):
    return team_of(j)["rig"]


def _gate_files(j):
    out = []
    p = os.path.join(j["folder"], "gate.json")
    if os.path.isfile(p):
        out.append(p)
    d = os.path.join(j["folder"], "gates")
    if os.path.isdir(d):
        out += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".json")]
    return out


def _load_gate(j, path):
    try:
        with open(path) as f:
            g = json.load(f)
    except (OSError, ValueError) as e:
        return {"job": j["name"], "id": os.path.basename(path), "error": f"Can't read {os.path.basename(path)}: {e}"}
    if not isinstance(g, dict):
        return None
    gid = str(g.get("id") or ("gate" if os.path.basename(path) == "gate.json" else os.path.basename(path)[:-5]))
    if not ID_RE.match(gid):
        return None
    kind = "approve" if g.get("kind") == "approve" else "choose"
    opts = []
    for o in (g.get("options") or [])[:40]:
        if not isinstance(o, dict) or not ID_RE.match(str(o.get("id") or "")):
            continue
        opts.append({"id": str(o["id"]), "title": str(o.get("title") or o["id"])[:120],
                     "summary": str(o.get("summary") or "")[:2000],
                     "image": _url(j["name"], o.get("image")), "file": _url(j["name"], o.get("file")),
                     "play": _url(j["name"], (o.get("play") or "").rstrip("/") + "/index.html", "play") if o.get("play") else None})
    n = len(opts)
    play = str(g.get("play") or "")   # one build for the whole gate, e.g. a milestone (R-015)
    pick = g.get("pick")
    lo = int(pick if isinstance(pick, int) else g.get("min") or (1 if kind == "choose" else 0))
    hi = int(pick if isinstance(pick, int) else g.get("max") or max(n, 1))
    dec_path = os.path.join(j["folder"], "decisions", gid + ".json")
    decision = None
    if os.path.isfile(dec_path):
        try:
            with open(dec_path) as f:
                decision = json.load(f)
        except (OSError, ValueError):
            decision = {"error": "unreadable"}
    rig = _rig_for(j)
    lead = str(g.get("lead") or "")
    return {"job": j["name"], "job_type": j["type"], "rig": rig, "id": gid, "kind": kind,
            "title": str(g.get("title") or gid)[:140], "question": str(g.get("question") or "")[:2000],
            "context": _url(j["name"], g.get("context")) if g.get("context") else None,
            "play": _url(j["name"], play.rstrip("/") + "/index.html", "play") if play else None,
            "min": max(0, min(lo, n)) if kind == "choose" else 0, "max": max(1, min(hi, n or 1)),
            "options": opts, "lead": lead if SEAT_RE.match(lead) else None,
            "max_soft": kind == "choose" and g.get("max_soft") is True,   # R-001: may go over "max" with a confirm
            "decision": decision, "open": decision is None,
            "created": os.path.getmtime(path)}


def list_gates(include_decided=10):
    gates = []
    for j in _jobs().values():
        for p in _gate_files(j):
            g = _load_gate(j, p)
            if g:
                gates.append(g)
    open_ = sorted([g for g in gates if g.get("open")], key=lambda g: g.get("created", 0))
    done = sorted([g for g in gates if not g.get("open") and not g.get("error")],
                  key=lambda g: (g["decision"] or {}).get("decided_at", ""), reverse=True)[:include_decided]
    return {"open": open_, "decided": done, "errors": [g for g in gates if g.get("error")]}


def rig_cmd(rig_bin, *args):
    """The rig command as a list. RIG_BIN may carry a prefix, e.g. when the console runs as its own user:
    RIG_BIN="sudo -n -u <you> /usr/local/lib/rig-console/rig-owner" (R-005 step 3, option A; setup/rig-owner)."""
    return shlex.split(rig_bin) + list(args)


def _rig_seats(rig, rig_bin):
    """The rig's seat names from one `rig ps`, or None if that failed (never a guess)."""
    try:
        r = subprocess.run(rig_cmd(rig_bin, "ps", "--nodes", "-A", "--json"), capture_output=True, text=True, timeout=20)
        rows = json.loads(r.stdout or "[]")
        rows = rows if isinstance(rows, list) else rows.get("items") or rows.get("rows") or []
        return [x.get("canonicalSessionName") for x in rows if x.get("rigName") == rig]
    except Exception as e:
        print("rig ps for decision routing failed:", f"{type(e).__name__}: {e}"[:200], flush=True)
        return None


def _lead_session(g, rig_bin, names=None):
    """The seat to tell: g["lead"] if it's a seat in this job's rig, else a "*lead" seat."""
    rig = g.get("rig")
    names = names if names is not None else (_rig_seats(rig, rig_bin) if rig else None)
    if not names:
        return None
    # gate.json's "lead" is seat-written: only honour it if that seat really is in this job's rig,
    # so a gate can't route your decision to another team (MA-007 finding 5c).
    if g.get("lead") and f"{g['lead']}@{rig}" in names:
        return f"{g['lead']}@{rig}"
    return next((s for s in names if s and s.split("@")[0].endswith("lead") and not s.startswith("advisor")), None)


def tell_whom(g, rec, rig_bin):
    """The gate's own lead if it's a seat in the job's rig, else the launch record's lead, else a *lead seat.
    One `rig ps` for the whole choice: on 2026-10-13 a failed first call (7 s after a restart) let the
    fallback pick the launch record's lead although the gate named another seat. If `rig ps` fails twice,
    tell the gate's named lead (else the record's) unchecked, inside this job's rig: the rig comes from the
    launch record, so it can't reach another team, and telling the named seat beats telling nobody (Rig
    Architect, 08:50Z). Every choice is logged."""
    rig = g.get("rig")
    if not rig:
        return None
    names = _rig_seats(rig, rig_bin)
    if names is None:
        names = _rig_seats(rig, rig_bin)   # one retry
    if names is None:
        lead = g.get("lead") or (rec or {}).get("lead")
        who = f"{lead}@{rig}" if lead and SEAT_RE.match(str(lead)) else None
        print(f"decision {g.get('id')}: couldn't list team {rig}'s seats twice; telling the named lead unchecked -> {who}", flush=True)
        return who
    own = g.get("lead") and f"{g['lead']}@{rig}" in names and f"{g['lead']}@{rig}"
    who = own or _lead_session({**g, "lead": rec["lead"]} if rec and rec.get("lead") else g, rig_bin, names)
    print(f"decision {g.get('id')}: gate lead {g.get('lead')!r}, record lead {(rec or {}).get('lead')!r} -> {who}", flush=True)
    return who


def decide(job, gid, body, rig_bin):
    if not ID_RE.match(job or "") or not ID_RE.match(gid or ""):
        raise ValueError("Unknown gate")
    j = _jobs().get(job)
    if not j:
        raise ValueError("Unknown job")
    g = next((x for x in (_load_gate(j, p) for p in _gate_files(j)) if x and x.get("id") == gid), None)
    if not g or g.get("error"):
        raise ValueError("Unknown gate")
    if not g["open"]:
        raise ValueError("Already decided")
    note = str(body.get("note") or "")[:4000].strip()
    by_id = {o["id"]: o for o in g["options"]}
    closing = bool(body.get("close"))
    if closing:
        # Decided elsewhere (e.g. in chat) or the team is gone: close the gate without recording a choice.
        verdict, chosen = "closed", []
        note = note or "Closed by the user without a decision here (handled outside the console)."
    elif g["kind"] == "approve":
        verdict = body.get("verdict")
        if verdict not in ("approve", "send_back"):
            raise ValueError("Choose approve or send back")
        if verdict == "send_back" and not note:
            raise ValueError("Say what needs to change")
        chosen = []
    else:
        verdict = None
        chosen = [i for i in dict.fromkeys(body.get("chosen") or []) if i in by_id]
        over = g["max_soft"] and body.get("over_max") is True and len(chosen) > g["max"]
        if not (g["min"] <= len(chosen) <= g["max"] or (over and g["min"] <= len(chosen))):
            want = g["min"] if g["min"] == g["max"] else f"{g['min']}–{g['max']}"
            raise ValueError(f"Pick {want}")
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    record = {"job": job, "gate": gid, "title": g["title"], "kind": g["kind"], "decided_at": stamp,
              "decided_by": "user (Rig Console)", "chosen": chosen, "verdict": verdict, "note": note}
    if g["kind"] == "choose" and not closing and len(chosen) > g["max"]:
        record["over_max"], record["max"] = True, g["max"]
    ddir = os.path.join(j["folder"], "decisions")
    os.makedirs(ddir, exist_ok=True)
    # Text the team wrote (title, question, option titles) is quoted, never laid out as the user's own words:
    # a gate's question could otherwise contain a fake "## Notes from the user" (MA-007 finding 5b).
    quote = lambda t: "\n".join("> " + ln for ln in str(t).splitlines() or [""])
    lines = [f"# Decision on gate `{gid}`", "",
             f"Job `{job}`. Decided {stamp} by the user in Rig Console. The decision is the fields in `{gid}.json`;",
             "lines starting with > are quoted from the team's own gate, not written by the user.", "",
             "**The team's gate:**", quote(g["title"]), ""]
    if g["question"]:
        lines += [quote(g["question"]), ""]
    if closing:
        lines += ["**Closed without a decision in the console.** Don't act on this gate; follow the user's direct instructions."]
    elif g["kind"] == "approve":
        lines += ["**Verdict: APPROVED**" if verdict == "approve" else "**Verdict: SENT BACK for changes**"]
    else:
        flat = lambda t: " ".join(str(t).split()).lstrip("#")   # option titles are team text: one line, no headings
        if record.get("over_max"):
            lines += [f"**Over the maximum, on purpose:** the user picked {len(chosen)} where the gate allowed {g['max']}.", ""]
        lines += ["## Chosen, in the order picked"] + [f"{i}. `{c}`: {flat(by_id[c]['title'])}" for i, c in enumerate(chosen, 1)]
        rest = [o for o in g["options"] if o["id"] not in chosen]
        if rest:
            lines += ["", "## Not chosen"] + [f"- `{o['id']}`: {flat(o['title'])}" for o in rest]
    if note:
        lines += ["", "## Notes from the user", note]
    with open(os.path.join(ddir, gid + ".md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    tmp = os.path.join(ddir, f".{gid}.tmp")
    with open(tmp, "w") as f:
        json.dump(record, f, indent=2)
    os.replace(tmp, os.path.join(ddir, gid + ".json"))   # the .json appearing is what closes the gate
    record_decision(os.path.join(ddir, gid + ".json"))
    summary = "closed without deciding" if closing else ("approved" if verdict == "approve" else "sent back") if g["kind"] == "approve" else ", ".join(chosen)
    S._add_many([(datetime.now().timestamp(), "decision", g.get("rig"), None, None,
                  f"You decided “{g['title']}”: {summary}"[:300], None, job, json.dumps(record)[:4000])])
    # Who hears about it: the gate's own "lead" if that seat is in the job's rig (the rig itself comes from
    # the operator's launch record, so a gate can't route to another team), else the record's lead. In the
    # architects job each architect owns its gates; before this, every decision went to the record's lead.
    lead = tell_whom(g, _launch(j), rig_bin) if rig_bin and not closing else None
    sent = False
    if lead:
        msg = (f"The user decided gate '{g['title']}' for job {job}. Read {os.path.join(ddir, gid + '.md')} "
               f"(also {gid}.json) and continue from it.")
        try:
            sent = subprocess.run(rig_cmd(rig_bin, "send", lead, msg), capture_output=True, text=True, timeout=30).returncode == 0
        except Exception:
            sent = False
    # _record: the decision exactly as saved, for the owner's history (PL-071); serve.py strips it before replying.
    return {"saved": True, "decided_at": stamp, "lead": lead, "lead_notified": sent, "_record": record}


def _read_text(path, limit=200_000):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read(limit)
    except OSError:
        return ""


def _section(md, title):
    """Body of a '## <title>' section (title matched as a prefix, case-insensitive)."""
    m = re.search(r"^##\s+" + re.escape(title) + r"[^\n]*\n(.*?)(?=^##\s|\Z)", md, re.M | re.S | re.I)
    return m.group(1).strip() if m else ""


def _clean(t, n=600):
    t = re.sub(r"\s+", " ", re.sub(r"[*`]", "", str(t or ""))).strip()
    return t[:n]


def _build_info(j, name):
    """What a build is, for the Play page. Agent-written text: the page escapes all of it.
    Sources, first wins per field:
      1. <build folder>/build.json  {"title", "pitch", "controls", "judge", "bugs"}   (see JOBS.md)
      2. a gate option whose "play" points at this build (title, summary, image)
      3. specs/proto-spec-<name>.md or proto-spec-<name>.md ("# Proto spec: <id> <Title>", What it is, Controls)
      4. lead-summary.md ("## <name> <Title>" with Question / Couldn't judge / Known bugs / Watch out)
    """
    info = {}
    def put(k, v):
        if v and not info.get(k):
            info[k] = v
    folder = j["folder"]
    if ID_RE.match(name):
        try:
            with open(os.path.join(folder, "builds", name, "build.json")) as f:
                meta = json.load(f)
            if isinstance(meta, dict):
                for k in ("title", "pitch", "controls", "judge", "bugs"):
                    put(k, _clean(meta.get(k), 140 if k == "title" else 800))
        except (OSError, ValueError):
            pass
    for p in _gate_files(j):
        try:
            with open(p) as f:
                g = json.load(f)
        except (OSError, ValueError):
            continue
        for o in (g.get("options") or []) if isinstance(g, dict) else []:
            if isinstance(o, dict) and str(o.get("play") or "").rstrip("/") in (f"builds/{name}", name):
                put("title", _clean(o.get("title"), 140))
                put("pitch", _clean(o.get("summary"), 600))
                put("image", _url(j["name"], o.get("image")))
    for rel in (f"specs/proto-spec-{name}.md", f"proto-spec-{name}.md"):
        md = _read_text(os.path.join(folder, rel))
        if not md:
            continue
        m = re.search(r"^#\s*Proto spec:\s*\S+\s+(.+)$", md, re.M)
        put("title", _clean(m.group(1), 140) if m else "")
        put("pitch", _clean(_section(md, "What it is").split("\n\n")[0]))
        put("controls", _clean(_section(md, "Controls"), 800))
        info.setdefault("links", []).append({"label": "Spec", "url": _url(j["name"], rel)})
        break
    md = _read_text(os.path.join(folder, "lead-summary.md"))
    sec = re.search(r"^##\s+" + re.escape(name) + r"\b\s*(.*?)\n(.*?)(?=^##\s|\Z)", md, re.M | re.S) if md else None
    if sec:
        put("title", _clean(sec.group(1), 140))
        field = lambda k: next((_clean(re.sub(r"^-\s*\*\*[^*]+\*\*:?\s*", "", l)) for l in sec.group(2).splitlines()
                                if re.match(r"^- \*\*" + k, l, re.I)), "")
        put("question", field("Question"))
        put("judge", field("Couldn.t judge"))
        put("bugs", field("Known bugs"))
        put("watch", field("Watch out"))
        put("verdict", field("Lead"))
    rv = f"reviews/lead-{name}.md"
    if os.path.isfile(os.path.join(folder, rv)):
        info.setdefault("links", []).append({"label": "Lead's review", "url": _url(j["name"], rv)})
    info["links"] = [l for l in info.get("links", []) if l["url"]]
    return info


# ---------- Decision fingerprints (R-005 step 1)
# A gate closes when <job>/decisions/<id>.json exists, and seats can write files in their own job folder.
# So the console remembers a fingerprint of every decision file it writes, and flags any decision file it
# didn't write (or that changed after it wrote it). Files that existed before this check started are
# trusted once, as the baseline. This is detection, not prevention: a seat running as the same user could
# also edit the fingerprint file. Running the console as its own user (R-005 step 3) closes that.
STATE = os.path.expanduser(os.environ.get("RIG_STATE_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")))
FINGERPRINTS = os.path.join(STATE, "decision-fingerprints.json")
_fp_lock = threading.Lock()


def _sha(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def _fp_load():
    try:
        with open(FINGERPRINTS) as f:
            d = json.load(f)
        return d if isinstance(d, dict) and isinstance(d.get("files"), dict) else None
    except (OSError, ValueError):
        return None


def _fp_save(d):
    os.makedirs(STATE, exist_ok=True)
    tmp = FINGERPRINTS + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f, indent=1)
    os.replace(tmp, FINGERPRINTS)


def _decision_files():
    for j in _jobs().values():
        d = os.path.join(j["folder"], "decisions")
        if os.path.isdir(d):
            for fn in sorted(os.listdir(d)):
                if fn.endswith(".json") and ID_RE.match(fn[:-5]):
                    yield j["name"], fn[:-5], os.path.join(d, fn)


def record_decision(path):
    """Called right after the console writes a decision file."""
    with _fp_lock:
        d = _fp_load() or {"baseline_at": datetime.now().astimezone().isoformat(timespec="seconds"), "files": {}}
        d["files"][os.path.realpath(path)] = _sha(path)
        _fp_save(d)


def unverified_decisions():
    """Decision files the console didn't write, or that changed since it wrote them."""
    with _fp_lock:
        d = _fp_load()
        if d is None:   # first run: trust what's already there
            d = {"baseline_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                 "files": {os.path.realpath(p): _sha(p) for _, _, p in _decision_files()}}
            _fp_save(d)
            return []
    out = []
    for job, gid, p in _decision_files():
        known, now = d["files"].get(os.path.realpath(p)), _sha(p)
        if known == now:
            continue
        try:
            with open(p) as f:
                verdict = (json.load(f) or {}).get("verdict")
        except (OSError, ValueError, AttributeError):
            verdict = None
        out.append({"job": job, "gate": gid, "changed": known is not None, "closed": verdict == "closed"})
    return out


# ---------- The owner's inbox, "Needs you": small jobs and questions only the owner can do (R-018, PL-018/023)
# Architects post <TASKS_JOB>/tasks/<id>.json:
#   {"kind": "do"|"ask", "title", "action", "asked_by", "why"?, "blocks"?, "recommend"?, "details"?, "urgent"?}
# "do": run a command, restart something (Done / Won't do). "ask": missing information or a quick opinion
# (a free-text answer, or Skip). A task is open until the console writes decisions/task-<id>.json, the same
# rule as gates; the record keeps the whole card, so answered cards stay readable for RESOLVED_DAYS.
# Teams never post tasks, and a choice between options is always a gate, never a task.
TASKS_JOB = os.environ.get("RIG_TASKS_JOB", "architects")
ASKER_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}(@[A-Za-z0-9._-]{1,64})?$")
RESOLVED_DAYS = 14
RESULTS = {"do": ("done", "wont"), "ask": ("answered", "skipped")}


MAX_STEPS = 20


def _cut(s, n):
    """Card text, shortened visibly (…) rather than silently (Rig, 18:07Z: a cut recommend lost commands)."""
    s = str(s or "").strip()
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


def _steps(raw):
    """Owner steps (JOBS.md §4b): [{"where", "run" or "say", "check"}], in order. Malformed steps are dropped."""
    out = []
    for s in raw if isinstance(raw, list) else []:
        if not isinstance(s, dict) or not (str(s.get("run") or "").strip() or str(s.get("say") or "").strip()):
            continue
        run = str(s.get("run") or "").strip()
        if len(run) > 1000:   # a shortened command could still run and do something else: never show one
            run, s = "", {**s, "say": "This command is too long for a card; see Details."}
        out.append({"where": _cut(s.get("where"), 80), "run": run,
                    "say": _cut(s.get("say"), 400), "check": _cut(s.get("check"), 300)})
    return out[:MAX_STEPS]


def _task_dirs():
    j = _jobs().get(TASKS_JOB)
    return (os.path.join(j["folder"], "tasks"), os.path.join(j["folder"], "decisions")) if j else (None, None)


def resolved_tasks(now=None):
    """Answered cards from the last RESOLVED_DAYS, newest first."""
    _, ddir = _task_dirs()
    out, now = [], now or datetime.now().timestamp()
    try:
        names = [n for n in os.listdir(ddir) if n.startswith("task-") and n.endswith(".json")]
    except (OSError, TypeError):
        return out
    for n in names:
        p = os.path.join(ddir, n)
        try:
            if now - os.path.getmtime(p) > RESOLVED_DAYS * 86400:
                continue
            with open(p, encoding="utf-8") as f:
                r = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(r, dict) and r.get("task"):
            out.append({k: r.get(k) for k in ("task", "kind", "title", "action", "why", "blocks", "recommend", "steps", "asked_by",
                                              "result", "answer", "note", "decided_at")})
    return sorted(out, key=lambda r: r.get("decided_at") or "", reverse=True)


def list_tasks():
    j = _jobs().get(TASKS_JOB)
    if not j:
        return []
    tdir, ddir = os.path.join(j["folder"], "tasks"), os.path.join(j["folder"], "decisions")
    out = []
    try:
        names = sorted(os.listdir(tdir))
    except OSError:
        return out
    for fn in names:
        tid = fn[:-5]
        if not fn.endswith(".json") or not ID_RE.match(tid) or os.path.exists(os.path.join(ddir, f"task-{tid}.json")):
            continue
        try:
            with open(os.path.join(tdir, fn), encoding="utf-8") as f:
                t = json.load(f)
        except (OSError, ValueError):
            t = None
        if not isinstance(t, dict) or not str(t.get("title") or "").strip() or not str(t.get("action") or "").strip():
            out.append({"id": tid, "error": f'tasks/{fn} needs a "title" and an "action"'})
            continue
        asker = str(t.get("asked_by") or "")
        details = str(t.get("details") or "")[:300]
        out.append({"id": tid, "job": TASKS_JOB, "kind": "ask" if t.get("kind") == "ask" else "do",
                    "title": _cut(t["title"], 100), "action": _cut(t["action"], 600),
                    "why": _cut(t.get("why"), 400), "blocks": _cut(t.get("blocks"), 300),
                    "recommend": _cut(t.get("recommend"), 1000), "steps": _steps(t.get("steps")),
                    "asked_by": asker if ASKER_RE.match(asker) else "", "urgent": t.get("urgent") is True,
                    "details": details, "details_url": _url(TASKS_JOB, details),
                    "created": os.path.getmtime(os.path.join(tdir, fn))})
    # Architects update an open card instead of adding another; flag any that slip through.
    titles = {}
    for t in out:
        if not t.get("error"):
            titles.setdefault(t["title"].strip().lower(), []).append(t)
    for same in titles.values():
        for t in same:
            t["duplicate"] = len(same) > 1
    return out


def answer_task(tid, body):
    """The owner's answer: Done / Won't do for "do", a free-text answer or Skip for "ask".
    Returns the record and who to tell."""
    t = next((x for x in list_tasks() if x["id"] == tid and not x.get("error")), None)
    if not t:
        raise ValueError("That card is already answered or gone")
    result = body.get("result")
    if result not in RESULTS[t["kind"]]:
        raise ValueError("Answer it, or Skip" if t["kind"] == "ask" else "Choose Done or Won't do")
    answer = str(body.get("answer") or "")[:4000].strip()
    if result == "answered" and not answer:
        raise ValueError("Write your answer first, or Skip")
    note = str(body.get("note") or "")[:2000].strip()
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    record = {"job": TASKS_JOB, "task": tid, **{k: t[k] for k in ("kind", "title", "action", "why", "blocks", "recommend", "steps", "asked_by")},
              "result": result, "answer": answer, "note": note, "decided_at": stamp, "decided_by": "user (Rig Console)"}
    ddir = os.path.join(_jobs()[TASKS_JOB]["folder"], "decisions")
    os.makedirs(ddir, exist_ok=True)
    quote = lambda s: "\n".join("> " + ln for ln in str(s).splitlines() or [""])
    label = {"done": "DONE", "wont": "WON’T DO", "answered": "ANSWERED", "skipped": "SKIPPED"}[result]
    lines = [f"# Card `{tid}`: {label}", "",
             f"Answered {stamp} by the user in Rig Console. The answer is the fields in `task-{tid}.json`;",
             "lines starting with > are quoted from the card as it was posted.", "", quote(t["title"]), quote(t["action"])]
    for i, s in enumerate(t.get("steps") or [], 1):
        lines.append(quote(f"{i}. [{s['where'] or 'step'}] {s['run'] or s['say']}" + (f" -- check: {s['check']}" if s["check"] else "")))
    if answer:
        lines += ["", "## The user's answer", answer]
    if note:
        lines += ["", "## Note from the user", note]
    with open(os.path.join(ddir, f"task-{tid}.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    tmp = os.path.join(ddir, f".task-{tid}.tmp")
    with open(tmp, "w") as f:
        json.dump(record, f, indent=2)
    path = os.path.join(ddir, f"task-{tid}.json")
    os.replace(tmp, path)   # the .json appearing is what closes the task
    record_decision(path)
    return record, t["asked_by"], path


def _builds_dir(j):
    """The job's builds folder: job.json "builds", but only builds/ or a folder inside it. job.json is
    team-written, so "builds": "decisions" (or ".") must not put other files on the builds port (MA-020)."""
    try:
        with open(os.path.join(j["folder"], "job.json")) as f:
            d = str((json.load(f) or {}).get("builds") or "builds")
    except (OSError, ValueError, AttributeError):
        return "builds"
    d = os.path.normpath(d)
    return d if d.split(os.sep)[0] == "builds" and not os.path.isabs(d) else "builds"


def build_file(job, rel):
    """rel (a path in the job folder) only if it lies inside the job's builds folder (_builds_dir).
    The builds port serves nothing else (MA-013, MA-020)."""
    j = _jobs().get(job)
    if not j:
        return None
    base, full = safe_path(job, _builds_dir(j)), safe_path(job, rel)
    return full if base and full and full.startswith(base + os.sep) else None


def list_builds():
    out = []
    for j in _jobs().values():
        base = safe_path(j["name"], _builds_dir(j))
        if not base or not os.path.isdir(base):
            continue
        cands = [("latest", base)] if os.path.isfile(os.path.join(base, "index.html")) else []
        cands += [(d, os.path.join(base, d)) for d in sorted(os.listdir(base))
                  if ID_RE.match(d) and os.path.isfile(os.path.join(base, d, "index.html"))]
        for name, folder in cands:
            files = [os.path.join(r, f) for r, _, fs in os.walk(folder) for f in fs]
            rel = os.path.relpath(folder, j["folder"])
            out.append({"job": j["name"], "job_type": j["type"], "name": name, "title": j["title"],
                        "info": _build_info(j, name if name != "latest" else ""),
                        "url": f"/go/play/{j['name']}/{rel}/index.html",
                        "updated": max((os.path.getmtime(f) for f in files), default=0),
                        "size_mb": round(sum(os.path.getsize(f) for f in files) / 1e6, 1)})
    return sorted(out, key=lambda b: b["updated"], reverse=True)
