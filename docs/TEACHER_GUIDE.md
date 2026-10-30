# Teacher Guide — Subsea Oil Pipeline Insulation Performance

**Course:** BMEE402P · Heat and Mass Transfer Lab · Mini Project 6  
**Institution:** School of Mechanical Engineering, VIT Vellore

## 1. Project objective

The project compares seven insulation materials for a multilayer subsea oil pipeline. The central engineering question is whether the insulation system can limit radial heat loss sufficiently to keep the bulk oil at or above the project's 45 °C wax-risk threshold over a 10 km line.

The project evaluates:

- radial thermal resistance per unit length through cylindrical layers;
- inlet heat loss per unit length;
- bulk-oil temperature reduction along the pipeline;
- distance at which the bulk-oil temperature reaches 45 °C;
- the conventional cylindrical critical-radius check; and
- the original interface-temperature and ANSYS result screenshots supplied in the presentation.

## 2. Baseline model inputs

| Quantity | Baseline value |
|---|---:|
| Pipe inner diameter | 400 mm |
| Steel wall thickness | 20 mm |
| Insulation thickness | 50 mm |
| Polymer jacket thickness | 5 mm |
| Concrete coating thickness | 50 mm |
| Biofouling thickness | 1 mm |
| Steel / jacket / concrete / biofouling conductivity | 45 / 0.30 / 1.70 / 0.60 W/m·K |
| Oil mass flow rate | 106.8 kg/s |
| Oil specific heat | 2,200 J/kg·K |
| Oil-side / seawater-side convection coefficient | 100 / 500 W/m²·K |
| Seawater temperature | 4 °C |
| Wax-risk threshold | 45 °C |
| Pipeline length | 10 km |
| Oil inlet cases | 110 °C and 50 °C |

Insulation conductivities transcribed from the presentation are: Aerogel 0.025, Rigid PU Foam 0.030, Advanced Syntactic Foam 0.120, Syntactic PP 0.150, Wood 0.150, Solid PP 0.200 and Hylam 0.250 W/m·K.

## 3. Method and equations

For a cylindrical conduction layer, resistance per unit length is:

\[
R'_j=\frac{\ln(r_{o,j}/r_{i,j})}{2\pi k_j}
\]

For inner or outer convection:

\[
R'_{conv}=\frac{1}{2\pi r h}
\]

All radial resistances are added in series:

\[
R'_{total}=\frac{1}{2\pi r_i h_i}+\sum_j\frac{\ln(r_{o,j}/r_{i,j})}{2\pi k_j}+\frac{1}{2\pi r_o h_o}
\]

The analytical axial energy balance assumes constant mass flow, constant specific heat, constant layer conductivities and a seawater temperature that does not vary along the line:

\[
T(x)=T_{sea}+(T_{in}-T_{sea})\exp\left[-\frac{x}{\dot m C_p R'_{total}}\right]
\]

The inlet heat loss per unit length is:

\[
q'(0)=\frac{T_{in}-T_{sea}}{R'_{total}}
\]

The bulk-oil distance to the 45 °C threshold is:

\[
x_{wax}=\dot m C_p R'_{total}\ln\left(\frac{T_{in}-T_{sea}}{T_{wax}-T_{sea}}\right)
\]

For the conventional critical-radius comparison used in the presentation:

\[
r_{cr}=\frac{k}{h_o}
\]

## 4. Recalculated baseline results

The Python project recalculates the outputs from the stated geometry and equations. Values below are rounded to two decimals.

### 110 °C inlet

| Insulation | Inlet heat loss (W/m) | Outlet oil temperature (°C) | Threshold distance (km) |
|---|---:|---:|---:|
| Aerogel | 79.15 | 106.68 | 298.89 |
| Rigid PU Foam | 94.48 | 106.05 | 250.39 |
| Advanced Syntactic Foam | 345.19 | 96.28 | 68.53 |
| Syntactic PP | 419.38 | 93.57 | 56.41 |
| Wood | 419.38 | 93.57 | 56.41 |
| Solid PP | 534.19 | 89.54 | 44.29 |
| Hylam | 639.18 | 86.01 | 37.01 |

All seven materials remain above 45 °C after 10 km in this inlet case.

### 50 °C inlet

| Insulation | Inlet heat loss (W/m) | Outlet oil temperature (°C) | Threshold distance (km) |
|---|---:|---:|---:|
| Aerogel | 34.35 | 48.56 | 36.21 |
| Rigid PU Foam | 41.00 | 48.29 | 30.33 |
| Advanced Syntactic Foam | 149.80 | 44.05 | 8.30 |
| Syntactic PP | 182.00 | 42.87 | 6.83 |
| Wood | 182.00 | 42.87 | 6.83 |
| Solid PP | 231.82 | 41.12 | 5.36 |
| Hylam | 277.38 | 39.59 | 4.48 |

Only Aerogel and Rigid PU Foam remain above 45 °C after 10 km in this inlet case.

## 5. Interpretation

- **Aerogel** has the lowest calculated conductivity and therefore the highest insulation resistance among the listed options. It gives the lowest calculated heat loss in both inlet cases.
- **Rigid PU Foam** is the next-best thermal performer and also passes the 50 °C inlet case over 10 km in this analytical model.
- **Advanced Syntactic Foam, Syntactic PP, Wood, Solid PP and Hylam** fall below the 45 °C bulk-oil threshold before 10 km in the 50 °C inlet case.
- The presentation flags practical concerns for Aerogel moisture ingress and PU-foam crushing under deep-sea pressure. These are material-selection considerations, not failure modes solved by this Python model.

## 6. Source-data and modelling notes

1. The interface-temperature values in `data/interface_temperatures.csv` are transcribed from the presentation. The dashboard displays them separately; they are not used to calibrate the analytical model.
2. The slide-reported result values are retained in `data/presentation_reference_results.csv`. The dashboard includes a baseline comparison so discrepancies remain visible.
3. Using the exact stated geometry and constants, the analytical calculation gives approximately 79.15 W/m for Aerogel at a 110 °C inlet, whereas the presentation table reports 79.5 W/m. For Hylam at a 50 °C inlet, the analytical calculation gives approximately 277.38 W/m, whereas the presentation reports 277.8 W/m. These differences are not hidden by hard-coded overrides.
4. The presentation's ANSYS screenshots report reaction-probe values of 79.528 W and 94.48 W for Aerogel and Rigid PU Foam, respectively. The dashboard preserves the screenshots and warns that an ANSYS reaction-probe total in W should not be treated as directly interchangeable with analytical heat loss per unit length in W/m unless the model depth and probe definition are known.
5. The title refers to “high thermal stress”, but the equations and results shown in the presentation are a heat-transfer analysis. The supplied data do not support a thermoelastic stress or strain calculation.

## 7. Scope and limitations to state clearly

- The Python model is steady-state and one-dimensional in the radial direction, with an axial bulk-oil energy balance.
- Thermal conductivity is constant for each layer. Temperature-, pressure-, moisture- and ageing-dependent conductivity are not modelled.
- The 45 °C value is used as a bulk-oil threshold proxy. Wax precipitation, deposition kinetics, deposit thickness and pressure-drop growth are not calculated.
- Hydrostatic-pressure collapse, foam crushing, thermal expansion stress and structural integrity are not simulated.
- The four ANSYS screenshots are included as reference evidence; the original ANSYS model files are not part of this Python package.
- This is an educational model, not a certified pipeline design tool. Material selection requires separate qualification for operating temperature, hydrostatic pressure, moisture exposure, joints and mechanical loading.

## 8. Suggested dashboard demonstration

1. **Performance overview:** compare heat loss and oil-temperature profiles for the 110 °C case.
2. Switch the sidebar to **50 °C inlet** and point out that only Aerogel and Rigid PU Foam remain above 45 °C at 10 km.
3. Expand **Baseline validation** to compare recalculated model outputs with the presentation table.
4. **Thermal model:** select a material and explain how each cylindrical layer contributes to total resistance.
5. **Interface temperatures:** show the data-acquisition table as source data, not as a fitted input.
6. **Critical radius:** compare the calculated critical radii with the 270 mm insulation outer radius from the baseline geometry.
7. **ANSYS references:** show the original simulation screenshots and distinguish them from the Python calculation.
8. End with **Interpretation & limitations**. Emphasise the limits of the 45 °C proxy and the absence of a thermo-mechanical stress model.

## 9. Likely questions

**Why does lower conductivity reduce heat loss?**  
For a fixed cylindrical geometry, lower conductivity increases the insulation conduction resistance. A larger total resistance reduces heat flow for the same temperature difference.

**Why do the materials separate more clearly in the 50 °C case?**  
The inlet oil begins only 5 °C above the 45 °C threshold. The available temperature margin is small, so higher heat loss causes the bulk oil to cross the threshold earlier.

**Does crossing 45 °C prove that wax deposits form?**  
No. It identifies a project-defined thermal risk threshold. Actual deposition depends on crude-oil composition, wax appearance temperature, flow conditions, surface temperature and deposition kinetics, none of which are solved here.

**Does the project calculate thermal stress?**  
No. It calculates thermal resistance, heat loss and oil temperature. A stress calculation would need the material elastic properties, thermal expansion coefficients, restraints, geometry and appropriate mechanical boundary conditions.

**Why are a few recalculated values not identical to the presentation?**  
The program uses the stated layer dimensions, conductivities and boundary coefficients directly. Small differences are disclosed in the comparison rather than forcing the computed output to equal a rounded slide value.
