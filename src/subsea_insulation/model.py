"""One-dimensional steady-state thermal model for a multilayer subsea pipe.

The implementation follows the equations and nominal inputs shown in the
BMEE402P Mini Project 6 presentation. Conductivities are treated as constants.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log, pi
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PipelineGeometry:
    """Pipe and coating dimensions, all in metres."""

    inner_diameter_m: float = 0.400
    steel_thickness_m: float = 0.020
    insulation_thickness_m: float = 0.050
    jacket_thickness_m: float = 0.005
    concrete_thickness_m: float = 0.050
    biofouling_thickness_m: float = 0.001

    # Fixed layer conductivities from the presentation (W/m.K).
    steel_k_W_mK: float = 45.0
    jacket_k_W_mK: float = 0.30
    concrete_k_W_mK: float = 1.70
    biofouling_k_W_mK: float = 0.60

    def __post_init__(self) -> None:
        dimensions = (
            self.inner_diameter_m,
            self.steel_thickness_m,
            self.insulation_thickness_m,
            self.jacket_thickness_m,
            self.concrete_thickness_m,
            self.biofouling_thickness_m,
        )
        if any(value <= 0 for value in dimensions):
            raise ValueError("All pipe diameters and layer thicknesses must be positive.")
        conductivities = (
            self.steel_k_W_mK,
            self.jacket_k_W_mK,
            self.concrete_k_W_mK,
            self.biofouling_k_W_mK,
        )
        if any(value <= 0 for value in conductivities):
            raise ValueError("All layer thermal conductivities must be positive.")

    @property
    def radii_m(self) -> dict[str, float]:
        """Return the interface radii from the oil side to seawater side."""
        r_inner = self.inner_diameter_m / 2.0
        r_steel_outer = r_inner + self.steel_thickness_m
        r_insulation_outer = r_steel_outer + self.insulation_thickness_m
        r_jacket_outer = r_insulation_outer + self.jacket_thickness_m
        r_concrete_outer = r_jacket_outer + self.concrete_thickness_m
        r_fouling_outer = r_concrete_outer + self.biofouling_thickness_m
        return {
            "oil_inner_wall": r_inner,
            "steel_outer": r_steel_outer,
            "insulation_outer": r_insulation_outer,
            "jacket_outer": r_jacket_outer,
            "concrete_outer": r_concrete_outer,
            "external_surface": r_fouling_outer,
        }


@dataclass(frozen=True)
class OperatingConditions:
    """Operating conditions in SI units, with temperatures in degrees Celsius."""

    pipeline_length_m: float = 10_000.0
    oil_mass_flow_kg_s: float = 106.8
    oil_specific_heat_J_kgK: float = 2_200.0
    h_oil_W_m2K: float = 100.0
    h_seawater_W_m2K: float = 500.0
    seawater_temperature_C: float = 4.0
    wax_threshold_C: float = 45.0
    oil_inlet_temperature_C: float = 110.0

    def __post_init__(self) -> None:
        positive_values = (
            self.pipeline_length_m,
            self.oil_mass_flow_kg_s,
            self.oil_specific_heat_J_kgK,
            self.h_oil_W_m2K,
            self.h_seawater_W_m2K,
        )
        if any(value <= 0 for value in positive_values):
            raise ValueError("Length, flow rate, specific heat and film coefficients must be positive.")
        if self.oil_inlet_temperature_C <= self.seawater_temperature_C:
            raise ValueError("Oil inlet temperature must exceed seawater temperature.")
        if self.wax_threshold_C <= self.seawater_temperature_C:
            raise ValueError("Wax threshold must exceed seawater temperature for this model.")
        if self.oil_inlet_temperature_C <= self.wax_threshold_C:
            raise ValueError("Oil inlet temperature must exceed the wax threshold.")


def calculate_resistance_breakdown(
    insulation_k_W_mK: float,
    geometry: PipelineGeometry | None = None,
    conditions: OperatingConditions | None = None,
) -> pd.DataFrame:
    """Calculate the per-unit-length thermal resistance of each element.

    Units are K.m/W. For a cylindrical layer, R' = ln(r_o/r_i)/(2*pi*k).
    For the convection films, R' = 1/(2*pi*r*h).
    """
    geometry = geometry or PipelineGeometry()
    conditions = conditions or OperatingConditions()
    if insulation_k_W_mK <= 0:
        raise ValueError("Insulation conductivity must be positive.")

    r = geometry.radii_m
    rows = [
        {
            "component": "Oil-side convection",
            "inner_radius_mm": np.nan,
            "outer_radius_mm": r["oil_inner_wall"] * 1000,
            "conductivity_W_mK": np.nan,
            "resistance_K_m_W": 1.0 / (2.0 * pi * r["oil_inner_wall"] * conditions.h_oil_W_m2K),
        },
        {
            "component": "Steel wall",
            "inner_radius_mm": r["oil_inner_wall"] * 1000,
            "outer_radius_mm": r["steel_outer"] * 1000,
            "conductivity_W_mK": geometry.steel_k_W_mK,
            "resistance_K_m_W": log(r["steel_outer"] / r["oil_inner_wall"]) / (2.0 * pi * geometry.steel_k_W_mK),
        },
        {
            "component": "Thermal insulation",
            "inner_radius_mm": r["steel_outer"] * 1000,
            "outer_radius_mm": r["insulation_outer"] * 1000,
            "conductivity_W_mK": insulation_k_W_mK,
            "resistance_K_m_W": log(r["insulation_outer"] / r["steel_outer"]) / (2.0 * pi * insulation_k_W_mK),
        },
        {
            "component": "Polymer jacket",
            "inner_radius_mm": r["insulation_outer"] * 1000,
            "outer_radius_mm": r["jacket_outer"] * 1000,
            "conductivity_W_mK": geometry.jacket_k_W_mK,
            "resistance_K_m_W": log(r["jacket_outer"] / r["insulation_outer"]) / (2.0 * pi * geometry.jacket_k_W_mK),
        },
        {
            "component": "Concrete coating",
            "inner_radius_mm": r["jacket_outer"] * 1000,
            "outer_radius_mm": r["concrete_outer"] * 1000,
            "conductivity_W_mK": geometry.concrete_k_W_mK,
            "resistance_K_m_W": log(r["concrete_outer"] / r["jacket_outer"]) / (2.0 * pi * geometry.concrete_k_W_mK),
        },
        {
            "component": "Biofouling film",
            "inner_radius_mm": r["concrete_outer"] * 1000,
            "outer_radius_mm": r["external_surface"] * 1000,
            "conductivity_W_mK": geometry.biofouling_k_W_mK,
            "resistance_K_m_W": log(r["external_surface"] / r["concrete_outer"]) / (2.0 * pi * geometry.biofouling_k_W_mK),
        },
        {
            "component": "Seawater-side convection",
            "inner_radius_mm": r["external_surface"] * 1000,
            "outer_radius_mm": np.nan,
            "conductivity_W_mK": np.nan,
            "resistance_K_m_W": 1.0 / (2.0 * pi * r["external_surface"] * conditions.h_seawater_W_m2K),
        },
    ]
    result = pd.DataFrame(rows)
    result.attrs["total_resistance_K_m_W"] = float(result["resistance_K_m_W"].sum())
    return result


def total_thermal_resistance(
    insulation_k_W_mK: float,
    geometry: PipelineGeometry | None = None,
    conditions: OperatingConditions | None = None,
) -> float:
    """Return total radial thermal resistance per unit pipe length (K.m/W)."""
    breakdown = calculate_resistance_breakdown(insulation_k_W_mK, geometry, conditions)
    return float(breakdown["resistance_K_m_W"].sum())


def oil_temperature_C(
    distance_m: float | np.ndarray,
    total_resistance_K_m_W: float,
    conditions: OperatingConditions,
) -> float | np.ndarray:
    """Oil bulk temperature at axial distance x using the presentation equation."""
    if total_resistance_K_m_W <= 0:
        raise ValueError("Total thermal resistance must be positive.")
    x = np.asarray(distance_m, dtype=float)
    exponent = -x / (
        conditions.oil_mass_flow_kg_s
        * conditions.oil_specific_heat_J_kgK
        * total_resistance_K_m_W
    )
    values = conditions.seawater_temperature_C + (
        conditions.oil_inlet_temperature_C - conditions.seawater_temperature_C
    ) * np.exp(exponent)
    if np.ndim(distance_m) == 0:
        return float(values)
    return values


def calculate_material_result(
    material: str,
    insulation_k_W_mK: float,
    conditions: OperatingConditions | None = None,
    geometry: PipelineGeometry | None = None,
) -> dict[str, float | str | bool]:
    """Calculate heat loss, outlet temperature and wax-threshold distance."""
    conditions = conditions or OperatingConditions()
    geometry = geometry or PipelineGeometry()
    breakdown = calculate_resistance_breakdown(insulation_k_W_mK, geometry, conditions)
    resistance = float(breakdown["resistance_K_m_W"].sum())
    delta_inlet = conditions.oil_inlet_temperature_C - conditions.seawater_temperature_C
    heat_loss_at_inlet = delta_inlet / resistance
    outlet_temperature = oil_temperature_C(conditions.pipeline_length_m, resistance, conditions)
    wax_distance_m = (
        conditions.oil_mass_flow_kg_s
        * conditions.oil_specific_heat_J_kgK
        * resistance
        * log(delta_inlet / (conditions.wax_threshold_C - conditions.seawater_temperature_C))
    )
    critical_radius_m = insulation_k_W_mK / conditions.h_seawater_W_m2K
    return {
        "material": material,
        "k_W_mK": float(insulation_k_W_mK),
        "R_K_m_per_W": resistance,
        "heat_loss_W_per_m": heat_loss_at_inlet,
        "T_outlet_C": outlet_temperature,
        "wax_distance_km": wax_distance_m / 1000.0,
        "passes_pipeline": bool(outlet_temperature >= conditions.wax_threshold_C),
        "critical_radius_mm": critical_radius_m * 1000.0,
    }


def compare_materials(
    materials: Iterable[tuple[str, float]],
    conditions: OperatingConditions | None = None,
    geometry: PipelineGeometry | None = None,
) -> pd.DataFrame:
    """Return a material comparison table sorted from lowest heat loss upward."""
    rows = [
        calculate_material_result(name, conductivity, conditions, geometry)
        for name, conductivity in materials
    ]
    return pd.DataFrame(rows).sort_values("heat_loss_W_per_m", ascending=True).reset_index(drop=True)


def calculate_temperature_profile(
    material: str,
    insulation_k_W_mK: float,
    conditions: OperatingConditions | None = None,
    geometry: PipelineGeometry | None = None,
    points: int = 201,
) -> pd.DataFrame:
    """Generate an axial oil-temperature profile for a selected material."""
    conditions = conditions or OperatingConditions()
    geometry = geometry or PipelineGeometry()
    if points < 2:
        raise ValueError("At least two profile points are required.")
    resistance = total_thermal_resistance(insulation_k_W_mK, geometry, conditions)
    distance = np.linspace(0.0, conditions.pipeline_length_m, points)
    temperature = oil_temperature_C(distance, resistance, conditions)
    return pd.DataFrame(
        {
            "distance_km": distance / 1000.0,
            "oil_temperature_C": temperature,
            "material": material,
        }
    )
