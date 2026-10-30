"""Recalculate both baseline inlet cases and save the comparison CSV."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from subsea_insulation.model import OperatingConditions, compare_materials  # noqa: E402


def main() -> None:
    materials = pd.read_csv(ROOT / "data" / "materials.csv")
    material_pairs = zip(materials["material"], materials["k_W_mK"].astype(float))
    material_pairs = list(material_pairs)

    cases = []
    for inlet_temperature in (110.0, 50.0):
        conditions = OperatingConditions(oil_inlet_temperature_C=inlet_temperature)
        case = compare_materials(material_pairs, conditions)
        case.insert(0, "inlet_temperature_C", inlet_temperature)
        cases.append(case)

    output = pd.concat(cases, ignore_index=True)
    output_path = ROOT / "outputs" / "recalculated_baseline_results.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False)
    print(f"Saved {len(output)} rows to {output_path.relative_to(ROOT)}")
    print(output.to_string(index=False, float_format=lambda value: f"{value:.3f}"))


if __name__ == "__main__":
    main()
