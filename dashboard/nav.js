// Shared top bar for every desktop page: same links, same place, same look.
// Include right after <body>: <script src="/nav.js"></script>
// Page-specific controls (e.g. a run picker) can carry data-rc-tools and get moved into the bar.
(() => {
  const PAGES = [["/", "Niche board"], ["/graph.html", "Live graph"], ["/runs.html", "Run report"],
                 ["/decide.html", "Decisions"], ["/play.html", "Play builds"]];
  const here = location.pathname === "/index.html" ? "/" : location.pathname;
  const phone = matchMedia("(max-width: 700px)").matches;
  const cur = (PAGES.find(([p]) => p === here) || [here, document.title])[1];
  const css = `<style>
    :root{--rcnav:50px}
    .rcnav{position:sticky;top:0;z-index:30;height:var(--rcnav);display:flex;align-items:center;gap:6px 18px;padding:0 18px;
      background:color-mix(in srgb,var(--paper) 92%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line);
      font-family:var(--font);white-space:nowrap;overflow-x:auto;scrollbar-width:none}
    .rcnav::-webkit-scrollbar{display:none}
    .rcbrand{font-weight:800;font-size:15px;letter-spacing:-.02em;color:var(--ink);text-decoration:none;margin-right:4px}
    .rclinks{display:flex;align-items:center;gap:4px}
    .rclinks a{position:relative;color:var(--muted);text-decoration:none;font-weight:600;font-size:13.5px;padding:6px 10px;border-radius:8px}
    .rclinks a:hover{color:var(--ink);background:var(--raised)}
    .rclinks a[aria-current="page"]{color:var(--ink);background:var(--raised);box-shadow:inset 0 -2px 0 var(--signal)}
    .rclinks .n{display:inline-block;min-width:17px;margin-left:5px;padding:0 5px;border-radius:9px;background:var(--cut);color:#fff;font-size:11px;line-height:17px;text-align:center}
    .rctools{display:flex;align-items:center;gap:8px}
    .rctools:empty{display:none}
    .rctools select{background:var(--raised);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:4px 8px;font:600 13px var(--font)}
    .rcsp{flex:1}
    .rcnav #healthSlot,.rcnav #alertSlot{flex-shrink:0}
    .rcpage{font-weight:700;font-size:14px;color:var(--muted)}
  </style>`;
  const links = PAGES.map(([p, label]) => `<a href="${p === "/" ? "/?desktop=1" : p}"${p === here ? ' aria-current="page"' : ""}${p === "/decide.html" ? ' id="rcDecide"' : ""}>${label}</a>`).join("");
  const html = phone
    ? `${css}<div class="rcnav"><a class="rcbrand" href="/m.html">‹ Rig Console</a><span class="rcpage">${cur}</span><span class="rcsp"></span><div id="healthSlot" hidden></div><div id="alertSlot" hidden></div></div>`
    : `${css}<div class="rcnav"><a class="rcbrand" href="/?desktop=1">Rig Console</a><nav class="rclinks" aria-label="Pages">${links}</nav><div class="rctools" id="rcTools"></div><span class="rcsp"></span><div id="healthSlot"></div><div id="alertSlot"></div></div>`;
  document.currentScript.insertAdjacentHTML("afterend", html);
  document.addEventListener("DOMContentLoaded", () => {
    const tools = document.getElementById("rcTools");
    if (tools) document.querySelectorAll("[data-rc-tools]").forEach(el => tools.appendChild(el));
  });
  // Show how many decisions are waiting, on every page.
  async function gates(){
    const a = document.getElementById("rcDecide"); if (!a || document.hidden) return;
    try {
      const n = ((await (await fetch("/api/gates", {cache: "no-store"})).json()).open || []).length;
      a.innerHTML = "Decisions" + (n ? `<span class="n">${n}</span>` : "");
    } catch {}
  }
  gates(); setInterval(gates, 20000);
})();
