"""One page per job (R-013, R-014, R-015, R-023; PL-034): what a team is doing and making, in one place.

Read-only. Everything comes from the job folder (team-written: shown as plain text by the page, files linked
through the console's sandboxed /job/ route) or from trusted records (launch record, gates, the queue snapshot).
Tabs: Overview (decisions, milestones, builds), Docs (R-014), Assets (R-013), Docket (R-023, architects only).
"""
import json, os, re
from datetime import datetime, timezone

import gates as G

IMG = (".png", ".jpg", ".jpeg", ".webp", ".gif")
AUDIO = (".ogg", ".wav", ".mp3")
VIDEO = (".webm", ".mp4")
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{3,8}$")
MAX_ASSETS = 400
MAX_DOCS = 120


def _job(name):
    j = G._jobs().get(name)
    if not j:
        raise ValueError("Unknown job")
    return j


def _read_json(j, rel, limit=2_000_000):
    p = G.safe_path(j["name"], rel)
    if not p or not os.path.isfile(p) or os.path.islink(p) or os.path.getsize(p) > limit:
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _read_text(j, rel, limit=200_000):
    p = G.safe_path(j["name"], rel)
    if not p or not os.path.isfile(p) or os.path.islink(p):
        return ""
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read(limit)
    except OSError:
        return ""


def _s(v, n=300):
    return str(v)[:n] if v is not None else ""


def _link(j, rel):
    return G._url(j["name"], rel) if isinstance(rel, str) and rel else None


# ---------- Overview
def _milestones(j):
    d = _read_json(j, "milestones.json")
    if not isinstance(d, dict) or not isinstance(d.get("milestones"), list):
        return None
    out = []
    for m in d["milestones"][:40]:
        if not isinstance(m, dict):
            continue
        tests = m.get("tests") if isinstance(m.get("tests"), dict) else {}
        qb = m.get("quality_bar") if isinstance(m.get("quality_bar"), dict) else {}
        num = lambda v: v if isinstance(v, int) and v >= 0 else 0
        out.append({"id": _s(m.get("id"), 40), "title": _s(m.get("title"), 120), "status": _s(m.get("status"), 30),
                    "plan": _link(j, m.get("plan")), "packet": _link(j, m.get("packet")),
                    "download": _link(j, m.get("download")),
                    "play": f"/go/play/{j['name']}/{m['build'].strip('/')}/index.html"
                            if isinstance(m.get("build"), str) and G.build_file(j["name"], m["build"].strip("/") + "/index.html") else None,
                    "tests": {"passed": num(tests.get("passed")), "failed": num(tests.get("failed")), "at": _s(tests.get("at"), 40)},
                    "quality_bar": {k: num(qb.get(k)) for k in ("pass", "fail", "not_yet")},
                    "exploits_open": num(m.get("exploits_open")),
                    "vision_check": m.get("vision_check") if m.get("vision_check") in ("PASS", "FAIL") else None,
                    "gate": _s(m.get("gate"), 64) or None})
    return {"game": _s(d.get("game"), 120), "milestones": out}


def overview(name):
    j = _job(name)
    meta = _read_json(j, "job.json") or {}
    team = G.team_of(j)
    gates = G.list_gates(50)
    mine = lambda g: g.get("job") == name
    return {
        "job": name, "title": _s(meta.get("title") or j.get("title") or name, 140), "type": _s(meta.get("type") or j.get("type"), 40),
        "team": {"rig": team.get("rig"), "lead": team.get("lead"), "source": team.get("source")},
        "open_gates": [{"id": g["id"], "title": _s(g.get("title"), 140), "kind": g.get("kind")} for g in gates["open"] if mine(g)],
        "decided": [{"id": g["id"], "title": _s(g.get("title"), 140), "at": (g.get("decision") or {}).get("decided_at")}
                    for g in gates["decided"] if mine(g)][:8],
        "builds": [{"name": b["name"], "url": b["url"], "updated": b["updated"], "size_mb": b["size_mb"],
                    "title": _s((b.get("info") or {}).get("title"), 120)} for b in G.list_builds() if b["job"] == name],
        "milestones": _milestones(j),
        # The lead's end-of-run model notes (SHARED-RULES §6), kept in the job folder: linked from the Report tab.
        "model_files": [{"name": f, "url": u} for f in ("model-notes.jsonl", "model-metrics.csv") if (u := _link(j, f))],
        "tabs": {"docs": bool(docs(name)["groups"]), "assets": bool(assets(name)["items"]),
                 "report": bool(team.get("rig")), "docket": name == G.TASKS_JOB},
    }


# ---------- Docs (R-014): the design package in the order of docs/handoff.md, palette swatches, inbox by status
def _title(j, rel):
    for ln in _read_text(j, rel, 4000).splitlines():
        m = re.match(r"^#\s+(.+)", ln)
        if m:
            return m.group(1).strip()[:120]
    return os.path.basename(rel)


def _front(text):
    """YAML-ish front matter: key: value lines between --- fences."""
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    out = {}
    for ln in (m.group(1).splitlines() if m else []):
        k, _, v = ln.partition(":")
        if k.strip():
            out[k.strip().lower()] = v.strip()[:200]
    return out


def _palette(j):
    d = _read_json(j, "art/bible/palette.json")
    if isinstance(d, dict) and isinstance(d.get("source"), str) and not d.get("roles") and not d.get("colors"):
        d = _read_json(j, d["source"])   # a pointer file (bridge-design): follow it once, inside the job
    if not isinstance(d, dict):
        return []
    src = d.get("roles") or d.get("colors") or d
    if isinstance(src, list):
        pairs = [(c.get("name"), c.get("hex")) for c in src if isinstance(c, dict)]
    elif isinstance(src, dict):
        pairs = list(src.items())
    else:
        pairs = []
    return [{"name": _s(n, 60), "hex": h} for n, h in pairs if isinstance(h, str) and HEX_RE.match(h)][:80]


def docs(name):
    j = _job(name)
    base = G.safe_path(name, "docs")
    files = sorted(f for f in os.listdir(base) if f.endswith(".md")) if base and os.path.isdir(base) else []
    handoff = _read_text(j, "docs/handoff.md")
    order = ["handoff.md"] if handoff and "handoff.md" in files else []   # the guide comes first, then what it lists
    for ref in re.findall(r"(?:`|\()(?:docs/)?([\w.-]+\.md)(?:`|\))", handoff):   # handoff order first (R-014)
        if ref in files and ref not in order:
            order.append(ref)
    order += [f for f in files if f not in order]
    groups = []
    if order:
        groups.append({"name": "Design package" if handoff else "Docs",
                       "docs": [{"path": f"docs/{f}", "title": _title(j, f"docs/{f}"), "url": _link(j, f"docs/{f}")} for f in order[:MAX_DOCS]]})
    top = [f for f in ("brief.md", "README.md") if G.safe_path(name, f) and os.path.isfile(G.safe_path(name, f))]
    if top:
        groups.append({"name": "The job", "docs": [{"path": f, "title": _title(j, f), "url": _link(j, f)} for f in top]})
    inbox = []
    ibase = G.safe_path(name, "inbox")
    for sub in (sorted(os.listdir(ibase)) if ibase and os.path.isdir(ibase) else []):
        sdir = os.path.join(ibase, sub)
        if not os.path.isdir(sdir) or os.path.islink(sdir):
            continue
        for f in sorted(os.listdir(sdir))[-200:]:
            if not f.endswith(".md"):
                continue
            rel = f"inbox/{sub}/{f}"
            fm = _front(_read_text(j, rel, 3000))
            inbox.append({"id": fm.get("id") or f[:-3], "title": fm.get("title") or f[:-3], "status": (fm.get("status") or "open").lower()[:30],
                          "by": fm.get("by", ""), "opened": fm.get("opened", ""), "kind": fm.get("kind") or sub, "url": _link(j, rel)})
    return {"job": name, "groups": groups, "palette": _palette(j), "inbox": inbox}


# ---------- Docket (R-023): each architect's work, from live queue rows, open gates and Needs you cards only
ACTIVE = ("pending", "in-progress", "blocked")


def _ts(iso):
    try:
        return datetime.fromisoformat(str(iso).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _rows(raw):
    rows = raw.get("items", raw) if isinstance(raw, dict) else raw
    return [r for r in rows or [] if isinstance(r, dict) and r.get("qitemId")]


def docket(ps, queue_full, queue_compact, snap_mtime, tasks, now=None):
    """ps: _ps.json rows; queue_full: _queue_active.json (has summaries) or None; queue_compact: _queue.json rows;
    snap_mtime: when the queue snapshot was written; tasks: open Needs you cards."""
    now = now or datetime.now(timezone.utc).timestamp()
    rig = G.TASKS_JOB
    seats = sorted({r.get("canonicalSessionName") for r in ps if (r.get("canonicalSessionName") or "").endswith("@" + rig)})
    full = queue_full is not None
    rows = _rows(queue_full) if full else [r for r in _rows(queue_compact) if r.get("state") in ACTIVE]
    if not rows and queue_full is None and not queue_compact:
        return {"error": "Couldn't read the queue, so the docket can't be shown.", "seats": []}
    # OpenRig's stuck sweep files a recovery row per stuck item: show it as a mark on that item, not as work.
    stalled, recoveries = set(), set()
    for r in rows:
        for t in r.get("tags") or []:
            if t.startswith("stuck-sweep:"):
                recoveries.add(r["qitemId"])
                stalled.add(t.rsplit(":", 1)[-1])
    def line(r, peer=None):
        return {"id": r["qitemId"], "summary": _s(r.get("summary"), 200) if full else "",
                "state": r.get("state"), "age_s": int(now - (_ts(r.get("tsCreated")) or now)),
                "not_delivered": str(r.get("lastNudgeResult") or "").startswith("failed") and r.get("state") == "pending",
                "stalled": r["qitemId"] in stalled, "peer": peer, "blocked_on": _s(r.get("blockedOn"), 120) or None,
                "body": _s(r.get("body"), 2000) if full else ""}
    work = [r for r in rows if r["qitemId"] not in recoveries and r.get("state") in ACTIVE]
    gates = G.list_gates(0)["open"]
    out = []
    for s in seats:
        member = s.split("@")[0]
        mine_in = [r for r in work if r.get("destinationSession") == s]
        out.append({"seat": s,
                    "working": [line(r) for r in mine_in if r.get("state") == "in-progress"],
                    "next": [line(r) for r in mine_in if r.get("state") == "pending"],
                    "waiting_owner": [{"kind": "decision", "title": _s(g.get("title"), 140), "url": f"/decide.html?job={g['job']}&gate={g['id']}"}
                                      for g in gates if g.get("job") == rig and g.get("lead") in (member, s)]
                                     + [{"kind": "card", "title": _s(t.get("title"), 100), "url": "/needs.html"}
                                        for t in tasks if t.get("asked_by") in (s, member)],
                    "waiting_others": [line(r, r.get("destinationSession")) for r in work
                                       if r.get("sourceSession") == s and r.get("destinationSession") != s]
                                      + [line(r, r.get("blockedOn")) for r in mine_in if r.get("state") == "blocked"]})
    return {"seats": out, "summaries": full, "snapshot_at": snap_mtime}


# ---------- Assets (R-013): the manifest when there is one, else a scan of the art, audio and model folders
def _kind(path):
    p = path.lower()
    return "image" if p.endswith(IMG) else "audio" if p.endswith(AUDIO) else "video" if p.endswith(VIDEO) else None


def assets(name):
    j = _job(name)
    man = _read_json(j, "assets/manifest.json")
    items = []
    if isinstance(man, dict) and isinstance(man.get("assets"), list):
        for a in man["assets"][:MAX_ASSETS]:
            if not isinstance(a, dict) or not isinstance(a.get("file"), str):
                continue
            prev = a.get("preview") or a.get("model_preview") or a.get("file")
            items.append({"id": _s(a.get("id"), 80), "title": _s(a.get("title") or a.get("id"), 120), "type": _s(a.get("type"), 30),
                          "set": _s(a.get("set"), 60), "status": _s(a.get("status"), 30), "route": _s(a.get("route"), 40),
                          "ai_made": a.get("ai_made") is True, "licence": _s(a.get("licence"), 120), "by": _s(a.get("by"), 60),
                          "file": _link(j, a["file"]), "preview": _link(j, prev) if isinstance(prev, str) else None,
                          "media": _kind(prev if isinstance(prev, str) else a["file"]) or _kind(a["file"]),
                          "notes": _s(a.get("notes"), 400)})
        return {"job": name, "source": "manifest", "items": items}
    for root_rel in ("art", "audio", "models", "assets"):
        base = G.safe_path(name, root_rel)
        if not base or not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            dirs[:] = sorted(d for d in dirs if not d.startswith(".") and not os.path.islink(os.path.join(root, d)))
            for f in sorted(files):
                full = os.path.join(root, f)
                if os.path.islink(full) or not _kind(f):
                    continue
                rel = os.path.relpath(full, os.path.realpath(j["folder"]))
                items.append({"id": rel, "title": f, "type": _kind(f), "set": os.path.relpath(root, base) if root != base else root_rel,
                              "status": "", "file": _link(j, rel), "preview": _link(j, rel), "media": _kind(f),
                              "ai_made": None, "updated": os.path.getmtime(full)})
                if len(items) >= MAX_ASSETS:
                    return {"job": name, "source": "scan", "items": items, "capped": True}
    return {"job": name, "source": "scan", "items": items}
