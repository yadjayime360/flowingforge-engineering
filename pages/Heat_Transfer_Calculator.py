"""
pages/2_Heat_Transfer_Calculator.py
=====================================
Module B - Heat Transfer Calculator (5 marks)

Two calculations:
  1) Steady-state conduction through a single-layer flat wall (Fourier's Law)
  2) Newton's Law of Cooling - time to cool from T0 to a target temperature,
     with a live cooling-curve plot.
"""

import math

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from engineering import CoolingBody, FlatWall

st.set_page_config(page_title="Heat Transfer Calculator", page_icon="🌡️", layout="wide")
st.title("🌡️ Heat Transfer Calculator")

tab1, tab2 = st.tabs(["🧱 Conduction through a flat wall", "❄️ Newton's Law of Cooling"])

# ======================================================================
# TAB 1 - Fourier's Law, single-layer flat wall conduction
# ======================================================================
with tab1:
    st.subheader("Steady-state conduction through a flat wall (Fourier's Law)")
    st.write(
        "Models heat flowing through one flat layer of material of "
        "uniform thickness and conductivity, e.g. a furnace wall, an "
        "insulation panel, or a window pane - once conditions have "
        "settled (steady state, no change with time)."
    )

    col1, col2 = st.columns([1, 1.3])

    with col1:
        st.markdown("**Inputs**")
        L_mm = st.number_input(
            "Wall thickness, L (mm)", min_value=1.0, value=200.0, step=10.0,
            help="Distance the heat has to travel through the material, "
            "measured perpendicular to the wall face.",
        )
        k = st.number_input(
            "Thermal conductivity, k (W/m.K)", min_value=0.001, value=0.8,
            step=0.05, format="%.3f",
            help="How easily heat passes through the material. Roughly: "
            "still air approx 0.025, brick approx 0.7-1.0, "
            "steel approx 45-60, copper approx 390 (all W/m.K).",
        )
        area = st.number_input(
            "Wall area, A (m2)", min_value=0.01, value=10.0, step=1.0,
            help="Surface area of the wall face through which heat flows.",
        )
        T_hot = st.number_input(
            "Hot-side surface temperature, T_hot (degC)", value=60.0,
            help="Temperature of the warmer face of the wall.",
        )
        T_cold = st.number_input(
            "Cold-side surface temperature, T_cold (degC)", value=20.0,
            help="Temperature of the cooler face of the wall.",
        )

    try:
        wall = FlatWall(thickness=L_mm / 1000, conductivity=k, area=area)
        q_flux = wall.heat_flux(T_hot, T_cold)
        Q_rate = wall.heat_rate(T_hot, T_cold)

        with col2:
            st.markdown("**Results**")
            m1, m2 = st.columns(2)
            m1.metric("Heat flux, q''", f"{q_flux:,.1f} W/m2")
            m2.metric("Total heat rate, Q", f"{Q_rate:,.1f} W")
            st.write(f"That is approximately **{Q_rate/1000:,.3f} kW** flowing "
                     f"through the wall continuously while these conditions hold.")

            if q_flux < 0:
                st.info(
                    "Heat flux is negative - heat is actually flowing from "
                    "the 'cold' side to the 'hot' side, because T_cold is "
                    "greater than T_hot as entered."
                )

        with st.expander("✅ Verification against a hand-calculated example"):
            st.markdown(
                """
                For a brick wall with **L = 0.2 m**, **k = 0.8 W/m.K**,
                **A = 10 m2**, T_hot = 60 degC, T_cold = 20 degC:

                q'' = k(T_hot - T_cold)/L = 0.8 x 40 / 0.2 = **160 W/m2**

                Q = q'' x A = 160 x 10 = **1600 W (1.6 kW)**

                This matches the default values pre-loaded in the app above.
                """
            )
    except ValueError as e:
        st.error(f"Invalid input: {e}")

# ======================================================================
# TAB 2 - Newton's Law of Cooling
# ======================================================================
with tab2:
    st.subheader("Newton's Law of Cooling")
    st.write(
        "Models how an object's temperature decays exponentially toward "
        "the temperature of its surroundings over time - "
        "T(t) = T_inf + (T0 - T_inf) x exp(-k t)."
    )

    col1, col2 = st.columns([1, 1.3])

    with col1:
        st.markdown("**Inputs**")
        T0 = st.number_input(
            "Initial temperature, T0 (degC)", value=90.0,
            help="Starting temperature of the object at time t = 0.",
        )
        T_inf = st.number_input(
            "Ambient temperature, T_inf (degC)", value=25.0,
            help="Temperature of the surrounding air/fluid, which the "
            "object's temperature approaches over time.",
        )
        k_cool = st.slider(
            "Cooling constant, k (1/min)", min_value=0.001, max_value=0.5,
            value=0.05, step=0.001, format="%.3f",
            help="Rate at which the object exchanges heat with its "
            "surroundings - larger k means faster cooling (depends on "
            "surface area, heat transfer coefficient, mass, and "
            "specific heat of the object).",
        )
        default_target = min(T0, T_inf) + abs(T0 - T_inf) * 0.1 if T0 > T_inf else max(T0, T_inf) - abs(T_inf - T0) * 0.1
        T_target = st.number_input(
            "Target temperature (degC)", value=round(default_target, 1),
            help="The temperature you want to know the time-to-reach for. "
            "Must lie strictly between T0 and T_inf.",
        )

    try:
        body = CoolingBody(T0=T0, T_inf=T_inf, k=k_cool)

        with col2:
            st.markdown("**Results**")
            try:
                t_reach = body.time_to_reach(T_target)
                st.metric(f"Time to reach {T_target:g} degC", f"{t_reach:,.1f} min")
            except ValueError as e:
                st.warning(str(e))
                t_reach = None

        # ----------------------------------------------------------
        # Live cooling curve
        # ----------------------------------------------------------
        st.markdown("**Cooling curve**")

        t_max = t_reach * 1.5 if t_reach else 120.0
        t_max = max(t_max, 5.0)
        t_vals = np.linspace(0, t_max, 200)
        T_vals = [body.temperature_at(t) for t in t_vals]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(t_vals, T_vals, color="#2ca02c", linewidth=2, label="T(t)")
        ax.axhline(T_inf, color="gray", linestyle=":", label="Ambient (T_inf)")
        if t_reach:
            ax.axvline(t_reach, color="#d62728", linestyle="--",
                       label=f"t = {t_reach:.1f} min ({T_target:g} degC)")
        ax.set_xlabel("Time, minutes")
        ax.set_ylabel("Temperature, degC")
        ax.set_title("Temperature vs time (Newton's Law of Cooling)")
        ax.grid(alpha=0.3)
        ax.legend()
        st.pyplot(fig)

        with st.expander("✅ Verification against an analytical example"):
            st.markdown(
                """
                For T0 = 600 degC, T_inf = 25 degC, k = 0.02 per minute,
                target = 50 degC:

                t = -ln[(50 - 25) / (600 - 25)] / 0.02 approx **156.8 minutes**

                Try these values above - the app returns the same result,
                and T(156.8) evaluates back to 50.0 degC exactly.
                """
            )
    except ValueError as e:
        st.error(f"Invalid input: {e}")

"""
pages/3_Rock_Fluid_Dashboard.py
=================================
Module C - Rock & Fluid Data Dashboard (5 marks)

Load a user-uploaded CSV of rock or fluid data, show summary statistics,
allow interactive filtering on a numeric column, produce a histogram and
a crossplot, and let the user download the filtered data as CSV.
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Rock & Fluid Data Dashboard", page_icon="📊", layout="wide")
st.title("📊 Rock & Fluid Data Dashboard")
st.caption(
    "Upload a CSV of rock or fluid sample data (e.g. porosity, "
    "permeability, depth) to explore, filter, and visualise it."
)

SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "..", "sample_data", "rock_samples.csv")

# --------------------------------------------------------------------
# 1) File upload / sample data loading
# --------------------------------------------------------------------
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

use_sample = False
if uploaded_file is None:
    use_sample = st.checkbox(
        "No file? Load the bundled sample rock dataset instead "
        "(120 samples: porosity, permeability, depth, lithology).",
        value=True,
    )

df = None
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"Loaded **{uploaded_file.name}** - {len(df):,} rows, {len(df.columns)} columns.")
    except Exception as e:
        st.error(f"Could not read that file as a CSV: {e}")
elif use_sample:
    try:
        df = pd.read_csv(SAMPLE_PATH)
        st.info("Using the bundled sample dataset (`sample_data/rock_samples.csv`).")
    except FileNotFoundError:
        st.error("Sample dataset not found. Please upload a CSV file instead.")

if df is None:
    st.stop()

numeric_cols = df.select_dtypes(include="number").columns.tolist()

if not numeric_cols:
    st.warning("This file has no numeric columns to analyse. Please upload a "
               "CSV with at least one numeric column (e.g. porosity).")
    st.stop()

# --------------------------------------------------------------------
# 2) Preview + summary statistics
# --------------------------------------------------------------------
st.subheader("Data preview")
st.dataframe(df.head(10), width='stretch')

st.subheader("Summary statistics")
st.dataframe(df[numeric_cols].describe().T, width='stretch')

# --------------------------------------------------------------------
# 3) Interactive filtering
# --------------------------------------------------------------------
st.subheader("Filter the data")

def guess_default(cols, keyword, fallback_idx=0):
    for c in cols:
        if keyword in c.lower():
            return c
    return cols[fallback_idx]

filter_col = st.selectbox(
    "Filter by column", numeric_cols,
    index=numeric_cols.index(guess_default(numeric_cols, "poros")),
    help="Choose which numeric column to filter samples on.",
)

col_min = float(df[filter_col].min())
col_max = float(df[filter_col].max())

if col_min == col_max:
    st.info(f"All values of {filter_col} are equal ({col_min}); nothing to filter.")
    filtered_df = df.copy()
else:
    threshold = st.slider(
        f"Show only samples where {filter_col} >",
        min_value=col_min, max_value=col_max, value=col_min,
        help=f"Drag to keep only rows where {filter_col} exceeds this value.",
    )
    filtered_df = df[df[filter_col] > threshold]

st.write(f"**{len(filtered_df):,}** of **{len(df):,}** samples match the filter.")
st.dataframe(filtered_df, width='stretch', height=250)

# --------------------------------------------------------------------
# 4) Charts
# --------------------------------------------------------------------
st.subheader("Charts")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("**Histogram**")
    hist_col = st.selectbox(
        "Column to plot as a histogram", numeric_cols,
        index=numeric_cols.index(filter_col), key="hist_col",
    )
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    ax1.hist(filtered_df[hist_col].dropna(), bins=20, color="#1f77b4", edgecolor="white")
    ax1.set_xlabel(hist_col)
    ax1.set_ylabel("Count")
    ax1.set_title(f"Distribution of {hist_col}")
    ax1.grid(alpha=0.3, axis="y")
    st.pyplot(fig1)

with chart_col2:
    st.markdown("**Crossplot**")
    other_cols = [c for c in numeric_cols if c != hist_col] or numeric_cols
    x_col = st.selectbox("X axis", numeric_cols, index=numeric_cols.index(hist_col), key="x_col")
    y_col = st.selectbox(
        "Y axis", other_cols,
        index=0,
        key="y_col",
    )
    log_y = st.checkbox(
        "Log scale on Y axis",
        value=("perm" in y_col.lower()),
        help="Useful when plotting permeability, which often spans "
        "several orders of magnitude.",
    )

    fig2, ax2 = plt.subplots(figsize=(5, 4))
    ax2.scatter(filtered_df[x_col], filtered_df[y_col], color="#d62728",
                alpha=0.7, edgecolor="white")
    ax2.set_xlabel(x_col)
    ax2.set_ylabel(y_col)
    if log_y:
        ax2.set_yscale("log")
    ax2.set_title(f"{y_col} vs {x_col}")
    ax2.grid(alpha=0.3)
    st.pyplot(fig2)

# --------------------------------------------------------------------
# 5) Download filtered data
# --------------------------------------------------------------------
st.subheader("Export")
st.download_button(
    "⬇️ Download filtered data (CSV)",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_data.csv",
    mime="text/csv",
)
