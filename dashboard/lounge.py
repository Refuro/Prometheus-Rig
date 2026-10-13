"""The Architects Lounge: a just-for-fun feed the owner reads (R-019, PL-019). Read-only.

Posts are files in <architects job>/lounge/<UTC time>-<seat>.md (conventions: lounge/README.md, owned by
the Rig Architect): optional "reply_to:" and "image:" header lines, a blank line, then the text.
Posts are agent-written, untrusted data: the page shows the text as plain text, images only from inside a
job or research folder (served sandboxed like any job file), and nothing here ever notifies anyone.
"""
import os, re

import gates as G

POST_RE = re.compile(r"^(\d{8}T\d{4,6}Z)-([A-Za-z0-9._-]{1,64})\.md$")
MAX_POSTS = 200


def _image_url(path):
    """A console URL for an image inside a job or research folder, else None."""
    if not path or not path.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
        return None
    real = os.path.realpath(os.path.expanduser(path))
    for name, j in G._jobs().items():
        base = os.path.realpath(j["folder"])
        if real.startswith(base + os.sep) and os.path.isfile(real):
            return f"/job/{name}/{os.path.relpath(real, base)}"
    data = os.path.realpath(os.path.expanduser(os.environ.get("RIG_RESEARCH_DIR", "~/openrig/research")))
    if real.startswith(data + os.sep) and os.path.isfile(real):
        return f"/data/{os.path.relpath(real, data)}"
    return None


def posts():
    """Newest first, replies nested under their parent (one level; deeper replies attach to the top post)."""
    j = G._jobs().get(G.TASKS_JOB)
    if not j:
        return []
    d = os.path.join(j["folder"], "lounge")
    try:
        names = sorted((n for n in os.listdir(d) if POST_RE.match(n)), reverse=True)[:MAX_POSTS]
    except OSError:
        return []
    by_id = {}
    for n in names:
        p = os.path.join(d, n)
        try:
            if os.path.islink(p) or os.path.getsize(p) > 8000:
                continue
            with open(p, encoding="utf-8", errors="replace") as f:
                raw = f.read()
        except OSError:
            continue
        head, _, body = raw.partition("\n\n") if re.match(r"^(reply_to|image):", raw) else ("", "", raw)
        hdr = {}
        for line in head.splitlines():
            k, _, v = line.partition(":")
            hdr[k.strip().lower()] = v.strip()
        m = POST_RE.match(n)
        t = m.group(1)
        by_id[n] = {"id": n, "seat": m.group(2), "at": f"{t[:4]}-{t[4:6]}-{t[6:8]} {t[9:11]}:{t[11:13]} UTC",
                    "text": body.strip()[:2000], "image": _image_url(hdr.get("image")),
                    "reply_to": hdr.get("reply_to") or None, "replies": []}
    top = []
    for pid in sorted(by_id):   # oldest first, so replies land in order
        p = by_id[pid]
        parent, seen = by_id.get(p["reply_to"] or ""), {pid}
        while parent and parent["reply_to"] in by_id and parent["id"] not in seen:   # flatten; posts are untrusted, so no loops
            seen.add(parent["id"])
            parent = by_id[parent["reply_to"]]
        if parent and parent["id"] in seen:
            parent = None
        (parent["replies"] if parent and parent is not p else top).append(p)
    top.reverse()   # newest thread first
    return top
