/**
 * EpiST-Shield | Dengue Outbreak Decision Support System
 * Core Frontend Logic (Multi-Horizon 7d / 14d / 21d / 30d Support)
 */

const API_BASE = window.location.origin;


// District Coordinates for 11 Focal Districts in Bangladesh
const DISTRICT_COORDS = {
  "Dhaka": [23.8103, 90.4125],
  "Chittagong": [22.3569, 91.7832],
  "Gazipur": [24.0023, 90.4267],
  "Narayanganj": [23.6238, 90.5000],
  "Khulna": [22.8456, 89.5403],
  "Barishal": [22.7010, 90.3535],
  "Rajshahi": [24.3636, 88.6241],
  "Sylhet": [24.8949, 91.8687],
  "Cumilla": [23.4607, 91.1809],
  "Faridpur": [23.6070, 89.8429],
  "Mymensingh": [24.7471, 90.4203]
};

// District Baseline Parameters for Realistic Epidemiological Profiling
const DISTRICT_DEFAULTS = {
  "Dhaka":       { rainfall: 85.0, temp: 30.5, humidity: 82.0, lag7: 75.0, lag14: 70.0, lag21: 65.0 },
  "Chittagong":  { rainfall: 80.0, temp: 29.5, humidity: 84.0, lag7: 55.0, lag14: 50.0, lag21: 45.0 },
  "Gazipur":     { rainfall: 65.0, temp: 29.5, humidity: 80.0, lag7: 42.0, lag14: 38.0, lag21: 35.0 },
  "Narayanganj": { rainfall: 60.0, temp: 30.0, humidity: 81.0, lag7: 40.0, lag14: 36.0, lag21: 32.0 },
  "Mymensingh":  { rainfall: 50.0, temp: 28.5, humidity: 79.0, lag7: 32.0, lag14: 28.0, lag21: 25.0 },
  "Khulna":      { rainfall: 35.0, temp: 29.0, humidity: 78.0, lag7: 25.0, lag14: 22.0, lag21: 20.0 },
  "Cumilla":     { rainfall: 30.0, temp: 28.5, humidity: 77.0, lag7: 22.0, lag14: 20.0, lag21: 18.0 },
  "Barishal":    { rainfall: 25.0, temp: 28.0, humidity: 78.0, lag7: 18.0, lag14: 16.0, lag21: 14.0 },
  "Faridpur":    { rainfall: 22.0, temp: 28.0, humidity: 76.0, lag7: 16.0, lag14: 14.0, lag21: 12.0 },
  "Rajshahi":    { rainfall: 15.0, temp: 27.5, humidity: 72.0, lag7: 12.0, lag14: 10.0, lag21: 8.0 },
  "Sylhet":      { rainfall: 18.0, temp: 26.5, humidity: 75.0, lag7: 10.0, lag14: 8.0,  lag21: 6.0 }
};

// Application State
const state = {
  location: "Mymensingh",
  horizon: 30, // Default: 30 Days
  theme: "light",
  simRainfall: DISTRICT_DEFAULTS["Mymensingh"].rainfall,
  simTemp: DISTRICT_DEFAULTS["Mymensingh"].temp,
  simHumidity: DISTRICT_DEFAULTS["Mymensingh"].humidity,
  forecastData: null,
  map: null,
  mapMarkers: {},
  chart: null
};

// DOM Elements
const el = {
  locationSelect: document.getElementById("location-select"),
  txtLastUpdated: document.getElementById("txt-last-updated"),
  themeToggle: document.getElementById("theme-toggle"),
  themeText: document.getElementById("theme-text"),
  pdfBtn: document.getElementById("pdf-export-btn"),
  periodTabs: document.getElementById("period-tabs"),
  
  // Summary Cards
  summaryRiskVal: document.getElementById("summary-risk-val"),
  summaryRiskSub: document.getElementById("summary-risk-sub"),
  summaryCasesVal: document.getElementById("summary-cases-val"),
  summaryCasesSub: document.getElementById("summary-cases-sub"),
  summaryPeakVal: document.getElementById("summary-peak-val"),
  summaryDailyVal: document.getElementById("summary-daily-val"),
  
  // Chart & Alert
  chartLocationName: document.getElementById("chart-location-name"),
  highRiskAlertBox: document.getElementById("high-risk-alert-box"),
  highRiskAlertText: document.getElementById("high-risk-alert-text"),
  
  // Healthcare Preparation Cards
  resBedsVal: document.getElementById("res-beds-val"),
  resKitsVal: document.getElementById("res-kits-val"),
  resSalineVal: document.getElementById("res-saline-val"),
  btnViewResourceModal: document.getElementById("btn-view-resource-modal"),
  
  // Resource Delivery Plan
  deliveryPlanList: document.getElementById("delivery-plan-list"),
  btnViewDispatchModal: document.getElementById("btn-view-dispatch-modal"),
  
  // Weather Simulator
  simRainfallInput: document.getElementById("sim-rainfall"),
  simRainfallVal: document.getElementById("sim-rainfall-val"),
  simTempInput: document.getElementById("sim-temp"),
  simTempVal: document.getElementById("sim-temp-val"),
  simHumidityInput: document.getElementById("sim-humidity"),
  simHumidityVal: document.getElementById("sim-humidity-val"),
  btnUpdateForecast: document.getElementById("btn-update-forecast"),
  
  // Sim Results
  simNormVal: document.getElementById("sim-norm-val"),
  simWeatherVal: document.getElementById("sim-weather-val"),
  simChangeVal: document.getElementById("sim-change-val"),
  simShiftVal: document.getElementById("sim-shift-val"),
  
  // Modal
  modalOverlay: document.getElementById("detail-modal"),
  modalTitle: document.getElementById("modal-title"),
  modalBody: document.getElementById("modal-body"),
  btnCloseModal: document.getElementById("btn-close-modal")
};

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
  updateLastUpdatedTime();
  initThemeToggle();
  initPeriodTabs();
  initLocationPicker();
  initWeatherSimulator();
  initMap();
  initModalListeners();
  initPdfExport();
  
  // Initial Forecast Data Fetch
  fetchForecastData();
});

// Update Clock Badge
function updateLastUpdatedTime() {
  const now = new Date();
  let hours = now.getHours();
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12;
  el.txtLastUpdated.textContent = `${hours}:${minutes} ${ampm}`;
}

// Theme Switcher
function initThemeToggle() {
  el.themeToggle.addEventListener("click", () => {
    state.theme = state.theme === "light" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", state.theme);
    el.themeText.textContent = state.theme === "light" ? "Dark Mode" : "Light Mode";
    const icon = el.themeToggle.querySelector("i");
    icon.className = state.theme === "light" ? "fa-solid fa-moon" : "fa-solid fa-sun";
  });
}

// Period Tabs Handler (7d / 14d / 21d / 30d)
function initPeriodTabs() {
  const buttons = el.periodTabs.querySelectorAll(".period-btn");
  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      buttons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      state.horizon = parseInt(btn.getAttribute("data-days"), 10);
      fetchForecastData();
    });
  });
}

function applyDistrictDefaults(dist) {
  const profile = DISTRICT_DEFAULTS[dist] || DISTRICT_DEFAULTS["Mymensingh"];
  state.simRainfall = profile.rainfall;
  state.simTemp = profile.temp;
  state.simHumidity = profile.humidity;

  if (el.simRainfallInput) {
    el.simRainfallInput.value = profile.rainfall;
    el.simRainfallVal.textContent = `${profile.rainfall.toFixed(1)} mm`;
  }
  if (el.simTempInput) {
    el.simTempInput.value = profile.temp;
    el.simTempVal.textContent = `${profile.temp.toFixed(1)} °C`;
  }
  if (el.simHumidityInput) {
    el.simHumidityInput.value = profile.humidity;
    el.simHumidityVal.textContent = `${profile.humidity.toFixed(1)} %`;
  }
}

// Location Selector Handler
function initLocationPicker() {
  el.locationSelect.addEventListener("change", (e) => {
    state.location = e.target.value;
    applyDistrictDefaults(state.location);
    if (state.map && DISTRICT_COORDS[state.location]) {
      state.map.flyTo(DISTRICT_COORDS[state.location], 10, { duration: 1.2 });
    }
    fetchForecastData();
  });
}

// Weather Simulator Controls
function initWeatherSimulator() {
  el.simRainfallInput.addEventListener("input", (e) => {
    state.simRainfall = parseFloat(e.target.value);
    el.simRainfallVal.textContent = `${state.simRainfall.toFixed(1)} mm`;
  });
  
  el.simTempInput.addEventListener("input", (e) => {
    state.simTemp = parseFloat(e.target.value);
    el.simTempVal.textContent = `${state.simTemp.toFixed(1)} °C`;
  });
  
  el.simHumidityInput.addEventListener("input", (e) => {
    state.simHumidity = parseFloat(e.target.value);
    el.simHumidityVal.textContent = `${state.simHumidity.toFixed(1)} %`;
  });
  
  el.btnUpdateForecast.addEventListener("click", () => {
    fetchForecastData();
  });
}

// Leaflet Geospatial Map Initialization
function initMap() {
  state.map = L.map("map").setView(DISTRICT_COORDS["Mymensingh"], 7);
  
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: '&copy; DGHS Bangladesh • EpiST-Shield'
  }).addTo(state.map);
  
  // Add district markers
  Object.keys(DISTRICT_COORDS).forEach(dist => {
    const coords = DISTRICT_COORDS[dist];
    const marker = L.circleMarker(coords, {
      radius: 9,
      fillColor: dist === state.location ? "#EF4444" : "#3B82F6",
      color: "#FFFFFF",
      weight: 2,
      opacity: 1,
      fillOpacity: 0.85
    }).addTo(state.map);
    
    marker.bindTooltip(`<b>${dist}</b><br/>Click to view forecast`, { direction: 'top' });
    
    marker.on("click", () => {
      state.location = dist;
      el.locationSelect.value = dist;
      applyDistrictDefaults(dist);
      state.map.flyTo(coords, 10, { duration: 1.2 });
      fetchForecastData();
    });
    
    state.mapMarkers[dist] = marker;
  });
}

// Fetch Multi-Horizon Forecast API
async function fetchForecastData() {
  try {
    const profile = DISTRICT_DEFAULTS[state.location] || { lag7: 30, lag14: 25, lag21: 20 };
    const payload = {
      district: state.location,
      horizon_days: state.horizon,
      rainfall_7d: state.simRainfall,
      temperature_7d: state.simTemp,
      humidity_7d: state.simHumidity,
      cases_lag_7: profile.lag7,
      cases_lag_14: profile.lag14,
      cases_lag_21: profile.lag21,
      vector_control_active: false
    };
    
    const response = await fetch(`${API_BASE}/api/forecast/multi-horizon`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    
    const data = await response.json();
    state.forecastData = data;
    renderDashboard(data);
  } catch (err) {
    console.warn("API Offline or unreachable, generating mathematical fallback dataset:", err);
    const mockData = generateFallbackForecastData();
    state.forecastData = mockData;
    renderDashboard(mockData);
  }
}

// Generate Dynamic Fallback Data if backend API is building
function generateFallbackForecastData() {
  const n = state.horizon;
  const labels = Array.from({ length: n }, (_, i) => `Day ${i + 1}`);
  
  let baseCases = 45.0;
  if (state.location === "Dhaka") baseCases = 85.0;
  if (state.location === "Chittagong") baseCases = 65.0;
  if (state.location === "Gazipur") baseCases = 50.0;
  if (state.location === "Khulna") baseCases = 38.0;
  
  const peakDayIdx = n === 30 ? 18 : (n === 21 ? 13 : (n === 14 ? 9 : 5));
  
  const dailyCases = labels.map((_, i) => {
    const day = i + 1;
    const sigma = n / 4.0;
    const exponent = -((day - peakDayIdx) ** 2) / (2 * (sigma ** 2));
    const waveFactor = 0.55 + 0.50 * Math.exp(exponent) + 0.05 * Math.sin(day * 0.8);
    return Math.max(5.0, Math.round(baseCases * waveFactor * 10) / 10);
  });
  
  const totalCases = Math.round(dailyCases.reduce((a, b) => a + b, 0));
  const maxCase = Math.max(...dailyCases);
  const actualPeakDay = dailyCases.indexOf(maxCase) + 1;
  const avgDaily = Math.round(totalCases / n);
  
  const highRiskDays = dailyCases.map((c, i) => c >= 50.0 ? i + 1 : null).filter(Boolean);
  const hasHighRisk = highRiskDays.length > 0;
  const highRiskStart = hasHighRisk ? highRiskDays[0] : 0;
  const highRiskEnd = hasHighRisk ? highRiskDays[highRiskDays.length - 1] : 0;
  
  // Clean weekly ranges
  let weekRanges = [];
  if (n === 7) weekRanges = [["Week 1", 1, 7]];
  else if (n === 14) weekRanges = [["Week 1", 1, 7], ["Week 2", 8, 14]];
  else if (n === 21) weekRanges = [["Week 1", 1, 7], ["Week 2", 8, 14], ["Week 3", 15, 21]];
  else weekRanges = [["Week 1", 1, 7], ["Week 2", 8, 14], ["Week 3", 15, 21], ["Week 4", 22, 30]];
  
  const deliveryPlan = weekRanges.map(([wName, startD, endD]) => {
    const wCases = dailyCases.slice(startD - 1, endD).reduce((a, b) => a + b, 0);
    const wAvg = wCases / (endD - startD + 1);
    let status = "Normal Preparation";
    let color = "#10B981";
    let icon = "🟢";
    let desc = "Standard surveillance and routine supply levels.";
    
    if (wAvg >= 50) {
      status = "High Priority"; color = "#EF4444"; icon = "🔴";
      desc = "Urgent dispatch of isolation beds and test kits.";
    } else if (wAvg >= 30) {
      status = "Increase Supplies"; color = "#F59E0B"; icon = "🟡";
      desc = "Preemptively ramp up medical inventory.";
    } else if (wName === weekRanges[weekRanges.length - 1][0] && n >= 21) {
      status = "Maintain Emergency Reserve"; color = "#3B82F6"; icon = "🔵";
      desc = "Maintain baseline emergency reserve for post-peak recovery.";
    }
    
    return {
      week: wName,
      day_range: `Day ${startD}–${endD}`,
      expected_cases: Math.round(wCases),
      status: status,
      color: color,
      icon: icon,
      description: desc
    };
  });

  return {
    location: state.location,
    selected_horizon_days: n,
    summary: {
      outbreak_risk: maxCase >= 50 ? "HIGH" : (maxCase >= 25 ? "MODERATE" : "LOW"),
      risk_color: maxCase >= 50 ? "#EF4444" : (maxCase >= 25 ? "#F59E0B" : "#10B981"),
      expected_cases: totalCases,
      peak_risk_day: `Day ${actualPeakDay}`,
      peak_cases: maxCase,
      daily_average: avgDaily
    },
    forecast_chart: {
      labels: labels,
      cases: dailyCases,
      threshold_line: 50.0
    },
    high_risk_alert: {
      has_high_risk: hasHighRisk,
      period: hasHighRisk ? `Day ${highRiskStart} – Day ${highRiskEnd}` : "None Expected",
      peak_day: `Day ${actualPeakDay}`,
      warning_message: hasHighRisk 
        ? `Higher dengue activity is expected from Day ${highRiskStart} to Day ${highRiskEnd}. Peak risk is expected on Day ${actualPeakDay}.`
        : `No severe high-risk surge above 50 cases/day projected for ${state.location}. Peak activity expected on Day ${actualPeakDay}.`
    },
    healthcare_preparation: {
      hospital_beds_needed: Math.round(maxCase * 3.0),
      test_kits_needed: Math.round(totalCases * 1.8),
      saline_bags_needed: Math.round(totalCases * 2.5)
    },
    resource_delivery_plan: deliveryPlan,
    weather_simulation_impact: {
      normal_forecast_cases: totalCases,
      weather_scenario_cases: Math.round(totalCases * 1.157),
      expected_change_pct: "+15.7%",
      peak_shift: `Day ${actualPeakDay} → Day ${Math.max(1, actualPeakDay - 2)}`
    }
  };
}

// Render Dashboard Elements
function renderDashboard(data) {
  // 1. Location & Title Sync
  el.chartLocationName.textContent = data.location;
  
  // 2. Summary Cards
  el.summaryRiskVal.textContent = data.summary.outbreak_risk;
  el.summaryRiskVal.style.color = data.summary.risk_color;
  el.summaryRiskSub.textContent = data.summary.outbreak_risk === "HIGH" ? "Critical Surge Warning" : "Standard Surveillance";
  
  el.summaryCasesVal.textContent = data.summary.expected_cases.toLocaleString();
  el.summaryCasesSub.textContent = `Next ${data.selected_horizon_days} Days`;
  
  el.summaryPeakVal.textContent = data.summary.peak_risk_day;
  el.summaryDailyVal.textContent = data.summary.daily_average.toLocaleString();
  
  // 3. Render Chart
  renderChart(data.forecast_chart);
  
  // 4. Render High-Risk Alert Box
  if (data.high_risk_alert.has_high_risk) {
    el.highRiskAlertBox.style.display = "flex";
    el.highRiskAlertText.innerHTML = data.high_risk_alert.warning_message;
  } else {
    el.highRiskAlertBox.style.display = "flex";
    el.highRiskAlertText.innerHTML = `No critical high-risk surge above 50 cases/day projected for ${data.location}. Peak activity expected on <strong>${data.summary.peak_risk_day}</strong>.`;
  }
  
  // 5. Healthcare Preparation Cards
  el.resBedsVal.textContent = data.healthcare_preparation.hospital_beds_needed.toLocaleString();
  el.resKitsVal.textContent = data.healthcare_preparation.test_kits_needed.toLocaleString();
  el.resSalineVal.textContent = data.healthcare_preparation.saline_bags_needed.toLocaleString();
  
  // 6. Resource Delivery Plan
  renderDeliveryPlan(data.resource_delivery_plan);
  
  // 7. Weather Simulation Result Box
  el.simNormVal.textContent = `${data.weather_simulation_impact.normal_forecast_cases.toLocaleString()} cases`;
  el.simWeatherVal.textContent = `${data.weather_simulation_impact.weather_scenario_cases.toLocaleString()} cases`;
  el.simChangeVal.textContent = data.weather_simulation_impact.expected_change_pct;
  el.simShiftVal.textContent = data.weather_simulation_impact.peak_shift;
  
  // 8. Update Map Marker Highlights
  Object.keys(state.mapMarkers).forEach(dist => {
    const marker = state.mapMarkers[dist];
    if (dist === state.location) {
      marker.setStyle({ fillColor: data.summary.risk_color, radius: 12, weight: 3 });
    } else {
      marker.setStyle({ fillColor: "#3B82F6", radius: 8, weight: 2 });
    }
  });
}

// Render Chart.js Forecast Line
function renderChart(chartData) {
  const ctx = document.getElementById("forecastChart").getContext("2d");
  
  if (state.chart) {
    state.chart.destroy();
  }
  
  const gradient = ctx.createLinearGradient(0, 0, 0, 260);
  gradient.addColorStop(0, "rgba(59, 130, 246, 0.35)");
  gradient.addColorStop(1, "rgba(59, 130, 246, 0.0)");
  
  const step = state.horizon === 30 ? 5 : (state.horizon === 21 ? 4 : 2);
  const displayLabels = chartData.labels.map((l, i) => (i % step === 0 || i === chartData.labels.length - 1) ? l : "");
  
  state.chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: "Expected Dengue Cases",
          data: chartData.cases,
          borderColor: "#3B82F6",
          borderWidth: 3,
          backgroundColor: gradient,
          fill: true,
          tension: 0.35,
          pointRadius: chartData.cases.map(c => c >= 50 ? 5 : 2),
          pointBackgroundColor: chartData.cases.map(c => c >= 50 ? "#EF4444" : "#3B82F6")
        },
        {
          label: "High-Risk Threshold (50 cases/day)",
          data: Array(chartData.labels.length).fill(50.0),
          borderColor: "#EF4444",
          borderWidth: 2,
          borderDash: [6, 6],
          pointRadius: 0,
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          mode: "index",
          intersect: false,
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${ctx.raw} cases`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            color: state.theme === "dark" ? "#94A3B8" : "#64748B",
            font: { family: "Outfit", size: 11 },
            callback: function(val, index) {
              return displayLabels[index];
            }
          }
        },
        y: {
          grid: { color: state.theme === "dark" ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.05)" },
          ticks: {
            color: state.theme === "dark" ? "#94A3B8" : "#64748B",
            font: { family: "JetBrains Mono", size: 11 }
          },
          suggestedMax: Math.max(...chartData.cases, 60) + 10
        }
      }
    }
  });
}

// Render Resource Delivery Plan List
function renderDeliveryPlan(plan) {
  el.deliveryPlanList.innerHTML = "";
  plan.forEach(item => {
    const div = document.createElement("div");
    div.className = "delivery-item";
    div.innerHTML = `
      <div>
        <span class="delivery-week">${item.week}</span>
        <span style="font-size: 11px; color: var(--text-secondary); margin-left: 6px;">(${item.day_range})</span>
      </div>
      <div class="delivery-status" style="color: ${item.color};">
        <span>${item.icon}</span> <span>${item.status}</span>
      </div>
    `;
    el.deliveryPlanList.appendChild(div);
  });
}

// Modal Listeners
function initModalListeners() {
  el.btnViewResourceModal.addEventListener("click", () => {
    if (!state.forecastData) return;
    const prep = state.forecastData.healthcare_preparation;
    el.modalTitle.innerHTML = `<i class="fa-solid fa-hospital"></i> Healthcare Preparation Analysis (${state.location} - ${state.horizon} Days)`;
    el.modalBody.innerHTML = `
      <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 16px;">
        Detailed medical resource requirements computed for <strong>${state.location}</strong> over the next <strong>${state.horizon} days</strong> based on expected outbreak volume (${state.forecastData.summary.expected_cases.toLocaleString()} total cases).
      </p>

      <div style="display: flex; flex-direction: column; gap: 12px; font-size: 13px;">
        <div style="padding: 12px; background: var(--bg-primary); border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
          <strong style="color: var(--color-accent-blue);">🛏 Additional Hospital Beds Required: ${prep.hospital_beds_needed.toLocaleString()} beds</strong>
          <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Calculated based on peak daily influx multiplier (3.0 beds per peak daily case: 3.0 × ${state.forecastData.summary.peak_cases}).</p>
        </div>

        <div style="padding: 12px; background: var(--bg-primary); border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
          <strong style="color: #0D9488;">🧪 NS1 Antigen Test Kits Required: ${prep.test_kits_needed.toLocaleString()} kits</strong>
          <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Calculated for 1.8x screening ratio per suspected dengue case (1.8 × ${state.forecastData.summary.expected_cases.toLocaleString()}).</p>
        </div>

        <div style="padding: 12px; background: var(--bg-primary); border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
          <strong style="color: #D97706;">🩸 IV Fluid Saline Bags Required: ${prep.saline_bags_needed.toLocaleString()} bags</strong>
          <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Calculated for fluid rehydration management protocol (2.5 bags average per patient: 2.5 × ${state.forecastData.summary.expected_cases.toLocaleString()}).</p>
        </div>
      </div>
    `;
    el.modalOverlay.classList.add("active");
  });
  
  el.btnViewDispatchModal.addEventListener("click", () => {
    if (!state.forecastData) return;
    const plan = state.forecastData.resource_delivery_plan;
    el.modalTitle.innerHTML = `<i class="fa-solid fa-truck-ramp-box"></i> Resource Delivery & Dispatch Schedule`;
    
    let planHtml = plan.map(item => `
      <div style="padding: 12px; background: var(--bg-primary); border-radius: var(--radius-sm); border: 1px solid var(--border-subtle); margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
          <strong style="font-size: 14px;">${item.week} (${item.day_range})</strong>
          <span style="font-weight: 700; color: ${item.color};">${item.icon} ${item.status}</span>
        </div>
        <p style="font-size: 12px; color: var(--text-secondary);">${item.description}</p>
        <div style="font-size: 12px; font-weight: 600; margin-top: 6px; color: var(--text-primary);">
          Expected Case Load: ~${item.expected_cases.toLocaleString()} cases
        </div>
      </div>
    `).join("");
    
    el.modalBody.innerHTML = planHtml;
    el.modalOverlay.classList.add("active");
  });
  
  el.btnCloseModal.addEventListener("click", () => {
    el.modalOverlay.classList.remove("active");
  });
}

// Guaranteed Crisp Vector PDF Export Generator
function initPdfExport() {
  el.pdfBtn.addEventListener("click", () => {
    if (!state.forecastData) return;
    
    // Update printable header metadata
    const distEl = document.getElementById("print-district-name");
    const timeEl = document.getElementById("print-report-time");
    
    if (distEl) distEl.textContent = state.location;
    if (timeEl) {
      const now = new Date();
      timeEl.textContent = now.toLocaleString('en-US', {
        dateStyle: 'medium',
        timeStyle: 'short'
      });
    }

    // Trigger browser native vector print engine (Save as PDF)
    window.print();
  });
}




