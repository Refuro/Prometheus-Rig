// Health strip: is the plumbing up? Shared by every Rig Console page.
(() => {
  const NAMES = {logger: "Logger", daemon: "OpenRig", ollama: "Ollama", disk: "Disk", ubuntu: "Ubuntu"};
  const box = document.createElement("div");
  box.className = "health";
  box.innerHTML = `<style>
    .health{display:flex;flex-wrap:wrap;gap:6px 12px;font-size:12px;color:var(--muted)}
    .health span{display:inline-flex;align-items:center;gap:5px;white-space:nowrap}
    .health i{width:7px;height:7px;border-radius:50%;background:#3cb371}
    .health span.bad{color:var(--cut, #c2412b);font-weight:600}
    .health span.bad i{background:var(--cut, #c2412b)}
  </style>`;
  async function poll(){
    let h = {};
    try { h = await (await fetch("/api/health", {cache:"no-store"})).json(); } catch { h = {dashboard:{ok:false, detail:"server not reachable"}}; }
    box.querySelectorAll("span").forEach(s => s.remove());
    Object.entries(h).forEach(([k, v]) => {
      const s = document.createElement("span");
      s.className = v.ok ? "" : "bad"; s.title = v.detail || "";
      s.innerHTML = `<i></i>${NAMES[k] || k}`;
      box.appendChild(s);
    });
  }
  window.addEventListener("DOMContentLoaded", () => {
    (document.getElementById("healthSlot") || document.body).appendChild(box);
    poll(); setInterval(poll, 30000);
  });
})();
