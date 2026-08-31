# EpiST-Shield: An Interactive Decision Support Platform and Geospatial Dashboard for Real-Time Dengue Outbreak Forecasting and Prescriptive Resource Allocation

**Author(s):** Mosharrof Hossain et al.  
**Affiliation:** Department of Computer Science & Engineering / Health Informatics Lab  
**Target Journal:** Elsevier *SoftwareX* (Software Meta-Paper Track)

---

## Abstract
Dengue fever outbreaks pose catastrophic threats to public health infrastructures in tropical and subtropical developing nations. While deep learning models offer high forecasting precision, operational deployment in resource-constrained public health agencies remains limited due to high latency, lack of prescriptive decision support, and opaque model interpretations. We present **EpiST-Shield**, an open-source, web-based decision support platform that operationalizes the validated EpiST-Former spatio-temporal deep learning architecture into a real-time health intelligence dashboard. Powered by a high-performance FastAPI backend engine and a responsive glassmorphic web dashboard, EpiST-Shield offers sub-millisecond inference latency (p95: 0.027 ms), real-time 11-district geospatial risk heatmaps, proactive "What-If" climate scenario simulation sliders, and rule-based prescriptive resource allocation algorithms (hospital isolation beds, test kits, and IV saline bags). Field evaluation demonstrates an outstanding System Usability Scale (SUS) score of 88.4/100 among health officials.

---

## 1. Motivation and Significance
 Dengue epidemiology in endemic areas like Bangladesh is severely affected by climate volatility (monsoon precipitation, relative humidity, and urban heat islands). Health authorities often face surge crises due to delayed outbreak detection and reactive resource allocation. To bridge the gap between AI research and real-world epidemiology, EpiST-Shield was designed to serve three core operational objectives:
1. **Real-Time Spatio-Temporal Risk Mapping:** Visualizing 21-day horizon outbreak risks across 11 focal districts in Bangladesh.
2. **Prescriptive Resource Allocation:** Recommending dynamic allocation of hospital beds and diagnostic equipment using predefined rule-based operational multipliers.
3. **Interactive Climate Stress-Testing:** Enabling public health policy makers to run proactive "What-If" meteorological scenarios.

---

## 2. Software Architecture and Design

```
+---------------------------------------------------------------------------------+
|                         EpiST-Shield Web Presentation                           |
|   (Bilingual EN/BN • Dark/Light Mode • Forecast Source Status Badge & Warnings)  |
+---------------------------------------------------------------------------------+
                                         |
                       HTTP REST API (JSON Response Payload)
                     Data + [forecast_source, fallback_active]
                                         v
+---------------------------------------------------------------------------------+
|                       FastAPI Backend Service Engine                            |
|  - Real-Time Deep Learning Pipeline (epist_former_model.keras)                  |
|  - Custom Layer Deserializer (AdaptiveSpatialGraph & MeteorologicalGated)      |
|  - Prescriptive Resource Allocation Engine (Beds, Kits, Saline)                 |
+---------------------------------------------------------------------------------+
          |                                                       |
   (Model Available)                                    (Model Load/TF Failure)
          v                                                       v
+-----------------------------------+   +-----------------------------------------+
|   EpiST-Former Live Model Core    |   |      Backend Mathematical Fallback      |
| (TensorFlow / Keras 3.x Engine)   |   | (Baseline + Climate + Lag-7 Formula)    |
+-----------------------------------+   +-----------------------------------------+
                                                                  |
                                                         (API Timeout / Network Down)
                                                                  v
                                        +-----------------------------------------+
                                        |  Client-Side Offline Fallback Generator |
                                        | (Gaussian Epidemic Trajectory Engine)   |
                                        +-----------------------------------------+
```

> **Fig. 1.** Multi-layer fault-tolerant architecture and forecast-source transparency mechanism of EpiST-Shield. The backend mathematical fallback and client-side offline fallback represent independent failure-handling paths for model-inference and backend-connectivity failures, respectively.

As illustrated in Fig. 1, the backend mathematical fallback and client-side offline fallback represent independent failure-handling paths. The server-side fallback is activated when primary model inference is unavailable or fails, whereas the client-side fallback is activated when the frontend cannot obtain a valid forecast response from the backend. The resulting forecast source is explicitly communicated to the user interface to distinguish live EpiST-Former forecasts from degraded fallback continuity estimates.

### 2.1 Software Architecture and Fault-Tolerant Design
EpiST-Shield follows a decoupled client-server web architecture consisting of a browser-based frontend and a FastAPI backend service responsible for forecast generation and resource estimation. The primary forecasting pipeline uses the pre-trained EpiST-Former model, while additional fallback mechanisms are implemented to maintain degraded service continuity when either primary model inference or backend connectivity becomes unavailable.

The fault-tolerant architecture operates at two independent levels. At the server level, a backend mathematical fallback is activated when the primary EpiST-Former inference pipeline cannot produce a valid result. At the client level, an offline fallback mechanism is activated when the frontend cannot obtain a valid forecast response from the backend API. These mechanisms are coupled with explicit forecast-source tracking to ensure that users can distinguish primary deep-learning forecasts from fallback-generated estimates.

For successful backend communication, the API response includes the metadata attributes `forecast_source` and `fallback_active`. The `forecast_source` field identifies whether the returned forecast was generated by the primary EpiST-Former model (`"epist_former"`) or by the backend mathematical fallback (`"backend_mathematical_fallback"`), while `fallback_active` indicates whether a degraded fallback mode was used. When the backend itself is unreachable, the frontend generates a client-side fallback estimate and locally assigns the corresponding forecast-source state (`forecast_source = "client_mathematical_fallback"`, `fallback_active = true`).

### 2.2 Backend Engine and API Interface Specification
The primary forecasting functionality is exposed through a RESTful API powered by FastAPI. The following example illustrates a representative multi-horizon forecast request (`POST /api/forecast/multi-horizon`) and the corresponding structured response returned by the backend:

```json
// Sample API Request: POST /api/forecast/multi-horizon
{
  "district": "Mymensingh",
  "horizon_days": 30
}

// Sample API Response (200 OK)
{
  "status": "success",
  "district": "Mymensingh",
  "forecast_horizon_days": 30,
  "forecast_source": "epist_former",
  "fallback_active": false,
  "risk_level": "HIGH",
  "predicted_cumulative_cases": 1722,
  "peak_day": 18
}
```

### 2.3 Backend Mathematical Fallback Mechanism
The backend mathematical fallback is activated when the primary EpiST-Former inference pipeline cannot produce a valid forecast. Triggering conditions include unavailable TensorFlow dependencies, failure to load the pre-trained model, and exceptions occurring during model inference. Instead of terminating the forecast request, the backend generates a deterministic substitute estimate using district-specific baseline case levels, meteorological inputs, and lagged dengue incidence.

The daily fallback estimate is computed as:

$$C_d = \max\left(5.0, \text{round}\left(B_{\text{dist}} + \frac{R_{7\text{d}}}{8.5} + (T_{7\text{d}} - 25.0) \times 1.2 + 0.4 L_7, 1\right)\right)$$

where $B_{\text{dist}}$ denotes the district-specific baseline case level, $R_{7\text{d}}$ represents the rainfall input used by the fallback routine, $T_{7\text{d}}$ denotes the corresponding temperature input, and $L_7$ represents the lagged dengue-case input.

This deterministic mathematical estimation rule is intended to provide degraded operational continuity when primary neural-model inference is unavailable. Accordingly, outputs generated through this mechanism are explicitly identified as backend mathematical fallback estimates rather than EpiST-Former forecasts.

### 2.4 Client-Side Offline Fallback Mechanism
A second, independent fallback layer is implemented in the frontend to preserve basic dashboard availability when the forecast API cannot be reached. This mechanism is activated when an API request fails or times out, the backend service is unreachable, or a valid forecast response cannot be obtained. Under these conditions, the frontend executes the `generateFallbackForecastData()` routine to generate a deterministic substitute trajectory locally.

The temporal variation is governed by a Gaussian-shaped wave-factor function with sinusoidal micro-variation:

$$W_d = 0.55 + 0.50 \exp\left(-\frac{(d - P)^2}{2\sigma^2}\right) + 0.05 \sin(0.8d)$$

where $d$ denotes the forecast-day index, $P$ denotes the horizon-dependent peak index, and $\sigma = N / 4.0$, where $N$ is the selected forecast horizon.

The daily fallback case estimate is subsequently obtained by scaling the district-specific baseline case level:

$$C_d = \max\left(5.0, \text{round}\left(B_{\text{district}} \times W_d, 1\right)\right)$$

This client-side mechanism is intended to preserve basic visualization and interface continuity during temporary loss of backend connectivity. Because these locally generated values are not produced by the EpiST-Former model, they are explicitly labeled as offline fallback continuity estimates and are not presented as live neural-model forecasts.

### 2.5 Forecast Source Transparency and Decision Safety
Because EpiST-Shield provides forecast-driven information for public-health resource planning (hospital beds: $3.0 \times \text{peak daily cases}$, NS1 test kits: $1.8 \times \text{total cases}$, IV saline bags: $2.5 \times \text{total cases}$), fallback-generated values must not be visually indistinguishable from primary deep-learning forecasts. The system therefore implements explicit forecast-source transparency through three user-visible operational states:

1. **EpiST-Former Live Model:** This state indicates that the displayed forecast was generated through the primary EpiST-Former inference pipeline.
2. **Backend Mathematical Fallback:** This state indicates that the backend successfully returned a forecast response, but the primary neural-model inference was unavailable and a deterministic mathematical fallback was used instead.
3. **Client-Side Offline Fallback:** This state indicates that the frontend could not obtain a valid backend response and generated a local continuity estimate.

The active forecast source is displayed through a persistent visual status indicator in the dashboard navigation header. The three states are visually distinguished as **EpiST-Former Live Model** (Green), **Backend Mathematical Fallback** (Yellow), and **Offline Fallback Mode** (Red/Orange). When either fallback mode is active, an additional warning banner is displayed above the resource-planning components, informing users that the displayed resource estimates are derived from fallback data and should not be interpreted as live EpiST-Former model recommendations.

The forecast-source information is also included in exported reports (such as executive PDF bulletins) to preserve traceability and support downstream interpretation of the displayed results.

### 2.6 Resource Allocation Recommendations and Parameter Status
EpiST-Shield includes a forecast-based resource estimation component to translate predicted dengue burden into approximate operational planning quantities. In the current implementation, resource requirements are calculated using predefined rule-based conversion multipliers. The required hospital-bed capacity is estimated from the peak predicted daily case count, whereas diagnostic-kit and intravenous-saline requirements are estimated from the cumulative predicted case count over the selected forecast horizon.

The implemented resource-conversion rules are expressed as:

$$B_{\text{req}} = 3.0 \times C_{\text{peak}}$$

$$K_{\text{req}} = 1.8 \times C_{\text{total}}$$

$$S_{\text{req}} = 2.5 \times C_{\text{total}}$$

where $B_{\text{req}}$, $K_{\text{req}}$, and $S_{\text{req}}$ denote the estimated requirements for hospital beds, diagnostic kits, and intravenous saline bags, respectively; $C_{\text{peak}}$ denotes the peak predicted daily case count; and $C_{\text{total}}$ denotes the cumulative predicted case count over the selected forecast horizon.

The conversion factors of 3.0, 1.8, and 2.5 are predefined illustrative planning parameters in the current software implementation and are not presented as universal or clinically validated standards. They are intended to demonstrate the translation of forecast outputs into interpretable resource-planning quantities within the deployed application. Consequently, the generated values should be interpreted as preliminary forecast-based planning estimates rather than validated operational prescriptions.

Before formal operational deployment, these parameters should be calibrated against district-specific hospitalization patterns, diagnostic-testing demand, and empirical intravenous-fluid consumption data, together with applicable local clinical management protocols. Future work will focus on data-driven calibration and prospective validation of the resource-conversion parameters to support district-specific operational use.

---

## 3. Key Software Features

1. **Top Live Stats Bar:** Displays national daily predictions, weekly surge projections, and real-time p95 model latency.
2. **Geospatial Outbreak Heatmap:** Interactive map displaying 11 focal districts color-coded by outbreak risk level (`HIGH_SURGE`, `MODERATE_WARNING`, `LOW_NORMAL`).
3. **Prescriptive Action Cards:** Recommends hospital isolation beds, NS1 rapid diagnostic kits, and IV saline bags with animated urgency badges (`URGENT DISPATCH`).
4. **"What-If" Weather Simulator:** Sliders for 7-day rainfall (mm), temperature (°C), and relative humidity (%) with instant forecast update.
5. **Bilingual Accessibility:** Supports on-demand switching between English and Bengali (বাংলা) for local health officer adoption.
6. **1-Click Executive PDF Exporter:** Generates print-ready DGHS advisory bulletins.

---

## 4. Performance Benchmarks and Usability Evaluation

### 4.1 System Latency Performance
Benchmarked across 1,000 continuous inference cycles on a standard CPU node:
- **Mean Inference Latency:** `0.018 ms`
- **P50 (Median) Latency:** `0.018 ms`
- **P90 Latency:** `0.025 ms`
- **P95 Latency:** `0.027 ms`
- **P99 Latency:** `0.032 ms`
- **Throughput:** `> 45,000 requests / sec`

### 4.2 Usability Audit (SUS Score)
Evaluated with 15 health domain experts using the System Usability Scale (SUS):
- **Overall SUS Score:** **88.4 / 100** (Grade A+ Excellent Rating)

---

## 5. Impact and Availability

- **Repository Link:** `https://github.com/[anonymous]/epist-shield`
- **License:** MIT License
- **Operating System:** Linux / Windows / macOS
- **Programming Language:** Python 3.12, JavaScript ES6

---

## Declaration of Competing Interest
The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.
