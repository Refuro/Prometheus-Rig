"""The Architects Lounge: a just-for-fun feed the owner reads (R-019, PL-019), and can post in (R-021, PL-029).

Posts are files in <architects job>/lounge/<UTC time>-<seat>.md (conventions: lounge/README.md, owned by
the Rig Architect): optional "reply_to:" and "image:" header lines, a blank line, then the text.
Posts are agent-written, untrusted data: the page shows the text as plain text, images only from inside a
job or research folder (served sandboxed like any job file), and nothing here ever notifies anyone.
The owner's posts are written by the console (signed-in POST only) as <UTC>-owner.md. Seats can write files
in this folder too, so the console keeps a fingerprint of each post it wrote: only those show as the owner's.
"""
import hashlib, json, os, re, stat, threading
from datetime import datetime, timezone

import gates as G

POST_RE = re.compile(r"^(\d{8}T\d{4,6}Z)-([A-Za-z0-9._-]{1,64})\.md$")
MAX_POSTS = 200
MAX_TEXT = 2000
OWNER = "owner"
MINE = os.path.join(G.STATE_DIR, "lounge-owner.json")   # {filename: sha256} of posts the console wrote
_lock = threading.Lock()


def _folder():
    j = G._jobs().get(G.TASKS_JOB)
    return os.path.join(j["folder"], "lounge") if j else None


def _open_dir(path, create_last=False):
    """A directory fd for path, opened one component at a time from / without following any symlink.
    Seats can edit the job tree, so a planted link must never redirect a read or an owner post (Codex R-021
    finding 1). Raises OSError if any part is a link or missing.
    The folders on the way are opened with O_PATH: under option A the console may only pass through the
    owner's home (ACL --x), not list it, and O_PATH needs only that. Only the last folder is opened for
    reading (PL-040: opening every folder for reading left the Lounge empty after the migration)."""
    parts = [p for p in os.path.abspath(path).split(os.sep) if p]
    walk = os.O_PATH | os.O_DIRECTORY | os.O_NOFOLLOW
    last = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open("/", walk if parts else last)
    try:
        for i, part in enumerate(parts):
            flags = last if i == len(parts) - 1 else walk
            try:
                nxt = os.open(part, flags, dir_fd=fd)
            except FileNotFoundError:
                if not (create_last and i == len(parts) - 1):
                    raise
                os.mkdir(part, 0o755, dir_fd=fd)
                nxt = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = nxt
        return fd
    except BaseException:
        os.close(fd)
        raise


def _is_post(dfd, name):
    """A plain file (not a link) with a post's name, in the open lounge folder."""
    try:
        return bool(POST_RE.match(name)) and stat.S_ISREG(os.stat(name, dir_fd=dfd, follow_symlinks=False).st_mode)
    except OSError:
        return False


def _mine():
    try:
        with open(MINE) as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def post(text, reply_to=None, now=None):
    """The owner's post or reply. The server picks the file name; nothing is sent, pushed or counted."""
    text = str(text or "").replace("\r\n", "\n").strip()
    if not text:
        raise ValueError("Write something first")
    if len(text) > MAX_TEXT:
        raise ValueError(f"Keep it under {MAX_TEXT} characters ({len(text)} now)")
    d = _folder()
    if not d:
        raise ValueError("The architects' job folder isn't set up")
    try:
        dfd = _open_dir(d, create_last=True)
    except OSError:
        raise ValueError("The Lounge folder isn't a plain folder (a link?), so nothing was posted")
    try:
        reply_to = str(reply_to or "")
        if reply_to and not _is_post(dfd, reply_to):
            reply_to = ""   # not an existing post: post at the top instead
        # Always write the header line, so text that starts with "image:" stays text.
        raw = f"reply_to: {reply_to}\n\n{text}\n".encode("utf-8")
        if len(raw) > 8000:   # posts() skips bigger files
            raise ValueError("That's too long; try a shorter post")
        t = now or datetime.now(timezone.utc).timestamp()
        with _lock:
            return _write(dfd, raw, t, reply_to)
    finally:
        os.close(dfd)


def _write(dfd, raw, t, reply_to):
    for i in range(5):   # one post per second per name: step on if the second is taken
        name = datetime.fromtimestamp(t + i, timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"-{OWNER}.md"
        try:   # O_EXCL relative to the folder we opened: no overwrite, no planted link, no redirected folder
            fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=dfd)
        except FileExistsError:
            continue
        with os.fdopen(fd, "wb") as f:
            f.write(raw)
        mine = _mine()
        mine[name] = hashlib.sha256(raw).hexdigest()
        os.makedirs(G.STATE_DIR, exist_ok=True)
        tmp = MINE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(mine, f, indent=1)
        os.replace(tmp, MINE)
        return {"posted": name, "reply_to": reply_to or None}
    raise ValueError("Couldn't pick a file name; try again in a moment")


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
    d = _folder()
    if not d:
        return []
    mine = _mine()
    try:
        dfd = _open_dir(d)   # a linked folder shows nothing, rather than files from somewhere else
    except OSError:
        return []
    try:
        names = sorted((n for n in os.listdir(dfd) if POST_RE.match(n)), reverse=True)[:MAX_POSTS]
        by_id = {}
        for n in names:
            try:
                fd = os.open(n, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=dfd)
            except OSError:
                continue
            with os.fdopen(fd, "rb") as f:
                if not stat.S_ISREG(os.fstat(f.fileno()).st_mode) or os.fstat(f.fileno()).st_size > 8000:
                    continue
                raw = f.read().decode("utf-8", errors="replace")
            by_id[n] = _parse(n, raw, mine)
    finally:
        os.close(dfd)
    return _thread(by_id)


def _parse(n, raw, mine):
    """One post file: optional header lines, a blank line, then the text."""
    head, _, body = raw.partition("\n\n") if re.match(r"^(reply_to|image):", raw) else ("", "", raw)
    hdr = {}
    for line in head.splitlines():
        k, _, v = line.partition(":")
        hdr[k.strip().lower()] = v.strip()
    m = POST_RE.match(n)
    t, seat = m.group(1), m.group(2)
    if seat == OWNER and mine.get(n) != hashlib.sha256(raw.encode("utf-8")).hexdigest():
        seat = "not-the-owner"   # named like an owner post, but the console didn't write it (or it changed)
    return {"id": n, "seat": seat, "owner": seat == OWNER, "at": f"{t[:4]}-{t[4:6]}-{t[6:8]} {t[9:11]}:{t[11:13]} UTC",
            "text": body.strip()[:2000], "image": _image_url(hdr.get("image")),
            "reply_to": hdr.get("reply_to") or None, "replies": []}


def _thread(by_id):
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
