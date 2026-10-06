/* Historical surveillance explorer.
 *
 * Every figure on this page comes from a DGHS bulletin for the selected date.
 * Nothing is modelled, simulated or defaulted. Where a district has no bulletin
 * that day the map leaves it unfilled and the panel says so, because a missing
 * report is not a zero -- conflating the two is what the previous version did.
 */
(function () {
  "use strict";

  var D = null;              // the loaded dataset
  var idx = 0;               // selected date index
  var map = null, layer = null, chart = null;

  // sequential ramp, one hue, light to dark; grey is reserved for "no bulletin"
  var RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"];
  var BREAKS = [1, 5, 15, 40, 100, 300];
  var NO_DATA = "#e8e7e0", CENSORED = "#eda100";

  function colourFor(v, status) {
    if (v === null || v === undefined) return status === 2 ? CENSORED : NO_DATA;
    for (var i = 0; i < BREAKS.length; i++) if (v < BREAKS[i]) return RAMP[i];
    return RAMP[RAMP.length - 1];
  }

  function fmt(n) {
    return n === null || n === undefined ? "—" : n.toLocaleString();
  }

  function el(id) { return document.getElementById(id); }

  // ---------------------------------------------------------------- map
  function initMap() {
    map = L.map("surv-map", { zoomControl: true }).setView([23.8, 90.3], 6.4);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap", maxZoom: 10
    }).addTo(map);
    layer = L.layerGroup().addTo(map);
  }

  function drawMap() {
    layer.clearLayers();
    var cases = D.cases[idx], status = D.status[idx];
    D.districts.forEach(function (d, j) {
      if (!d.latlon) return;
      var v = cases[j], s = status[j];
      var r = v === null ? 5 : Math.max(5, Math.min(26, 5 + Math.sqrt(v) * 1.6));
      var note = v === null
        ? (s === 2 ? "no bulletin — period total is known, daily split is not"
                   : "no bulletin for this date")
        : v + " admitted";
      L.circleMarker([d.latlon[0], d.latlon[1]], {
        radius: r, fillColor: colourFor(v, s), color: "#fcfcfb",
        weight: v === null ? 0.8 : 1.2, fillOpacity: v === null ? 0.55 : 0.85
      }).bindTooltip("<strong>" + d.name + "</strong><br>" + note,
        { direction: "top" }).addTo(layer);
    });
  }

  // -------------------------------------------------------------- chart
  function initChart() {
    chart = new Chart(el("surv-chart"), {
      type: "line",
      data: { labels: [], datasets: [{
        label: "National admissions", data: [], borderColor: "#256abf",
        backgroundColor: "rgba(37,106,191,0.10)", borderWidth: 2,
        pointRadius: 0, fill: true, tension: 0.25, spanGaps: false }] },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false },
          tooltip: { callbacks: { label: function (c) {
            return c.parsed.y === null ? "no bulletin"
              : c.parsed.y.toLocaleString() + " admitted"; } } } },
        scales: { x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } },
                  y: { beginAtZero: true, grid: { color: "#e1e0d9" } } }
      }
    });
  }

  function drawChart() {
    var W = 90;                                   // a 180-day window, centred
    var a = Math.max(0, idx - W), b = Math.min(D.dates.length, idx + W + 1);
    chart.data.labels = D.dates.slice(a, b);
    chart.data.datasets[0].data = D.national.slice(a, b);
    var pts = D.dates.slice(a, b).map(function (_, i) { return a + i === idx ? 5 : 0; });
    chart.data.datasets[0].pointRadius = pts;
    chart.data.datasets[0].pointBackgroundColor = "#eb6834";
    chart.update("none");
  }

  // -------------------------------------------------------------- panel
  function drawPanel() {
    var cases = D.cases[idx], status = D.status[idx], occ = D.occupancy[idx];
    var obs = 0, cen = 0, none = 0, total = 0, occTotal = 0, haveOcc = false;
    var ranked = [];
    D.districts.forEach(function (d, j) {
      var v = cases[j];
      if (v === null) { status[j] === 2 ? cen++ : none++; }
      else { obs++; total += v; ranked.push([v, d.name]); }
      if (occ[j] !== null) { occTotal += occ[j]; haveOcc = true; }
    });
    ranked.sort(function (x, y) { return y[0] - x[0]; });

    el("surv-date").textContent = D.dates[idx];
    el("surv-total").textContent = obs ? fmt(total) : "—";
    // Dhaka is one district whose metropolitan hospitals report separately,
    // so it counts once here rather than as a 65th unit
    var dup = dhakaDouble(cases);
    el("surv-reporting").textContent = (obs - dup) + " of 64";
    el("surv-occupancy").textContent = haveOcc ? fmt(occTotal) : "—";
    el("surv-coverage").textContent =
      (obs - dup) + " reporting · " + cen + " period-total only · " +
      none + " no bulletin" + (dup ? " · Dhaka's metropolitan and non-metropolitan returns counted as one district" : "");

    var rows = ranked.slice(0, 10).map(function (p) {
      return "<tr><td>" + label(p[1]) + "</td><td class='num'>" + fmt(p[0]) + "</td></tr>";
    }).join("");
    el("surv-top").innerHTML = rows ||
      "<tr><td colspan='2' class='muted'>No district reported on this date.</td></tr>";

    var banner = el("surv-nodata");
    if (banner) banner.style.display = obs ? "none" : "block";
  }

  // ------------------------------------------------------------ calendar
  function buildCalendar() {
    var years = {};
    D.dates.forEach(function (t, i) {
      var y = t.slice(0, 4), m = t.slice(5, 7);
      years[y] = years[y] || {};
      (years[y][m] = years[y][m] || []).push(i);
    });
    var ys = Object.keys(years).sort();
    var sel = el("surv-year");
    sel.innerHTML = ys.map(function (y) {
      return "<option value='" + y + "'>" + y + "</option>"; }).join("");
    sel.value = D.dates[idx].slice(0, 4);
    sel.onchange = function () { renderMonths(years, sel.value); };
    renderMonths(years, sel.value);
    window.__years = years;
  }

  function renderMonths(years, y) {
    var MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
    var host = el("surv-calendar");
    var html = "";
    for (var m = 1; m <= 12; m++) {
      var key = String(m).padStart(2, "0");
      var days = years[y][key] || [];
      var cells = "";
      var inMonth = new Date(+y, m, 0).getDate();
      var byDay = {};
      days.forEach(function (i) { byDay[+D.dates[i].slice(8, 10)] = i; });
      for (var dd = 1; dd <= inMonth; dd++) {
        var i = byDay[dd];
        if (i === undefined) {
          cells += "<span class='cal-cell cal-missing' title='no bulletin'></span>";
        } else {
          var v = D.national[i];
          cells += "<span class='cal-cell' data-i='" + i + "' title='" +
            D.dates[i] + " · " + (v === null ? "no bulletin" : v + " admitted") +
            "' style='background:" + colourFor(v, 1) + "'></span>";
        }
      }
      html += "<div class='cal-month'><div class='cal-month-name'>" + MON[m-1] +
              "</div><div class='cal-grid'>" + cells + "</div></div>";
    }
    host.innerHTML = html;
    host.querySelectorAll(".cal-cell[data-i]").forEach(function (c) {
      c.onclick = function () { select(+c.dataset.i); };
    });
    markSelected();
  }

  function markSelected() {
    document.querySelectorAll(".cal-cell").forEach(function (c) {
      c.classList.toggle("cal-sel", +c.dataset.i === idx);
    });
  }

  function select(i) {
    idx = Math.max(0, Math.min(D.dates.length - 1, i));
    var y = D.dates[idx].slice(0, 4);
    if (el("surv-year").value !== y) {
      el("surv-year").value = y;
      renderMonths(window.__years, y);
    }
    drawMap(); drawChart(); drawPanel(); markSelected();
  }

  // ----------------------------------------------------------------- init
  function wire() {
    el("surv-prev").onclick = function () { select(idx - 1); };
    el("surv-next").onclick = function () { select(idx + 1); };
    el("surv-peak").onclick = function () {
      var best = 0;
      D.national.forEach(function (v, i) {
        if (v !== null && v > (D.national[best] || 0)) best = i; });
      select(best);
    };
    document.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") select(idx - 1);
      if (e.key === "ArrowRight") select(idx + 1);
    });
  }

  fetch("data/surveillance.json").then(function (r) { return r.json(); })
    .then(function (data) {
      D = data;
      el("surv-meta").textContent = D.meta.date_min + " to " + D.meta.date_max +
        " · " + D.meta.n_dates.toLocaleString() + " bulletins · " +
        "64 districts, Dhaka sub-categorised into its metropolitan and non-metropolitan parts";
      // open on the largest day on record, which is a real date, not a default
      var best = 0;
      D.national.forEach(function (v, i) {
        if (v !== null && v > (D.national[best] || 0)) best = i; });
      idx = best;
      initMap(); initChart(); buildCalendar(); wire(); select(idx);
    })
    .catch(function (e) {
      var h = el("surv-meta");
      if (h) h.textContent = "Could not load the surveillance record: " + e;
    });

  /* The bulletins report Dhaka's metropolitan hospitals on a line of their own.
     That is a sub-category of Dhaka district, not a 65th district, so a count of
     reporting districts must not count it twice. Returns the overcount. */
  function dhakaDouble(cases) {
    var di = -1, ci = -1;
    D.districts.forEach(function (d, j) {
      if (d.name === "Dhaka") di = j;
      else if (d.name === "DhakaCity") ci = j;
    });
    if (di < 0 || ci < 0) return 0;
    return (cases[di] !== null && cases[ci] !== null) ? 1 : 0;
  }

  /* Dhaka's two bulletin lines are named for what they are, so no reader can
     mistake the metropolitan return for a district of its own. */
  function label(name) {
    if (name === "DhakaCity") return "Dhaka — metropolitan hospitals";
    if (name === "Dhaka") return "Dhaka — rest of the district";
    return name;
  }
})();
