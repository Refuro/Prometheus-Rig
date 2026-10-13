// Health: is the plumbing up? Shared by every Rig Console page.
// In the desktop top bar it's one pill ("All OK" / "2 issues") that opens the full list;
// anywhere else (the phone view's "System health" section) it's the full list.
(() => {
  const NAMES = {logger: "Snapshot logger", daemon: "OpenRig", alerts: "Alerts", push: "Phone push", ollama: "Ollama", disk: "Disk", keepalive: "Keep-alive", ubuntu: "Ubuntu", dashboard: "Dashboard", isolation: "Console isolation", token: "Console token", hostname: "Tailscale name"};
  // level: required (default) turns the pill red; advisory turns it amber; optional just shows "off".
  const tier = v => v.ok ? "ok" : v.level === "optional" ? "off" : v.level === "advisory" ? "warn" : "bad";
  const SHORT = {logger: "Logger", daemon: "OpenRig", keepalive: "keepalive"};
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const box = document.createElement("div");
  box.className = "health";
  box.innerHTML = `<style>
    .health{position:relative;display:flex;flex-wrap:wrap;gap:6px 12px;font-size:12px;color:var(--muted)}
    .health > span{display:inline-flex;align-items:center;gap:5px;white-space:nowrap}
    .health i{width:7px;height:7px;border-radius:50%;background:#3cb371;flex:none}
    .health span.bad{color:var(--cut, #c2412b);font-weight:600}
    .health span.bad i,.health .hp.bad i,.health li.bad i{background:var(--cut, #c2412b)}
    .health span.warn i,.health .hp.warn i,.health li.warn i{background:var(--signal, #c98200)}
    .health span.off i,.health li.off i{background:var(--idle, #8a94a4)}
    .health span.off{opacity:.7}
    .health .hp.warn{color:var(--signal, #c98200);border-color:color-mix(in srgb,var(--signal, #c98200) 45%,transparent)}
    .health .hl li.warn b{color:var(--signal, #c98200)}
    .health .hp{all:unset;cursor:pointer;display:inline-flex;align-items:center;gap:7px;font-size:12.5px;font-weight:650;color:var(--muted);padding:5px 10px;border-radius:999px;border:1px solid var(--line)}
    .health .hp:hover{color:var(--ink)}
    .health .hp.bad{color:var(--cut, #c2412b);border-color:color-mix(in srgb,var(--cut, #c2412b) 45%,transparent);background:var(--cut-soft, transparent)}
    .health .hp:focus-visible{outline:2px solid var(--signal);outline-offset:2px}
    .health .hl{position:absolute;right:0;top:calc(100% + 8px);width:300px;margin:0;padding:8px;list-style:none;border-radius:14px;background:var(--raised);border:1px solid var(--line);
      box-shadow:0 18px 40px color-mix(in srgb,#000 30%,transparent);white-space:normal;z-index:50}
    .health .hl[hidden]{display:none}
    .health .hl li{display:grid;grid-template-columns:10px 1fr;gap:2px 10px;padding:7px 8px;border-radius:9px}
    .health .hl li i{margin-top:5px}
    .health .hl li b{font-size:13px;color:var(--ink)}
    .health .hl li span{grid-column:2;font-size:12px;color:var(--muted)}
    .health .hl li.bad b{color:var(--cut, #c2412b)}
  </style>`;
  let compact = false, h = {};
  function draw(){
    box.querySelectorAll(":scope > span, :scope > .hp, :scope > .hl").forEach(n => n.remove());
    const rows = Object.entries(h);
    if (!compact) {
      rows.forEach(([k, v]) => {
        const s = document.createElement("span");
        const t = tier(v); s.className = t === "ok" ? "" : t; s.title = v.detail || "";
        s.innerHTML = `<i></i>${esc(SHORT[k] || NAMES[k] || k)}`;
        box.appendChild(s);
      });
      return;
    }
    const bad = rows.filter(([, v]) => tier(v) === "bad"), warn = rows.filter(([, v]) => tier(v) === "warn");
    const b = document.createElement("button");
    b.type = "button"; b.className = "hp" + (bad.length ? " bad" : warn.length ? " warn" : "");
    b.setAttribute("aria-expanded", "false");
    b.title = bad.concat(warn).length ? bad.concat(warn).map(([k, v]) => `${NAMES[k] || k}: ${v.detail}`).join("\n") : "Everything the console depends on is up";
    b.innerHTML = `<i></i>${bad.length ? `${bad.length} ${bad.length === 1 ? "issue" : "issues"}` : warn.length ? `${warn.length} to check` : "All OK"}`;
    const list = document.createElement("ul");
    list.className = "hl"; list.hidden = true;
    const rank = {bad: 0, warn: 1, off: 3, ok: 2};
    list.innerHTML = rows.sort((a, c) => rank[tier(a[1])] - rank[tier(c[1])]).map(([k, v]) =>
      `<li class="${tier(v) === "ok" ? "" : tier(v)}"><i></i><b>${esc(NAMES[k] || k)}</b><span>${esc(v.detail || (v.ok ? "OK" : "Problem"))}</span></li>`).join("");
    b.onclick = e => { e.stopPropagation(); list.hidden = !list.hidden; b.setAttribute("aria-expanded", !list.hidden); };
    box.append(b, list);
  }
  document.addEventListener("click", e => { const l = box.querySelector(".hl"); if (l && !l.hidden && !box.contains(e.target)) l.hidden = true; });
  document.addEventListener("keydown", e => { const l = box.querySelector(".hl"); if (e.key === "Escape" && l && !l.hidden) l.hidden = true; });
  async function poll(){
    const open = !!box.querySelector(".hl:not([hidden])");
    try { h = await (await fetch("/api/health", {cache:"no-store"})).json(); } catch { h = {dashboard:{ok:false, detail:"server not reachable"}}; }
    draw();
    if (open) box.querySelector(".hl").hidden = false;
  }
  window.addEventListener("DOMContentLoaded", () => {
    const slot = document.getElementById("healthSlot");
    compact = !!(slot && slot.closest(".rcnav"));
    (slot || document.body).appendChild(box);
    poll(); setInterval(poll, 30000);
  });
})();
