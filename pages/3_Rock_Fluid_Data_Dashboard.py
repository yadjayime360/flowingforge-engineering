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
