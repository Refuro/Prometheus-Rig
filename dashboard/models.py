"""Model report cards, read-only, for the Models page (/api/models).

The Model Architect owns the files in models/ (ROLES.md). The console only reads them:
  cards/<model>--<role>.md   one report card per model and seat role
  <model>.md                 what held across roles, per model
  observations.jsonl         the evidence ledger, one JSON object per line
  metrics.csv                one row per seat per run
  roles/*.md                 assessments of the architects and the operator
  BRIEFS.md, ROUTING.md      briefs graded by effect; the routing guide

Leads don't write into models/. They write model-notes.jsonl in their own job folder (SHARED-RULES §6,
format in models/HARVEST.md); lines not yet harvested into the ledger show here as "not yet reviewed".

Override the folder with RIG_MODELS_DIR. Nothing here writes.
"""
import csv, glob, hashlib, io, json, os

import store as S

DIR = os.path.expanduser(os.environ.get("RIG_MODELS_DIR",
                                        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models")))
MAX_BYTES = 2_000_000


def _read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read(MAX_BYTES)
    except OSError:
        return None


def _model_id(m):
    # The ledger writes "gemma4:12b"; card files can't contain ":", so they use "gemma4-12b".
    return str(m or "").strip().lower().replace(":", "-")


def _observations():
    text, out, skipped = _read(os.path.join(DIR, "observations.jsonl")) or "", [], 0
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            o = json.loads(line)
        except ValueError:
            skipped += 1
            continue
        if not isinstance(o, dict) or not o.get("id"):
            skipped += 1
            continue
        o["model"] = _model_id(o.get("model"))
        out.append(o)
    return out, skipped


REVIEW_RE = __import__("re").compile(r"^[a-z0-9][a-z0-9-]{0,39}$")


def review(rid):
    """The Model Architect's report for one game or run: models/reviews/<rid>/report.md and nothing else
    (owner, 2026-10-14: make the Diplomacy analysis findable without exposing the rest of models/)."""
    if not REVIEW_RE.match(str(rid or "")):
        raise ValueError("Unknown review")
    # Every step is opened without following links: a link at reviews/ or reviews/<id>/ could otherwise point
    # anywhere the console can read (review-1 finding 2). Folders are opened O_PATH, so a pass-through folder
    # still works (PL-040).
    fds = []
    try:
        fds.append(os.open(DIR, os.O_PATH | os.O_DIRECTORY))
        for part in ("reviews", rid):
            fds.append(os.open(part, os.O_PATH | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fds[-1]))
        # O_NONBLOCK: a FIFO planted as report.md would otherwise block this open until a writer came (review-2).
        fd = os.open("report.md", os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fds[-1])
    except OSError:
        return {"id": rid, "text": None}
    finally:
        for d in fds:
            os.close(d)
    # Check the raw descriptor first, and close it on every refusal: a directory used to make fdopen raise
    # and leak it (review-2).
    try:
        if not __import__("stat").S_ISREG(os.fstat(fd).st_mode):
            os.close(fd)
            return {"id": rid, "text": None}
        f = os.fdopen(fd, "rb")
    except OSError:
        os.close(fd)
        return {"id": rid, "text": None}
    with f:
        return {"id": rid, "text": f.read(MAX_BYTES).decode("utf-8", errors="replace")}


def _metrics():
    text = _read(os.path.join(DIR, "metrics.csv"))
    if not text:
        return []
    try:
        rows = list(csv.DictReader(io.StringIO(text)))
    except csv.Error:
        return []
    for r in rows:
        r["model_id"] = _model_id((r.get("model") or "").split(" ")[0])
    return rows


def _notes(observations, limit=200):
    """Leads' end-of-run notes still sitting in job folders (model-notes.jsonl, SHARED-RULES §6, PD-015),
    i.e. not yet harvested into the ledger by the Model Architect. Newest files first."""
    # A note is harvested when a ledger line carries its harvest_hash (models/HARVEST.md, MA-009):
    # sha1(job folder name + "\x1f" + the note line, whitespace-trimmed), hex, first 16 characters.
    harvested = {o.get("harvest_hash") for o in observations if o.get("harvest_hash")}
    out = []
    jobs = sorted(S.discover_jobs(), key=lambda j: -_mtime(os.path.join(j["folder"], "model-notes.jsonl")))
    for j in jobs:
        text = _read(os.path.join(j["folder"], "model-notes.jsonl"))
        if not text:
            continue
        ts = _mtime(os.path.join(j["folder"], "model-notes.jsonl"))
        for line in text.splitlines():
            try:
                n = json.loads(line)
            except ValueError:
                continue
            hh = hashlib.sha1((os.path.basename(j["folder"].rstrip(os.sep)) + "\x1f" + line.strip()).encode()).hexdigest()[:16]
            if not isinstance(n, dict) or hh in harvested:
                continue
            n["harvest_hash"] = hh
            n["job"], n["ts"], n["model"] = j["name"], ts, _model_id(n.get("model"))
            out.append(n)
            if len(out) >= limit:
                return out
    return out


def _mtime(p):
    try:
        return os.path.getmtime(p)
    except OSError:
        return 0


def _launched():
    """Which model the operator put in each seat, from launch records (MA-010, MA-013)."""
    try:
        import gates as G
        return G.launched_seats()
    except Exception:
        return {}


def load():
    if not os.path.isdir(DIR):
        return {"missing": True, "dir": os.path.basename(DIR.rstrip(os.sep))}
    cards, newest = [], 0
    for f in sorted(glob.glob(os.path.join(DIR, "cards", "*.md"))):
        name = os.path.basename(f)[:-3]
        if "--" not in name:
            continue
        model, role = name.split("--", 1)
        md = _read(f)
        if md is None:
            continue
        newest = max(newest, os.path.getmtime(f))
        cards.append({"file": "cards/" + os.path.basename(f), "model": _model_id(model),
                      "role": role.replace("-", " "), "md": md})
    summaries = {}
    for m in sorted({c["model"] for c in cards}):
        md = _read(os.path.join(DIR, m + ".md"))
        if md is not None:
            summaries[m] = md
    roles = []
    for f in sorted(glob.glob(os.path.join(DIR, "roles", "*.md"))):
        md = _read(f)
        if md is not None:
            roles.append({"file": "roles/" + os.path.basename(f), "role": os.path.basename(f)[:-3].replace("-", " "), "md": md})
    obs, skipped = _observations()
    for p in ("observations.jsonl", "metrics.csv", "ROUTING.md", "BRIEFS.md"):
        try:
            newest = max(newest, os.path.getmtime(os.path.join(DIR, p)))
        except OSError:
            pass
    return {"cards": cards, "summaries": summaries, "observations": obs, "skipped_lines": skipped,
            "metrics": _metrics(), "roles": roles, "briefs": _read(os.path.join(DIR, "BRIEFS.md")) or "",
            "routing": _read(os.path.join(DIR, "ROUTING.md")) or "", "notes": _notes(obs), "launched": _launched(), "updated": newest}
