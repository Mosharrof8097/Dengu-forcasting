"""Tests for the EpiST-Shield API.

These exist because Reviewer 4 observed that the repository had none, and
because the specific failures this project has already suffered -- a fallback
reported as a model result, missing days read as zeros, a count that treats
Dhaka's two returns as two districts -- are all cheap to assert and were all
expensive to find by hand.

Each test names the defect it guards against.
"""
import os
import sys

import numpy as np
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from main import app  # noqa: E402

client = TestClient(app)

A_BULLETIN_DAY = "2023-09-26"       # the 2023 epidemic, every unit reporting
A_BLANK_DAY = "2024-09-01"          # inside the Jul-Dec 2024 source gap


# ----------------------------------------------------------------- health
def test_service_declares_no_fallback():
    """The deployed service previously ran a fallback while the manuscript
    said it did not. There is now no fallback path, and health must say so."""
    h = client.get("/api/health").json()
    assert h["model"]["loaded"] is True
    assert h["model"]["fallback"].startswith("none")
    assert h["tensorflow_required"] is False


def test_all_three_artifacts_present():
    a = client.get("/api/health").json()["artifacts"]
    assert all(a.values()), f"missing artifacts: {a}"


# -------------------------------------------------------------- districts
def test_dhaka_is_one_district_not_two():
    """Dhaka's metropolitan hospitals report separately. That is a
    sub-category, and counting it as a 65th district overstates coverage."""
    d = client.get("/api/districts").json()
    assert d["count"] == 64
    assert d["reporting_units"] == 65
    by = {x["name"]: x for x in d["districts"]}
    assert by["DhakaCity"]["parent"] == "Dhaka"
    assert by["Dhaka"]["parent"] is None


# ----------------------------------------------------------------- record
def test_a_day_with_no_bulletin_is_not_a_day_of_zeros():
    """The defect this whole rebuild exists to correct. A blank day must be
    reported as blank, never as a day on which nobody was admitted."""
    r = client.get(f"/api/record/{A_BLANK_DAY}").json()
    assert r["bulletin_issued"] is False
    assert r["reporting_units"] == 0
    assert r["national_admissions"] is None
    assert all(v["admissions"] is None for v in r["districts"].values())
    assert "not because there were no cases" in r["note"]


def test_a_real_bulletin_day_reports_its_districts():
    r = client.get(f"/api/record/{A_BULLETIN_DAY}").json()
    assert r["bulletin_issued"] is True
    assert r["reporting_units"] == 65
    assert r["national_admissions"] == 3123


def test_a_date_outside_the_record_is_404_not_an_empty_day():
    assert client.get("/api/record/1999-01-01").status_code == 404


# --------------------------------------------------------------- forecast
@pytest.mark.parametrize("h", [1, 2, 4])
def test_intervals_are_calibrated_at_every_horizon(h):
    """Conformalisation is the reason these intervals can be used for
    capacity. If coverage drifts away from nominal the claim fails."""
    s = client.get(f"/api/forecast?district=DhakaCity&horizon={h}").json()["skill"]
    assert 0.85 <= s["cov90"] <= 0.95, f"t+{h} cov90 {s['cov90']}"


@pytest.mark.parametrize("h", [1, 2, 4])
def test_the_model_beats_persistence_on_interval_score(h):
    """The published claim is about uncertainty, not point accuracy. This
    asserts the claim that is actually made."""
    s = client.get(f"/api/forecast?district=DhakaCity&horizon={h}").json()["skill"]
    assert s["wis"] < s["wis_persistence"]


def test_forecast_quantiles_never_cross():
    """A q05 above a q95 is incoherent, and conformal widening is applied per
    quantile, so it is worth checking rather than assuming."""
    s = client.get("/api/forecast?district=DhakaCity&horizon=1").json()["series"]
    q = s["q"]
    for lo, hi in (("q05", "q25"), ("q25", "q50"), ("q50", "q75"), ("q75", "q95")):
        a, b = np.array(q[lo]), np.array(q[hi])
        assert (a <= b + 1e-6).all(), f"{lo} exceeds {hi}"


def test_unknown_district_is_404():
    assert client.get("/api/forecast?district=Atlantis").status_code == 404


# --------------------------------------------------------------- planning
def test_capacity_rises_with_service_level():
    prev = -1
    for lvl in (50, 75, 90, 95, 99):
        b = client.get(f"/api/planning/Chattogram?service_level={lvl}").json()["beds"]
        assert b >= prev, f"capacity fell going to the {lvl}% level"
        prev = b


def test_season_needs_at_least_as_many_beds_as_the_annual_figure():
    """Dengue here is a July-November disease. Sizing on the annual
    distribution under-provisions the season, and the seasonal figure must
    reflect that."""
    season = client.get("/api/planning/Chattogram?season=true&service_level=95").json()
    year = client.get("/api/planning/Chattogram?season=false&service_level=95").json()
    assert season["beds"] >= year["beds"]


def test_dhaka_capacity_is_both_of_its_parts():
    d = client.get("/api/planning/Dhaka?service_level=95").json()
    c = d["combined_dhaka"]
    assert c["beds"] == pytest.approx(
        c["parts"]["rest_of_district"] + c["parts"]["metropolitan"])
    # the stay reported beside a combined bed count must describe both parts,
    # not whichever part the lookup happened to land on
    assert c["length_of_stay_days"]["median"] > d["length_of_stay_days"]["median"]


def test_an_uninterpolated_service_level_is_refused():
    """Only five quantiles were estimated. Interpolating between them would
    imply precision the sample does not support."""
    assert client.get("/api/planning/Dhaka?service_level=87").status_code == 422


def test_no_consumable_figures_are_served():
    """Test kits and saline were produced by multipliers with no source. They
    must not reappear anywhere in the response."""
    body = client.get("/api/planning/Dhaka").text.lower()
    for word in ("kit", "saline", "multiplier"):
        assert word not in body or word == "multiplier" and "no multiplier" in body


# ------------------------------------------------------------------ model
def test_the_published_model_runs_without_tensorflow():
    assert "tensorflow" not in sys.modules
    info = client.get("/api/model/info").json()
    assert info["parameters"] == 146177
    assert info["runtime"] == "numpy"


def test_the_model_loads_when_main_is_imported_by_path():
    """It did not. `from epist_numpy import ...` resolves only when the
    directory holding it is already on sys.path -- true when uvicorn is
    started inside backend/, false under a serverless handler that loads
    main.py by file path. Every local run worked while the deployment
    answered ModuleNotFoundError on every model request and still reported
    itself healthy.

    Loading by path with the directory deliberately absent from sys.path is
    what reproduces it; simply changing the working directory does not.
    """
    import subprocess
    backend = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
    probe = (
        "import importlib.util, sys\n"
        f"sys.path = [p for p in sys.path if p not in ({backend!r}, '')]\n"
        f"spec = importlib.util.spec_from_file_location('m', {backend + '/main.py'!r})\n"
        "m = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(m)\n"
        "print(m._model is not None, m._model_error)\n"
    )
    out = subprocess.run([sys.executable, "-c", probe], cwd="/",
                         capture_output=True, text=True, timeout=180)
    assert out.stdout.startswith("True"), (
        f"model did not load: {out.stdout.strip()} {out.stderr[-400:]}")


def test_the_model_loads_under_a_package_style_import():
    """A serverless handler commonly imports the entry point as
    `backend.main`, with only the project root on sys.path. That is the shape
    the Vercel deployment uses, and the one that left the model unloaded in
    production while every other import style worked."""
    import subprocess
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    probe = (
        "import sys\n"
        f"sys.path = [p for p in sys.path if p not in ({root + '/backend'!r}, '')]\n"
        f"sys.path.insert(0, {root!r})\n"
        "import backend.main as m\n"
        "print(m._model is not None, m._model_error)\n"
    )
    out = subprocess.run([sys.executable, "-c", probe], cwd="/",
                         capture_output=True, text=True, timeout=180)
    assert out.stdout.startswith("True"), (
        f"model did not load: {out.stdout.strip()} {out.stderr[-400:]}")


def test_prediction_is_deterministic():
    rng = np.random.default_rng(0)
    p = {"bio": rng.normal(size=(21, 3)).tolist(),
         "weather": rng.normal(size=(21, 3)).tolist()}
    a = client.post("/api/model/predict", json=p).json()["prediction"]
    b = client.post("/api/model/predict", json=p).json()["prediction"]
    assert a == b


@pytest.mark.parametrize("bad", [
    {"bio": [[1, 2, 3]], "weather": [[1, 2, 3]]},            # too short
    {"bio": [[1, 2]] * 21, "weather": [[1, 2, 3]] * 21},     # wrong width
])
def test_malformed_input_is_refused_rather_than_guessed(bad):
    """The previous service manufactured inputs when they were missing, which
    is how fallback output came to be reported as model output."""
    assert client.post("/api/model/predict", json=bad).status_code == 422


def test_non_finite_input_is_refused():
    """JSON has no NaN, so a conforming client cannot send one -- but Python's
    parser accepts the bare literal, so a careless one can. Posting the raw
    body is the only way to reach the server's finiteness check; encoding it
    client-side fails before the request is made."""
    body = ('{"bio": [' + ", ".join(["[NaN, 0, 0]"] * 21) + '], '
            '"weather": [' + ", ".join(["[0, 0, 0]"] * 21) + ']}')
    r = client.post("/api/model/predict", content=body,
                    headers={"Content-Type": "application/json"})
    assert r.status_code == 422, r.text


# ------------------------------------------------------------------- app
def test_the_application_is_served():
    for path in ("/", "/forecast.html", "/plan.html", "/app.css"):
        assert client.get(path).status_code == 200, path


def test_retired_interface_is_gone():
    """The files carrying the hard-coded latency string, the usability score
    and the resource multipliers were deleted, not edited."""
    front = os.path.join(os.path.dirname(__file__), "..", "frontend")
    for gone in ("app.js", "index.css", "bd-districts.json"):
        assert not os.path.exists(os.path.join(front, gone)), gone
