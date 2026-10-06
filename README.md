# EpiST-Shield

A decision-support application for dengue in Bangladesh, built on a
surveillance panel rebuilt from 1,674 DGHS daily bulletin PDFs.

The application has three tabs, deliberately separated by what backs each one:

| Tab | Shows | Rests on |
|---|---|---|
| **Record** | What happened | Bulletin facts only. Nothing modelled. |
| **Forecast** | What may happen | Rolling-origin forecasts whose outcomes are already known |
| **Plan** | What to prepare | The observed occupancy distribution at a service level you choose |

---

## The dataset

Rebuilt from the source PDFs rather than from intermediate files, because the
intermediate files turned out to be wrong.

| | |
|---|---|
| Source | DGHS daily dengue press releases |
| PDFs | 1,674, covering 1,669 distinct dates |
| Span | 2019-08-27 to 2026-07-07 |
| Resolution | daily, per district |
| Units | **64 districts.** Dhaka is reported in two parts — its metropolitan hospitals and the rest of the district — so there are 65 reporting units and 64 districts |
| Validation | 28 checks, **0 failures** |

**Where the bulletin record is complete, national annual totals reconstruct to
the published DGHS figures at 1.00×** — 2022: 62,084 against 62,382; 2023:
321,146 against 321,179. 2019 and 2024 fall short because only 125 and 238
bulletin dates survive for those years. That is a gap in the source, not an
extraction error, and the application says so wherever those years appear.

Further evidence: the stock identity
`cumulative − discharged − deaths = currently admitted` holds on **0 of
108,321 rows violating**; printed district subtotals agree with the sum of
their component rows in **8,025 of 8,025** cases; district attribution shows
**0 mismatches in 8,342 rows**.

### What is absent, and stays absent

* **2019 January–August and 2024 July–December have no bulletins.** They are
  not interpolated. Missing days are rendered as gaps, never as zeros.
* These are **hospital admissions, not infections.** Anyone not admitted does
  not appear.
* There is no serotype, vector or intervention data, because the bulletins
  carry none.
* 18.5% of district-days fall inside gaps whose period total is known from the
  cumulative column but whose daily split is not. They are marked separately
  and are not split.

---

## Forecast performance

Six-fold rolling origin with an embargo. The folds deliberately straddle
changes of epidemic phase, because forecasting across such a change is the
actual use case; a random split would score far better and mean nothing.

| Horizon | WIS | WIS, persistence | Gain | MAE (median) | MAE, persistence | 90% coverage |
|---|---|---|---|---|---|---|
| t+1 | 12.81 | 16.86 | **−24.0%** | 19.07 | 18.55 | 91.2% |
| t+2 | 18.81 | 25.85 | **−27.2%** | 27.02 | 27.93 | 89.8% |
| t+4 | 31.09 | 40.46 | **−23.2%** | 45.34 | 43.27 | 90.1% |

**Read this carefully, because it is easy to overstate.** On point accuracy the
model and persistence are tied — the model is slightly worse at t+1, slightly
better at t+2, slightly worse at t+4. The weekly lag-1 autocorrelation on this
panel is 0.973, so last week's count is already an extremely strong guess and
no model will beat it by much.

The model's advantage is in its **interval**. Weighted interval score is
roughly a quarter better at every horizon, and after conformalisation
(Romano et al.) coverage sits at nominal. Persistence intervals cover 73% at a
nominal 90% — badly wrong, in the direction that under-sizes capacity.

Coverage is not uniform across folds and the application shows the breakdown
rather than the average. At t+1 the first growth fold covers **70.2%** — too
narrow, in the dangerous direction — while quiet folds over-cover.

---

## Resource planning

There are no multipliers. An earlier version derived beds as 3.0 × peak daily
cases, test kits as 1.8 × total cases and saline as 2.5 × total cases. Those
constants had no source and have been **removed rather than re-derived**.

* **Beds** are not derived from cases at all. The bulletins report patients
  currently admitted per district, which *is* bed demand. The application
  shows the empirical distribution of that column and asks you for a service
  level. The identity above reproduces the printed stock on 99.3% of 106,179
  consecutive day-pairs, so the column can be trusted.
* **Length of stay** is measured by Little's Law on days with at least five
  admissions — Dhaka metropolitan 4.66 d, Chattogram 3.21 d, Khulna 3.90 d.
  It is reported for interpretation; the bed figure does not depend on it.
* **Test kits and saline are not shown anywhere.** The bulletins contain no
  consumable data, and a number with no provenance is worse than a blank.

A service level is a judgement about what being short costs against what idle
capacity costs. The application asks for it rather than choosing one.

---

## The model

`EpiST-Former`, 146,177 parameters, runs in **numpy alone**.

TensorFlow is needed to train this network, not to run it. The forward pass is
matrix arithmetic, reimplemented in `backend/epist_numpy.py` against weights
exported to a 536 KB `.npz`. `backend/verify_against_keras.py` asserts
agreement with the original Keras model to **7.9 × 10⁻⁶** maximum absolute
difference.

This matters for a specific reason. TensorFlow was previously absent from
`requirements.txt` while the code still required it, so the deployed service
was permanently in a fallback it did not advertise. **There is now no fallback
path at all**, and `GET /api/health` says so.

Input is a 21-step window: `bio (21, 3)` and `weather (21, 3)`, read from the
saved model rather than from documentation.

---

## Running it

```bash
git clone <repository-url>
cd epist-shield

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

uvicorn backend.main:app --reload --port 8000
```

Then open <http://localhost:8000>. The API is at `/docs`.

Requirements are `fastapi`, `uvicorn`, `pydantic` and `numpy` — nothing else,
and no TensorFlow. `requirements-dev.txt` adds TensorFlow for the equivalence
test alone.

### Tests

```bash
pip install -r requirements-dev.txt pytest httpx
python -m pytest tests/ -v
```

26 tests. Each one guards against a defect this project has already shipped
once: a blank day read as zeros, Dhaka counted as two districts, crossing
quantiles, intervals drifting from nominal, the model being credited with a
point-accuracy win it does not have, malformed input being guessed at rather
than refused.

CI runs them on Python 3.10 and 3.12 and **fails if TensorFlow is importable
in the runtime environment**, so the dependency cannot creep back in unnoticed.

---

## API

Every endpoint serves a validated artifact or the published model. Nothing is
simulated.

| Endpoint | Returns |
|---|---|
| `GET /api/health` | model state, artifacts present, no fallback |
| `GET /api/districts` | 64 districts, 65 reporting units, Dhaka's parent marked |
| `GET /api/record/{date}` | bulletin facts, with `bulletin_issued` |
| `GET /api/forecast?district=&horizon=` | rolling-origin series, skill, per-fold coverage |
| `GET /api/forecast/skill` | headline skill at every horizon |
| `GET /api/planning/{district}` | occupancy distribution, measured length of stay |
| `POST /api/model/predict` | the published model; caller supplies the windows |
| `GET /api/model/info` | parameters, input shape, equivalence statement |

`/api/model/predict` requires real 21×3 windows and refuses malformed or
non-finite input. It will not manufacture an input in order to have something
to return — the previous service's habit of doing so is how fallback output
came to be reported as model output.

A date with no bulletin returns `bulletin_issued: false` and nulls, with a note
saying the record is empty rather than the day being case-free. Conflating
those two is the defect this rebuild exists to correct.

---

---

## Regenerating the data the application reads

The application serves three artifacts from `frontend/data/`. The code that
produces them is in `pipeline/`, in this repository — an earlier arrangement
scattered it across three sibling directories and assumed one person's folder
layout, so a clone of this repository could run the application but could not
rebuild its inputs.

| Artifact | Built by | Needs |
|---|---|---|
| `surveillance.json` | `pipeline/export_for_app.py` | the locked dataset |
| `forecasts.json` | `pipeline/export_forecasts_for_app.py` | the evaluation output |
| `planning.json` | `pipeline/export_planning_for_app.py` | the locked dataset |

```bash
pip install -r requirements-dev.txt

python pipeline/export_for_app.py           --dataset     /path/to/dengue64/data/processed
python pipeline/export_planning_for_app.py  --dataset     /path/to/dengue64/data/processed
python pipeline/export_forecasts_for_app.py --experiments /path/to/dengue64/experiments
```

`--dataset` and `--experiments` may also be given as `DENGUE64_DATA` and
`DENGUE64_EXPERIMENTS`. The three small lookup tables these scripts need —
district names, divisions and census population — travel with the repository
in `pipeline/reference/`. The large inputs do not: `grid_v1.csv` (12 MB), the
repaired district geometry (3.7 MB) and the weekly quantile predictions
(6.4 MB) are outputs of the **dengue64 dataset pipeline**, which is a separate
artifact with its own validation and its own lock file.

The model weights are exported the same way:

```bash
python pipeline/export_weights.py          # needs TensorFlow; see requirements-dev.txt
python backend/verify_against_keras.py     # asserts the numpy port still matches
```

`export_weights.py` refuses to write a file whose key names do not match what
`backend/epist_numpy.py` reads, because such a file would load cleanly and
then fail at the first lookup.

---

## Status of this revision

This repository was substantially rebuilt in response to peer review. Nineteen
defects were found and corrected, including six in the dataset behind the
originally published results, four we introduced during the revision itself,
and several figures and tables whose numbers were not measured.

`_archive/` holds the superseded material and is excluded from the repository.

Known gaps, stated rather than hidden:

* Intervals under-cover during epidemic growth (70.2% at t+1 in the first
  growth fold, against a nominal 90%).
* The forecasts served are retrospective. The application does not currently
  produce a live forecast for an unknown future.
* The published `EpiST-Former` network and the `QuantileGBM-CQR` forecasts
  shown in the Forecast tab are **different analyses**. The former is served
  by `/api/model/predict`; the latter produced the evaluation table above.

---

## License

MIT. See [LICENSE](LICENSE).
