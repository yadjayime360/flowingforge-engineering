# Fluid Flow & Heat Transfer Engineering Suite

**PE 262 - Computer Programming (Capstone Project)**

A multi-page Streamlit web application that bundles three engineering
calculators into one deployed tool:

- **🔧 Pipe Flow Analyser** - fluid selection (with auto-populated
  properties), pipe geometry inputs, Darcy-Weisbach pressure drop,
  Reynolds number and flow-regime classification, an interactive
  pressure-drop-vs-flow-rate plot, and CSV export.
- **🌡️ Heat Transfer Calculator** - steady-state conduction through a
  flat wall (Fourier's Law) and Newton's Law of Cooling (time to reach
  a target temperature), with a live cooling-curve plot.
- **📊 Rock & Fluid Data Dashboard** - upload a CSV of rock/fluid sample
  data, view summary statistics, filter interactively, visualise with a
  histogram and crossplot, and download the filtered subset.

## Live app

🔗 **Live Streamlit app:** _\<paste your Streamlit Community Cloud URL
here after deploying\>_

## Project structure

```
.
├── Home.py                          # Landing page / app entry point
├── engineering.py                   # OOP engineering toolkit (Fluid, Pipe, FlatWall, CoolingBody)
├── pages/
│   ├── 1_Pipe_Flow_Analyser.py      # Module A
│   ├── 2_Heat_Transfer_Calculator.py# Module B
│   └── 3_Rock_Fluid_Dashboard.py    # Module C
├── sample_data/
│   └── rock_samples.csv             # Sample dataset for Module C
├── requirements.txt
└── README.md
```

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run Home.py
```

## Deploying to Streamlit Community Cloud

1. Push this repository to a **public** GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with
   GitHub, and click **New app**.
3. Select this repository/branch, set the main file path to `Home.py`,
   and click **Deploy**.
4. Once live, copy the app URL into the "Live app" section above and
   into your submission.

## Engineering design (OOP)

All physics lives in `engineering.py`, kept separate from the UI code so
it can be tested and reused independently:

| Class | Represents | Key methods |
|---|---|---|
| `Fluid` | A Newtonian fluid | `reynolds()`, `flow_regime()`, `kinematic_viscosity()` |
| `Pipe` | A circular pipe section | `velocity()`, `friction_factor()`, `pressure_drop()`, `report()` |
| `FlatWall` | A single-layer plane wall | `heat_flux()`, `heat_rate()` |
| `CoolingBody` | An object cooling toward ambient | `temperature_at()`, `time_to_reach()` |

Every method has a docstring, and constructors raise `ValueError` on
physically invalid input (e.g. non-positive diameter) so the Streamlit
pages can catch the error and show a friendly message instead of
crashing.

## Verification

Each calculator page includes a "✅ Verification" expander that walks
through a hand-calculated or analytical example and shows it matches
the app's output. See `engineering.py` docstrings for the underlying
formulas (Darcy-Weisbach, Swamee-Jain, Fourier's Law, Newton's Law of
Cooling).

## AI usage documentation

AI assistance (Claude) was used to help scaffold this project. All
generated code was read, tested against hand-calculated/analytical
examples, and adjusted before being included. Example prompts used:

1. **"Write an OOP `Pipe` class that computes Darcy-Weisbach pressure
   drop, using 64/Re for laminar flow and an explicit approximation to
   the Colebrook equation for turbulent flow."**
   *Verified by:* recalculating velocity, Reynolds number, and pressure
   drop by hand for water through a 50 mm x 200 m pipe at 0.01 m3/s and
   confirming the app's output matched.
   *Corrected:* the first draft used a constant turbulent friction
   factor (f = 0.02) with no dependence on pipe roughness or Reynolds
   number; this was replaced with the Swamee-Jain formula so the
   roughness input actually affects the result.

2. **"Build a Streamlit page for Newton's Law of Cooling with a slider
   for the cooling constant and a live cooling-curve plot."**
   *Verified by:* checking the analytical time-to-target formula
   `t = -ln[(T_target - T_inf)/(T0 - T_inf)]/k` against a worked example
   (T0=600°C, T_inf=25°C, k=0.02/min, target=50°C → t ≈ 156.8 min) and
   confirming the plotted curve passes through that point.
   *Corrected:* the first version let `T_target` be entered outside the
   valid range between `T0` and `T_inf`, which produced a math domain
   error from `log()` of a negative number; added input validation in
   `CoolingBody.time_to_reach()` that raises a clear `ValueError`
   instead of crashing.

3. **"Add file upload, summary statistics, filtering, and two charts to
   a rock/fluid data dashboard in Streamlit."**
   *Verified by:* uploading the bundled sample CSV and manually
   cross-checking the reported mean/min/max porosity against
   `pandas.DataFrame.describe()` run separately in a notebook.
   *Corrected:* the histogram/crossplot column pickers originally
   assumed columns named exactly `porosity` and `permeability_mD`
   existed; generalised so any numeric column can be selected, since a
   different CSV may use different column names.

_(Replace this section with your own actual prompts and findings before
submitting — this log should reflect the work you personally did.)_
