// Shared top bar for every desktop page: same links, same place, same look.
// Include right after <body>: <script src="/nav.js"></script>
// Page-specific controls (e.g. a run picker) can carry data-rc-tools and get moved into the bar.
//
// Five groups, by what you're doing (R-027): Now (what's happening), Decide (what waits for you), Teams (the
// work), Record (what happened), System (the plumbing). Every page lives in exactly one group; the group's
// pages sit in a second row under the bar. Add a new page to its group here, never as a new top-level link.
(() => {
  const GROUPS = [
    ["Now", [["/", "Live", "Every agent, live"]]],
    ["Decide", [["/needs.html", "Needs you", "To-dos and questions only you can answer"], ["/decide.html", "Decisions", "Choices teams are waiting on"],
                ["/messages.html", "Messages", "What you asked each seat, with its reply"]]],
    ["Teams", [["/job.html", "Jobs", "Each team's work: overview, docs, assets, report"], ["/play.html", "Builds", "Playable builds"],
               ["/diplomacy.html", "Diplomacy", "The agents' Diplomacy game"], ["/research.html", "Niche board", "Research funnels and checkpoints"],
               ["/runs.html", "Run report", "Timelines, usage, evidence, approvals"]]],
    ["Record", [["/digest.html", "Digest", "What happened today, and on earlier days"], ["/oplog.html", "Operator log", "What the operator did, and why"], ["/lounge.html", "Lounge", "The architects' feed"],
                ["/models.html", "Models", "Report cards for models, roles and briefs"]]],
    ["System", [["/system.html", "System", "What runs where, and who owns what"]]],
  ];
  // Pages that belong to a group without their own second-row link.
  const ALIAS = {"/graph.html": "/", "/index.html": "/", "/seat.html": "/"};
  const here = ALIAS[location.pathname] || location.pathname;
  const phone = matchMedia("(max-width: 700px)").matches;
  const group = GROUPS.find(([, pages]) => pages.some(([p]) => p === here)) || null;
  const cur = (GROUPS.flatMap(([, p]) => p).find(([p]) => p === here) || [here, document.title.split(" · ")[0]])[1];
  const rows = !phone && group && (group[1].length > 1 || group[0] === "Now");
  const css = `<style>
    :root{--rcnav:${rows ? 86 : 50}px}
    .rcbar{position:sticky;top:0;z-index:30;background:color-mix(in srgb,var(--paper) 92%,transparent);backdrop-filter:blur(10px);
      border-bottom:1px solid var(--line);font-family:var(--font);white-space:nowrap}
    .rcnav{height:50px;display:flex;align-items:center;gap:6px 16px;padding:0 18px}
    .rcbrand{display:flex;align-items:center;gap:8px;font-weight:800;font-size:15px;letter-spacing:-.02em;color:var(--ink);text-decoration:none;margin-right:6px}
    .rcbrand img{width:20px;height:20px}
    .rclinks{display:flex;align-items:center;gap:4px}
    .rclinks a{all:unset;cursor:pointer;position:relative;color:var(--muted);font-weight:650;font-size:13.5px;padding:6px 11px;border-radius:8px}
    .rclinks a:hover{color:var(--ink);background:var(--raised)}
    .rclinks a[aria-current="true"]{color:var(--ink);background:var(--raised);box-shadow:inset 0 -2px 0 var(--signal)}
    .rclinks a:focus-visible,.rcsub a:focus-visible{outline:2px solid var(--signal);outline-offset:2px}
    .rcnav .n,.rcsub .n{display:inline-block;min-width:17px;margin-left:5px;padding:0 5px;border-radius:9px;background:var(--cut);color:#fff;font-size:11px;line-height:17px;text-align:center}
    .rcsub{height:36px;display:flex;align-items:center;gap:2px;padding:0 18px 0 46px;overflow-x:auto;scrollbar-width:none}
    .rcsub::-webkit-scrollbar{display:none}
    .rcsub a{color:var(--muted);text-decoration:none;font-weight:600;font-size:12.5px;padding:4px 10px;border-radius:7px}
    .rcsub a:hover{color:var(--ink)}
    .rcsub a[aria-current="page"]{color:var(--ink);background:var(--raised)}
    .rcsub .lbl{font:600 11px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:var(--faint);letter-spacing:.04em;margin-right:8px}
    .rcface{display:inline-flex;align-items:center;gap:6px;color:var(--muted);text-decoration:none;font:600 12px var(--font);padding:3px 9px 3px 4px;border-radius:999px}
    .rcface:hover,.rcface[aria-current="page"]{background:var(--raised);color:var(--ink)}
    .rcface i{width:20px;height:20px;border-radius:50%;display:grid;place-items:center;font:800 10px var(--font);font-style:normal;color:var(--ink);
      background:var(--raised);box-shadow:0 0 0 2px var(--faint)}
    .rcface i.working{box-shadow:0 0 0 2px var(--ok);animation:rcpulse 1.6s ease-in-out infinite}
    .rcface i.waiting{box-shadow:0 0 0 2px var(--signal)}
    .rcface i.blocked{box-shadow:0 0 0 2px var(--cut)}
    @keyframes rcpulse{50%{box-shadow:0 0 0 4px color-mix(in srgb,var(--ok) 35%,transparent)}}
    @media (prefers-reduced-motion:reduce){.rcface i.working{animation:none}}
    .rcfaces{display:flex;align-items:center;gap:2px}
    .rcsince{display:flex;align-items:center;gap:6px;font-size:12.5px;color:var(--muted);white-space:nowrap}
    .rcsince[hidden]{display:none}
    .rcsince a{color:var(--ink);font-weight:650}
    .rcsince .lbl{margin-right:2px}
    .rcseen{all:unset;cursor:pointer;font:700 11.5px var(--font);color:var(--ink);padding:2px 9px;border:1px solid var(--line);border-radius:999px;margin-left:4px}
    .rcseen:hover{border-color:var(--signal)}
    .rctools{display:flex;align-items:center;gap:8px}
    .rctools:empty{display:none}
    .rctools select{background:var(--raised);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:4px 8px;font:600 13px var(--font)}
    .rcsp{flex:1}
    .rcnav #healthSlot,.rcnav #alertSlot{flex-shrink:0}
    .rcpage{font-weight:700;font-size:14px;color:var(--muted)}
  </style>`;
  const top = ([g, pages]) => `<a href="${pages[0][0]}" data-g="${g}"${group && group[0] === g ? ' aria-current="true"' : ""} title="${pages.map(p => p[1]).join(", ")}">${g}</a>`;
  const sub = !rows ? "" : group[0] === "Now"
    ? `<div class="rcsub"><span class="rcfaces" id="rcFaces" aria-label="Architects"><span class="lbl">ARCHITECTS</span></span>
        <span class="rcsp"></span><span class="rcsince" id="rcSince" hidden></span></div>`
    : `<nav class="rcsub" aria-label="${group[0]} pages">${group[1].map(([p, label, what]) =>
        `<a href="${p}" title="${what}"${p === here ? ' aria-current="page"' : ""}${p === "/decide.html" ? ' id="rcDecide"' : p === "/needs.html" ? ' id="rcNeeds"' : ""}>${label}</a>`).join("")}</nav>`;
  const html = phone
    ? `${css}<div class="rcbar"><div class="rcnav"><a class="rcbrand" href="/m.html">‹ Rig Console</a><span class="rcpage">${cur}</span><span class="rcsp"></span><div id="healthSlot" hidden></div><div id="alertSlot" hidden></div></div></div>`
    : `${css}<div class="rcbar"><div class="rcnav"><a class="rcbrand" href="/" title="Now: the live graph"><img src="/icon.svg" alt="">Rig Console</a>
        <nav class="rclinks" aria-label="Sections">${GROUPS.map(top).join("")}</nav>
        <div class="rctools" id="rcTools"></div><span class="rcsp"></span><div id="healthSlot"></div><div id="alertSlot"></div></div>${sub}</div>`;
  document.currentScript.insertAdjacentHTML("afterend", html);
  document.addEventListener("DOMContentLoaded", () => {
    const tools = document.getElementById("rcTools");
    if (tools) document.querySelectorAll("[data-rc-tools]").forEach(el => tools.appendChild(el));
  });
  // Changes need this browser to be signed in, even on this PC (R-005): agents run here too, so only the
  // owner's cookie counts. Show a sign-in button when it's missing, and catch any refused change.
  const signinUrl = () => "/signin?next=" + encodeURIComponent(location.pathname + location.search);
  function signinBanner(){
    if (document.getElementById("rcSignin")) return;
    const b = document.createElement("a");
    b.id = "rcSignin"; b.href = signinUrl();
    b.textContent = "Sign in to make changes";
    b.style.cssText = "flex-shrink:0;font:700 12.5px var(--font);color:#111;background:var(--signal);padding:6px 11px;border-radius:999px;text-decoration:none";
    const slot = document.querySelector(".rcnav .rcsp");
    if (slot) slot.after(b); else document.body.prepend(b);
  }
  async function session(){
    try {
      const s = await (await fetch("/api/session", {cache: "no-store"})).json();
      if (s.token_set && !s.signed_in) signinBanner();
    } catch {}
  }
  const _fetch = window.fetch.bind(window);
  window.fetch = async (...args) => {
    const r = await _fetch(...args);
    if (r.status === 401 && ((args[1] || {}).method || "GET").toUpperCase() === "POST") signinBanner();
    return r;
  };
  document.addEventListener("DOMContentLoaded", session);
  // What waits for you, on every page: open decisions and Needs you cards, summed on "Decide" and split on its
  // second row.
  const counts = {gates: 0, needs: 0};
  const badge = n => n ? `<span class="n">${n}</span>` : "";
  function paint(){
    const d = document.querySelector('.rclinks a[data-g="Decide"]'); if (d) d.innerHTML = "Decide" + badge(counts.gates + counts.needs);
    const g = document.getElementById("rcDecide"); if (g) g.innerHTML = "Decisions" + badge(counts.gates);
    const n = document.getElementById("rcNeeds"); if (n) n.innerHTML = "Needs you" + badge(counts.needs);
  }
  async function poll(){
    if (document.hidden || phone) return;
    try { counts.gates = ((await (await fetch("/api/gates", {cache: "no-store"})).json()).open || []).length; } catch {}
    try { counts.needs = (await (await fetch("/api/needs", {cache: "no-store"})).json()).count || 0; } catch {}
    paint();
  }
  poll(); setInterval(poll, 20000);
  // The architects' faces on Now's second row: a ring per seat (working pulses, waiting on you, blocked, idle).
  // Each opens that architect's profile. Names come from the console's own graph, escaped.
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const ring = st => /^needs_input/.test(st) ? "waiting" : /^working|running/.test(st) ? "working" : /blocked|error|limit/.test(st) ? "blocked" : "";
  async function faces(){
    const row = document.getElementById("rcFaces"); if (!row || document.hidden) return;
    try {
      const g = await (await fetch("/api/graph", {cache: "no-store"})).json();
      const seen = new Set();   // one face per seat, even if a seat is listed twice
      const arch = (g.nodes || []).filter(n => n.rig === "architects" && !seen.has(n.id) && seen.add(n.id)).sort((a, b) => String(a.name).localeCompare(b.name));
      const seat = new URLSearchParams(location.search).get("seat");
      row.innerHTML = `<span class="lbl">ARCHITECTS</span>` + arch.map(n => {
        const short = String(n.name || "").replace(/^arch-/, "");
        const st = n.alert === "limit" ? "blocked" : ring(String(n.state || ""));
        return `<a class="rcface" href="/seat.html?seat=${encodeURIComponent(n.id)}"${seat === n.id ? ' aria-current="page"' : ""} title="${esc(n.id)}: ${esc(n.state || "unknown")}">` +
               `<i class="${st}">${esc(short.charAt(0).toUpperCase())}</i>${esc(short)}</a>`;
      }).join("");
    } catch {}
  }
  faces(); setInterval(faces, 15000);
  // "Since you last looked" on Now (since.js, shared with the phone page).
  if (rows && group[0] === "Now" && location.pathname !== "/seat.html") {
    const s = document.createElement("script");
    s.src = "/since.js";
    s.onload = () => window.rcSince(document.getElementById("rcSince"));
    document.head.appendChild(s);
  }
})();
