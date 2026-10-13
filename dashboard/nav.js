// Shared top bar for every desktop page: same links, same place, same look.
// Include right after <body>: <script src="/nav.js"></script>
// Page-specific controls (e.g. a run picker) can carry data-rc-tools and get moved into the bar.
//
// Three everyday pages sit in the bar. Everything else is under "More", grouped by what it's for,
// so the bar doesn't grow every time a page is added: add new pages to MORE, not to MAIN.
(() => {
  // "Needs you" (R-018/R-020): the owner's own inbox page of to-dos and questions, with a count of open cards.
  const MAIN = [["/", "Live"], ["/needs.html", "Needs you"], ["/decide.html", "Decisions"], ["/play.html", "Builds"]];
  const MORE = [
    ["Teams", [["/job.html", "Jobs", "Each team's decisions, milestones, builds, docs and art"], ["/diplomacy.html", "Diplomacy", "The agents' Diplomacy game: board, press, pause"]]],
    ["Research", [["/research.html", "Niche board", "Research funnels and checkpoints"], ["/runs.html", "Run report", "Timelines, usage, evidence, approvals"]]],
    ["Console", [["/models.html", "Models", "Report cards for models, roles and briefs"], ["/system.html", "System", "What runs where, and who owns what"], ["/lounge.html", "Lounge", "The architects' just-for-fun feed"], ["/messages.html", "Messages", "What you asked each seat, with its reply"], ["/oplog.html", "Operator log", "What the operator did, and why"]]],
  ];
  const ALIAS = {"/graph.html": "/", "/index.html": "/"};
  const here = ALIAS[location.pathname] || location.pathname;
  const phone = matchMedia("(max-width: 700px)").matches;
  const all = MAIN.concat(...MORE.map(g => g[1]));
  const cur = (all.find(([p]) => p === here) || [here, document.title.split(" · ")[0]])[1];
  const inMore = MORE.some(g => g[1].some(([p]) => p === here));
  const css = `<style>
    :root{--rcnav:50px}
    .rcnav{position:sticky;top:0;z-index:30;height:var(--rcnav);display:flex;align-items:center;gap:6px 16px;padding:0 18px;
      background:color-mix(in srgb,var(--paper) 92%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line);
      font-family:var(--font);white-space:nowrap}
    .rcbrand{display:flex;align-items:center;gap:8px;font-weight:800;font-size:15px;letter-spacing:-.02em;color:var(--ink);text-decoration:none;margin-right:6px}
    .rcbrand img{width:20px;height:20px}
    .rclinks{display:flex;align-items:center;gap:4px}
    .rclinks a,.rcmore > button{all:unset;cursor:pointer;position:relative;color:var(--muted);font-weight:600;font-size:13.5px;padding:6px 10px;border-radius:8px}
    .rclinks a:hover,.rcmore > button:hover{color:var(--ink);background:var(--raised)}
    .rclinks a[aria-current="page"],.rcmore > button.cur{color:var(--ink);background:var(--raised);box-shadow:inset 0 -2px 0 var(--signal)}
    .rclinks a:focus-visible,.rcmore > button:focus-visible{outline:2px solid var(--signal);outline-offset:2px}
    .rclinks .n{display:inline-block;min-width:17px;margin-left:5px;padding:0 5px;border-radius:9px;background:var(--cut);color:#fff;font-size:11px;line-height:17px;text-align:center}
    .rcmore{position:relative}
    .rcmore > button::after{content:"";display:inline-block;width:6px;height:6px;margin-left:7px;border-right:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:translateY(-3px) rotate(45deg)}
    .rcmenu{position:absolute;top:calc(100% + 8px);left:0;min-width:270px;padding:8px;border-radius:14px;background:var(--raised);border:1px solid var(--line);
      box-shadow:0 18px 40px color-mix(in srgb,#000 30%,transparent);white-space:normal;z-index:50}
    .rcmenu h6{margin:6px 8px 4px;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--faint)}
    .rcmenu a{display:block;padding:8px 10px;border-radius:9px;text-decoration:none;color:var(--ink)}
    .rcmenu a:hover,.rcmenu a:focus-visible{background:var(--surface,var(--paper));outline:none}
    .rcmenu a b{display:block;font-size:13.5px;font-weight:650}
    .rcmenu a span{display:block;font-size:12px;color:var(--muted)}
    .rcmenu a[aria-current="page"]{box-shadow:inset 3px 0 0 var(--signal)}
    .rctools{display:flex;align-items:center;gap:8px}
    .rctools:empty{display:none}
    .rctools select{background:var(--raised);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:4px 8px;font:600 13px var(--font)}
    .rcsp{flex:1}
    .rcnav #healthSlot,.rcnav #alertSlot{flex-shrink:0}
    .rcpage{font-weight:700;font-size:14px;color:var(--muted)}
  </style>`;
  const link = ([p, label]) => `<a href="${p}"${p === here ? ' aria-current="page"' : ""}${p === "/decide.html" ? ' id="rcDecide"' : p === "/needs.html" ? ' id="rcNeeds"' : ""}>${label}</a>`;
  const menu = MORE.map(([g, items]) => `<h6>${g}</h6>` + items.map(([p, label, what]) =>
    `<a href="${p}" role="menuitem"${p === here ? ' aria-current="page"' : ""}><b>${label}</b><span>${what}</span></a>`).join("")).join("");
  const html = phone
    ? `${css}<div class="rcnav"><a class="rcbrand" href="/m.html">‹ Rig Console</a><span class="rcpage">${cur}</span><span class="rcsp"></span><div id="healthSlot" hidden></div><div id="alertSlot" hidden></div></div>`
    : `${css}<div class="rcnav"><a class="rcbrand" href="/" title="Home: the live graph"><img src="/icon.svg" alt="">Rig Console</a>
        <nav class="rclinks" aria-label="Pages">${MAIN.map(link).join("")}
          <div class="rcmore"><button type="button" id="rcMoreBtn" aria-haspopup="true" aria-expanded="false" class="${inMore ? "cur" : ""}">${inMore ? cur : "More"}</button>
            <div class="rcmenu" id="rcMenu" role="menu" hidden>${menu}</div></div></nav>
        <div class="rctools" id="rcTools"></div><span class="rcsp"></span><div id="healthSlot"></div><div id="alertSlot"></div></div>`;
  document.currentScript.insertAdjacentHTML("afterend", html);
  document.addEventListener("DOMContentLoaded", () => {
    const tools = document.getElementById("rcTools");
    if (tools) document.querySelectorAll("[data-rc-tools]").forEach(el => tools.appendChild(el));
    const btn = document.getElementById("rcMoreBtn"), m = document.getElementById("rcMenu");
    if (!btn) return;
    const open = v => { m.hidden = !v; btn.setAttribute("aria-expanded", v); if (v) m.querySelector("a").focus(); };
    btn.onclick = e => { e.stopPropagation(); open(m.hidden); };
    document.addEventListener("click", e => { if (!m.hidden && !m.contains(e.target)) open(false); });
    document.addEventListener("keydown", e => { if (e.key === "Escape" && !m.hidden) { open(false); btn.focus(); } });
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
  // Show how many decisions are waiting, on every page.
  async function gates(){
    const a = document.getElementById("rcDecide"); if (!a || document.hidden) return;
    try {
      const n = ((await (await fetch("/api/gates", {cache: "no-store"})).json()).open || []).length;
      a.innerHTML = "Decisions" + (n ? `<span class="n">${n}</span>` : "");
    } catch {}
  }
  gates(); setInterval(gates, 20000);
  // And how many cards are open on the Needs you page.
  async function needs(){
    const a = document.getElementById("rcNeeds"); if (!a || document.hidden) return;
    try {
      const n = (await (await fetch("/api/needs", {cache: "no-store"})).json()).count;
      a.innerHTML = "Needs you" + (n ? `<span class="n">${n}</span>` : "");
    } catch {}
  }
  needs(); setInterval(needs, 20000);
})();
