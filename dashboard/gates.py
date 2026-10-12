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
"builds" in job.json) is playable at /play/<job>/<build>/. Godot web exports work as-is:
the server sends the isolation headers Godot 4 needs.
"""
import json, os, re, subprocess
from datetime import datetime

import store as S

ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
SEAT_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def _jobs():
    return {j["name"]: j for j in S.discover_jobs() if ID_RE.match(j["name"])}


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
    return f"/{kind}/{job}/{rel.lstrip('/')}" if full and os.path.exists(full) else None


def _rig_for(j):
    if j.get("rig"):
        return j["rig"]
    for r in S.jobs_list():
        if r["name"] == j["name"] and r.get("rig"):
            return r["rig"]
    return None


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
            "min": max(0, min(lo, n)) if kind == "choose" else 0, "max": max(1, min(hi, n or 1)),
            "options": opts, "lead": lead if SEAT_RE.match(lead) else None,
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


def _lead_session(g, rig_bin):
    rig = g.get("rig")
    if not rig:
        return None
    if g.get("lead"):
        return f"{g['lead']}@{rig}"
    try:
        r = subprocess.run([rig_bin, "ps", "--nodes", "-A", "--json"], capture_output=True, text=True, timeout=20)
        rows = json.loads(r.stdout or "[]")
        rows = rows if isinstance(rows, list) else rows.get("items") or rows.get("rows") or []
        names = [x.get("canonicalSessionName") for x in rows if x.get("rigName") == rig]
        lead = next((s for s in names if s and s.split("@")[0].endswith("lead") and not s.startswith("advisor")), None)
        return lead
    except Exception:
        return None


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
        if not (g["min"] <= len(chosen) <= g["max"]):
            want = g["min"] if g["min"] == g["max"] else f"{g['min']}–{g['max']}"
            raise ValueError(f"Pick {want}")
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    record = {"job": job, "gate": gid, "title": g["title"], "kind": g["kind"], "decided_at": stamp,
              "decided_by": "user (Rig Console)", "chosen": chosen, "verdict": verdict, "note": note}
    ddir = os.path.join(j["folder"], "decisions")
    os.makedirs(ddir, exist_ok=True)
    lines = [f"# Decision: {g['title']}", "", f"Job `{job}`, gate `{gid}`. Decided {stamp} by the user in Rig Console.", ""]
    if g["question"]:
        lines += [f"**Question:** {g['question']}", ""]
    if closing:
        lines += ["**Closed without a decision in the console.** Don't act on this gate; follow the user's direct instructions."]
    elif g["kind"] == "approve":
        lines += ["**Verdict: APPROVED**" if verdict == "approve" else "**Verdict: SENT BACK for changes**"]
    else:
        lines += ["## Chosen, in the order picked"] + [f"{i}. **{by_id[c]['title']}** (`{c}`)" for i, c in enumerate(chosen, 1)]
        rest = [o for o in g["options"] if o["id"] not in chosen]
        if rest:
            lines += ["", "## Not chosen"] + [f"- {o['title']} (`{o['id']}`)" for o in rest]
    if note:
        lines += ["", "## Notes from the user", note]
    with open(os.path.join(ddir, gid + ".md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    tmp = os.path.join(ddir, f".{gid}.tmp")
    with open(tmp, "w") as f:
        json.dump(record, f, indent=2)
    os.replace(tmp, os.path.join(ddir, gid + ".json"))   # the .json appearing is what closes the gate
    summary = "closed without deciding" if closing else ("approved" if verdict == "approve" else "sent back") if g["kind"] == "approve" else ", ".join(chosen)
    S._add_many([(datetime.now().timestamp(), "decision", g.get("rig"), None, None,
                  f"You decided “{g['title']}”: {summary}"[:300], None, job, json.dumps(record)[:4000])])
    lead, sent = (_lead_session(g, rig_bin) if rig_bin and not closing else None), False
    if lead:
        msg = (f"The user decided gate '{g['title']}' for job {job}. Read {os.path.join(ddir, gid + '.md')} "
               f"(also {gid}.json) and continue from it.")
        try:
            sent = subprocess.run([rig_bin, "send", lead, msg], capture_output=True, text=True, timeout=30).returncode == 0
        except Exception:
            sent = False
    return {"saved": True, "decided_at": stamp, "lead": lead, "lead_notified": sent}


def list_builds():
    out = []
    for j in _jobs().values():
        meta_dir = "builds"
        try:
            with open(os.path.join(j["folder"], "job.json")) as f:
                meta_dir = (json.load(f) or {}).get("builds") or "builds"
        except (OSError, ValueError):
            pass
        base = safe_path(j["name"], meta_dir)
        if not base or not os.path.isdir(base):
            continue
        cands = [("latest", base)] if os.path.isfile(os.path.join(base, "index.html")) else []
        cands += [(d, os.path.join(base, d)) for d in sorted(os.listdir(base))
                  if ID_RE.match(d) and os.path.isfile(os.path.join(base, d, "index.html"))]
        for name, folder in cands:
            files = [os.path.join(r, f) for r, _, fs in os.walk(folder) for f in fs]
            rel = os.path.relpath(folder, j["folder"])
            out.append({"job": j["name"], "job_type": j["type"], "name": name, "title": j["title"],
                        "url": f"/play/{j['name']}/{rel}/index.html",
                        "updated": max((os.path.getmtime(f) for f in files), default=0),
                        "size_mb": round(sum(os.path.getsize(f) for f in files) / 1e6, 1)})
    return sorted(out, key=lambda b: b["updated"], reverse=True)
