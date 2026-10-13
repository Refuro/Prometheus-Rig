"""The operator's log, read-only (R-022, PL-031).

The operator appends to <RIG_OPERATOR_DIR>/log-YYYY-MM.md (format: README.md beside it, owned by the Rig
Architect): a "## YYYY-MM-DD" heading per UTC day, then lines "- HH:MMZ · kind · sentence · ref: evidence".
It's agent-written: the page shows it as plain text, and nothing here notifies or counts anything.
"""
import os, re

DIR = os.path.expanduser(os.environ.get("RIG_OPERATOR_DIR", "~/openrig/operator"))
FILE_RE = re.compile(r"^log-(\d{4}-\d{2})\.md$")
LINE_RE = re.compile(r"^-\s*(\d{1,2}:\d{2}Z?)\s*·\s*([a-z-]{1,20})\s*·\s*(.*?)(?:\s*·\s*ref:\s*(.*))?$")
MAX_BYTES = 2_000_000


def months():
    try:
        return sorted((m.group(1) for m in map(FILE_RE.match, os.listdir(DIR)) if m), reverse=True)
    except OSError:
        return []


def read(month=None):
    """{"month", "months", "days": [{"day", "entries": [{"time", "kind", "text", "ref"} or {"text"}]}]},
    newest day first and newest entry first."""
    ms = months()
    month = month if month in ms else (ms[0] if ms else None)
    out = {"month": month, "months": ms, "days": []}
    if not month:
        return out
    p = os.path.join(DIR, f"log-{month}.md")
    try:
        if os.path.islink(p) or os.path.getsize(p) > MAX_BYTES:
            return {**out, "error": "The log file is too big or not a plain file"}
        with open(p, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except OSError:
        return out
    day = None
    for ln in lines:
        h = re.match(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$", ln)
        if h:
            day = {"day": h.group(1), "entries": []}
            out["days"].append(day)
            continue
        if not ln.startswith("-") or day is None:
            continue
        m = LINE_RE.match(ln.strip())
        e = ({"time": m.group(1), "kind": m.group(2), "text": m.group(3)[:600], "ref": (m.group(4) or "")[:300]}
             if m else {"text": ln.lstrip("- ").strip()[:600]})   # off-format lines are shown as they are
        day["entries"].append(e)
    for d in out["days"]:
        d["entries"].reverse()
    out["days"].reverse()
    return out
