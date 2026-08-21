"""
engineering.py
================
Core object-oriented engineering toolkit for the PE 262 Capstone project.

This module defines the physical objects used across the Streamlit app:

    Fluid       - a Newtonian fluid with density and viscosity
    Pipe        - a circular pipe section (uses a Fluid to compute flow behaviour)
    FlatWall    - a single-layer plane wall for steady-state conduction (Fourier's Law)
    CoolingBody - an object cooling in an ambient environment (Newton's Law of Cooling)

Every public method is documented with a docstring and raises a ValueError
(rather than crashing with a raw exception) when given physically invalid
input, so the Streamlit front-end can catch these errors and show a friendly
message instead of a traceback.
"""

import math

# --------------------------------------------------------------------------
# A small built-in fluid property library, used to auto-populate the
# Pipe Flow Analyser when the user selects a common fluid instead of
# typing in their own density/viscosity values.
# --------------------------------------------------------------------------
FLUID_LIBRARY = {
    "Water (20 degC)":    {"density": 998.0,  "viscosity": 1.002e-3},
    "Air (20 degC, 1 atm)": {"density": 1.204, "viscosity": 1.825e-5},
    "Crude oil (medium)": {"density": 870.0,  "viscosity": 8.0e-3},
    "Seawater (20 degC)": {"density": 1025.0, "viscosity": 1.08e-3},
    "Diesel":             {"density": 832.0,  "viscosity": 3.5e-3},
}


class Fluid:
    """A Newtonian fluid with the key thermophysical properties needed
    for pipe-flow calculations."""

    def __init__(self, name, density, viscosity):
        """
        Create a Fluid.

        Parameters
        ----------
        name : str
            Fluid identifier, e.g. "water".
        density : float
            Fluid density, kg/m3. Must be > 0.
        viscosity : float
            Dynamic viscosity, Pa.s. Must be > 0.
        """
        if density is None or density <= 0:
            raise ValueError("Density must be a positive number (kg/m3).")
        if viscosity is None or viscosity <= 0:
            raise ValueError("Viscosity must be a positive number (Pa.s).")

        self.name = str(name)
        self.density = float(density)
        self.viscosity = float(viscosity)

    def kinematic_viscosity(self):
        """Return kinematic viscosity nu = mu / rho (m2/s)."""
        return self.viscosity / self.density

    def reynolds(self, velocity, diameter):
        """
        Return the Reynolds number Re = rho * v * D / mu (dimensionless).

        Parameters
        ----------
        velocity : float
            Mean flow velocity, m/s.
        diameter : float
            Characteristic diameter, m.
        """
        if diameter <= 0:
            raise ValueError("Diameter must be positive.")
        return self.density * abs(velocity) * diameter / self.viscosity

    def flow_regime(self, velocity, diameter):
        """Classify the flow as Laminar / Transitional / Turbulent and
        return a human-readable string including the Reynolds number."""
        Re = self.reynolds(velocity, diameter)
        if Re < 2300:
            regime = "Laminar"
        elif Re < 4000:
            regime = "Transitional"
        else:
            regime = "Turbulent"
        return f"{regime} (Re={Re:,.0f})"

    def __repr__(self):
        return f"Fluid('{self.name}', rho={self.density}, mu={self.viscosity})"


class Pipe:
    """A circular pipe section used to compute flow velocity, Reynolds
    number, friction factor, and pressure drop for a fluid flowing
    through it (Darcy-Weisbach equation)."""

    def __init__(self, diameter, length, roughness=0.000046):
        """
        Create a Pipe.

        Parameters
        ----------
        diameter : float
            Internal pipe diameter, m. Must be > 0.
        length : float
            Pipe length, m. Must be > 0.
        roughness : float, optional
            Absolute internal roughness, m. Defaults to 0.000046 m
            (typical commercial steel pipe).
        """
        if diameter is None or diameter <= 0:
            raise ValueError("Pipe diameter must be a positive number (m).")
        if length is None or length <= 0:
            raise ValueError("Pipe length must be a positive number (m).")
        if roughness is None or roughness < 0:
            raise ValueError("Roughness cannot be negative.")

        self.D = float(diameter)
        self.L = float(length)
        self.eps = float(roughness)

    def area(self):
        """Return the internal cross-sectional area, m2."""
        return math.pi * (self.D / 2) ** 2

    def velocity(self, Q):
        """
        Return mean flow velocity, m/s, for volumetric flow rate Q (m3/s).
        """
        if Q is None or Q < 0:
            raise ValueError("Flow rate must be zero or a positive number (m3/s).")
        return Q / self.area()

    def friction_factor(self, fluid, Q):
        """
        Return the Darcy friction factor f (dimensionless).

        Laminar flow (Re < 2300): f = 64 / Re (exact).
        Turbulent flow (Re >= 2300): f is estimated with the Swamee-Jain
        explicit approximation to the Colebrook equation, which accounts
        for both Reynolds number and relative pipe roughness:

            f = 0.25 / [log10( eps/(3.7*D) + 5.74/Re^0.9 )]^2
        """
        v = self.velocity(Q)
        if v == 0:
            return 0.0
        Re = fluid.reynolds(v, self.D)
        if Re < 2300:
            return 64.0 / Re
        rel_rough = self.eps / self.D
        f = 0.25 / (math.log10(rel_rough / 3.7 + 5.74 / Re ** 0.9)) ** 2
        return f

    def pressure_drop(self, fluid, Q):
        """
        Return the frictional pressure drop, Pa, using the Darcy-Weisbach
        equation:  dP = f * (L/D) * rho * v^2 / 2
        """
        v = self.velocity(Q)
        f = self.friction_factor(fluid, Q)
        return f * (self.L / self.D) * fluid.density * v ** 2 / 2

    def report(self, fluid, Q):
        """Return a dict summarising velocity, Re, friction factor and
        pressure drop for the given fluid and flow rate."""
        v = self.velocity(Q)
        Re = fluid.reynolds(v, self.D)
        f = self.friction_factor(fluid, Q)
        dP = self.pressure_drop(fluid, Q)
        return {
            "velocity_m_s": v,
            "reynolds": Re,
            "friction_factor": f,
            "pressure_drop_Pa": dP,
            "pressure_drop_bar": dP / 1e5,
            "pressure_drop_kPa": dP / 1e3,
        }

    def __repr__(self):
        return f"Pipe(D={self.D}, L={self.L}, eps={self.eps})"


class FlatWall:
    """A single-layer plane wall used for steady-state 1-D conduction
    (Fourier's Law)."""

    def __init__(self, thickness, conductivity, area):
        """
        Create a FlatWall.

        Parameters
        ----------
        thickness : float
            Wall thickness L, m. Must be > 0.
        conductivity : float
            Thermal conductivity k, W/(m.K). Must be > 0.
        area : float
            Cross-sectional area normal to heat flow, m2. Must be > 0.
        """
        if thickness is None or thickness <= 0:
            raise ValueError("Wall thickness must be a positive number (m).")
        if conductivity is None or conductivity <= 0:
            raise ValueError("Thermal conductivity must be a positive number (W/m.K).")
        if area is None or area <= 0:
            raise ValueError("Area must be a positive number (m2).")

        self.L = float(thickness)
        self.k = float(conductivity)
        self.A = float(area)

    def heat_flux(self, T_hot, T_cold):
        """Return heat flux q'' = k * (T_hot - T_cold) / L, in W/m2."""
        return self.k * (T_hot - T_cold) / self.L

    def heat_rate(self, T_hot, T_cold):
        """Return total heat transfer rate Q = q'' * A, in W."""
        return self.heat_flux(T_hot, T_cold) * self.A

    def __repr__(self):
        return f"FlatWall(L={self.L}, k={self.k}, A={self.A})"


class CoolingBody:
    """An object cooling (or heating) toward an ambient temperature,
    governed by Newton's Law of Cooling:

        T(t) = T_inf + (T0 - T_inf) * exp(-k * t)
    """

    def __init__(self, T0, T_inf, k):
        """
        Create a CoolingBody.

        Parameters
        ----------
        T0 : float
            Initial temperature of the body, degC.
        T_inf : float
            Ambient (surrounding) temperature, degC.
        k : float
            Cooling constant, 1/min (or 1/s, as long as time units are
            used consistently elsewhere). Must be > 0.
        """
        if k is None or k <= 0:
            raise ValueError("Cooling constant k must be a positive number.")
        if T0 == T_inf:
            raise ValueError("Initial temperature and ambient temperature cannot be equal.")

        self.T0 = float(T0)
        self.T_inf = float(T_inf)
        self.k = float(k)

    def temperature_at(self, t):
        """Return the body temperature, degC, at time t (>= 0)."""
        if t < 0:
            raise ValueError("Time cannot be negative.")
        return self.T_inf + (self.T0 - self.T_inf) * math.exp(-self.k * t)

    def time_to_reach(self, T_target):
        """
        Return the time required to reach T_target, using the analytical
        (rearranged) solution:

            t = -ln[(T_target - T_inf) / (T0 - T_inf)] / k

        Raises ValueError if T_target is not physically reachable (i.e.
        it lies on the wrong side of T0, or exactly at T_inf).
        """
        numerator = T_target - self.T_inf
        denominator = self.T0 - self.T_inf

        if denominator > 0 and not (self.T_inf < T_target < self.T0):
            raise ValueError(
                "Target temperature must lie strictly between the ambient "
                "temperature and the initial temperature when cooling."
            )
        if denominator < 0 and not (self.T0 < T_target < self.T_inf):
            raise ValueError(
                "Target temperature must lie strictly between the initial "
                "temperature and the ambient temperature when heating."
            )

        ratio = numerator / denominator
        return -math.log(ratio) / self.k

    def __repr__(self):
        return f"CoolingBody(T0={self.T0}, T_inf={self.T_inf}, k={self.k})"
