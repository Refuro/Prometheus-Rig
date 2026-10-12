// Rig Console alerts: desktop notifications, an optional chime, and a count in
// the tab title whenever an agent needs approval, gets stuck, or a run reaches
// a checkpoint. Shared by the niche board and the live graph.
(() => {
  const KEY = "rigConsoleAlerts";
  const store = { get(){ try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch { return {}; } },
                  set(v){ try { localStorage.setItem(KEY, JSON.stringify(v)); } catch {} } };
  let prefs = Object.assign({ on: false, sound: true }, store.get());
  const seen = new Set();
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

  async function poll(){
    let graph = {}, runs = [];
    try { graph = await (await fetch("/api/graph", {cache:"no-store"})).json(); } catch {}
    try { runs = await (await fetch("/api/runs", {cache:"no-store"})).json(); } catch {}
    const now = [];
    (graph.alerts || []).filter(a => !a.dismissed).forEach(a => now.push({
      key: `${a.kind}:${a.node}`, title: a.text, body: a.detail || "Open Rig Console to see it.",
      href: a.url || `/graph.html?seat=${encodeURIComponent(a.node)}` }));
    (Array.isArray(runs) ? runs : []).filter(r => r.phase === "checkpoint").forEach(r => now.push({
      key: `checkpoint:${r.run}`, title: `${r.run} is waiting for your decision`,
      body: "Pick which niches get a deep dive.", href: `/?run=${encodeURIComponent(r.run)}` }));
    const keys = new Set(now.map(a => a.key));
    if (!first) now.filter(a => !seen.has(a.key)).forEach(fire);
    // forget resolved alerts so they notify again if they come back
    [...seen].forEach(k => { if (!keys.has(k)) seen.delete(k); });
    keys.forEach(k => seen.add(k));
    first = false;
    document.title = now.length ? `(${now.length}) ${baseTitle}` : baseTitle;
    render(now.length);
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
  </style><button type="button" id="alertBtn"></button><label><input type="checkbox" id="alertSound"> Sound</label>`;
  function render(){
    const b = box.querySelector("#alertBtn"), s = box.querySelector("#alertSound");
    const denied = "Notification" in window && Notification.permission === "denied";
    b.textContent = prefs.on ? "Alerts on" : denied ? "Notifications blocked" : "Turn on alerts";
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
