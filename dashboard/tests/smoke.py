#!/usr/bin/env python3
"""Rig Console smoke test: starts a private server on a copy of tests/fixtures and checks
every page, API, safety rule and decision flow. Touches no real rig, data or state.

    python3 dashboard/tests/smoke.py          # exit code 0 = all passed
    python3 dashboard/tests/smoke.py -v       # also print the server log

Standard library only. Takes about 15-30 s (it waits for the 10 s collector to run once).
"""
import http.client, json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
DASH = os.path.dirname(HERE)
TOKEN = "smoke-test-token"
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("  PASS  " if ok else "  FAIL  ") + name + (f"  ({detail})" if detail and not ok else ""))


def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


class Client:
    def __init__(self, port): self.port = port
    def req(self, method, path, body=None, headers=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=20)
        h = dict(headers or {})
        data = None
        if body is not None:
            data = json.dumps(body).encode(); h.setdefault("Content-Type", "application/json")
        c.request(method, path, body=data, headers=h)
        r = c.getresponse(); raw = r.read(); c.close()
        return r.status, {k.lower(): v for k, v in r.getheaders()}, raw
    def json(self, path, **kw):
        st, h, raw = self.req("GET", path, **kw)
        return st, json.loads(raw or b"null") if st == 200 else None
    def post(self, path, body, console_header=True):
        h = {"X-Rig-Console": "1"} if console_header else {}
        st, _, raw = self.req("POST", path, body, h)
        try: return st, json.loads(raw)
        except ValueError: return st, None


def main():
    verbose = "-v" in sys.argv
    tmp = tempfile.mkdtemp(prefix="rig-console-smoke-")
    fx = os.path.join(tmp, "fx")
    shutil.copytree(os.path.join(HERE, "fixtures"), fx)
    jobs_cfg = os.path.join(tmp, "jobs.json")
    json.dump({"roots": [{"root": os.path.join(fx, "research"), "type": "research"},
                         {"root": os.path.join(fx, "jobs"), "type": "general"}]}, open(jobs_cfg, "w"))
    port = free_port()
    env = {**os.environ, "PORT": str(port), "HOST": "127.0.0.1", "RIG_CONSOLE_TOKEN": TOKEN, "RIG_BIN": "",
           "RIG_SNAPSHOTS": os.path.join(fx, "snapshots"), "RIG_RESEARCH_DIR": os.path.join(fx, "research"),
           "RIG_STATE_DIR": os.path.join(tmp, "state"), "RIG_DB": os.path.join(tmp, "console.db"),
           "RIG_JOBS_CONFIG": jobs_cfg}
    for k in ("NTFY_TOPIC", "NTFY_CLICK"):
        env.pop(k, None)
    log = open(os.path.join(tmp, "server.log"), "w")
    srv = subprocess.Popen([sys.executable, os.path.join(DASH, "serve.py")], cwd=DASH, env=env, stdout=log, stderr=subprocess.STDOUT)
    c = Client(port)
    try:
        for _ in range(50):
            try:
                if c.req("GET", "/api/health")[0] == 200: break
            except OSError: time.sleep(0.2)
        print(f"Rig Console smoke test (server on :{port}, data in {tmp})")

        print("Pages")
        for p in ["/", "/graph.html", "/runs.html", "/decide.html", "/play.html", "/m.html", "/nav.js", "/manifest.json"]:
            st, _, _ = c.req("GET", p)
            check(f"GET {p}", st == 200, st)

        print("Graph and alerts")
        st, g = c.json("/api/graph")
        names = {n["name"]: n for n in (g or {}).get("nodes", [])}
        check("graph lists running seats only", st == 200 and set(names) == {"operator-agent", "demo-lead", "demo-analyst", "demo-skeptic"}, sorted(names))
        kinds = {a["kind"] for a in (g or {}).get("alerts", [])}
        check("approval alert for the seat at a prompt", "approval" in kinds, kinds)
        check("context alert at 86%", "context" in kinds, kinds)
        check("gate alert for open decisions", "gate" in kinds, kinds)
        check("unclaimed handoff not yet 'stuck' wording", all(a["kind"] != "frozen" for a in g["alerts"]), kinds)
        lead = names.get("demo-lead", {})
        check("working seat shows its action", "niches.json" in (lead.get("action") or ""), lead.get("action"))
        check("blocked seat shows what it asks", "count_posts" in (names.get("demo-analyst", {}).get("action") or ""))
        st, runs = c.json("/api/runs")
        check("research run listed", st == 200 and any(r.get("run") == "run-demo" for r in runs or []))

        print("Event store (waits for the collector)")
        evs = []
        for _ in range(40):
            st, e = c.json("/api/events?limit=200")
            evs = (e or {}).get("events", [])
            if any(x["kind"] == "playtest" for x in evs) and any(x["kind"] == "handoff" for x in evs): break
            time.sleep(1)
        kinds = {x["kind"] for x in evs}
        check("handoffs recorded from the queue", "handoff" in kinds, kinds)
        check("custom events read from events.jsonl", "playtest" in kinds, kinds)
        check("bad events.jsonl lines skipped", not any(x["kind"] == "bad kind" for x in evs))
        check("file events credited via job.json writers",
              any(x["kind"] == "file" and x.get("seat") == "demo-analyst@demo-team" and x["text"].startswith("pitches/") for x in evs))
        st, rp = c.json("/api/replay?rig=demo-team&run=run-demo")
        check("replay returns the team's history", st == 200 and rp.get("events"), (rp or {}).get("error"))
        st, jobs = c.json("/api/jobs")
        check("jobs registry", st == 200 and {j["name"] for j in jobs} >= {"pitch-demo", "run-demo"})

        print("Gates and builds")
        st, gs = c.json("/api/gates")
        ids = {x["id"] for x in (gs or {}).get("open", [])}
        check("open gates found", ids == {"pick-2", "approve-brief"}, ids)
        check("broken gate file reported, not crashing", len((gs or {}).get("errors", [])) == 1)
        pick = next((x for x in gs["open"] if x["id"] == "pick-2"), {})
        check("invalid option ids dropped", [o["id"] for o in pick.get("options", [])] == ["p01", "p02", "p03"])
        st, b = c.json("/api/builds")
        check("playable build listed", st == 200 and b and b[0]["url"].endswith("/builds/p01/index.html"))
        st, h, _ = c.req("GET", "/play/pitch-demo/builds/p01/index.html")
        check("builds served with cross-origin isolation", st == 200 and h.get("cross-origin-embedder-policy") == "require-corp")
        st, h, _ = c.req("GET", "/job/pitch-demo/pitches/p01.md")
        check("agent files served sandboxed", st == 200 and h.get("content-security-policy") == "sandbox")
        for bad in ["/job/pitch-demo/../../../etc/passwd", "/job/pitch-demo/%2e%2e/%2e%2e/snapshots/_ps.json", "/job/nope/x.md"]:
            st, _, _ = c.req("GET", bad)
            check(f"path escape refused: {bad}", st in (403, 404), st)

        print("Decisions")
        st, r = c.post("/api/gate?job=pitch-demo&gate=pick-2", {"chosen": ["p01"]})
        check("wrong pick count rejected", r and "error" in r, r)
        st, r = c.post("/api/gate?job=pitch-demo&gate=pick-2", {"chosen": ["p02", "p01"]}, console_header=False)
        check("POST without console header refused (CSRF)", st == 403, st)
        st, r = c.post("/api/gate?job=pitch-demo&gate=pick-2", {"chosen": ["p02", "p01"], "note": "smoke"})
        check("valid decision saved", r and r.get("saved"), r)
        dec = os.path.join(fx, "jobs", "pitch-demo", "decisions", "pick-2.json")
        check("decision file written in pick order", os.path.exists(dec) and json.load(open(dec))["chosen"] == ["p02", "p01"])
        st, r = c.post("/api/gate?job=pitch-demo&gate=pick-2", {"chosen": ["p01", "p03"]})
        check("decided gate can't be decided twice", r and "error" in r, r)
        st, r = c.post("/api/gate?job=pitch-demo&gate=approve-brief", {"close": True})
        check("gate closed without deciding", r and r.get("saved") and not r.get("lead_notified"), r)
        st, gs = c.json("/api/gates")
        check("no gates left open", not gs["open"], [x["id"] for x in gs["open"]])

        print("Remote access")
        proxy = {"X-Forwarded-For": "100.64.0.5"}
        st, _, body = c.req("GET", "/decide.html?job=a&gate=b", headers=proxy)
        check("remote page without login gets sign-in page", st == 401 and b'name="token"' in body and b'value="a"' in body, st)
        st, _, _ = c.req("GET", "/api/graph", headers=proxy)
        check("remote API without login refused", st == 403, st)
        st, h, _ = c.req("GET", f"/m.html?token={TOKEN}&x=1", headers=proxy)
        check("token sign-in redirects without the token", st == 303 and h.get("location") == "/m.html?x=1", (st, h.get("location")))
        check("cookie is Lax, Secure, HttpOnly", all(s in h.get("set-cookie", "") for s in ("SameSite=Lax", "Secure", "HttpOnly")), h.get("set-cookie"))
        st, _, _ = c.req("GET", "/api/graph", headers={**proxy, "Cookie": f"rc_token={TOKEN}"})
        check("cookie grants access", st == 200, st)
        st, _, _ = c.req("GET", "/api/graph", headers={**proxy, "Cookie": "rc_token=wrong"})
        check("wrong cookie refused", st == 403, st)
        st, _, _ = c.req("GET", "/manifest.json", headers=proxy)
        check("app manifest public (needed to install)", st == 200, st)
    finally:
        srv.terminate()
        try: srv.wait(5)
        except subprocess.TimeoutExpired: srv.kill()
        log.close()
        if verbose:
            print("\n--- server log ---\n" + open(os.path.join(tmp, "server.log")).read())
    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} passed")
    shutil.rmtree(tmp, ignore_errors=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
