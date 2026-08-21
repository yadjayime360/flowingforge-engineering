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
