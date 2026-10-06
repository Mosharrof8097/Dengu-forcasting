"""EpiST-Shield API.

What this service does, and what it refuses to do
-------------------------------------------------
It serves the application and the three validated artifacts the application
reads, and it runs the published forecasting model. It does not invent
anything, which is a change from the version the reviewers examined.

Removed outright, with the reason:

* **TensorFlow.** It was absent from requirements.txt, so `HAS_TF` was False in
  production and every response came from a fallback while the manuscript
  stated `fallback_active: false`. The published network now runs through
  `epist_numpy`, verified equal to Keras to 7.9e-06. There is no fallback left
  to be in, so the question of which one is served no longer arises.

* **The synthetic trajectory.** The old `/api/forecast/multi-horizon` returned
  `0.55 + 0.50*exp(-(d-peak)^2/2s^2) + 0.05*sin(0.8d)` scaled by one model
  output, with the peak day hard-coded per horizon. That is a drawn shape, not
  a forecast. Forecasts now come from the rolling-origin evaluation, where each
  one was made before its outcome was known.

* **Fabricated inputs.** `DISTRICT_BASE_CASES` supplied invented baseline case
  counts and the weather fields were accepted unvalidated. `/api/model/predict`
  now requires the caller to provide the real 21-day windows. The service will
  not manufacture an input in order to have something to return.

* **The resource multipliers** (3.0 beds, 1.8 kits, 2.5 saline) and the
  `0.655` vector-control factor. None had a source. Bed demand is served from
  the observed occupancy distribution instead; consumables are not served at
  all, because the bulletins contain no consumable data.

* **`DISTRICTS_11`.** The panel has 64 districts, with Dhaka reported in two
  parts. The district list is read from the data rather than hard-coded.
"""
import json
import os
import time
from typing import Dict, List, Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

HERE = os.path.dirname(os.path.abspath(__file__))
FRONTEND = os.path.abspath(os.path.join(HERE, "..", "frontend"))
DATA = os.path.join(FRONTEND, "data")

app = FastAPI(
    title="EpiST-Shield API",
    description="Dengue surveillance record, rolling-origin forecasts and "
                "capacity planning for Bangladesh. Every endpoint serves a "
                "validated artifact or the published model; nothing is "
                "simulated.",
    version="3.0.0",
)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


# --------------------------------------------------------------- artifacts
def _load(name: str) -> Optional[dict]:
    """Artifacts are read once at import. They are a few megabytes and never
    change while the process lives, so re-reading per request would buy
    nothing. A missing file is not fatal: the endpoints that need it say so,
    and the rest of the service keeps working."""
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        print(f"warning: {name} not found at {p}")
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


RECORD = _load("surveillance.json")
FORECASTS = _load("forecasts.json")
PLANNING = _load("planning.json")

# Dhaka's metropolitan hospitals report separately. That is a sub-category of
# Dhaka district, not a 65th district, and the count must say so.
METRO_OF = {"DhakaCity": "Dhaka"}


def _districts() -> List[dict]:
    if not RECORD:
        return []
    out = []
    for d in RECORD["districts"]:
        out.append({
            "name": d["name"],
            "division": d.get("division"),
            "latlon": d.get("latlon"),
            "population": d.get("population"),
            "parent": METRO_OF.get(d["name"]),
        })
    return out


def _need(obj, what: str):
    if obj is None:
        raise HTTPException(
            503, f"{what} is not available: its artifact was not found in "
                 f"{DATA}. Run the scripts in pipeline/ to produce it.")
    return obj


# ------------------------------------------------------------------- model
_model = None
_model_error = None
try:
    from epist_numpy import get_model, LOOKBACK, N_BIO, N_WEATHER
    _model = get_model()
except Exception as exc:                                  # noqa: BLE001
    _model_error = f"{type(exc).__name__}: {exc}"
    LOOKBACK, N_BIO, N_WEATHER = 21, 3, 3
    print(f"warning: EpiST-Former unavailable -- {_model_error}")


# ------------------------------------------------------------------ health
@app.get("/api/health")
def health():
    """Facts about this deployment. No grades, no scores, no claims that a
    reader cannot check against the repository."""
    return {
        "status": "online",
        "version": app.version,
        "model": {
            "name": "EpiST-Former",
            "runtime": "numpy",
            "loaded": _model is not None,
            "error": _model_error,
            "parameters": _model.n_params if _model else None,
            "equivalence": "verified against the Keras reference to 7.9e-06 "
                           "maximum absolute difference; see "
                           "verify_against_keras.py",
            "fallback": "none; this service has no fallback path",
        },
        "artifacts": {
            "record": bool(RECORD),
            "forecasts": bool(FORECASTS),
            "planning": bool(PLANNING),
        },
        "tensorflow_required": False,
    }


# ----------------------------------------------------------------- record
@app.get("/api/districts")
def districts():
    _need(RECORD, "the surveillance record")
    ds = _districts()
    return {
        "count": len([d for d in ds if d["parent"] is None]),
        "reporting_units": len(ds),
        "note": "64 districts. Dhaka is reported in two parts -- its "
                "metropolitan hospitals and the rest of the district -- which "
                "is why there are 65 reporting units and 64 districts.",
        "districts": ds,
    }


@app.get("/api/record/{date}")
def record(date: str):
    """Bulletin facts for one date. A district absent from the bulletin is
    returned as null, never as zero -- conflating the two is the defect this
    rebuild exists to correct."""
    r = _need(RECORD, "the surveillance record")
    try:
        i = r["dates"].index(date)
    except ValueError:
        raise HTTPException(
            404, f"no bulletin for {date}. The record runs "
                 f"{r['dates'][0]} to {r['dates'][-1]} and covers "
                 f"{len(r['dates'])} dates; days without a bulletin are absent "
                 f"from it.")
    names = [d["name"] for d in r["districts"]]
    cases, occ = r["cases"][i], r["occupancy"][i]
    reporting = sum(1 for v in cases if v is not None)

    # The record spans every calendar day, but only 1,669 of 2,507 carry a
    # bulletin. Returning all-nulls without saying why invites the caller to
    # read them as zeros, which is the precise confusion this dataset was
    # rebuilt to remove -- so the response states it outright.
    return {
        "date": date,
        "bulletin_issued": reporting > 0,
        "reporting_units": reporting,
        "national_admissions": r["national"][i],
        "districts": {n: {"admissions": cases[j], "occupancy": occ[j]}
                      for j, n in enumerate(names)},
        "note": ("no bulletin was issued for this date; every value is null "
                 "because the record is empty, not because there were no "
                 "cases") if reporting == 0 else
                "null for a district means it did not appear in this "
                "bulletin; it does not mean zero",
        "meta": r["meta"],
    }


# --------------------------------------------------------------- forecasts
@app.get("/api/forecast")
def forecast(district: str, horizon: int = 1):
    """A rolling-origin forecast series: at each origin the model saw only
    earlier data, and the outcome is now known. This is deliberately not a
    prediction of an unknown future -- it is the evidence on which such a
    prediction would rest."""
    f = _need(FORECASTS, "the forecast evaluation")
    s = f["series"].get(district)
    if s is None:
        raise HTTPException(
            404, f"no forecasts for '{district}'. Available: "
                 f"{', '.join(f['districts'][:5])}, ...")
    h = s.get(str(horizon))
    if h is None:
        raise HTTPException(
            404, f"horizon t+{horizon} was not evaluated. Available: "
                 f"{', '.join(sorted(s))}")
    return {
        "district": district,
        "horizon": horizon,
        "skill": f["skill"].get(str(horizon)),
        "coverage_by_fold": f["coverage_by_fold"].get(str(horizon)),
        "series": h,
        "meta": f["meta"],
    }


@app.get("/api/forecast/skill")
def skill():
    f = _need(FORECASTS, "the forecast evaluation")
    return {"skill": f["skill"], "coverage_by_fold": f["coverage_by_fold"],
            "meta": f["meta"]}


# ---------------------------------------------------------------- planning
@app.get("/api/planning/{district}")
def planning(district: str, season: bool = True, service_level: int = 95):
    """Capacity from the observed occupancy distribution. There is no
    multiplier: the service level is the judgement, and it belongs to the
    caller."""
    p = _need(PLANNING, "the planning inputs")
    rec = p["districts"].get(district)
    if rec is None:
        raise HTTPException(404, f"no planning record for '{district}'")
    if service_level not in (50, 75, 90, 95, 99):
        raise HTTPException(
            422, "service_level must be one of 50, 75, 90, 95, 99 -- these are "
                 "the quantiles estimated from the record, and interpolating "
                 "between them would imply precision the sample does not "
                 "support")

    key = "occupancy_season" if season else "occupancy"
    beds = rec[key]["quantiles"].get(str(service_level))

    # Dhaka's requirement is both of its reported parts. Summing the two
    # quantiles is conservative -- the parts need not peak on the same day --
    # and the response says so rather than hiding the assumption.
    combined = None
    if district == "Dhaka" and "DhakaCity" in p["districts"]:
        mrec = p["districts"]["DhakaCity"]
        metro = mrec[key]["quantiles"].get(str(service_level))
        if beds is not None and metro is not None:
            # Weighted by admissions: a plain mean of the two medians would
            # give the part with 20 admissions a day the same say as the part
            # with 1,300, and the reported stay would describe neither.
            combined = {
                "beds": beds + metro,
                "parts": {"rest_of_district": beds, "metropolitan": metro},
                "length_of_stay_days": _blended_los(rec, mrec),
                "caveat": "the sum of two quantiles; the two parts need not "
                          "reach their peaks on the same day, so this is an "
                          "upper estimate",
            }

    return {
        "district": district,
        "service_level": service_level,
        "period": "July-November" if season else "whole year",
        "beds": beds,
        "combined_dhaka": combined,
        "length_of_stay_days": rec["los_days"],
        "observed": {"days": rec["n_days"],
                     "peak_occupancy": rec["occupancy"]["max"],
                     "mean_admissions_per_day": rec["admissions"]["mean"]},
        "quantiles": rec[key]["quantiles"],
        "meta": p["meta"],
    }


def _blended_los(*recs):
    """Length of stay across several reporting units, weighted by how many
    patients each admits."""
    num = den = 0.0
    n = 0
    for r in recs:
        los, adm = r["los_days"]["median"], r["admissions"]["mean"]
        if los is None or not adm:
            continue
        num += los * adm
        den += adm
        n += r["los_days"]["n"]
    if den == 0:
        return None
    return {"median": round(num / den, 2), "n": n,
            "basis": "weighted by mean daily admissions across the parts"}


# ------------------------------------------------------------------- model
class PredictRequest(BaseModel):
    """The caller supplies the real windows. The service does not synthesise
    them: an invented input produces an invented output that is
    indistinguishable from a real one, which is how the previous version came
    to report fallback numbers as model numbers."""
    bio: List[List[float]] = Field(
        ..., description="21 x 3 — the biological window the model was trained "
                         "on, oldest row first, already scaled as in training")
    weather: List[List[float]] = Field(
        ..., description="21 x 3 — the matching weather window, same scaling")


@app.post("/api/model/predict")
def predict(req: PredictRequest):
    if _model is None:
        raise HTTPException(503, f"model unavailable: {_model_error}")
    bio = np.asarray(req.bio, dtype=np.float32)
    wx = np.asarray(req.weather, dtype=np.float32)
    for name, arr in (("bio", bio), ("weather", wx)):
        want = (LOOKBACK, N_BIO if name == "bio" else N_WEATHER)
        if arr.shape != want:
            raise HTTPException(
                422, f"{name} must have shape {want}, got {tuple(arr.shape)}")
    if not np.isfinite(bio).all() or not np.isfinite(wx).all():
        raise HTTPException(422, "inputs contain NaN or infinity")

    t0 = time.perf_counter()
    y = _model.predict_one(bio, wx)
    ms = (time.perf_counter() - t0) * 1000.0
    return {
        "prediction": y,
        "latency_ms": round(ms, 3),
        "model": "EpiST-Former (numpy)",
        "note": "a single measurement on this request, not a benchmark and "
                "not a published figure",
    }


@app.get("/api/model/info")
def model_info():
    if _model is None:
        raise HTTPException(503, f"model unavailable: {_model_error}")
    return {
        "name": "EpiST-Former",
        "parameters": _model.n_params,
        "runtime": "numpy",
        "input": {"bio": [LOOKBACK, N_BIO], "weather": [LOOKBACK, N_WEATHER]},
        "equivalence": "max abs difference 7.9e-06 against the Keras "
                       "reference; asserted by verify_against_keras.py",
        "caveat": "this is the network published with the manuscript. The "
                  "forecasts served by /api/forecast come from the "
                  "rolling-origin quantile evaluation on the rebuilt "
                  "64-district panel, which is a different and later "
                  "analysis.",
    }


# The mount is last so that every /api route is matched before it.
if os.path.isdir(FRONTEND):
    app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="app")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
