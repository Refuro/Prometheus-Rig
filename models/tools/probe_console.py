"""Re-test of PL-014 (MA-013 gaps) against a throwaway console on fixture data. Never touches the live console."""
import http.client, json, os, shutil, socket, subprocess, sys, tempfile, time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DASH = os.path.join(REPO, "dashboard")
TOKEN = "probe-token-123"
TS = "mypc.tail1234.ts.net"


def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def req(port, method, path, headers=None, body=None):
    c = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    h = {"Host": "localhost"}
    h.update(headers or {})
    c.request(method, path, body=body, headers=h)
    r = c.getresponse()
    data = r.read()
    return r.status, dict(r.getheaders()), data


results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def start(tmp, fx, token, label):
    port, play = free_port(), free_port()
    jobs_cfg = os.path.join(tmp, f"jobs-{label}.json")
    json.dump({"roots": [{"root": os.path.join(fx, "research"), "type": "research"},
                         {"root": os.path.join(fx, "jobs"), "type": "general"}]}, open(jobs_cfg, "w"))
    env = {**os.environ, "PORT": str(port), "PLAY_PORT": str(play), "HOST": "127.0.0.1", "RIG_CONSOLE_TOKEN": token,
           "RIG_BIN": "", "RIG_SNAPSHOTS": os.path.join(fx, "snapshots"), "RIG_RESEARCH_DIR": os.path.join(fx, "research"),
           "RIG_STATE_DIR": os.path.join(tmp, f"state-{label}"), "RIG_DB": os.path.join(tmp, f"{label}.db"),
           "RIG_JOBS_CONFIG": jobs_cfg, "RIG_MODELS_DIR": os.path.join(fx, "models"), "RIG_BRIEFS_DIR": os.path.join(fx, "briefs"),
           "RIG_LAUNCHES_DIR": os.path.join(tmp, "launches"), "RIG_CONSOLE_HOSTS": TS}
    for k in ("NTFY_TOPIC", "NTFY_CLICK"):
        env.pop(k, None)
    log = open(os.path.join(tmp, f"{label}.log"), "w")
    srv = subprocess.Popen([sys.executable, os.path.join(DASH, "serve.py")], cwd=DASH, env=env, stdout=log, stderr=subprocess.STDOUT)
    for _ in range(60):
        try:
            if req(port, "GET", "/api/health")[0] == 200:
                break
        except OSError:
            time.sleep(0.25)
    return srv, port, play


tmp = tempfile.mkdtemp(prefix="ma-probe-")
fx = os.path.join(tmp, "fx")
shutil.copytree(os.path.join(DASH, "tests", "fixtures"), fx, copy_function=shutil.copyfile)
job = os.path.join(fx, "jobs", "pitch-demo")
os.makedirs(os.path.join(job, "builds", "game"), exist_ok=True)
open(os.path.join(job, "builds", "game", "index.html"), "w").write("<p>build</p>")
open(os.path.join(job, "evil.html"), "w").write("<script>steal()</script>")
os.makedirs(os.path.join(job, "decisions"), exist_ok=True)
open(os.path.join(job, "decisions", "x.json"), "w").write('{"verdict":"approve"}')
os.symlink(os.path.join(job, "decisions", "x.json"), os.path.join(job, "builds", "game", "link.json"))

srv, port, play = start(tmp, fx, TOKEN, "a")
try:
    print(f"console :{port}, builds :{play}, data {tmp}")
    # (a) builds port scope
    st = req(play, "GET", "/play/pitch-demo/builds/game/index.html")[0]
    check("(a) a real build file is served", st == 200, st)
    st = req(play, "GET", "/play/pitch-demo/evil.html")[0]
    check("(a) a job file outside builds/ is refused", st == 404, st)
    st = req(play, "GET", "/play/pitch-demo/decisions/x.json")[0]
    check("(a) decisions/ is refused", st == 404, st)
    st = req(play, "GET", "/play/pitch-demo/builds/game/link.json")[0]
    check("(a) a symlink in builds/ pointing at decisions/ is refused", st == 404, st)
    st = req(play, "GET", "/play/pitch-demo/builds/%2e%2e/decisions/x.json")[0]
    check("(a) an encoded .. escape is refused", st == 404, st)
    # (a') the job chooses its own builds folder in job.json, which team seats write
    jj = os.path.join(job, "job.json")
    meta = json.load(open(jj)) if os.path.exists(jj) else {}
    meta["builds"] = "decisions"
    json.dump(meta, open(jj, "w"))
    st = req(play, "GET", "/play/pitch-demo/decisions/x.json")[0]
    check("(a') job.json 'builds': 'decisions' does NOT expose decisions/", st == 404, st)
    meta["builds"] = "."
    json.dump(meta, open(jj, "w"))
    st = req(play, "GET", "/play/pitch-demo/evil.html")[0]
    check("(a') job.json 'builds': '.' does NOT expose the job folder", st == 404, st)
    meta["builds"] = "builds"
    json.dump(meta, open(jj, "w"))

    # (b) Tailscale name pinned
    st = req(port, "GET", "/api/health", {"Host": "evil.ts.net"})[0]
    check("(b) an unlisted *.ts.net Host is refused", st != 200, st)
    st = req(port, "GET", "/api/health", {"Host": TS})[0]
    check("(b) the pinned Tailscale name is accepted", st == 200, st)

    # (c) X-Forwarded-Host on /go/play/
    st, h, _ = req(port, "GET", "/go/play/pitch-demo/builds/game/index.html?token=" + TOKEN, {"X-Forwarded-Host": "evil.example"})
    loc = h.get("Location", "")
    check("(c) a forged X-Forwarded-Host doesn't redirect off-site", "evil.example" not in loc, f"{st} {loc}")

    # baseline: changes need sign-in
    st = req(port, "POST", "/api/decide", {"Content-Type": "application/json"}, b"{}")[0]
    check("baseline: an unsigned POST is refused", st in (401, 403), st)
finally:
    srv.terminate(); srv.wait(5)

# (d) no token configured: changes refused
srv, port, play = start(tmp, fx, "", "b")
try:
    st, _, body = req(port, "POST", "/api/decide", {"Content-Type": "application/json"}, b"{}")
    check("(d) with no token set, a POST is refused", st == 403, f"{st} {body[:80]!r}")
finally:
    srv.terminate(); srv.wait(5)

print(f"\n{sum(results)}/{len(results)} passed")
shutil.rmtree(tmp, ignore_errors=True)
