// charset: utf-8
/* Washer ML dashboard panel – vanilla web component, no build step. */
const L = {
  en: {
    title: "Washer ML", idle: "Ready", running: "Running", ending: "Finishing…", power: "Power", program: "Program",
    remaining: "Remaining", min: "min", progress: "Progress", recognizing: "recognising…",
    graph24: "Power – last 3 hours", graphLive: "Current cycle vs. learned program",
    live: "Current cycle", learnedCurve: "Learned program", noRun: "No program running. The live comparison appears when a program starts.",
    programs: "Learned programs", noPrograms: "Nothing learned yet – press “Learn from history” or run a program.",
    cycles: "Runs", save: "Save", del: "Delete", rename: "Rename", cfg: "Configuration", sensor: "Power sensor",
    startW: "Start threshold (W)", endW: "Quiet threshold (W)", minCycle: "Minimum program length (min)",
    quiet: "Learned quiet time before “finished”", learnBtn: "Learn from history", days: "days",
    reset: "Reset learning", resetConfirm: "Delete everything that was learned?", saved: "Saved", learning: "Learning…",
    done: "Done", runs: "runs", started: "Started", duration: "Duration", energy: "Energy", pickSensor: "Select power sensor…",
    delConfirm: "Delete this program and its runs?", thresholds: "thresholds", energyShort: "kWh",
  },
  de: {
    title: "Washer ML", idle: "Bereit", running: "Läuft", ending: "Endet gleich…", power: "Leistung", program: "Programm",
    remaining: "Restzeit", min: "Min", progress: "Fortschritt", recognizing: "wird erkannt…",
    graph24: "Leistung – letzte 3 Stunden", graphLive: "Aktueller Lauf vs. gelerntes Programm",
    live: "Aktueller Lauf", learnedCurve: "Gelerntes Programm", noRun: "Kein Programm aktiv. Der Live-Vergleich erscheint beim Start.",
    programs: "Gelernte Programme", noPrograms: "Noch nichts gelernt – „Aus Verlauf lernen“ drücken oder ein Programm laufen lassen.",
    cycles: "Läufe", save: "Speichern", del: "Löschen", rename: "Umbenennen", cfg: "Konfiguration", sensor: "Leistungssensor",
    startW: "Start-Schwelle (W)", endW: "Ruhe-Schwelle (W)", minCycle: "Mindestlaufzeit (Min)",
    quiet: "Gelernte Ruhezeit bis „fertig“", learnBtn: "Aus Verlauf lernen", days: "Tage",
    reset: "Lernen zurücksetzen", resetConfirm: "Alles Gelernte löschen?", saved: "Gespeichert", learning: "Lerne…",
    done: "Fertig", runs: "Läufe", started: "Start", duration: "Dauer", energy: "Energie", pickSensor: "Leistungssensor wählen…",
    delConfirm: "Programm und zugehörige Läufe löschen?", thresholds: "Schwellen", energyShort: "kWh",
  },
};

const STYLE = `
:host{display:block;background:var(--primary-background-color);color:var(--primary-text-color);min-height:100vh;
  font-family:var(--paper-font-body1_-_font-family,Roboto,sans-serif)}
.wrap{max-width:1100px;margin:0 auto;padding:16px}
header{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:12px}
header h1{margin:0;font-size:22px;font-weight:500;flex:1}
.chip{padding:4px 12px;border-radius:14px;font-size:13px;font-weight:600;background:var(--secondary-background-color)}
.chip.run{background:var(--primary-color);color:#fff}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:16px}
@media(max-width:520px){.grid{grid-template-columns:1fr}.wrap{padding:10px}}
.card{background:var(--card-background-color);border-radius:12px;padding:16px;box-shadow:var(--ha-card-box-shadow,0 1px 3px rgba(0,0,0,.2))}
.card.wide{grid-column:1/-1}
.card h2{margin:0 0 10px;font-size:16px;font-weight:500}
.stats{display:flex;gap:24px;flex-wrap:wrap}
.stat .v{font-size:26px;font-weight:500}.stat .k{font-size:12px;color:var(--secondary-text-color)}
svg{width:100%;height:auto;display:block}
.axis{stroke:var(--divider-color);stroke-width:1}.lbl{fill:var(--secondary-text-color);font-size:10px}
.legend{display:flex;gap:16px;font-size:12px;color:var(--secondary-text-color);margin-top:4px;flex-wrap:wrap}
.legend i{display:inline-block;width:14px;height:3px;margin-right:6px;vertical-align:middle}
.prog{display:grid;grid-template-columns:130px 1fr auto;gap:10px;align-items:center;padding:8px 0;border-top:1px solid var(--divider-color)}
.prog:first-of-type{border-top:0}
.prog .meta{font-size:12px;color:var(--secondary-text-color)}
input,select{background:var(--secondary-background-color);color:var(--primary-text-color);border:1px solid var(--divider-color);
  border-radius:8px;padding:8px;font-size:14px;width:100%;box-sizing:border-box}
label{display:block;font-size:12px;color:var(--secondary-text-color);margin:10px 0 4px}
button{background:var(--primary-color);color:#fff;border:0;border-radius:8px;padding:9px 16px;font-size:14px;cursor:pointer;margin:8px 8px 0 0}
button.sec{background:var(--secondary-background-color);color:var(--primary-text-color)}
button.danger{background:var(--error-color,#db4437)}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:6px 4px;border-top:1px solid var(--divider-color)}
th{color:var(--secondary-text-color);font-weight:500;border-top:0}
.row{display:flex;gap:8px;align-items:center}.row input{flex:1}
.msg{font-size:13px;color:var(--secondary-text-color);margin-top:8px;min-height:18px}
.empty{color:var(--secondary-text-color);font-size:13px;padding:12px 0}
`;

function chart({series, w = 520, h = 190, xMax, yMax, xFmt, lines = [], shade}) {
  const pad = {l: 38, r: 8, t: 8, b: 20};
  const iw = w - pad.l - pad.r, ih = h - pad.t - pad.b;
  const all = series.flatMap(s => s.pts.map(p => p[1]));
  const ym = yMax || Math.max(100, ...all) * 1.08;
  const xs = xMax || Math.max(1, ...series.flatMap(s => s.pts.map(p => p[0])));
  // square-root y scale: keeps the 20-50 W standby/tail details visible next to 2000 W heating
  const X = x => pad.l + (x / xs) * iw, Y = y => pad.t + ih - Math.sqrt(Math.max(0, Math.min(y, ym)) / ym) * ih;
  let g = "";
  for (const y of [0, 50, 200, 500, 1000, 2000].filter(v => v <= ym)) {
    g += `<line class="axis" x1="${pad.l}" x2="${w - pad.r}" y1="${Y(y)}" y2="${Y(y)}" opacity=".5"/>` +
         `<text class="lbl" x="${pad.l - 4}" y="${Y(y) + 3}" text-anchor="end">${y}</text>`;
  }
  for (let i = 0; i <= 4; i++) {
    const x = xs * i / 4;
    g += `<text class="lbl" x="${X(x)}" y="${h - 5}" text-anchor="middle">${xFmt ? xFmt(x) : Math.round(x)}</text>`;
  }
  (shade || []).forEach(([a, b]) => {
    g += `<rect x="${X(a)}" y="${pad.t}" width="${Math.max(1, X(b) - X(a))}" height="${ih}" fill="var(--primary-color)" opacity=".12"/>`;
  });
  lines.forEach(l => {
    g += `<line x1="${pad.l}" x2="${w - pad.r}" y1="${Y(l.y)}" y2="${Y(l.y)}" stroke="${l.color}" stroke-dasharray="4 4" opacity=".7"/>` +
         `<text class="lbl" x="${w - pad.r}" y="${Y(l.y) - 3}" text-anchor="end" fill="${l.color}">${l.label}</text>`;
  });
  series.forEach(s => {
    if (!s.pts.length) return;
    const d = s.pts.map((p, i) => `${i ? "L" : "M"}${X(p[0]).toFixed(1)},${Y(p[1]).toFixed(1)}`).join("");
    g += `<path d="${d}" fill="none" stroke="${s.color}" stroke-width="${s.width || 1.6}" ${s.dash ? `stroke-dasharray="${s.dash}"` : ""} stroke-linejoin="round"/>`;
  });
  return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="xMidYMid meet">${g}</svg>`;
}

function spark(curve, color = "var(--primary-color)") {
  if (!curve || !curve.length) return "";
  const w = 300, h = 44, m = Math.max(50, ...curve);
  const d = curve.map((v, i) => `${i ? "L" : "M"}${(i / Math.max(1, curve.length - 1) * w).toFixed(1)},${(h - 2 - Math.sqrt(v / m) * (h - 4)).toFixed(1)}`).join("");
  return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" style="height:44px"><path d="${d}" fill="none" stroke="${color}" stroke-width="1.5"/></svg>`;
}

class WasherMLPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({mode: "open"});
    this._snap = []; this._sel = 0; this._hist = []; this._msg = {}; this._busy = false;
    this._editing = false;
  }
  set hass(h) {
    const first = !this._hass;
    this._hass = h;
    if (first) { this._start(); }
  }
  set narrow(_) {} set panel(_) {} set route(_) {}
  get t() { return L[(this._hass?.language || "en").slice(0, 2)] || L.en; }
  connectedCallback() { if (this._hass && !this._timer) this._start(); }
  disconnectedCallback() { clearInterval(this._timer); this._timer = null; }

  _start() {
    this._refresh(true);
    this._timer = setInterval(() => this._refresh(false), 5000);
  }

  async _refresh(full) {
    try {
      this._snap = await this._hass.callWS({type: "washer_ml/snapshot"});
      const s = this._snap[this._sel];
      if (s && (full || !this._histAt || Date.now() - this._histAt > 60000)) await this._loadHistory(s);
    } catch (e) { this._error = String(e.message || e); }
    if (!this._editing) this._render();
  }

  async _loadHistory(s) {
    const end = new Date(), start = new Date(end - 3 * 3600 * 1000);
    try {
      const r = await this._hass.callWS({type: "history/history_during_period", start_time: start.toISOString(),
        end_time: end.toISOString(), entity_ids: [s.power_entity], include_start_time_state: true,
        significant_changes_only: false, minimal_response: true, no_attributes: true});
      const rows = r[s.power_entity] || [];
      this._hist = rows.map(x => {
        const ts = x.lu !== undefined ? x.lu : Date.parse(x.last_updated) / 1000;
        return [Math.max(ts, start / 1000), parseFloat(x.s !== undefined ? x.s : x.state)];
      }).filter(p => isFinite(p[1]));
      this._histRange = [start / 1000, end / 1000];
      this._histAt = Date.now();
    } catch (e) { this._hist = []; }
  }

  async _call(service, data, busyMsg) {
    this._msg = {text: busyMsg || ""}; this._render();
    try { await this._hass.callService("washer_ml", service, data); this._msg = {text: this.t.done}; }
    catch (e) { this._msg = {text: String(e.message || e), err: true}; }
    await this._refresh(true);
  }

  _render() {
    const t = this.t, s = this._snap[this._sel];
    const root = this.shadowRoot;
    if (!s) {
      root.innerHTML = `<style>${STYLE}</style><div class="wrap"><header><h1>${t.title}</h1></header>
        <div class="card"><div class="empty">${this._error || "…"}<br>Settings → Devices &amp; services → Add integration → Washer ML</div></div></div>`;
      return;
    }
    const mt = s.live?.match;
    const confident = mt && mt.confidence >= 0.3;
    const status = !s.running ? t.idle : (s.live?.quiet_since ? t.ending : t.running);
    const hist = (this._histRange && this._hist.length) ? this._hist : [];
    // power graph (last 3 h) as step line
    let pts = [], shade = [];
    if (hist.length) {
      const [t0, t1] = this._histRange;
      hist.forEach((p, i) => {
        pts.push([(p[0] - t0) / 60, p[1]]);
        const nx = hist[i + 1] ? hist[i + 1][0] : t1;
        pts.push([(nx - t0) / 60, p[1]]);
      });
    }
    const fmtAgo = x => { const m = 180 - x; return m < 1 ? "now" : `-${Math.round(m)} ${t.min}`; };
    const g1 = chart({series: [{pts, color: "var(--primary-color)"}], xMax: 180, xFmt: fmtAgo,
      lines: s.config.start_w === s.config.end_w
        ? [{y: s.config.end_w, color: "#fb8c00", label: `start/end ${s.config.end_w} W`}]
        : [{y: s.config.start_w, color: "#43a047", label: `start ${s.config.start_w} W`},
           {y: s.config.end_w, color: "#fb8c00", label: `quiet ${s.config.end_w} W`}], shade});
    // live comparison
    let g2 = `<div class="empty">${t.noRun}</div>`;
    if (s.live) {
      const ser = [{pts: s.live.series.map((v, i) => [i, v]), color: "var(--primary-color)", width: 2}];
      if (s.live.prototype) ser.push({pts: s.live.prototype.map((v, i) => [i, v]), color: "#fb8c00", dash: "5 4"});
      g2 = chart({series: ser, xFmt: x => `${Math.round(x)}`, xMax: Math.max(s.live.series.length, (s.live.prototype || []).length, 10)}) +
        `<div class="legend"><span><i style="background:var(--primary-color)"></i>${t.live}</span>` +
        (s.live.prototype ? `<span><i style="background:#fb8c00"></i>${t.learnedCurve}${confident ? " · " + mt.name : ""}</span>` : "") + `<span>${t.min}</span></div>`;
    }
    const progs = s.programs.length ? s.programs.map(p => `
      <div class="prog"><div>${spark(p.curve)}</div>
        <div><input data-rename="${p.id}" value="${p.name.replace(/"/g, "&quot;")}"><div class="meta">${p.id} · ${p.count} ${t.runs} · ${p.duration_min} ${t.min} · ${(p.energy_wh / 1000).toFixed(2)} ${t.energyShort}</div></div>
        <div><button class="sec" data-save="${p.id}">${t.save}</button><button class="danger" data-del="${p.id}">${t.del}</button></div></div>`).join("")
      : `<div class="empty">${t.noPrograms}</div>`;
    const cyc = s.history.length ? `<table><tr><th>${t.started}</th><th>${t.program}</th><th>${t.duration}</th><th>${t.energy}</th></tr>` +
      s.history.map(h => `<tr><td>${new Date((h.end - h.duration_s) * 1000).toLocaleString([], {dateStyle: "short", timeStyle: "short"})}</td><td>${h.name}</td><td>${Math.round(h.duration_s / 60)} ${t.min}</td><td>${(h.energy_wh / 1000).toFixed(2)} ${t.energyShort}</td></tr>`).join("") + "</table>"
      : `<div class="empty">–</div>`;
    const powers = Object.keys(this._hass.states).filter(e => e.startsWith("sensor.") &&
      (this._hass.states[e].attributes.device_class === "power" || this._hass.states[e].attributes.unit_of_measurement === "W")).sort();
    if (!powers.includes(s.power_entity)) powers.unshift(s.power_entity);
    const opts = powers.map(e => `<option value="${e}" ${e === s.power_entity ? "selected" : ""}>${this._hass.states[e]?.attributes.friendly_name || e} (${e})</option>`).join("");
    const sel = this._snap.length > 1 ? `<select id="dev" style="width:auto">${this._snap.map((x, i) => `<option value="${i}" ${i === this._sel ? "selected" : ""}>${x.name}</option>`).join("")}</select>` : "";

    root.innerHTML = `<style>${STYLE}</style><div class="wrap">
      <header><h1>${t.title} · ${s.name}</h1>${sel}<span class="chip ${s.running ? "run" : ""}">${status}</span></header>
      <div class="grid">
        <div class="card wide"><div class="stats">
          <div class="stat"><div class="v">${s.power === null ? "–" : Math.round(s.power) + " W"}</div><div class="k">${t.power}</div></div>
          <div class="stat"><div class="v">${s.running ? (confident ? mt.name : t.recognizing) : "–"}</div><div class="k">${t.program}</div></div>
          <div class="stat"><div class="v">${s.running && confident ? Math.round(mt.remaining_s / 60) + " " + t.min : "–"}</div><div class="k">${t.remaining}</div></div>
          <div class="stat"><div class="v">${s.running && confident ? Math.round(mt.progress * 100) + " %" : "–"}</div><div class="k">${t.progress}</div></div>
        </div></div>
        <div class="card"><h2>${t.graph24}</h2>${g1}</div>
        <div class="card"><h2>${t.graphLive}</h2>${g2}</div>
        <div class="card"><h2>${t.programs}</h2>${progs}</div>
        <div class="card"><h2>${t.cfg}</h2>
          <label>${t.sensor}</label><select id="sensor">${opts}</select>
          <div class="row"><div style="flex:1"><label>${t.startW}</label><input id="sw" type="number" min="1" value="${s.config.start_w}"></div>
          <div style="flex:1"><label>${t.endW}</label><input id="ew" type="number" min="1" value="${s.config.end_w}"></div></div>
          <label>${t.minCycle}</label><input id="mc" type="number" min="1" value="${s.config.min_cycle_min}">
          <button id="savecfg">${t.save}</button>
          <hr style="border:0;border-top:1px solid var(--divider-color);margin:16px 0 4px">
          <div class="k" style="font-size:12px;color:var(--secondary-text-color)">${t.quiet}: <b>${s.end_delay_s} s</b></div>
          <div class="row" style="margin-top:8px"><input id="days" type="number" min="1" max="365" value="30" style="max-width:90px"><span>${t.days}</span>
            <button id="learn" style="margin:0">${t.learnBtn}</button></div>
          <button id="reset" class="danger">${t.reset}</button>
          <div class="msg ${this._msg.err ? "err" : ""}">${this._msg.text || ""}</div>
        </div>
        <div class="card wide"><h2>${t.cycles}</h2>${cyc}</div>
      </div></div>`;

    const $ = q => root.querySelector(q);
    root.querySelectorAll("input,select").forEach(el => {
      el.addEventListener("focus", () => this._editing = true);
      el.addEventListener("blur", () => this._editing = false);
    });
    $("#dev")?.addEventListener("change", e => { this._sel = +e.target.value; this._histAt = 0; this._refresh(true); });
    $("#savecfg").onclick = async () => {
      try {
        await this._hass.callWS({type: "washer_ml/configure", entry_id: s.entry_id, power_entity: $("#sensor").value,
          start_w: +$("#sw").value, end_w: +$("#ew").value, min_cycle_min: +$("#mc").value});
        this._msg = {text: t.saved};
        setTimeout(() => this._refresh(true), 1500);
      } catch (e) { this._msg = {text: String(e.message || e), err: true}; }
      this._editing = false; this._render();
    };
    $("#learn").onclick = () => { this._editing = false; this._call("learn_from_history", {entry_id: s.entry_id, days: +$("#days").value}, t.learning); };
    $("#reset").onclick = () => { if (confirm(t.resetConfirm)) this._call("reset_learning", {entry_id: s.entry_id}); };
    root.querySelectorAll("[data-save]").forEach(b => b.onclick = () => {
      const id = b.dataset.save; this._editing = false;
      this._call("rename_program", {entry_id: s.entry_id, program_id: id, name: root.querySelector(`[data-rename="${id}"]`).value});
    });
    root.querySelectorAll("[data-del]").forEach(b => b.onclick = () => {
      if (confirm(t.delConfirm)) this._call("delete_program", {entry_id: s.entry_id, program_id: b.dataset.del});
    });
  }
}
customElements.define("washer-ml-panel", WasherMLPanel);
