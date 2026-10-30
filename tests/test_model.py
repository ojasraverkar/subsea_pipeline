import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from subsea_insulation.model import (  # noqa: E402
    OperatingConditions,
    PipelineGeometry,
    calculate_material_result,
    calculate_temperature_profile,
    total_thermal_resistance,
)


def test_aerogel_resistance_matches_presentation():
    result = total_thermal_resistance(0.025)
    assert result == pytest.approx(1.33922, rel=1e-5)


def test_rigid_pu_outlet_matches_presentation_case():
    result = calculate_material_result("Rigid PU Foam", 0.03)
    assert result["T_outlet_C"] == pytest.approx(106.05, abs=0.02)
    assert result["wax_distance_km"] == pytest.approx(250.5, abs=0.2)


def test_fifty_degree_case_aerogel_passes_and_hylam_fails():
    conditions = OperatingConditions(oil_inlet_temperature_C=50.0)
    aerogel = calculate_material_result("Aerogel", 0.025, conditions)
    hylam = calculate_material_result("Hylam", 0.25, conditions)
    assert aerogel["passes_pipeline"] is True
    assert hylam["passes_pipeline"] is False
    assert aerogel["T_outlet_C"] == pytest.approx(48.56, abs=0.02)
    assert hylam["T_outlet_C"] == pytest.approx(39.59, abs=0.02)


def test_temperature_profile_is_monotonically_decreasing():
    profile = calculate_temperature_profile("Aerogel", 0.025)
    assert profile["oil_temperature_C"].iloc[0] == pytest.approx(110.0)
    assert profile["oil_temperature_C"].iloc[-1] < profile["oil_temperature_C"].iloc[0]
    assert profile["oil_temperature_C"].is_monotonic_decreasing


def test_geometry_radius_is_consistent_with_nominal_dimensions():
    r = PipelineGeometry().radii_m
    assert r["oil_inner_wall"] == pytest.approx(0.2)
    assert r["insulation_outer"] == pytest.approx(0.27)
    assert r["external_surface"] == pytest.approx(0.326)


def test_invalid_inlet_temperature_is_rejected():
    with pytest.raises(ValueError):
        OperatingConditions(oil_inlet_temperature_C=40.0)


def test_pass_flag_uses_the_selected_pipeline_length():
    conditions = OperatingConditions(pipeline_length_m=50_000.0, oil_inlet_temperature_C=110.0)
    hylam = calculate_material_result("Hylam", 0.25, conditions)
    assert hylam["wax_distance_km"] < 50.0
    assert hylam["passes_pipeline"] is False
