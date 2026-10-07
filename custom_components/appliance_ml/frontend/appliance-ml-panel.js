// charset: utf-8
/* Appliance ML dashboard panel – vanilla web component, no build step. */
const L = {
  en: {
    title: "Appliance ML", idle: "Ready", running: "Running", ending: "Finishing…", power: "Power", program: "Program",
    remaining: "Remaining", min: "min", progress: "Progress", recognizing: "recognising…",
    graph24: "Power – last 3 hours", graphLive: "Current cycle vs. learned program",
    live: "Current cycle", learnedCurve: "Learned program", noRun: "No program running. The live comparison appears when a program starts.",
    programs: "Learned programs", noPrograms: "Nothing learned yet – press “Learn from history” or run a program.",
    cycles: "Runs", save: "Save", del: "Delete", rename: "Rename", cfg: "Configuration", sensor: "Power sensor",
    startW: "Start threshold (W)", endW: "Quiet threshold (W)", minCycle: "Minimum program length (min)", maxEnd: "Max. quiet time before finished (min)",
    quiet: "Learned quiet time before “finished”", learnBtn: "Learn from history", days: "days",
    reset: "Reset learning", resetConfirm: "Delete everything that was learned?", saved: "Saved", learning: "Learning…",
    done: "Done", runs: "runs", started: "Started", duration: "Duration", energy: "Energy", pickSensor: "Select power sensor…",
    delConfirm: "Delete this program and its runs?", thresholds: "thresholds", energyShort: "kWh",
    activity: "Run-state entity", activeStates: "States meaning running (comma separated)", totalPower: "House total power sensor",
    programEntity: "Program entity (optional)", estNote: "Estimated mode: no power meter – energy is learned from the house power and the run state.",
    health: "Health", healthOk: "OK – everything looks normal", healthLearning: "Learning what is normal", healthProblem: "Needs attention",
    energy24: "Energy 24 h", usual: "usual", duty24: "Compressor duty 24 h", starts24: "Compressor starts 24 h", baseW: "Base / standby power",
    daily30: "Energy per rolling 24 h – last 30 days", refDays: "reference days", baseload: "House base load (lowest power)",
    baseline: "House baseline", estEnergy: "Estimated energy (total)", disturbed: "disturbed by other loads (not learned)",
    onW: "On threshold (W)", wSearch: "Search by name, device or entity id…", wShowAll: "Show all entities (not only power sensors)",
    tabOverview: "Overview", tabLearned: "What it learned", tabSettings: "Settings", addAppliance: "+ Add appliance",
    wTitle: "Add an appliance", wStep: "Step", wOf: "of", wWhat: "What do you want to track?", wName: "Name", next: "Next", back: "Back",
    wHow: "How is the power measured?", wPlug: "Smart plug with power measurement", wPlugSub: "Best accuracy. Any plug that reports watts (Shelly, Tasmota, Zigbee, TP-Link, Fritz!DECT…).",
    wNoPlug: "No plug – use the appliance's own status", wNoPlugSub: "For built-in machines (e.g. Home Connect dishwasher): the run state plus your house power is enough; the energy is learned.",
    recommended: "recommended", wPickPlug: "Pick the plug of this appliance",
    wTip: "Tip: switch the appliance on for a moment – the sensor whose value jumps is its plug. Values update live.",
    wNoSensors: "Nothing found. Tick “Show all entities”, change the search, or first add your plug to Home Assistant.",
    wPickState: "Entity that says the appliance is running", wPickHouse: "House total power sensor", wPickProgram: "Program name entity (optional, makes recognition exact)",
    none: "– none –", wStates: "States meaning “running”", wCreate: "Create", wDone: "Appliance added.",
    wDoneText: "Now just use the appliance as usual. It starts learning immediately: after the first complete run the program appears under “What it learned”. Existing history from the recorder is imported automatically.",
    wOpen: "Open dashboard", wCancel: "Cancel", remove: "Remove appliance", removeConfirm: "Remove this appliance and everything it learned?",
    lSummary: "What the ML has learned", lPrograms: "programs", lRuns: "runs observed", lQuiet: "quiet time before “finished”", lTypical: "typical run",
    lWhy: "Learning progress", lNone: "Nothing learned yet. Run the appliance once – after the first complete run the program shows up here with its power curve. The more runs, the better the recognition and the remaining-time estimate.",
    lCurve: "Typical power curve (median) with spread (10–90 %)", lDur: "Duration per run", lEn: "Energy per run", lLast: "last run",
    lConf1: "First run – recognition becomes reliable after 2–3 runs", lConfN: "Reliable", lMin: "min", lWh: "Wh", lHelp: "Rename a program so notifications show its real name (e.g. “Eco 50 °C”).",
    needPlug: "Choose a plug / sensor first.", needEstimated: "Choose the run-state entity and the house power sensor.", creating: "Creating…",
    typeNames: {washing_machine: "Washing machine", dishwasher: "Dishwasher", dryer: "Tumble dryer", oven: "Oven", other: "Other appliance", fridge: "Fridge / freezer (health)", baseload: "House base load (health)"},
  },
  de: {
    title: "Appliance ML", idle: "Bereit", running: "Läuft", ending: "Endet gleich…", power: "Leistung", program: "Programm",
    remaining: "Restzeit", min: "Min", progress: "Fortschritt", recognizing: "wird erkannt…",
    graph24: "Leistung – letzte 3 Stunden", graphLive: "Aktueller Lauf vs. gelerntes Programm",
    live: "Aktueller Lauf", learnedCurve: "Gelerntes Programm", noRun: "Kein Programm aktiv. Der Live-Vergleich erscheint beim Start.",
    programs: "Gelernte Programme", noPrograms: "Noch nichts gelernt – „Aus Verlauf lernen“ drücken oder ein Programm laufen lassen.",
    cycles: "Läufe", save: "Speichern", del: "Löschen", rename: "Umbenennen", cfg: "Konfiguration", sensor: "Leistungssensor",
    startW: "Start-Schwelle (W)", endW: "Ruhe-Schwelle (W)", minCycle: "Mindestlaufzeit (Min)", maxEnd: "Max. Ruhezeit bis „fertig“ (Min)",
    quiet: "Gelernte Ruhezeit bis „fertig“", learnBtn: "Aus Verlauf lernen", days: "Tage",
    reset: "Lernen zurücksetzen", resetConfirm: "Alles Gelernte löschen?", saved: "Gespeichert", learning: "Lerne…",
    done: "Fertig", runs: "Läufe", started: "Start", duration: "Dauer", energy: "Energie", pickSensor: "Leistungssensor wählen…",
    delConfirm: "Programm und zugehörige Läufe löschen?", thresholds: "Schwellen", energyShort: "kWh",
    activity: "Betriebszustands-Entität", activeStates: "Zustände für „läuft“ (Komma getrennt)", totalPower: "Hausverbrauchs-Sensor (Gesamt)",
    programEntity: "Programm-Entität (optional)", estNote: "Schätz-Modus: kein Leistungsmesser – der Verbrauch wird aus Hausleistung und Betriebszustand gelernt.",
    health: "Gesundheit", healthOk: "OK – alles unauffällig", healthLearning: "Lernt, was normal ist", healthProblem: "Bitte prüfen",
    energy24: "Energie 24 h", usual: "üblich", duty24: "Laufanteil Kompressor 24 h", starts24: "Kompressor-Starts 24 h", baseW: "Grundlast / Standby",
    daily30: "Energie je gleitende 24 h – letzte 30 Tage", refDays: "Referenztage", baseload: "Haus-Grundlast (niedrigste Leistung)",
    baseline: "Haus-Grundlast", estEnergy: "Geschätzte Energie (gesamt)", disturbed: "durch andere Verbraucher gestört (nicht gelernt)",
    onW: "Ein-Schwelle (W)", wSearch: "Suche nach Name, Gerät oder Entity-ID …", wShowAll: "Alle Entitäten anzeigen (nicht nur Leistungssensoren)",
    tabOverview: "Übersicht", tabLearned: "Was gelernt wurde", tabSettings: "Einstellungen", addAppliance: "+ Gerät hinzufügen",
    wTitle: "Gerät hinzufügen", wStep: "Schritt", wOf: "von", wWhat: "Was möchtest du erfassen?", wName: "Name", next: "Weiter", back: "Zurück",
    wHow: "Wie wird die Leistung gemessen?", wPlug: "Zwischenstecker mit Leistungsmessung", wPlugSub: "Beste Genauigkeit. Jeder Stecker, der Watt meldet (Shelly, Tasmota, Zigbee, TP-Link, Fritz!DECT …).",
    wNoPlug: "Kein Stecker – Gerätestatus verwenden", wNoPlugSub: "Für Einbaugeräte (z. B. Home-Connect-Geschirrspüler): Betriebszustand plus Hausverbrauch genügen; der Verbrauch wird gelernt.",
    recommended: "empfohlen", wPickPlug: "Wähle den Stecker dieses Geräts",
    wTip: "Tipp: Gerät kurz einschalten – der Sensor, dessen Wert springt, ist der richtige. Die Werte aktualisieren sich live.",
    wNoSensors: "Nichts gefunden. „Alle Entitäten anzeigen“ aktivieren, Suche ändern oder zuerst den Stecker in Home Assistant einbinden.",
    wPickState: "Entität, die „Gerät läuft“ meldet", wPickHouse: "Hausverbrauchs-Sensor (gesamt)", wPickProgram: "Programmnamen-Entität (optional, macht die Erkennung exakt)",
    none: "– keine –", wStates: "Zustände für „läuft“", wCreate: "Anlegen", wDone: "Gerät hinzugefügt.",
    wDoneText: "Jetzt das Gerät einfach wie gewohnt benutzen. Das Lernen beginnt sofort: nach dem ersten vollständigen Lauf erscheint das Programm unter „Was gelernt wurde“. Vorhandener Verlauf aus dem Recorder wird automatisch importiert.",
    wOpen: "Dashboard öffnen", wCancel: "Abbrechen", remove: "Gerät entfernen", removeConfirm: "Dieses Gerät samt allem Gelernten entfernen?",
    lSummary: "Was die KI gelernt hat", lPrograms: "Programme", lRuns: "beobachtete Läufe", lQuiet: "Ruhezeit bis „fertig“", lTypical: "typischer Lauf",
    lWhy: "Lernfortschritt", lNone: "Noch nichts gelernt. Gerät einmal laufen lassen – nach dem ersten kompletten Lauf erscheint das Programm hier mit seiner Leistungskurve. Je mehr Läufe, desto besser Erkennung und Restzeit.",
    lCurve: "Typische Leistungskurve (Median) mit Streuung (10–90 %)", lDur: "Dauer je Lauf", lEn: "Energie je Lauf", lLast: "letzter Lauf",
    lConf1: "Erster Lauf – zuverlässig ab 2–3 Läufen", lConfN: "Zuverlässig", lMin: "Min", lWh: "Wh", lHelp: "Programm umbenennen, damit Benachrichtigungen den echten Namen zeigen (z. B. „Eco 50 °C“).",
    needPlug: "Bitte zuerst einen Stecker / Sensor wählen.", needEstimated: "Bitte Betriebszustand und Hausverbrauchs-Sensor wählen.", creating: "Lege an…",
    typeNames: {washing_machine: "Waschmaschine", dishwasher: "Geschirrspüler", dryer: "Trockner", oven: "Backofen", other: "Anderes Gerät", fridge: "Kühlschrank / Gefrierer (Gesundheit)", baseload: "Haus-Grundlast (Gesundheit)"},
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
nav.tabs{display:flex;gap:4px;border-bottom:1px solid var(--divider-color);margin-bottom:16px;flex-wrap:wrap;align-items:center}
nav.tabs button{background:none;color:var(--secondary-text-color);border-radius:0;margin:0;padding:10px 16px;border-bottom:3px solid transparent}
nav.tabs button.on{color:var(--primary-color);border-bottom-color:var(--primary-color);font-weight:600}
nav.tabs .sp{flex:1}
nav.tabs button.add{color:var(--primary-color);font-weight:600}
.types{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin:8px 0}
.tcard,.opt,.plug{border:2px solid var(--divider-color);border-radius:12px;padding:12px;cursor:pointer;background:var(--secondary-background-color)}
.tcard{text-align:center;font-size:14px}.tcard .ic{font-size:30px;display:block;margin-bottom:4px}
.tcard.on,.opt.on,.plug.on{border-color:var(--primary-color);background:color-mix(in srgb,var(--primary-color) 12%,transparent)}
.opt{margin:8px 0}.opt b{display:block;font-size:15px}.opt span{font-size:12px;color:var(--secondary-text-color)}
.badge{font-size:11px;background:var(--primary-color);color:#fff;border-radius:8px;padding:1px 8px;margin-left:8px;font-weight:500}
.plug{display:flex;justify-content:space-between;align-items:center;gap:10px;margin:6px 0;padding:10px 12px}
.plug .w{font-size:20px;font-weight:600;white-space:nowrap}.plug .w.hot{color:var(--primary-color)}.plug small{color:var(--secondary-text-color);display:block;font-size:11px}
.steps{display:flex;gap:6px;margin-bottom:12px}.steps i{flex:1;height:4px;border-radius:2px;background:var(--divider-color)}.steps i.on{background:var(--primary-color)}
.hint{font-size:13px;color:var(--secondary-text-color);margin:8px 0}
.big{font-size:15px;line-height:1.5}
.err{color:var(--error-color,#db4437)}
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


function learnedChart(p, w = 520, h = 200) {
  const pad = {l: 38, r: 8, t: 8, b: 20}, iw = w - pad.l - pad.r, ih = h - pad.t - pad.b;
  const n = Math.max(2, p.model.length || p.curve.length), ym = Math.max(100, ...p.band_hi, ...p.model, ...p.curve) * 1.08;
  const X = i => pad.l + i / (n - 1) * iw, Y = y => pad.t + ih - Math.sqrt(Math.max(0, Math.min(y, ym)) / ym) * ih;
  let g = "";
  for (const y of [0, 50, 200, 500, 1000, 2000].filter(v => v <= ym))
    g += `<line class="axis" x1="${pad.l}" x2="${w - pad.r}" y1="${Y(y)}" y2="${Y(y)}" opacity=".5"/><text class="lbl" x="${pad.l - 4}" y="${Y(y) + 3}" text-anchor="end">${y}</text>`;
  for (let i = 0; i <= 4; i++) g += `<text class="lbl" x="${X((n - 1) * i / 4)}" y="${h - 5}" text-anchor="middle">${Math.round((n - 1) * i / 4)} min</text>`;
  const m = p.model.length ? p.model : p.curve;
  if (p.band_lo.length === m.length && m.length > 1) {
    const up = p.band_hi.map((v, i) => `${i ? "L" : "M"}${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join("");
    const dn = p.band_lo.map((v, i) => `L${X(m.length - 1 - i).toFixed(1)},${Y(p.band_lo[m.length - 1 - i]).toFixed(1)}`).join("");
    g += `<path d="${up}${dn}Z" fill="var(--primary-color)" opacity=".18"/>`;
  }
  const line = (arr, c, wd, dash) => arr.length ? `<path d="${arr.map((v, i) => `${i ? "L" : "M"}${X(i * (m.length - 1) / Math.max(1, arr.length - 1)).toFixed(1)},${Y(v).toFixed(1)}`).join("")}" fill="none" stroke="${c}" stroke-width="${wd}" ${dash ? `stroke-dasharray="${dash}"` : ""} stroke-linejoin="round"/>` : "";
  g += line(p.curve, "#fb8c00", 1.2, "4 3") + line(m, "var(--primary-color)", 2.2);
  return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="xMidYMid meet">${g}</svg>`;
}

function bars(vals, unit, color = "var(--primary-color)", h = 90) {
  if (!vals.length) return "";
  const w = 260, pad = {l: 30, b: 14, t: 6}, ih = h - pad.b - pad.t, mx = Math.max(...vals) * 1.1 || 1, bw = Math.min(28, (w - pad.l) / vals.length);
  let g = `<text class="lbl" x="${pad.l - 4}" y="${pad.t + 8}" text-anchor="end">${Math.round(mx / 1.1)}</text><text class="lbl" x="${pad.l - 4}" y="${pad.t + ih}" text-anchor="end">0</text>`;
  vals.forEach((v, i) => {
    const bh = v / mx * ih, last = i === vals.length - 1;
    g += `<rect x="${pad.l + i * bw + 1}" y="${pad.t + ih - bh}" width="${Math.max(2, bw - 2)}" height="${bh}" fill="${last ? "#fb8c00" : color}" opacity=".85"><title>${v} ${unit}</title></rect>`;
  });
  return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="xMidYMid meet">${g}</svg>`;
}

const TYPE_ICON = {washing_machine: "🧺", dishwasher: "🍽️", dryer: "🌬️", oven: "🔥", other: "🔌", fridge: "❄️", baseload: "🏠"};
const KEYWORDS = {
  washing_machine: ["wasch", "washer", "washing", "waschmasch"], dishwasher: ["geschirr", "dish", "spül", "spuel"],
  dryer: ["trockn", "dryer"], oven: ["ofen", "oven"], fridge: ["kühl", "kuehl", "fridge", "freez", "gefrier"], baseload: ["haus", "house", "total", "gesamt", "grid", "netz"],
};

const PANEL_VERSION = "1.3.1";

class ApplianceMLPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({mode: "open"});
    this._snap = []; this._sel = 0; this._hist = []; this._msg = {}; this._busy = false;
    this._editing = false;
    this._view = "main"; this._tab = "overview"; this._w = null;
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
      this._snap = (await this._hass.callWS({type: "appliance_ml/snapshot"})).map(x => ({
        mode: "metered", sources: {power_entity: x.power_entity}, history: [], programs: [], config: {}, ...x,
        programs: (x.programs || []).map(p => ({model: p.curve || [], band_lo: [], band_hi: [], durations_min: [], energies_wh: [], ...p}))}));
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
    try { await this._hass.callService("appliance_ml", service, data); this._msg = {text: this.t.done}; }
    catch (e) { this._msg = {text: String(e.message || e), err: true}; }
    await this._refresh(true);
  }



  _newWizard() {
    return {step: 1, type: "washing_machine", name: this.t.typeNames.washing_machine, nameTouched: false, mode: "plug",
            power: "", q: "", showAll: false, activity: "", total: "", program: "", states: "run,running,active,on", err: ""};
  }

  _deviceName(e) {
    const ent = this._hass.entities?.[e], dev = ent && this._hass.devices?.[ent.device_id];
    return dev ? (dev.name_by_user || dev.name || "") : "";
  }

  /** Entities usable as a power source. all=false: only power sensors; all=true: every sensor/number. */
  _powerSensors(type, all = false, q = "") {
    const kw = KEYWORDS[type] || [], st = this._hass.states;
    const isPower = e => st[e].attributes.device_class === "power" || st[e].attributes.unit_of_measurement === "W";
    let list = Object.keys(st).filter(e => /^(sensor|number|input_number)\./.test(e) && !e.startsWith("sensor.appliance_ml"));
    if (!all) list = list.filter(isPower);
    const needle = q.trim().toLowerCase();
    if (needle) list = list.filter(e => (e + " " + (st[e].attributes.friendly_name || "") + " " + this._deviceName(e)).toLowerCase().includes(needle));
    const score = e => { const n = (e + " " + (st[e].attributes.friendly_name || "") + " " + this._deviceName(e)).toLowerCase();
      return (kw.some(k => n.includes(k)) ? 0 : 2) + (isPower(e) ? 0 : 1); };
    return list.sort((a, b) => score(a) - score(b) || a.localeCompare(b)).slice(0, 200);
  }

  _plugListHtml(w) {
    const t = this.t, st = this._hass.states;
    const sensors = this._powerSensors(w.type, w.showAll || !!w.q, w.q || "");
    if (!sensors.length) return `<div class="empty">${t.wNoSensors}</div>`;
    return sensors.map(e => {
      const v = parseFloat(st[e].state), ok = isFinite(v), unit = st[e].attributes.unit_of_measurement || "";
      const dev = this._deviceName(e);
      return `<div class="plug ${w.power === e ? "on" : ""}" data-plug="${e}"><div>${st[e].attributes.friendly_name || e}<small>${dev ? dev + " · " : ""}${e}</small></div><div class="w ${ok && unit === "W" && v > 20 ? "hot" : ""}">${ok ? (v >= 100 ? Math.round(v) : v.toFixed(1)) : st[e].state} ${unit}</div></div>`;
    }).join("");
  }

  _wizardHtml() {
    const t = this.t, w = this._w, st = this._hass.states;
    const total = 3, steps = `<div class="steps">${[1, 2, 3].map(i => `<i class="${i <= w.step ? "on" : ""}"></i>`).join("")}</div>`;
    const monitor = w.type === "fridge" || w.type === "baseload";
    let body = "";
    if (w.step === 1) {
      body = `<h2>${t.wWhat}</h2><div class="types">${Object.keys(t.typeNames).map(k =>
        `<div class="tcard ${w.type === k ? "on" : ""}" data-type="${k}"><span class="ic">${TYPE_ICON[k]}</span>${t.typeNames[k]}</div>`).join("")}</div>
        <label>${t.wName}</label><input id="wname" value="${(w.name || "").replace(/"/g, "&quot;")}">`;
    } else if (w.step === 2) {
      const rec = w.type === "dishwasher" ? "noplug" : "plug";
      body = `<h2>${t.wHow}</h2>
        <div class="opt ${w.mode === "plug" ? "on" : ""}" data-mode="plug"><b>🔌 ${t.wPlug}${rec === "plug" ? `<span class="badge">${t.recommended}</span>` : ""}</b><span>${t.wPlugSub}</span></div>
        ${monitor ? "" : `<div class="opt ${w.mode === "noplug" ? "on" : ""}" data-mode="noplug"><b>📡 ${t.wNoPlug}${rec === "noplug" ? `<span class="badge">${t.recommended}</span>` : ""}</b><span>${t.wNoPlugSub}</span></div>`}`;
    } else if (w.mode === "plug") {
      body = `<h2>${t.wPickPlug}</h2><div class="hint">${t.wTip}</div>
        <input id="wq" placeholder="${t.wSearch}" value="${(w.q || "").replace(/"/g, "&quot;")}" style="margin-bottom:8px">
        <label style="display:flex;gap:8px;align-items:center;margin:0 0 8px"><input type="checkbox" id="wall" style="width:auto" ${w.showAll ? "checked" : ""}>${t.wShowAll}</label>
        <div id="plist">${this._plugListHtml(w)}</div>`;
    } else {
      const states = Object.keys(st).filter(e => /^(sensor|binary_sensor|switch|select|input_boolean|input_select)\./.test(e)).sort();
      const kw = KEYWORDS[w.type] || [];
      const rank = e => { const n = (e + (st[e].attributes.friendly_name || "")).toLowerCase(); return (kw.some(k => n.includes(k)) ? 0 : 2) + (/(operation|betriebs|state|status)/.test(n) ? 0 : 1); };
      const act = [...states].sort((a, b) => rank(a) - rank(b) || a.localeCompare(b));
      const house = this._powerSensors("baseload", true);
      if (!w.activity && act.length && rank(act[0]) <= 1) w.activity = act[0];
      if (!w.total && house.length && house.some(e => /(haus|house|total|gesamt|grid|netz)/.test((e + (st[e].attributes.friendly_name || "")).toLowerCase()))) w.total = house[0];
      const opt = (list, cur, empty) => (empty ? `<option value="">${t.none}</option>` : `<option value="">${t.pickSensor.replace("power sensor", "")}</option>`) +
        list.map(e => `<option value="${e}" ${cur === e ? "selected" : ""}>${st[e].attributes.friendly_name || e} (${e}) · ${st[e].state}</option>`).join("");
      body = `<h2>${t.wNoPlug}</h2><div class="hint">${t.wNoPlugSub}</div>
        <label>${t.wPickState}</label><select id="wact">${opt(act, w.activity)}</select>
        <label>${t.wStates}</label><input id="wstates" value="${w.states}">
        <label>${t.wPickHouse}</label><select id="wtot">${opt(house, w.total)}</select>
        <label>${t.wPickProgram}</label><select id="wprg">${opt(act, w.program, true)}</select>`;
    }
    const last = w.step === 3;
    return `<div class="wrap"><header><h1>${t.title} · ${t.wTitle}</h1></header>
      <div class="card" style="max-width:720px;margin:0 auto">${steps}<div class="hint">${t.wStep} ${w.step} ${t.wOf} ${total}</div>${body}
        <div class="msg ${w.err ? "err" : ""}">${w.err || ""}</div>
        <div class="row" style="margin-top:8px">${w.step > 1 ? `<button class="sec" id="wback">${t.back}</button>` : ""}
          ${this._snap.length || this._view === "add" ? `<button class="sec" id="wcancel">${t.wCancel}</button>` : ""}
          <span style="flex:1"></span>
          ${last ? `<button id="wcreate">${t.wCreate}</button>` : `<button id="wnext">${t.next}</button>`}</div>
      </div></div>`;
  }

  _bindWizard(root) {
    const w = this._w, t = this.t, $ = q => root.querySelector(q);
    root.querySelectorAll("input,select").forEach(el => {
      el.addEventListener("focus", () => this._editing = true);
      el.addEventListener("blur", () => this._editing = false);
    });
    const go = () => { this._editing = false; this._render(); };
    root.querySelectorAll("[data-type]").forEach(el => el.onclick = () => {
      const old = t.typeNames[w.type]; w.type = el.dataset.type;
      if (!w.nameTouched || w.name === old) w.name = t.typeNames[w.type].replace(/ \(.*\)/, "");
      if ((w.type === "fridge" || w.type === "baseload")) w.mode = "plug"; else if (w.type === "dishwasher") w.mode = "noplug"; else w.mode = "plug";
      go();
    });
    $("#wname")?.addEventListener("input", e => { w.name = e.target.value; w.nameTouched = true; });
    root.querySelectorAll("[data-mode]").forEach(el => el.onclick = () => { w.mode = el.dataset.mode; go(); });
    const bindPlugs = () => root.querySelectorAll("[data-plug]").forEach(el => el.onclick = () => { w.power = el.dataset.plug; go(); });
    bindPlugs();
    $("#wq")?.addEventListener("input", e => { w.q = e.target.value; $("#plist").innerHTML = this._plugListHtml(w); bindPlugs(); });
    $("#wall")?.addEventListener("change", e => { w.showAll = e.target.checked; go(); });
    $("#wact")?.addEventListener("change", e => w.activity = e.target.value);
    $("#wtot")?.addEventListener("change", e => w.total = e.target.value);
    $("#wprg")?.addEventListener("change", e => w.program = e.target.value);
    $("#wstates")?.addEventListener("input", e => w.states = e.target.value);
    if ($("#wback")) $("#wback").onclick = () => { w.step--; w.err = ""; go(); };
    if ($("#wcancel")) $("#wcancel").onclick = () => { this._view = "main"; this._w = null; go(); };
    if ($("#wnext")) $("#wnext").onclick = () => { if (!(w.name || "").trim()) { w.err = t.wName + "?"; return go(); } w.step++; w.err = ""; go(); };
    if ($("#wcreate")) $("#wcreate").onclick = async () => {
      if (w.mode === "plug" && !w.power) { w.err = t.needPlug; return go(); }
      if (w.mode === "noplug" && !(w.activity && w.total)) { w.err = t.needEstimated; return go(); }
      w.err = t.creating; go();
      try {
        const msg = {type: "appliance_ml/add", name: w.name.trim(), appliance_type: w.type};
        if (w.mode === "plug") msg.power_entity = w.power;
        else Object.assign(msg, {activity_entity: w.activity, total_power_entity: w.total, active_states: w.states.trim()},
                           w.program ? {program_entity: w.program} : {});
        const r = await this._hass.callWS(msg);
        this._view = "main"; this._tab = "learned"; this._w = null; this._newEntry = r.entry_id; this._justAdded = true;
        await new Promise(res => setTimeout(res, 1200));
        await this._refresh(true);
        const i = this._snap.findIndex(x => x.entry_id === r.entry_id); if (i >= 0) this._sel = i;
        this._render();
      } catch (e) { w.err = String(e.message || e); go(); }
    };
  }

  _learnedHtml(s, progs) {
    const t = this.t;
    const runs = s.history.length;
    const typical = s.programs.length ? s.programs.slice().sort((a, b) => b.count - a.count)[0] : null;
    const summary = `<div class="card wide"><h2>${t.lSummary}</h2><div class="stats">
      <div class="stat"><div class="v">${s.programs.length}</div><div class="k">${t.lPrograms}</div></div>
      <div class="stat"><div class="v">${runs}</div><div class="k">${t.lRuns}</div></div>
      <div class="stat"><div class="v">${typical ? typical.duration_min + " " + t.min : "–"}</div><div class="k">${t.lTypical}${typical ? " · " + typical.name : ""}</div></div>
      <div class="stat"><div class="v">${Math.round(s.end_delay_s / 60 * 10) / 10} ${t.min}</div><div class="k">${t.lQuiet}</div></div>
    </div>${this._justAdded ? `<div class="big" style="margin-top:12px">✅ <b>${t.wDone}</b> ${t.wDoneText}</div>` : ""}
    <div class="hint">${t.lHelp}</div></div>`;
    if (!s.programs.length) return summary + `<div class="card wide"><h2>${t.lWhy}</h2><div class="empty big">${t.lNone}</div></div>`;
    const cards = s.programs.map(p => `<div class="card wide">
      <div class="row"><input data-rename="${p.id}" value="${p.name.replace(/"/g, "&quot;")}" style="font-size:16px;font-weight:500">
        <button class="sec" data-save="${p.id}" style="margin:0">${t.save}</button><button class="danger" data-del="${p.id}" style="margin:0">${t.del}</button></div>
      <div class="hint">${p.count} ${t.runs} · ${p.duration_min} ${t.min} · ${(p.energy_wh / 1000).toFixed(2)} ${t.energyShort} · <b>${p.count >= 3 ? t.lConfN : t.lConf1}</b></div>
      <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr))">
        <div><div class="k hint">${t.lCurve}</div>${learnedChart(p)}
          <div class="legend"><span><i style="background:var(--primary-color)"></i>${t.learnedCurve}</span><span><i style="background:#fb8c00"></i>${t.lLast}</span></div></div>
        <div><div class="k hint">${t.lDur} (${t.lMin})</div>${bars(p.durations_min, t.lMin)}
          <div class="k hint">${t.lEn} (${t.lWh})</div>${bars(p.energies_wh, t.lWh, "#43a047")}</div></div></div>`).join("");
    return summary + cards;
  }

  _monitorHtml(s) {
    const t = this.t, m = s.monitor, sm = m.summary || {};
    const state = m.problems.length ? "bad" : (sm.learning ? "learn" : "ok");
    const color = state === "bad" ? "var(--error-color,#db4437)" : state === "learn" ? "var(--warning-color,#fb8c00)" : "var(--success-color,#43a047)";
    const label = state === "bad" ? t.healthProblem : state === "learn" ? `${t.healthLearning} (${sm.ref_days || 0}/5 ${t.refDays})` : t.healthOk;
    const fridge = m.kind === "fridge";
    const bars = m.daily.filter(d => d.kwh !== null);
    const maxv = Math.max(0.1, ...bars.map(d => d.kwh), sm.usual_energy_kwh || 0) * 1.15;
    const W = 520, H = 170, pad = {l: 40, r: 8, t: 8, b: 22}, iw = W - pad.l - pad.r, ih = H - pad.t - pad.b;
    const bw = iw / Math.max(1, m.daily.length) * 0.7;
    let g = "";
    for (const f of [0, .5, 1]) { const y = pad.t + ih - f * ih; g += `<line class="axis" x1="${pad.l}" x2="${W - pad.r}" y1="${y}" y2="${y}" opacity=".5"/><text class="lbl" x="${pad.l - 4}" y="${y + 3}" text-anchor="end">${(maxv * f / 1.15).toFixed(2)}</text>`; }
    m.daily.forEach((d, i) => {
      if (d.kwh === null) return;
      const x = pad.l + i * iw / m.daily.length, h = d.kwh / maxv * ih;
      g += `<rect x="${x}" y="${pad.t + ih - h}" width="${bw}" height="${h}" fill="${i === m.daily.length - 1 ? color : "var(--primary-color)"}" opacity=".85"/>`;
    });
    if (sm.usual_energy_kwh) { const y = pad.t + ih - sm.usual_energy_kwh / maxv * ih;
      g += `<line x1="${pad.l}" x2="${W - pad.r}" y1="${y}" y2="${y}" stroke="#fb8c00" stroke-dasharray="4 4"/><text class="lbl" x="${W - pad.r}" y="${y - 3}" text-anchor="end" fill="#fb8c00">${t.usual} ${sm.usual_energy_kwh} kWh</text>`; }
    g += `<text class="lbl" x="${pad.l}" y="${H - 6}">-30 d</text><text class="lbl" x="${W - pad.r}" y="${H - 6}" text-anchor="end">now</text>`;
    const stat = (v, k, u, usual) => `<div class="stat"><div class="v">${v === null || v === undefined ? "–" : v + (u || "")}</div><div class="k">${k}${usual ? ` · ${t.usual} ${usual}` : ""}</div></div>`;
    return `<div class="card wide" style="border-left:6px solid ${color}"><h2 style="color:${color}">${t.health}: ${label}</h2>
      ${m.texts.length ? `<ul style="margin:0 0 10px 18px">${m.texts.map(x => `<li>${x}</li>`).join("")}</ul>` : ""}
      <div class="stats">
        ${stat(s.power === null ? null : Math.round(s.power), t.power, " W")}
        ${fridge ? stat(sm.energy_kwh, t.energy24, " kWh", sm.usual_energy_kwh) : ""}
        ${fridge ? stat(sm.duty === undefined ? null : Math.round(sm.duty * 100), t.duty24, " %", sm.usual_duty === undefined ? "" : Math.round(sm.usual_duty * 100) + " %") : ""}
        ${fridge ? stat(sm.starts, t.starts24, "", sm.usual_starts) : ""}
        ${stat(fridge ? sm.base_w : sm.min_w, fridge ? t.baseW : t.baseload, " W", (fridge ? sm.usual_base_w : sm.usual_min_w) ?? "")}
      </div></div>
      <div class="card"><h2>${t.daily30}</h2><svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid meet">${g}</svg></div>`;
  }

  _render() {
    try { this._renderInner(); this._error = null; }
    catch (e) {
      console.error("appliance-ml panel", e);
      this.shadowRoot.innerHTML = `<style>${STYLE}</style><div class="wrap"><div class="card"><h2 class="err">Appliance ML panel error</h2><pre style="white-space:pre-wrap">${String(e && e.stack || e)}</pre><button id="reset">Reload</button></div></div>`;
      this.shadowRoot.querySelector("#reset").onclick = () => { this._view = "main"; this._tab = "overview"; this._w = null; this._editing = false; this._render(); };
    }
  }

  _renderInner() {
    const t = this.t, s = this._snap[this._sel];
    const root = this.shadowRoot;
    if (!s || this._view === "add") {
      if (!this._w) this._w = this._newWizard();
      root.innerHTML = `<style>${STYLE}</style>${this._wizardHtml()}`;
      this._bindWizard(root);
      return;
    }
    const mt = s.live?.match;
    const confident = mt && mt.confidence >= 0.3;
    const status = s.monitor ? (s.monitor.problems.length ? t.healthProblem : "OK") : (!s.running ? t.idle : (s.live?.quiet_since ? t.ending : t.running));
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
      s.history.map(h => `<tr><td>${new Date((h.end - h.duration_s) * 1000).toLocaleString([], {dateStyle: "short", timeStyle: "short"})}</td><td>${h.name}${h.disturbed ? ` <span title="${t.disturbed}">⚠</span>` : ""}</td><td>${Math.round(h.duration_s / 60)} ${t.min}</td><td>${(h.energy_wh / 1000).toFixed(2)} ${t.energyShort}</td></tr>`).join("") + "</table>"
      : `<div class="empty">–</div>`;
    const allEnts = Object.keys(this._hass.states).filter(e => /^(sensor|number|input_number|binary_sensor|switch|select|input_boolean|input_select)\./.test(e)).sort().map(e => `<option value="${e}">`).join("");
    const sel = this._snap.length > 1 ? `<select id="dev" style="width:auto">${this._snap.map((x, i) => `<option value="${i}" ${i === this._sel ? "selected" : ""}>${x.name}</option>`).join("")}</select>` : "";

    root.innerHTML = `<style>${STYLE}</style><div class="wrap">
      <header><h1>${t.title} · ${s.name}</h1>${sel}<span class="chip ${s.running || (s.monitor && !s.monitor.problems.length) ? "run" : ""}" ${s.monitor && s.monitor.problems.length ? `style="background:var(--error-color,#db4437);color:#fff"` : ""}>${status}</span></header>
      ${s.version !== PANEL_VERSION ? `<div class="card" style="border-left:6px solid var(--error-color,#db4437);margin-bottom:12px">⚠ Backend ${s.version || "1.1.x (old)"} ≠ panel ${PANEL_VERSION}: the integration code was not reloaded. Restart Home Assistant completely (Settings → System → Restart) so the new Python code is loaded.</div>` : ""}<nav class="tabs">${[["overview", t.tabOverview], ["learned", t.tabLearned], ["settings", t.tabSettings]].map(([k, l]) =>
        `<button data-tab="${k}" class="${this._tab === k ? "on" : ""}">${l}</button>`).join("")}<span class="sp"></span><button class="add" id="addbtn">${t.addAppliance}</button></nav>
      <div class="grid">
        ${this._tab === "overview" ? `
        ${s.monitor ? this._monitorHtml(s) : ""}
        <div class="card wide" style="${s.monitor ? "display:none" : ""}"><div class="stats">
          <div class="stat"><div class="v">${s.power === null ? "–" : Math.round(s.power) + " W"}</div><div class="k">${t.power}</div></div>
          <div class="stat"><div class="v">${s.running ? (confident ? mt.name : t.recognizing) : "–"}</div><div class="k">${t.program}</div></div>
          <div class="stat"><div class="v">${s.running && confident ? Math.round(mt.remaining_s / 60) + " " + t.min : "–"}</div><div class="k">${t.remaining}</div></div>
          <div class="stat"><div class="v">${s.running && confident ? Math.round(mt.progress * 100) + " %" : "–"}</div><div class="k">${t.progress}</div></div>
          ${s.mode === "estimated" ? `<div class="stat"><div class="v">${s.baseline_w ?? "–"} W</div><div class="k">${t.baseline}</div></div>
          <div class="stat"><div class="v">${s.est_energy_kwh ?? "–"} kWh</div><div class="k">${t.estEnergy}</div></div>` : ""}
        </div>${s.mode === "estimated" ? `<div class="meta" style="margin-top:8px;font-size:12px;color:var(--secondary-text-color)">${t.estNote}</div>` : ""}</div>
        <div class="card"><h2>${t.graph24}</h2>${g1}</div>
        ${s.monitor ? "" : `<div class="card"><h2>${t.graphLive}</h2>${g2}</div>`}
        ${s.monitor ? "" : `<div class="card wide"><h2>${t.cycles}</h2>${cyc}</div>`}
        ` : ""}
        ${this._tab === "learned" ? (s.monitor ? this._monitorHtml(s) : this._learnedHtml(s, progs)) : ""}
        ${this._tab === "settings" ? `
        <div class="card"><h2>${t.cfg}</h2>
          ${s.mode === "estimated" ? `
          <label>${t.activity}</label><input id="act" list="ents" value="${s.sources.activity_entity || ""}">
          <label>${t.activeStates}</label><input id="acts" value="${s.sources.active_states || ""}">
          <label>${t.totalPower}</label><input id="tot" list="ents" value="${s.sources.total_power_entity || ""}">
          <label>${t.programEntity}</label><input id="prg" list="ents" value="${s.sources.program_entity || ""}">
          <datalist id="ents">${allEnts}</datalist>` : `<label>${t.sensor}</label><input id="sensor" list="ents" value="${s.sources.power_entity || ""}"><datalist id="ents">${allEnts}</datalist>`}
          <div class="row" style="${s.mode === "estimated" || s.monitor ? "display:none" : ""}"><div style="flex:1"><label>${t.startW}</label><input id="sw" type="number" min="1" value="${s.config.start_w}"></div>
          <div style="flex:1"><label>${t.endW}</label><input id="ew" type="number" min="1" value="${s.config.end_w}"></div></div>
          ${s.mode === "estimated" ? `<input id="sw" type="hidden" value="${s.config.start_w}"><input id="ew" type="hidden" value="${s.config.end_w}">` : ""}
          ${s.monitor ? `<label>${t.onW}</label><input id="sw" type="number" min="1" value="${s.config.start_w}"><input id="ew" type="hidden" value="${s.config.start_w}">` : ""}
          <div class="row"><div style="flex:1"><label>${t.minCycle}</label><input id="mc" type="number" min="1" value="${s.config.min_cycle_min}"></div>
          <div style="flex:1"><label>${t.maxEnd}</label><input id="me" type="number" min="1" value="${s.config.max_end_min}"></div></div>
          <button id="savecfg">${t.save}</button>
          <hr style="border:0;border-top:1px solid var(--divider-color);margin:16px 0 4px">
          <div class="k" style="font-size:12px;color:var(--secondary-text-color)">${t.quiet}: <b>${s.end_delay_s} s</b></div>
          <div class="row" style="margin-top:8px"><input id="days" type="number" min="1" max="365" value="30" style="max-width:90px"><span>${t.days}</span>
            <button id="learn" style="margin:0">${t.learnBtn}</button></div>
          <button id="reset" class="danger">${t.reset}</button>
          <div class="msg ${this._msg.err ? "err" : ""}">${this._msg.text || ""}</div>
          <button id="remove" class="danger sec" style="background:none;color:var(--error-color,#db4437);border:1px solid var(--error-color,#db4437)">${t.remove}</button>
        </div>
        ` : ""}
      </div></div>`;

    const $ = q => root.querySelector(q);
    root.querySelectorAll("input,select").forEach(el => {
      el.addEventListener("focus", () => this._editing = true);
      el.addEventListener("blur", () => this._editing = false);
    });
    $("#dev")?.addEventListener("change", e => { this._sel = +e.target.value; this._histAt = 0; this._justAdded = false; this._refresh(true); });
    root.querySelectorAll("[data-tab]").forEach(b => b.onclick = () => { this._tab = b.dataset.tab; this._justAdded = this._justAdded && b.dataset.tab === "learned"; this._editing = false; this._render(); });
    if ($("#addbtn")) $("#addbtn").onclick = () => { this._view = "add"; this._w = this._newWizard(); this._render(); };
    if ($("#remove")) $("#remove").onclick = async () => {
      if (!confirm(t.removeConfirm)) return;
      await this._hass.callWS({type: "appliance_ml/remove", entry_id: s.entry_id}); this._sel = 0; this._tab = "overview"; await this._refresh(true);
    };
    if ($("#savecfg")) $("#savecfg").onclick = async () => {
      try {
        const msg = {type: "appliance_ml/configure", entry_id: s.entry_id,
          start_w: +$("#sw").value, end_w: +$("#ew").value, min_cycle_min: +$("#mc").value, max_end_min: +$("#me").value};
        if (s.mode === "estimated") {
          Object.assign(msg, {activity_entity: $("#act").value.trim(), active_states: $("#acts").value.trim(),
            total_power_entity: $("#tot").value.trim()});
          if ($("#prg").value.trim()) msg.program_entity = $("#prg").value.trim();
        } else msg.power_entity = $("#sensor").value.trim();
        await this._hass.callWS(msg);
        this._msg = {text: t.saved};
        setTimeout(() => this._refresh(true), 1500);
      } catch (e) { this._msg = {text: String(e.message || e), err: true}; }
      this._editing = false; this._render();
    };
    if ($("#learn")) $("#learn").onclick = () => { this._editing = false; this._call("learn_from_history", {entry_id: s.entry_id, days: +$("#days").value}, t.learning); };
    if ($("#reset")) $("#reset").onclick = () => { if (confirm(t.resetConfirm)) this._call("reset_learning", {entry_id: s.entry_id}); };
    root.querySelectorAll("[data-save]").forEach(b => b.onclick = () => {
      const id = b.dataset.save; this._editing = false;
      this._call("rename_program", {entry_id: s.entry_id, program_id: id, name: root.querySelector(`[data-rename="${id}"]`).value});
    });
    root.querySelectorAll("[data-del]").forEach(b => b.onclick = () => {
      if (confirm(t.delConfirm)) this._call("delete_program", {entry_id: s.entry_id, program_id: b.dataset.del});
    });
  }
}
customElements.define("appliance-ml-panel", ApplianceMLPanel);
