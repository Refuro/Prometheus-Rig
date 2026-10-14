"""The daily digest, layer 1 (R-026): one page per UTC day from data the console already reads. Read-only.

  decisions     gates opened and decided that day (gates.list_gates)
  to-dos        Needs you cards that appeared that day
  log entries   architecture-log headings that carry the day's date, per architect (seatprofile.ROLES)
  operator      the operator log's entries that day, counted by kind; `held` and `incident` lines quoted
  lounge        the architects' posts that day
  activity      handoffs done, approval waits, busiest teams, new teams (store.since_summary)

Everything here is agents' text going to the page as data; the page escapes it. Days are UTC, as the
operator log's are. Layer 2 (a seat writes ten lines) comes later.
"""
import re
from datetime import datetime, timedelta, timezone

import gates as G
import lounge as LG
import oplog as OL
import seatprofile as PR
import store as S

DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _bounds(day):
    d = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return d.timestamp(), (d + timedelta(days=1)).timestamp()


def _epoch(iso):
    """A decision's decided_at is local time with an offset (gates.py writes astimezone()), so compare it as an
    instant, not by its first ten characters (review-1 finding 3). No offset: read as UTC. Unreadable: never."""
    try:
        t = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    except ValueError:
        return -1
    return (t if t.tzinfo else t.replace(tzinfo=timezone.utc)).timestamp()


def days(n=14):
    today = datetime.now(timezone.utc).date()
    return [(today - timedelta(days=i)).isoformat() for i in range(n)]


def build(day=None):
    day = day or days(1)[0]
    if not DAY_RE.match(str(day)):
        raise ValueError("day must be YYYY-MM-DD")
    start, end = _bounds(day)
    g = G.list_gates(500)
    opened = [x for x in g["open"] + g["decided"] if start <= (x.get("created") or 0) < end]
    decided = [x for x in g["decided"] if start <= _epoch((x.get("decision") or {}).get("decided_at")) < end]
    gate = lambda x: {"title": str(x.get("title") or "")[:140], "job": x.get("job"), "url": f"/decide.html?job={x['job']}&gate={x['id']}"}
    cards = [str(t.get("title") or "")[:120] for t in G.list_tasks() if not t.get("error") and start <= (t.get("created") or 0) < end]
    logs = []
    for member, (name, _h, log, _g) in PR.ROLES.items():
        if not log:
            continue
        text = PR._read(log) or ""
        for i, title in re.findall(r"^##\s+([A-Z]{2,4}-\d{2,4})\s+(.+)$", text, re.M):
            if day in title:
                logs.append({"who": name, "id": i, "title": PR._plain(title, 160)})
    op = next((d for d in OL.read(day[:7]).get("days", []) if d["day"] == day), {"entries": []})
    kinds = {}
    for e in op["entries"]:
        kinds[e.get("kind") or "other"] = kinds.get(e.get("kind") or "other", 0) + 1
    quoted = [{"kind": e["kind"], "time": e.get("time"), "text": e["text"][:300]} for e in op["entries"] if e.get("kind") in ("held", "incident")][:10]
    lounge = []
    for p in LG.posts():
        for x in [p] + (p.get("replies") or []):
            if str(x.get("at") or "").startswith(day):
                lounge.append({"seat": x.get("seat"), "at": x.get("at"), "text": str(x.get("text") or "")[:400]})
    act = S.since_summary(start, end)
    head = [f"{len(opened)} decision{'s' if len(opened) != 1 else ''} opened", f"{len(decided)} decided"]
    if logs:
        head.append(f"{len(logs)} log entr{'ies' if len(logs) != 1 else 'y'}")
    if act["handoffs_done"]:
        head.append(f"{act['handoffs_done']} handoffs done")
    if kinds.get("incident"):
        head.append(f"{kinds['incident']} incident{'s' if kinds['incident'] != 1 else ''}")
    return {"day": day, "days": days(), "headline": " · ".join(head),
            "decisions_opened": [gate(x) for x in opened][:20], "decisions_decided": [gate(x) for x in decided][:20],
            "cards_new": cards[:20], "log_entries": logs[:40], "operator": {"counts": kinds, "quoted": quoted},
            "lounge": sorted(lounge, key=lambda x: x["at"])[:20], "activity": act}
