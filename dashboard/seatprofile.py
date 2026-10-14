"""Architect profiles (R-027): one page per architect seat, opened from the live screen. Read-only.

Everything comes from sources that already exist; nothing new is stored:
  live state           the console's graph (rig ps + screen)
  work                 the Docket's queue rows, open gates and Needs you cards (jobpage.docket)
  role                 the role's row in ROLES.md
  open items, ideas    the "Open items" table in architects/handoffs/<role>.md. Ideas are rows whose
                       "Waiting on" says "idea" (owner, 2026-10-14, on Rig's card docket-ideas-source)
  log                  the latest entry headings in the role's own architecture log
  grade                the Model Architect's assessment, models/roles/<role>.md
  lounge, messages     the architect's Lounge posts; your messages to that seat

The repo is the folder that holds models/ (RIG_MODELS_DIR, already set for the Models page), or RIG_REPO_DIR.
Files are read with a size cap. Their text is the architects' own and goes to the page as data: the page
escapes it.
"""
import os, re, stat

import models as MD

REPO = os.path.expanduser(os.environ.get("RIG_REPO_DIR") or os.path.dirname(os.path.abspath(MD.DIR)))
MAX = 400_000
# seat member -> (ROLES.md name, handoff file, architecture log, model grade file)
ROLES = {
    "arch-rig": ("Rig Architect", "rig-architect", "ARCHITECTURE-LOG.md", "rig-architect"),
    "arch-platform": ("Platform Architect", "platform-architect", "dashboard/ARCHITECTURE-LOG.md", "platform-architect"),
    "arch-studio": ("Studio Architect", "studio-architect", "studio/ARCHITECTURE-LOG.md", "studio-architect"),
    "arch-model": ("Model Architect", "model-architect", "models/LOG.md", None),
    "review-codex": ("Model Architect's reviewer", "review-codex", None, None),
}
SEAT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}@architects$")


def _read(rel):
    """A repo file by relative path, opened step by step without following links (the repo is agent-writable;
    review-1 found the same hole in the models reader). Only a regular file is read."""
    if not rel or rel.startswith("/") or any(p in ("", ".", "..") for p in rel.split("/")):
        return None
    parts, fds = rel.split("/"), []
    try:
        fds.append(os.open(REPO, os.O_PATH | os.O_DIRECTORY))
        for p in parts[:-1]:
            fds.append(os.open(p, os.O_PATH | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fds[-1]))
        # O_NONBLOCK: a FIFO in place of a repo file would otherwise block the open (review-2).
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fds[-1])
    except OSError:
        return None
    finally:
        for d in fds:
            os.close(d)
    # Type-check the raw descriptor and close it on every refusal (a directory used to leak it, review-2).
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            os.close(fd)
            return None
        f = os.fdopen(fd, "rb")
    except OSError:
        os.close(fd)
        return None
    with f:
        return f.read(MAX).decode("utf-8", errors="replace")


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _plain(s, n=400):
    """Table cells and headings, without Markdown emphasis, capped."""
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", str(s or "")).replace("`", "")
    return s if len(s) <= n else s[: n - 1] + "…"


def role_of(name):
    t = _read("ROLES.md") or ""
    for line in t.splitlines():
        c = _cells(line) if line.startswith("|") else []
        if len(c) >= 4 and re.sub(r"\*", "", c[0]).strip() == name:
            return {"is": _plain(c[1], 120), "owns": _plain(c[2], 400), "does": _plain(c[3], 500)}
    return None


def open_items(handoff):
    """The handoff's "Open items" table as rows of {header: cell}; ideas split out."""
    t = _read(f"architects/handoffs/{handoff}.md") or ""
    m = re.search(r"^##\s*(?:\d+\.\s*)?Open items\s*$", t, re.M | re.I)
    if not m:
        return None, []
    rows, head = [], None
    for line in t[m.end():].splitlines():
        if line.startswith("## "):
            break
        if not line.startswith("|"):
            if rows or head:
                if line.strip():
                    break
            continue
        c = _cells(line)
        if head is None:
            head = [_plain(h, 40) for h in c]
        elif not all(re.fullmatch(r":?-+:?", x) for x in c if x):
            rows.append({head[i] if i < len(head) else f"col{i}": _plain(v) for i, v in enumerate(c)})
    wait_key = next((h for h in (head or []) if h.lower().startswith("waiting")), None)
    ideas = [r for r in rows if wait_key and re.search(r"\bidea\b", r.get(wait_key, ""), re.I)]
    return [r for r in rows if r not in ideas], ideas


def log_entries(rel, n=6):
    t = _read(rel) or ""
    heads = re.findall(r"^##\s+([A-Z]{2,4}-\d{2,4})\s+(.+)$", t, re.M)
    return [{"id": i, "title": _plain(title, 160)} for i, title in heads[-n:]][::-1]


def grade(rel):
    t = _read(f"models/roles/{rel}.md") if rel else None
    if not t:
        return None
    paras = [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip() and not p.lstrip().startswith("#")]
    return {"summary": _plain(paras[0] if paras else "", 600), "file": f"models/roles/{rel}.md"}


def profile(seat, node, docket_seat, lounge_posts, messages):
    """seat: full seat id; node: its graph node or None; docket_seat: its Docket entry or None;
    lounge_posts: all Lounge posts (threaded); messages: your messages to this seat."""
    if not SEAT_RE.match(seat or ""):
        raise ValueError("Unknown seat")
    member = seat.split("@")[0]
    name, handoff, log, grade_file = ROLES.get(member, (member, None, None, None))
    items, ideas = open_items(handoff) if handoff else (None, [])
    flat = []
    for p in lounge_posts:
        flat.append(p)
        flat.extend(p.get("replies") or [])
    return {
        "seat": seat, "name": name, "member": member,
        "now": {k: (node or {}).get(k) for k in ("state", "action", "elapsed", "model", "runtime", "alert", "ctx")} if node else None,
        "role": role_of(name),
        "work": docket_seat,
        "open_items": items, "ideas": ideas,
        "ideas_source": f"architects/handoffs/{handoff}.md" if handoff else None,
        "log": log_entries(log) if log else [], "log_file": log,
        "grade": grade(grade_file),
        "lounge": [{"at": p["at"], "text": p["text"][:600]} for p in flat if p.get("seat") == member][:5],
        "messages": [{"id": m.get("id"), "question": str(m.get("question") or "")[:300], "asked_at": m.get("asked_at"),
                      "status": m.get("status")} for m in messages[-5:]][::-1],
        "handoff": f"architects/handoffs/{handoff}.md" if handoff else None,
    }
