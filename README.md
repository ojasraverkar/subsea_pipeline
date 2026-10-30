# Subsea Oil Pipeline Insulation Performance

**BMEE402P · Heat and Mass Transfer Lab · Mini Project 6**  
An educational Python implementation and Streamlit dashboard reconstructed from the supplied project presentation.

## What is included

- `app.py` — interactive Streamlit dashboard.
- `src/subsea_insulation/model.py` — reusable thermal-resistance and axial oil-cooling calculations.
- `data/materials.csv` — seven insulation materials and conductivities from the presentation.
- `data/interface_temperatures.csv` — the 14 interface-temperature records shown in the presentation.
- `data/presentation_reference_results.csv` — reported result tables transcribed from the presentation for traceability.
- `tests/test_model.py` — automated checks for the equations, geometry and baseline outputs.

## Run the dashboard

### Windows

1. Extract the ZIP to a normal folder.
2. Install Python 3.10 or newer.
3. Double-click `run_windows.bat`, or open a terminal in the extracted folder and run:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

### macOS / Linux

```bash
chmod +x run_unix.sh
./run_unix.sh
```

Streamlit will print a local URL, normally `http://localhost:8501`. Open it in a browser.

## Dashboard sections

1. **Performance overview** — comparison of all seven materials, inlet heat loss, outlet temperature, and wax-threshold distance.
2. **Thermal model** — equations, resistance network, layer radii, and a selected material's resistance breakdown.
3. **Interface temperatures** — the data-acquisition table transcribed from the presentation, plotted by interface.
4. **Critical radius** — critical-radius calculation and comparison with the pipe radii.
5. **ANSYS references** — original result screenshots supplied in the presentation, shown as evidence rather than live Python simulations.
6. **Interpretation & limitations** — project decision points, assumptions and model limitations.

The sidebar allows the inlet case, pipe length, seawater temperature, wax threshold, flow rate, convection coefficients and layer thicknesses to be changed. The material conductivities remain the values stated in the presentation.

## Model and equations

For a cylindrical layer, thermal resistance per unit length is:

\[
R'_j = \frac{\ln(r_{o,j}/r_{i,j})}{2\pi k_j}
\]

For a convection boundary:

\[
R'_{conv} = \frac{1}{2\pi r h}
\]

The total radial resistance is the sum of the oil-side convection resistance, steel, insulation, polymer jacket, concrete coating, biofouling film, and seawater-side convection resistance:

\[
R'_{total}=\frac{1}{2\pi r_i h_i}
+\sum_j\frac{\ln(r_{o,j}/r_{i,j})}{2\pi k_j}
+\frac{1}{2\pi r_o h_o}
\]

The bulk-oil temperature along the pipeline is:

\[
T(x)=T_{sea}+(T_{in}-T_{sea})\exp\left[-\frac{x}{\dot m C_p R'_{total}}\right]
\]

Inlet heat loss per unit length is calculated as:

\[
q'(0)=\frac{T_{in}-T_{sea}}{R'_{total}}
\]

The distance at which bulk oil reaches the project wax threshold is:

\[
x_{wax}=\dot m C_p R'_{total}\ln\left(\frac{T_{in}-T_{sea}}{T_{wax}-T_{sea}}\right)
\]

The critical radius used in the presentation is:

\[
r_{cr}=\frac{k}{h_o}
\]

## Baseline inputs transcribed from the presentation

| Input | Baseline value |
|---|---:|
| Pipe inner diameter | 400 mm |
| Steel wall thickness | 20 mm |
| Insulation thickness | 50 mm |
| Polymer jacket thickness | 5 mm |
| Concrete coating thickness | 50 mm |
| Biofouling thickness | 1 mm |
| Oil mass flow rate | 106.8 kg/s |
| Oil specific heat | 2,200 J/kg·K |
| Oil-side convection coefficient | 100 W/m²·K |
| Seawater-side convection coefficient | 500 W/m²·K |
| Seawater temperature | 4 °C |
| Wax threshold | 45 °C |
| Pipeline length | 10 km |
| Oil inlet cases | 110 °C and 50 °C |

## Validation against the presentation

The reconstructed equations and baseline geometry reproduce the main reported trends and almost all rounded values in the slides. Small discrepancies are retained transparently rather than forcing the code to match the slide values. For example, using the exact stated values, Aerogel inlet heat loss at a 110 °C inlet is approximately **79.15 W/m**, compared with **79.5 W/m** in the slide. For Hylam at a 50 °C inlet, the model gives approximately **277.38 W/m**, compared with **277.8 W/m** in the slide. The application displays values recalculated from the stated equations and inputs; the presentation's original numbers are retained in `data/presentation_reference_results.csv` for comparison.

The other displayed results reproduce the slide values closely, generally within the rounding precision shown. A complete row-by-row comparison is included in `outputs/model_validation_summary.md` and `outputs/model_vs_presentation.csv`.

## Important scope limitations

- The analytical calculation is steady-state and one-dimensional in the radial direction, with an axial bulk-oil energy balance.
- Thermal conductivity is constant for each layer. The code does **not** model how conductivity changes with temperature, pressure, water ingress or ageing.
- Waxing is represented only by the bulk-oil temperature crossing a threshold. Wax precipitation, deposition kinetics, deposit thickness and pressure-drop growth are not calculated.
- Hydrostatic-pressure collapse, foam crushing, thermal expansion stress and structural integrity are not simulated.
- The interface-temperature table is transcribed from the presentation and is displayed separately; it is not used to calibrate the analytical model.
- The title's phrase "high thermal stress" is not a structural stress result. A thermoelastic stress/strain calculation would require a separate mechanical model and additional inputs.
- Material suitability and field deployment require independent material, moisture, pressure and qualification testing. This is a teaching model, not a certified pipeline design tool.

## Recalculate the baseline outputs

From the project root, run:

```bash
python scripts/recalculate_baseline.py
```

This writes `outputs/recalculated_baseline_results.csv` for the 110 °C and 50 °C inlet cases.

## Run tests

```bash
pip install -e .[test]
pytest -q
```

## Project authorship

Prepared from the supplied BMEE402P Mini Project 6 presentation for educational demonstration. Keep the original presentation as the authoritative record of the team's source data and project framing.

A row-by-row baseline comparison is also included in `outputs/model_vs_presentation.csv`, with a readable summary in `outputs/model_validation_summary.md`.

## ANSYS reference images

The `assets/ansys_reference/` folder contains the four ANSYS 2023 R1 screenshots embedded in slides 9–10 of the supplied presentation. The dashboard has an **ANSYS references** tab that displays them with source-aware captions. These are reference screenshots only; the Python project does not contain the ANSYS solver model or reproduce its finite-element run.

## Suggested classroom walkthrough

For a guided demonstration, open the dashboard and proceed in this order: **Performance overview → Thermal model → Interface temperatures → Critical radius → ANSYS references → Interpretation & limitations**. The accompanying `docs/TEACHER_GUIDE.md` contains the main talking points, baseline results and likely questions.
