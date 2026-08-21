"""
pages/1_Pipe_Flow_Analyser.py
==============================
Module A - Pipe Flow Analyser (5 marks)

A complete pipe flow calculator: fluid selection with auto-populated
properties, pipe geometry and flow rate inputs, live results (velocity,
Reynolds number, friction factor, pressure drop), an interactive
pressure-drop-vs-flow-rate plot, and CSV export.
"""

import io

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from engineering import FLUID_LIBRARY, Fluid, Pipe

st.set_page_config(page_title="Pipe Flow Analyser", page_icon="🔧", layout="wide")
st.title("🔧 Pipe Flow Analyser")
st.caption(
    "Darcy-Weisbach pressure drop for flow through a circular pipe. "
    "Laminar flow uses the exact f = 64/Re; turbulent flow uses the "
    "Swamee-Jain approximation to the Colebrook equation."
)

# --------------------------------------------------------------------
# Sidebar inputs
# --------------------------------------------------------------------
st.sidebar.header("Fluid")
fluid_choice = st.sidebar.selectbox(
    "Fluid",
    list(FLUID_LIBRARY.keys()) + ["User-defined"],
    help="Pick a common fluid to auto-fill density and viscosity, or "
    "choose 'User-defined' to type your own values.",
)

if fluid_choice == "User-defined":
    fluid_name = st.sidebar.text_input("Fluid name", value="My fluid")
    density = st.sidebar.number_input(
        "Density (kg/m3)", min_value=0.01, value=1000.0, step=10.0,
        help="Mass per unit volume of the fluid.",
    )
    viscosity = st.sidebar.number_input(
        "Dynamic viscosity (Pa.s)", min_value=1e-6, value=1.0e-3,
        step=1e-4, format="%.5f",
        help="Resistance of the fluid to shear/flow.",
    )
else:
    fluid_name = fluid_choice
    density = FLUID_LIBRARY[fluid_choice]["density"]
    viscosity = FLUID_LIBRARY[fluid_choice]["viscosity"]
    st.sidebar.write(f"Density: **{density:g} kg/m3**")
    st.sidebar.write(f"Viscosity: **{viscosity:.2e} Pa.s**")

st.sidebar.header("Pipe geometry")
D_mm = st.sidebar.slider(
    "Internal diameter (mm)", min_value=5, max_value=500, value=50,
    help="Internal diameter of the pipe bore, in millimetres.",
)
L_m = st.sidebar.number_input(
    "Pipe length (m)", min_value=0.1, value=100.0, step=10.0,
    help="Total straight-line length of the pipe run, in metres.",
)
roughness_mm = st.sidebar.number_input(
    "Absolute roughness (mm)", min_value=0.0, value=0.046, step=0.01,
    format="%.4f",
    help="Internal surface roughness. 0.046 mm is typical for "
    "commercial steel pipe; use 0.0015 mm for drawn tubing/PVC.",
)

st.sidebar.header("Flow")
Q_value = st.sidebar.number_input(
    "Flow rate", min_value=0.0, value=10.0, step=1.0,
    help="Volumetric flow rate through the pipe.",
)
Q_unit = st.sidebar.radio(
    "Flow rate unit", ["L/s", "m3/s", "m3/h"], horizontal=True,
)

unit_to_m3s = {"L/s": 1e-3, "m3/s": 1.0, "m3/h": 1 / 3600}
Q = Q_value * unit_to_m3s[Q_unit]

# --------------------------------------------------------------------
# Build engineering objects and compute results
# --------------------------------------------------------------------
try:
    fluid = Fluid(fluid_name, density, viscosity)
    pipe = Pipe(diameter=D_mm / 1000, length=L_m, roughness=roughness_mm / 1000)
    results = pipe.report(fluid, Q)
    regime = fluid.flow_regime(results["velocity_m_s"], pipe.D)

    # --------------------------------------------------------------
    # Metric display
    # --------------------------------------------------------------
    st.subheader("Results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Velocity", f"{results['velocity_m_s']:.3f} m/s")
    c2.metric("Reynolds number", f"{results['reynolds']:,.0f}")
    c3.metric("Friction factor", f"{results['friction_factor']:.5f}")
    c4.metric("Pressure drop", f"{results['pressure_drop_bar']:.4f} bar")

    st.write(f"**Flow regime:** {regime}")
    st.write(
        f"**Pressure drop:** {results['pressure_drop_Pa']:.1f} Pa "
        f"= {results['pressure_drop_kPa']:.2f} kPa "
        f"= {results['pressure_drop_bar']:.4f} bar"
    )

    # --------------------------------------------------------------
    # Interactive plot: pressure drop vs flow rate
    # --------------------------------------------------------------
    st.subheader("Pressure drop vs flow rate")

    Q_max_plot = max(Q * 2, 0.001)
    Q_range = np.linspace(1e-6, Q_max_plot, 150)
    dP_range_bar = [pipe.pressure_drop(fluid, q) / 1e5 for q in Q_range]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(Q_range, dP_range_bar, color="#1f77b4", linewidth=2)
    ax.axvline(Q, color="#d62728", linestyle="--", linewidth=1.5,
               label=f"Current flow rate ({Q_value:g} {Q_unit})")
    ax.set_xlabel("Flow rate, m3/s")
    ax.set_ylabel("Pressure drop, bar")
    ax.set_title(f"Pressure drop vs flow rate - {fluid.name}, D={D_mm} mm, L={L_m} m")
    ax.grid(alpha=0.3)
    ax.legend()
    st.pyplot(fig)

    # --------------------------------------------------------------
    # CSV export
    # --------------------------------------------------------------
    st.subheader("Export")

    summary_df = pd.DataFrame([{
        "fluid": fluid.name,
        "density_kg_m3": fluid.density,
        "viscosity_Pa_s": fluid.viscosity,
        "diameter_mm": D_mm,
        "length_m": L_m,
        "roughness_mm": roughness_mm,
        "flow_rate_m3_s": Q,
        "velocity_m_s": results["velocity_m_s"],
        "reynolds": results["reynolds"],
        "friction_factor": results["friction_factor"],
        "pressure_drop_Pa": results["pressure_drop_Pa"],
        "pressure_drop_bar": results["pressure_drop_bar"],
    }])

    curve_df = pd.DataFrame({
        "flow_rate_m3_s": Q_range,
        "pressure_drop_bar": dP_range_bar,
    })

    col_a, col_b = st.columns(2)
    with col_a:
        st.download_button(
            "⬇️ Download result summary (CSV)",
            data=summary_df.to_csv(index=False).encode("utf-8"),
            file_name="pipe_flow_summary.csv",
            mime="text/csv",
        )
    with col_b:
        st.download_button(
            "⬇️ Download pressure-drop curve (CSV)",
            data=curve_df.to_csv(index=False).encode("utf-8"),
            file_name="pipe_flow_curve.csv",
            mime="text/csv",
        )

    with st.expander("Show raw results table"):
        st.dataframe(summary_df, width='stretch')

except ValueError as e:
    st.error(f"Invalid input: {e}")

with st.expander("✅ Verification against a hand-calculated example"):
    st.markdown(
        """
        For **water** (rho = 998 kg/m3, mu = 1.002e-3 Pa.s) through a
        **50 mm** diameter, **200 m** long pipe at **Q = 0.01 m3/s**:

        - Area: A = pi(0.025)^2 = 1.9635e-3 m2
        - Velocity: v = Q/A = 0.01 / 1.9635e-3 = **5.093 m/s**
        - Reynolds number: Re = rho*v*D/mu = 998*5.093*0.05/1.002e-3
          approx **253,600** (turbulent)
        - Darcy-Weisbach: dP = f*(L/D)*rho*v^2/2 approx **10.66 bar**

        These match the app's output for the same inputs (select
        *Water*, D = 50 mm, L = 100 m -> change to 200 m, Q = 10 L/s).
        """
    )
