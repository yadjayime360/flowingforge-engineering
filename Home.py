"""
Home.py
========
Landing page for the Fluid Flow & Heat Transfer Engineering Suite.

This is the entry point of the multi-page Streamlit app. Streamlit
automatically turns every file inside the pages/ folder into a separate
page, listed in the sidebar in numeric-prefix order.
"""

import streamlit as st

st.set_page_config(
    page_title="Fluid Flow & Heat Transfer Suite",
    page_icon="🛠️",
    layout="wide",
)

st.title("🛠️ Fluid Flow & Heat Transfer Engineering Suite")

st.markdown(
    """
    Welcome! This tool bundles three engineering calculators built for
    **PE 262 - Computer Programming (Capstone Project)**.

    Use the sidebar to navigate between modules:
    """
)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🔧 Pipe Flow Analyser")
    st.write(
        "Compute velocity, Reynolds number, friction factor and pressure "
        "drop for flow through a pipe, for a chosen fluid and pipe "
        "geometry. Includes an interactive pressure-drop-vs-flow-rate "
        "plot and CSV export."
    )

with col2:
    st.subheader("🌡️ Heat Transfer Calculator")
    st.write(
        "Calculate steady-state conduction through a flat wall "
        "(Fourier's Law) and the time for an object to cool toward an "
        "ambient temperature (Newton's Law of Cooling), with a live "
        "cooling-curve plot."
    )

with col3:
    st.subheader("📊 Rock & Fluid Data Dashboard")
    st.write(
        "Upload a CSV of rock or fluid sample data, view summary "
        "statistics, filter interactively, visualise the data with a "
        "histogram and crossplot, and download the filtered subset."
    )

st.divider()

st.markdown(
    """
    **About this app**

    Built with Python, Streamlit, pandas and matplotlib. All engineering
    calculations live in a separate, fully object-oriented module,
    `engineering.py` (classes: `Fluid`, `Pipe`, `FlatWall`,
    `CoolingBody`), which is imported by every calculator page below.

    Every calculation has been checked against a hand-calculated or
    analytical example - see the *Verification* note on each page.
    """
)

st.info(
    "👈 Pick a module from the sidebar to get started.",
    icon="👈",
)
