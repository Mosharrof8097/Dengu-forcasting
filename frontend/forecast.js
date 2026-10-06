/* Retrospective forecast viewer.

   The page shows forecasts whose outcomes are already known, because that is
   the only way a reader can judge a forecaster rather than trust it. Where the
   model is worse than the trivial baseline, the interface says so in the same
   size type as where it is better. */

const FOLD_READING = {
  F1_2023_rise: "growth into the 2023 epidemic",
  F2_2023_peak: "the 2023 peak — the hardest period in the record",
  F3_2024_low:  "the quiet phase after 2023",
  F4_2025_rise: "growth into 2025",
  F5_2025_peak: "the 2025 peak",
  F6_2026_low:  "the quiet start of 2026",
};

let F = null, chart = null;
const $ = id => document.getElementById(id);
const pct = v => v == null ? "—" : (100 * v).toFixed(1) + "%";

function skill() {
  return (F.skill || {})[$("fc-horizon").value] || {};
}

function renderHeadline() {
  const s = skill();
  const h = $("fc-horizon").value;

  const gain = s.wis_gain_pct;
  $("fc-wisgain").textContent = gain == null ? "—"
    : (gain > 0 ? gain.toFixed(0) + "%" : gain.toFixed(0) + "%");
  $("fc-wis-why").textContent = s.wis == null ? "—"
    : `WIS ${s.wis} against persistence ${s.wis_persistence} at t+${h}. `
      + (gain > 0
         ? "Lower is better, so the model's predictive distribution is the "
           + "better description of what was about to happen."
         : "The model is not better here. Persistence describes the "
           + "distribution at least as well at this horizon.");

  const better = s.mae_median != null && s.mae_median < s.mae_persistence;
  const dpc = (s.mae_median == null) ? null
    : 100 * (s.mae_median - s.mae_persistence) / s.mae_persistence;
  $("fc-maecmp").textContent = s.mae_median == null ? "—"
    : (Math.abs(dpc) < 2 ? "tied" : (better ? "better" : "worse"));
  $("fc-mae-why").textContent = s.mae_median == null ? "—"
    : `Median absolute error ${s.mae_median} against persistence `
      + `${s.mae_persistence}. ` + (Math.abs(dpc) < 2
        ? "There is no meaningful difference in the central estimate, and no "
          + "claim is made for one."
        : (better ? "The central estimate is the better of the two."
                  : "Persistence gives the better central estimate; the model "
                    + "is not recommended for point accuracy."));

  $("fc-cov").textContent = pct(s.cov90);

  /* A 90% interval will not land on exactly 90% in a finite sample, and
     treating 89.8% as a failure would be as misleading as hiding a real
     shortfall. The band below is the range within which the interval can be
     taken at face value; outside it the page says which way it is wrong. */
  const CAL_LO = 0.88, CAL_HI = 0.93;
  const c = s.cov90;
  const state = c == null ? "none"
              : c < CAL_LO ? "narrow" : c > CAL_HI ? "wide" : "ok";

  $("fc-cov-why").textContent =
    state === "none" ? "—"
    : state === "ok"
      ? `The interval is meant to contain the outcome 90% of the time and `
        + `contains it ${pct(c)} of the time. It can be read at face value.`
    : state === "narrow"
      ? `The interval is meant to contain the outcome 90% of the time and `
        + `contains it only ${pct(c)} of the time. It is too narrow.`
      : `The interval contains the outcome ${pct(c)} of the time against a `
        + `nominal 90%. It is wider than it needs to be — safe for planning, `
        + `but it overstates the uncertainty.`;

  const w = $("fc-covwarn");
  if (state === "narrow") {
    w.style.display = "";
    w.innerHTML = "<b>These intervals under-cover.</b> At a nominal 90% they "
      + `contain the outcome ${pct(c)} of the time, so capacity sized from the `
      + "upper bound would be short more often than the figure implies — an "
      + "error in the dangerous direction. The fold table below shows where "
      + "the shortfall falls. Treat the upper bound as a floor, not a ceiling.";
  } else {
    w.style.display = "none";
  }
}

function renderFolds() {
  const by = (F.coverage_by_fold || {})[$("fc-horizon").value] || {};
  const tb = $("fc-foldtbody");
  tb.innerHTML = "";
  for (const k of Object.keys(by).sort()) {
    const v = by[k];
    const tr = document.createElement("tr");
    const verdict = v >= 0.93 ? "wider than needed"
                  : v >= 0.88 ? "holds"
                  : v >= 0.80 ? "slightly narrow" : "too narrow";
    const col = v >= 0.88 ? "#2f8f5b" : v >= 0.80 ? "#7a5200" : "#b5341f";
    tr.innerHTML = `<td>${k}</td>`
      + `<td class="num" style="color:${col}">`
      + `${pct(v)}</td>`
      + `<td class="muted">${FOLD_READING[k] || ""} — ${verdict}</td>`;
    tb.appendChild(tr);
  }
}

/* Weeks with no bulletin are absent from the evaluation, which is correct --
   they were never forecast and never scored. But if they are simply left out
   of the array, Chart.js puts the week before a gap next to the week after it
   and draws a continuous line across a period with no data. That is the exact
   error the Record tab avoids by refusing to bridge gaps, and it would be
   worse here, where the line is a claim about forecast quality.

   So the series is laid back onto a complete weekly grid and the missing weeks
   are held as nulls, which spanGaps:false then renders as a break. */
function densify(s) {
  const DAY = 86400000, WEEK = 7 * DAY;
  const t0 = Date.parse(s.dates[0] + "T00:00:00Z");
  const t1 = Date.parse(s.dates[s.dates.length - 1] + "T00:00:00Z");
  const at = new Map(s.dates.map((d, i) => [d, i]));

  const dates = [], idx = [];
  for (let t = t0; t <= t1; t += WEEK) {
    const key = new Date(t).toISOString().slice(0, 10);
    dates.push(key);
    idx.push(at.has(key) ? at.get(key) : null);
  }
  const lift = arr => idx.map(i => i === null ? null : arr[i]);
  const q = {};
  for (const k of Object.keys(s.q)) q[k] = lift(s.q[k]);
  return { dates, actual: lift(s.actual), q,
           nWeeks: s.dates.length, nGap: dates.length - s.dates.length };
}

function renderChart() {
  const d = $("fc-district").value, h = $("fc-horizon").value;
  const raw = ((F.series || {})[d] || {})[h];
  const ctx = $("fc-chart");
  if (chart) chart.destroy();
  if (!raw) return;
  const s = densify(raw);

  $("fc-span").textContent =
    `${s.nWeeks} weeks evaluated, ${s.dates[0]} to ${s.dates[s.dates.length - 1]}`
    + (s.nGap ? ` · ${s.nGap} weeks with no bulletin are left as breaks in the line`
              : "");

  const band = (hi, lo, colour) => ([
    { label: hi, data: s.q[hi], borderWidth: 0, pointRadius: 0,
      backgroundColor: colour, fill: "+1", spanGaps: false },
    { label: lo, data: s.q[lo], borderWidth: 0, pointRadius: 0, fill: false,
      spanGaps: false },
  ]);

  chart = new Chart(ctx, {
    data: {
      labels: s.dates,
      datasets: [
        ...band("q95", "q05", "rgba(37,106,191,0.13)").map(x => ({ type: "line", ...x })),
        ...band("q75", "q25", "rgba(37,106,191,0.24)").map(x => ({ type: "line", ...x })),
        { type: "line", label: "Forecast (median)", data: s.q.q50,
          borderColor: "#256abf", borderWidth: 2, pointRadius: 0, fill: false,
          spanGaps: false },
        { type: "line", label: "Actual", data: s.actual,
          borderColor: "#eb6834", borderWidth: 2, pointRadius: 0,
          spanGaps: false, fill: false },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: {
          labels: {
            // the band edges are plumbing, not series the reader should parse
            filter: i => i.text === "Actual" || i.text === "Forecast (median)",
            boxWidth: 14, color: "#52514e", font: { size: 11.5 },
          },
        },
        tooltip: {
          callbacks: {
            label: c => {
              const n = c.dataset.label;
              if (n === "q05" || n === "q25") return null;
              const pretty = { q95: "90% interval upper", q75: "50% interval upper" }[n] || n;
              return `${pretty}: ${Math.round(c.parsed.y).toLocaleString()}`;
            },
          },
        },
      },
      scales: {
        x: { ticks: { color: "#52514e", maxTicksLimit: 10, font: { size: 10.5 } },
             grid: { display: false } },
        y: { beginAtZero: true,
             title: { display: true, text: "admissions in the week",
                      color: "#898781", font: { size: 11 } },
             ticks: { color: "#52514e" }, grid: { color: "#eceae3" } },
      },
    },
  });
}

function render() { renderHeadline(); renderFolds(); renderChart(); }

async function init() {
  let r;
  try { r = await fetch("data/forecasts.json"); } catch (e) { r = null; }
  if (!r || !r.ok) { $("fc-missing").style.display = ""; return; }
  F = await r.json();
  $("fc-body").style.display = "";

  // Dhaka's metropolitan unit is labelled as a part of Dhaka, not a 65th district
  const label = d => d === "DhakaCity" ? "Dhaka — metropolitan hospitals"
                   : d === "Dhaka" ? "Dhaka — rest of the district" : d;
  const ds = $("fc-district");
  for (const d of F.districts) {
    const o = document.createElement("option");
    o.value = d; o.textContent = label(d);
    ds.appendChild(o);
  }
  ds.value = F.districts.includes("DhakaCity") ? "DhakaCity" : F.districts[0];

  const hs = $("fc-horizon");
  for (const h of Object.keys(F.skill || {}).sort()) {
    const o = document.createElement("option");
    o.value = h; o.textContent = `t+${h} week${h === "1" ? "" : "s"}`;
    hs.appendChild(o);
  }

  $("fc-meta").textContent =
    `Model: ${F.meta.model}. ${F.meta.framing}. Intervals ${F.meta.intervals}.`;

  ds.addEventListener("change", render);
  hs.addEventListener("change", render);
  render();
}

init();
