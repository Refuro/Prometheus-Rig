// Rig Console alerts: desktop notifications, an optional chime, and a count in
// the tab title. Notifies for what the console marks worth it (decisions, the
// operator's notes, real blockers). Shared by the niche board and the live graph.
(() => {
  const KEY = "rigConsoleAlerts";
  const store = { get(){ try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch { return {}; } },
                  set(v){ try { localStorage.setItem(KEY, JSON.stringify(v)); } catch {} } };
  let prefs = Object.assign({ on: false, sound: true }, store.get());
  let first = true;
  const baseTitle = document.title;

  function chime(){
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      [660, 880].forEach((f, i) => {
        const o = ctx.createOscillator(), g = ctx.createGain();
        o.frequency.value = f; o.type = "sine";
        g.gain.setValueAtTime(0.0001, ctx.currentTime + i*0.16);
        g.gain.exponentialRampToValueAtTime(0.18, ctx.currentTime + i*0.16 + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + i*0.16 + 0.3);
        o.connect(g).connect(ctx.destination); o.start(ctx.currentTime + i*0.16); o.stop(ctx.currentTime + i*0.16 + 0.32);
      });
    } catch {}
  }

  function fire(a){
    if (!prefs.on) return;
    if ("Notification" in window && Notification.permission === "granted"){
      const n = new Notification(a.title, { body: a.body || "", tag: a.key });
      n.onclick = () => { window.focus(); if (a.href) location.href = a.href; n.close(); };
    }
    if (prefs.sound) chime();
  }

  // Only alerts the console marks `notify` (decisions, the operator's notes, real blockers) pop up; the rest
  // stay on the page. Each pops up once, and not again if it clears and returns within 6 hours (PL-017).
  const REPEAT_MS = 6 * 3600 * 1000, fired = new Map();
  async function poll(){
    let graph = {}, runs = [];
    try { graph = await (await fetch("/api/graph", {cache:"no-store"})).json(); } catch {}
    try { runs = await (await fetch("/api/runs", {cache:"no-store"})).json(); } catch {}
    const open = (graph.alerts || []).filter(a => !a.dismissed);
    const now = open.filter(a => a.notify).map(a => ({
      key: a.key || `${a.kind}:${a.node}`, title: `${a.notify}: ${a.text}`, body: a.detail || "Open Rig Console to see it.",
      href: a.url || `/graph.html?seat=${encodeURIComponent(a.node)}` }));
    (Array.isArray(runs) ? runs : []).filter(r => r.phase === "checkpoint").forEach(r => now.push({
      key: `checkpoint:${r.run}`, title: `Decision needed: ${r.run} is waiting for you`,
      body: "Pick which niches get a deep dive.", href: `/?run=${encodeURIComponent(r.run)}` }));
    const t = Date.now();
    const fresh = now.filter(a => !fired.has(a.key));
    now.forEach(a => fired.set(a.key, t));            // still there: keep it quiet
    for (const [k, at] of fired) if (t - at > REPEAT_MS) fired.delete(k);
    if (!first){
      if (fresh.length === 1) fire(fresh[0]);
      else if (fresh.length > 1) fire({key: "batch", title: `${fresh.length} things need you`, body: fresh.map(a => a.title).slice(0, 5).join("\n"), href: "/graph.html"});
    }
    first = false;
    const need = open.filter(a => a.act).length;   // the count is what needs you, not diagnostics
    document.title = need ? `(${need}) ${baseTitle}` : baseTitle;
    render(need);
  }

  // Small control: "Turn on alerts" / alerts on, with a sound toggle.
  const box = document.createElement("div");
  box.className = "alertctl";
  box.innerHTML = `<style>
    .alertctl{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--muted)}
    .alertctl button{all:unset;cursor:pointer;padding:6px 10px;border-radius:8px;border:1px solid var(--line);color:var(--ink);font-weight:600;font-size:13px}
    .alertctl button:hover{background:var(--paper)}
    .alertctl button:focus-visible{outline:2px solid var(--signal);outline-offset:2px}
    .alertctl .on{border-color:color-mix(in srgb,var(--advance) 60%,transparent)}
    .alertctl label{display:flex;align-items:center;gap:5px;cursor:pointer}
  </style><button type="button" id="alertBtn"></button><label title="Play a sound with alerts"><input type="checkbox" id="alertSound"><svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true"><path d="M2 6h3l4-3v10l-4-3H2z" fill="currentColor"/><path d="M11 5.5a3.5 3.5 0 0 1 0 5M12.8 3.6a6 6 0 0 1 0 8.8" stroke="currentColor" fill="none" stroke-width="1.4" stroke-linecap="round"/></svg><span style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">Sound</span></label>`;
  function render(){
    const b = box.querySelector("#alertBtn"), s = box.querySelector("#alertSound");
    const denied = "Notification" in window && Notification.permission === "denied";
    b.textContent = prefs.on ? "Alerts on" : denied ? "Alerts blocked" : "Turn on alerts";
    b.classList.toggle("on", prefs.on);
    b.title = denied ? "Allow notifications for localhost in your browser's site settings" : "";
    s.checked = prefs.sound; s.parentElement.style.display = prefs.on ? "" : "none";
  }
  box.querySelector("#alertBtn").onclick = async () => {
    if (prefs.on){ prefs.on = false; }
    else {
      if ("Notification" in window && Notification.permission === "default") await Notification.requestPermission();
      prefs.on = true; chime();
    }
    store.set(prefs); render();
  };
  box.querySelector("#alertSound").onchange = e => { prefs.sound = e.target.checked; store.set(prefs); };
  window.addEventListener("DOMContentLoaded", () => {
    (document.getElementById("alertSlot") || document.body).appendChild(box);
    render(); poll(); setInterval(poll, 10000);
  });
})();
