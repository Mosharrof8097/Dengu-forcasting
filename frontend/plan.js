/* Capacity planning from the observed occupancy distribution.
   Nothing here is modelled. The only judgement the interface asks for is the
   service level, and the derivation panel states what that choice means. */

const LEVELS = ["50", "75", "90", "95", "99"];

// Dhaka is one district. The bulletins report its metropolitan hospitals
// separately from the rest of the district, so it is shown as 64 districts
// with Dhaka sub-categorised, never as a 65th unit.
const DHAKA_PARENT = "Dhaka";
const DHAKA_METRO = "DhakaCity";

let P = null, chart = null;

const $ = id => document.getElementById(id);
const fmt = n => n == null ? "—" : Math.round(n).toLocaleString("en-US");

/** The 64 district names, Dhaka counted once. */
function districtNames() {
  return Object.keys(P.districts)
    .filter(d => d !== DHAKA_METRO)
    .sort();
}

/** Occupancy at the chosen level for a unit, or null where it is absent. */
function occAt(unit, period, lvl) {
  const r = P.districts[unit];
  if (!r) return null;
  const q = r[period] && r[period].quantiles;
  if (!q || q[lvl] == null) return null;
  return q[lvl];
}

/* A district's requirement is the sum of the parts the bulletins report for
   it. For every district but Dhaka that is a single series. Summing the two
   Dhaka quantiles is conservative -- the metropolitan and non-metropolitan
   peaks need not fall on the same day -- and the table says so. */
function occDistrict(name, period, lvl) {
  const a = occAt(name, period, lvl);
  if (name !== DHAKA_PARENT) return a;
  const b = occAt(DHAKA_METRO, period, lvl);
  return (a == null && b == null) ? null : (a || 0) + (b || 0);
}

function losOf(unit) {
  const r = P.districts[unit];
  return r && r.los_days ? r.los_days.median : null;
}

function peakOf(name, period) {
  const key = period === "occupancy" ? "max" : null;
  const main = P.districts[name];
  let v = key && main ? main.occupancy.max : (main ? main.occupancy.max : null);
  if (name === DHAKA_PARENT) {
    const m = P.districts[DHAKA_METRO];
    if (m) v = (v || 0) + (m.occupancy.max || 0);
  }
  return v;
}

function currentLevel() {
  return LEVELS[+$("pl-level").value];
}

function render() {
  const unit = $("pl-district").value;
  const period = $("pl-period").value;
  const lvl = currentLevel();
  $("pl-level-v").textContent = lvl + "%";

  const beds = occDistrict(unit, period, lvl);
  const periodLabel = period === "occupancy_season"
    ? "during the July–November season" : "across the whole year";

  $("pl-hero-v").textContent = fmt(beds);
  $("pl-hero-k").textContent =
    `Beds to have ready in ${unit === DHAKA_PARENT ? "Dhaka (both parts)" : unit}`;
  $("pl-hero-why").textContent = beds == null
    ? "This district has no usable occupancy record for the selected period."
    : `On ${lvl}% of recorded days ${periodLabel}, ${unit === DHAKA_PARENT
        ? "Dhaka" : unit} had at most ${fmt(beds)} dengue patients admitted at `
      + `once. Capacity set here is short on the remaining ${100 - +lvl}% of days.`;

  // Dhaka's cards must describe the same thing the headline does -- both of
  // its returns -- or the length of stay beside a combined bed figure would
  // be the length of stay of only one half of it
  const st = stats(unit);
  $("pl-los").textContent = st.los == null ? "—" : st.los.toFixed(2) + " d";
  $("pl-los-n").textContent = st.losNote;
  $("pl-max").textContent = fmt(peakOf(unit, period));
  $("pl-ndays").textContent = fmt(st.nDays);
  $("pl-adm").textContent = st.adm == null ? "—" : st.adm.toFixed(1);

  drawChart(unit, period, lvl);
  drawTable(period, lvl, unit);
}

function drawChart(unit, period, lvl) {
  const vals = LEVELS.map(l => occDistrict(unit, period, l));
  const sel = LEVELS.indexOf(lvl);
  const ctx = $("pl-chart");
  if (chart) chart.destroy();
  chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: LEVELS.map(l => l + "%"),
      datasets: [{
        label: "Beds occupied",
        data: vals,
        backgroundColor: LEVELS.map((_, i) => i === sel ? "#eb6834" : "#9ebde8"),
        borderRadius: 4,
        borderSkipped: "start",
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: c => `${fmt(c.parsed.y)} beds on ${c.label} of days`,
          },
        },
      },
      scales: {
        x: { title: { display: true, text: "service level", color: "#898781",
                      font: { size: 11 } },
             grid: { display: false }, ticks: { color: "#52514e" } },
        y: { beginAtZero: true,
             title: { display: true, text: "beds occupied", color: "#898781",
                      font: { size: 11 } },
             grid: { color: "#eceae3" }, ticks: { color: "#52514e" } },
      },
    },
  });
}

function drawTable(period, lvl, selected) {
  const rows = districtNames().map(d => ({
    name: d,
    beds: occDistrict(d, period, lvl),
    los: stats(d).los,
    peak: peakOf(d, period),
  })).sort((a, b) => (b.beds || 0) - (a.beds || 0));

  const tb = $("pl-tbody");
  tb.innerHTML = "";
  for (const r of rows) {
    tb.appendChild(row(r.name, r, r.name === selected, false));
    if (r.name === DHAKA_PARENT) {
      // the two parts Dhaka's figure is made of, so the sum is never opaque
      for (const [label, unit] of [["Metropolitan hospitals", DHAKA_METRO],
                                   ["Rest of the district", DHAKA_PARENT]]) {
        tb.appendChild(row(label, {
          beds: occAt(unit, period, lvl),
          los: losOf(unit),
          peak: P.districts[unit] ? P.districts[unit].occupancy.max : null,
        }, false, true));
      }
    }
  }
}

function row(label, r, highlight, isSub) {
  const tr = document.createElement("tr");
  if (highlight) tr.className = "hl";
  if (isSub) tr.className = (tr.className + " sub-row").trim();
  tr.innerHTML =
    `<td>${label}</td>` +
    `<td class="num">${fmt(r.beds)}</td>` +
    `<td class="num">${r.los == null ? "—" : r.los.toFixed(2)}</td>` +
    `<td class="num muted">${fmt(r.peak)}</td>`;
  return tr;
}

/* Summary statistics for the selected district. For every district but Dhaka
   this is one record. For Dhaka the two returns are combined: counts add, and
   length of stay is averaged weighted by admissions, because a plain mean of
   the two medians would give a district of 1,300 daily admissions the same
   say as one of 20. */
function stats(name) {
  const units = name === DHAKA_PARENT ? [DHAKA_PARENT, DHAKA_METRO] : [name];
  let nDays = 0, adm = 0, wsum = 0, wlos = 0, nObs = 0, haveAdm = false;
  for (const u of units) {
    const r = P.districts[u];
    if (!r) continue;
    nDays = Math.max(nDays, r.n_days);
    if (r.admissions.mean != null) { adm += r.admissions.mean; haveAdm = true; }
    if (r.los_days.median != null && r.admissions.mean) {
      wsum += r.admissions.mean;
      wlos += r.los_days.median * r.admissions.mean;
      nObs += r.los_days.n;
    }
  }
  const los = wsum > 0 ? wlos / wsum : null;
  let note;
  if (los == null) note = "too few busy days to measure";
  else if (units.length > 1)
    note = `weighted across Dhaka's two returns, from ${nObs.toLocaleString()} `
         + "days with \u22655 admissions";
  else note = `from ${nObs.toLocaleString()} days with \u22655 admissions`;
  return { nDays, adm: haveAdm ? adm : null, los, losNote: note };
}

async function init() {
  P = await (await fetch("data/planning.json")).json();

  const sel = $("pl-district");
  for (const d of districtNames()) {
    const o = document.createElement("option");
    o.value = d; o.textContent = d;
    if (d === DHAKA_PARENT) o.textContent = "Dhaka (metro + district)";
    sel.appendChild(o);
  }
  sel.value = DHAKA_PARENT;

  $("pl-meta").textContent =
    `${districtNames().length} districts · ` + P.meta.identity + ". " +
    P.meta.los.charAt(0).toUpperCase() + P.meta.los.slice(1) + ".";

  for (const id of ["pl-district", "pl-period", "pl-level"]) {
    $(id).addEventListener("input", render);
  }
  render();
}

init();
