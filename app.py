from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from subsea_insulation.model import (  # noqa: E402
    OperatingConditions,
    PipelineGeometry,
    calculate_material_result,
    calculate_resistance_breakdown,
    calculate_temperature_profile,
    compare_materials,
)

st.set_page_config(
    page_title="Subsea Pipeline Insulation | BMEE402P",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data

def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    materials = pd.read_csv(ROOT / "data" / "materials.csv")
    interface = pd.read_csv(ROOT / "data" / "interface_temperatures.csv")
    reference = pd.read_csv(ROOT / "data" / "presentation_reference_results.csv")
    return materials, interface, reference


materials_df, interface_df, presentation_reference = load_data()

st.markdown(
    """
    <style>
      html, body, [class*="css"] { font-family: 'Segoe UI', system-ui, sans-serif; }
      .block-container { padding-top: 1.6rem; padding-bottom: 2.5rem; max-width: 1500px; }
      .hero { padding: 1.25rem 1.5rem; border: 1px solid rgba(100,116,139,.25); border-radius: 16px;
              background: linear-gradient(115deg, rgba(15,45,71,.96), rgba(27,84,105,.94)); color: white; }
      .hero h1 { font-family: 'Segoe UI', system-ui, sans-serif; font-size: 1.8rem; line-height: 1.2; margin: 0 0 .35rem 0; color: white; }
      .hero p { margin: .2rem 0; color: #dceaf0; font-size: .96rem; }
      .eyebrow { letter-spacing: .12em; text-transform: uppercase; font-size: .72rem; font-weight: 700; color: #a9ced7; }
      .section-note { color: #64748b; font-size: .9rem; margin-top: -.4rem; }
      .info-card { border: 1px solid rgba(100,116,139,.25); border-radius: 12px; padding: 1rem 1.1rem; height: 100%; }
      .info-card h4 { margin: 0 0 .45rem 0; font-size: 1rem; }
      .info-card p { margin: 0; color: #64748b; font-size: .9rem; }
      .small-muted { color: #64748b; font-size: .82rem; }
      div[data-testid="stMetric"] { border: 1px solid rgba(100,116,139,.22); padding: .8rem 1rem; border-radius: 12px; }
      div[data-testid="stMetricLabel"] p { font-size: .82rem; }
      div[data-testid="stMetricValue"] { font-family: 'Segoe UI', system-ui, sans-serif; }
      .stTabs [data-baseweb="tab-list"] { gap: .5rem; }
      .stTabs [data-baseweb="tab"] { height: 2.8rem; padding: 0 1rem; }
      [data-testid="stSidebar"] { border-right: 1px solid rgba(100,116,139,.18); }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## Model controls")
    st.caption("Adjust the operating case. Material properties are taken from the project presentation.")
    scenario = st.selectbox("Reference case", ["110 °C inlet", "50 °C inlet", "Custom"], index=0)
    if scenario == "110 °C inlet":
        inlet_temperature = 110.0
        st.caption("Oil inlet set to the 110 °C presentation case.")
    elif scenario == "50 °C inlet":
        inlet_temperature = 50.0
        st.caption("Oil inlet set to the 50 °C presentation case.")
    else:
        inlet_temperature = st.slider("Custom oil inlet temperature (°C)", 46.0, 150.0, 80.0, 1.0)
    pipeline_length_km = st.slider("Pipeline length (km)", 1.0, 50.0, 10.0, 1.0)
    seawater_temperature = st.slider("Seawater temperature (°C)", -2.0, 15.0, 4.0, 0.5)
    wax_threshold = st.slider("Wax threshold (°C)", 30.0, 60.0, 45.0, 0.5)
    st.divider()
    st.markdown("**Flow and convection**")
    mass_flow = st.number_input("Oil mass flow (kg/s)", min_value=1.0, max_value=500.0, value=106.8, step=0.1)
    specific_heat = st.number_input("Oil specific heat (J/kg·K)", min_value=100.0, max_value=5000.0, value=2200.0, step=50.0)
    h_oil = st.number_input("Oil-side h (W/m²·K)", min_value=10.0, max_value=2000.0, value=100.0, step=10.0)
    h_seawater = st.number_input("Seawater-side h (W/m²·K)", min_value=10.0, max_value=5000.0, value=500.0, step=10.0)
    with st.expander("Advanced geometry", expanded=False):
        inner_diameter_mm = st.number_input("Pipe inner diameter (mm)", 100.0, 1000.0, 400.0, 5.0)
        steel_mm = st.number_input("Steel wall (mm)", 1.0, 100.0, 20.0, 1.0)
        insulation_mm = st.number_input("Insulation thickness (mm)", 5.0, 200.0, 50.0, 1.0)
        jacket_mm = st.number_input("Jacket thickness (mm)", 1.0, 30.0, 5.0, 1.0)
        concrete_mm = st.number_input("Concrete coating (mm)", 5.0, 200.0, 50.0, 1.0)
        fouling_mm = st.number_input("Biofouling film (mm)", 0.1, 10.0, 1.0, 0.1)

try:
    conditions = OperatingConditions(
        pipeline_length_m=pipeline_length_km * 1000.0,
        oil_mass_flow_kg_s=mass_flow,
        oil_specific_heat_J_kgK=specific_heat,
        h_oil_W_m2K=h_oil,
        h_seawater_W_m2K=h_seawater,
        seawater_temperature_C=seawater_temperature,
        wax_threshold_C=wax_threshold,
        oil_inlet_temperature_C=inlet_temperature,
    )
    geometry = PipelineGeometry(
        inner_diameter_m=inner_diameter_mm / 1000.0,
        steel_thickness_m=steel_mm / 1000.0,
        insulation_thickness_m=insulation_mm / 1000.0,
        jacket_thickness_m=jacket_mm / 1000.0,
        concrete_thickness_m=concrete_mm / 1000.0,
        biofouling_thickness_m=fouling_mm / 1000.0,
    )
except ValueError as exc:
    st.error(str(exc))
    st.stop()

material_pairs = list(zip(materials_df["material"], materials_df["k_W_mK"].astype(float)))
results = compare_materials(material_pairs, conditions, geometry)
best_material = results.iloc[0]
passing_count = int(results["passes_pipeline"].sum())

st.markdown(
    f"""
    <div class="hero">
      <div class="eyebrow">BMEE402P · Mini Project 6 · Heat and Mass Transfer</div>
      <h1>Subsea Oil Pipeline Insulation Performance</h1>
      <p>Thermal resistance, axial oil cooling and wax-threshold assessment for a multilayer subsea pipeline.</p>
      <p class="small-muted" style="color:#c5dbe3">School of Mechanical Engineering · VIT Vellore</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")

status_text = f"{passing_count} of {len(results)} materials remain at or above the wax threshold over {pipeline_length_km:g} km."
st.caption(f"Current case: {inlet_temperature:g} °C inlet · {seawater_temperature:g} °C seawater · {wax_threshold:g} °C wax threshold. {status_text}")

summary_tab, model_tab, interface_tab, critical_tab, ansys_tab, notes_tab = st.tabs(
    ["Performance overview", "Thermal model", "Interface temperatures", "Critical radius", "ANSYS references", "Interpretation & limitations"]
)

with summary_tab:
    st.subheader("Decision summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Best thermal insulator", str(best_material["material"]))
    c2.metric("Lowest inlet heat loss", f"{best_material['heat_loss_W_per_m']:.1f} W/m")
    c3.metric("Materials passing threshold", f"{passing_count} / {len(results)}")
    c4.metric("Pipeline outlet temperature · best", f"{best_material['T_outlet_C']:.2f} °C")

    left, right = st.columns([1.05, 1])
    with left:
        st.markdown("#### Heat loss at the oil inlet")
        heat_fig = px.bar(
            results.sort_values("heat_loss_W_per_m", ascending=True),
            x="heat_loss_W_per_m",
            y="material",
            orientation="h",
            labels={"heat_loss_W_per_m": "Heat loss per metre (W/m)", "material": "Insulation"},
            text_auto=".1f",
        )
        heat_fig.update_layout(height=390, margin=dict(l=5, r=10, t=10, b=10), showlegend=False)
        heat_fig.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(heat_fig, use_container_width=True)
    with right:
        st.markdown("#### Oil temperature along the pipeline")
        profile_fig = go.Figure()
        for material, conductivity in material_pairs:
            prof = calculate_temperature_profile(material, conductivity, conditions, geometry, points=121)
            profile_fig.add_trace(go.Scatter(
                x=prof["distance_km"], y=prof["oil_temperature_C"],
                mode="lines", name=material,
            ))
        profile_fig.add_hline(y=wax_threshold, line_dash="dash", line_color="#c0392b", annotation_text="Wax threshold")
        profile_fig.update_layout(
            height=390, margin=dict(l=5, r=10, t=10, b=10),
            xaxis_title="Distance along pipeline (km)", yaxis_title="Bulk oil temperature (°C)",
            legend=dict(orientation="h", y=-0.3),
        )
        st.plotly_chart(profile_fig, use_container_width=True)

    st.markdown("#### Material comparison")
    display = results.rename(columns={
        "material": "Insulation", "k_W_mK": "k (W/m·K)",
        "R_K_m_per_W": "R′ (K·m/W)", "heat_loss_W_per_m": "Inlet heat loss (W/m)",
        "T_outlet_C": f"Outlet temperature ({pipeline_length_km:g} km, °C)",
        "wax_distance_km": "Wax-threshold distance (km)", "passes_pipeline": "Passes pipeline?",
        "critical_radius_mm": "Critical radius (mm)",
    })
    comparison_style = display.style.format({
        "k (W/m·K)": "{:.3f}", "R′ (K·m/W)": "{:.4f}",
        "Inlet heat loss (W/m)": "{:.1f}",
        f"Outlet temperature ({pipeline_length_km:g} km, °C)": "{:.2f}",
        "Wax-threshold distance (km)": "{:.2f}", "Critical radius (mm)": "{:.3f}",
    }).apply(
        lambda column: [
            "color: #16794b; font-weight: 600" if value else "color: #b42318; font-weight: 600"
            for value in column
        ],
        subset=["Passes pipeline?"],
    )
    st.dataframe(comparison_style, use_container_width=True, hide_index=True)
    st.download_button(
        "Download current comparison (CSV)",
        data=results.to_csv(index=False).encode("utf-8"),
        file_name="subsea_insulation_comparison.csv",
        mime="text/csv",
    )

    with st.expander("Baseline validation against the values reported in the presentation"):
        st.caption("This comparison always uses the presentation's original 10 km geometry and operating inputs. It is independent of any custom sidebar settings above.")
        validation_inlet = st.selectbox("Presentation reference case", [110.0, 50.0], format_func=lambda value: f"{value:.0f} °C oil inlet")
        validation_conditions = OperatingConditions(oil_inlet_temperature_C=validation_inlet)
        validation_results = compare_materials(material_pairs, validation_conditions, PipelineGeometry())
        validation_reference = presentation_reference.loc[
            presentation_reference["inlet_temperature_C"] == validation_inlet
        ]
        validation_reference = validation_reference.rename(columns={
            "heat_loss_W_per_m": "slide_heat_loss_W_per_m",
            "T_10km_C": "slide_T_10km_C",
            "wax_distance_km": "slide_wax_distance_km",
        })
        validation_table = validation_results.merge(
            validation_reference,
            on="material",
            how="left",
            validate="one_to_one",
        )
        validation_display = validation_table[[
            "material", "heat_loss_W_per_m", "slide_heat_loss_W_per_m",
            "T_outlet_C", "slide_T_10km_C", "wax_distance_km", "slide_wax_distance_km",
        ]].rename(columns={
            "material": "Insulation",
            "heat_loss_W_per_m": "Model heat loss (W/m)",
            "slide_heat_loss_W_per_m": "Slide heat loss (W/m)",
            "T_outlet_C": "Model outlet (°C)",
            "slide_T_10km_C": "Slide outlet (°C)",
            "wax_distance_km": "Model threshold distance (km)",
            "slide_wax_distance_km": "Slide threshold distance (km)",
        })
        st.dataframe(validation_display.style.format({
            "Model heat loss (W/m)": "{:.2f}", "Slide heat loss (W/m)": "{:.2f}",
            "Model outlet (°C)": "{:.2f}", "Slide outlet (°C)": "{:.2f}",
            "Model threshold distance (km)": "{:.2f}", "Slide threshold distance (km)": "{:.2f}",
        }), use_container_width=True, hide_index=True)
        st.info("Small differences are retained transparently. The dashboard calculates from the stated dimensions and equations; it does not overwrite the original slide values to force a match.")

with model_tab:
    st.subheader("Analytical model and resistance network")
    st.markdown(
        r"""
        The model treats heat transfer as **steady-state radial conduction through concentric cylindrical layers**,
        with convection at the oil and seawater boundaries. The resulting resistance per metre is:

        \[
        R'_{total}=\frac{1}{2\pi r_i h_i}
        +\sum_j\frac{\ln(r_{o,j}/r_{i,j})}{2\pi k_j}
        +\frac{1}{2\pi r_o h_o}
        \]

        The bulk-oil temperature at axial position \(x\) is calculated using:

        \[
        T(x)=T_{sea}+(T_{in}-T_{sea})\exp\left[-\frac{x}{\dot m C_p R'_{total}}\right]
        \]

        The local heat loss per metre and distance to the wax threshold are:

        \[
        q'(x)=\frac{T(x)-T_{sea}}{R'_{total}},\qquad
        x_{wax}=\dot m C_p R'_{total}\ln\left(\frac{T_{in}-T_{sea}}{T_{wax}-T_{sea}}\right)
        \]
        """
    )
    st.caption("Notation: r = radius; k = thermal conductivity; h = convection coefficient; ṁ = oil mass flow; Cp = oil specific heat.")

    selected_material = st.selectbox("Inspect resistance breakdown for", materials_df["material"].tolist(), index=0)
    selected_k = float(materials_df.loc[materials_df["material"] == selected_material, "k_W_mK"].iloc[0])
    breakdown = calculate_resistance_breakdown(selected_k, geometry, conditions)
    total_r = float(breakdown["resistance_K_m_W"].sum())
    st.metric("Total resistance per metre", f"{total_r:.4f} K·m/W")
    col_a, col_b = st.columns([1.15, 1])
    with col_a:
        rb_fig = px.bar(
            breakdown, x="resistance_K_m_W", y="component", orientation="h",
            labels={"resistance_K_m_W": "Resistance (K·m/W)", "component": "Layer / boundary"},
            text_auto=".4f",
        )
        rb_fig.update_layout(height=390, margin=dict(l=5, r=10, t=10, b=10), showlegend=False)
        rb_fig.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(rb_fig, use_container_width=True)
    with col_b:
        r = geometry.radii_m
        radii_table = pd.DataFrame([
            ["Pipe inner wall", r["oil_inner_wall"] * 1000],
            ["Steel outer wall", r["steel_outer"] * 1000],
            ["Insulation outer wall", r["insulation_outer"] * 1000],
            ["Jacket outer wall", r["jacket_outer"] * 1000],
            ["Concrete outer wall", r["concrete_outer"] * 1000],
            ["External surface", r["external_surface"] * 1000],
        ], columns=["Interface", "Radius (mm)"])
        st.markdown("#### Model radii")
        st.dataframe(radii_table.style.format({"Radius (mm)": "{:.1f}"}), use_container_width=True, hide_index=True)
        st.markdown("#### Model inputs")
        st.write({
            "Oil mass flow (kg/s)": conditions.oil_mass_flow_kg_s,
            "Oil specific heat (J/kg·K)": conditions.oil_specific_heat_J_kgK,
            "Oil-side h (W/m²·K)": conditions.h_oil_W_m2K,
            "Seawater-side h (W/m²·K)": conditions.h_seawater_W_m2K,
        })
    st.download_button(
        "Download resistance breakdown (CSV)",
        data=breakdown.to_csv(index=False).encode("utf-8"),
        file_name=f"{selected_material.lower().replace(' ', '_')}_resistance_breakdown.csv",
        mime="text/csv",
    )

with interface_tab:
    st.subheader("Interface temperature data from the presentation")
    st.info("These values are transcribed from the presentation's data-acquisition table. They are displayed as reference data and are not used to calibrate the analytical model above.")
    selected_inlet = st.radio("Oil inlet case", [110, 50], horizontal=True)
    selected_interface_material = st.selectbox("Material", materials_df["material"].tolist(), key="interface_material")
    selected_row = interface_df[
        (interface_df["material"] == selected_interface_material)
        & (interface_df["oil_inlet_C"] == selected_inlet)
    ].iloc[0]
    interface_columns = [
        ("Oil inlet", "oil_inlet_C"), ("Inner wall", "inner_wall_C"),
        ("Steel / insulation", "steel_insulation_C"), ("Insulation / jacket", "insulation_jacket_C"),
        ("Jacket / concrete", "jacket_concrete_C"), ("Concrete / fouling", "concrete_fouling_C"),
        ("Outer surface", "outer_surface_C"), ("Seawater", "seawater_C"),
    ]
    plot_df = pd.DataFrame({"Interface": [label for label, _ in interface_columns], "Temperature (°C)": [selected_row[col] for _, col in interface_columns]})
    interface_fig = px.line(plot_df, x="Interface", y="Temperature (°C)", markers=True)
    interface_fig.update_layout(height=400, margin=dict(l=5, r=10, t=10, b=80), xaxis_tickangle=-25)
    st.plotly_chart(interface_fig, use_container_width=True)
    st.dataframe(interface_df, use_container_width=True, hide_index=True)
    st.download_button(
        "Download interface temperature data (CSV)",
        data=interface_df.to_csv(index=False).encode("utf-8"),
        file_name="interface_temperature_data.csv",
        mime="text/csv",
    )

with critical_tab:
    st.subheader("Critical radius of insulation")
    st.latex(r"r_{cr}=\frac{k}{h_o}")
    st.write("For the conventional cylindrical critical-radius check, the value is calculated using the seawater-side convection coefficient and each insulation conductivity.")
    critical = results[["material", "k_W_mK", "critical_radius_mm"]].copy()
    critical = critical.rename(columns={"material": "Insulation", "k_W_mK": "k (W/m·K)", "critical_radius_mm": "Critical radius (mm)"})
    st.dataframe(critical.style.format({"k (W/m·K)": "{:.3f}", "Critical radius (mm)": "{:.3f}"}), use_container_width=True, hide_index=True)
    radii = geometry.radii_m
    insulation_outer_mm = radii["insulation_outer"] * 1000
    external_radius_mm = radii["external_surface"] * 1000
    max_critical = float(critical["Critical radius (mm)"].max())
    k1, k2, k3 = st.columns(3)
    k1.metric("Insulation outer radius", f"{insulation_outer_mm:.1f} mm")
    k2.metric("Outer surface radius", f"{external_radius_mm:.1f} mm")
    k3.metric("Largest critical radius", f"{max_critical:.3f} mm")
    st.success("The insulation outer radius is much larger than the calculated critical radius for every listed material. Under this check, adding insulation reduces heat loss.")
    st.caption("The presentation uses 270 mm as the insulation outer radius for its baseline geometry; the external convection boundary in the full multilayer model is at the outside of the biofouling layer.")

with ansys_tab:
    st.subheader("ANSYS 2023 R1 thermal simulation references")
    st.caption("These are the original result screenshots embedded in the supplied presentation (slides 9 and 10). They are shown as source evidence; the Python dashboard does not execute or recreate the ANSYS finite-element analysis.")
    aerogel_col, pu_col = st.columns(2)
    with aerogel_col:
        st.markdown("#### Aerogel")
        st.image(str(ROOT / "assets" / "ansys_reference" / "aerogel_temperature_contour.png"), caption="Temperature contour · Aerogel case")
        st.image(str(ROOT / "assets" / "ansys_reference" / "aerogel_reaction_probe.png"), caption="Reaction probe · 79.528 W as displayed in ANSYS")
    with pu_col:
        st.markdown("#### Rigid PU Foam")
        st.image(str(ROOT / "assets" / "ansys_reference" / "rigid_pu_temperature_contour.png"), caption="Temperature contour · Rigid PU Foam case")
        st.image(str(ROOT / "assets" / "ansys_reference" / "rigid_pu_reaction_probe.png"), caption="Reaction probe · 94.48 W as displayed in ANSYS")
    st.warning("The ANSYS reaction-probe values are reproduced with the units shown in the screenshots. Do not assume they are directly interchangeable with the analytical model's heat-loss-per-unit-length output (W/m) without confirming the ANSYS model's out-of-plane depth and probe definition.")

with notes_tab:
    st.subheader("Engineering interpretation")
    pass_materials = results.loc[results["passes_pipeline"], "material"].tolist()
    fail_materials = results.loc[~results["passes_pipeline"], "material"].tolist()
    if pass_materials:
        st.markdown("**Materials that meet the selected wax-threshold criterion over the modelled length**")
        st.write(", ".join(pass_materials) + ".")
    if fail_materials:
        st.markdown("**Materials that fall below the selected threshold before the end of the line**")
        st.write(", ".join(fail_materials) + ".")
    st.markdown("#### Decision points carried over from the presentation")
    st.markdown(
        "- **Aerogel:** lowest calculated heat loss in the comparison; the presentation recommends moisture protection / sealed packs because wetting can reduce insulation performance.\n"
        "- **Rigid PU foam:** close thermal performance to Aerogel; the presentation flags crushing under deep-sea pressure as a design concern.\n"
        "- **Other listed materials:** may need a thicker insulation layer or a higher inlet temperature to satisfy the 45 °C criterion in the low-inlet case."
    )
    st.markdown("#### Scope and limitations")
    st.markdown(
        "1. **Steady-state, one-dimensional model:** heat transfer is represented by radial thermal resistances and an axial bulk-oil energy balance. Transient start-up and shutdown are not modelled.\n"
        "2. **Constant properties:** thermal conductivity is held constant for each layer. The calculation does not establish conductivity degradation or improvement with temperature, pressure, ageing or water ingress.\n"
        "3. **Waxing is a threshold proxy:** the model reports the distance at which bulk oil reaches 45 °C. It does not calculate wax precipitation, deposition rate, thickness growth or pressure-drop increase.\n"
        "4. **No structural / hydrostatic calculation:** pressure-induced crushing, thermal expansion stress and pipe integrity are not solved by this thermal model.\n"
        "5. **Separate interface dataset:** interface temperatures are copied from the presentation's data-acquisition table and are shown for discussion; they are not a calibration dataset for this analytical model.\n"
        "6. **Engineering validation required:** material ratings, deep-water suitability, wet insulation properties, field-joint performance and pressure resistance need independent testing before design use."
    )
    st.warning("Terminology note: although the project title refers to 'high thermal stress', this Python model calculates heat transfer and oil-temperature decay. It does not calculate thermoelastic stress or strain.")

st.divider()
st.caption("Prepared as an educational decision-support model from the BMEE402P Mini Project 6 presentation. Results depend on the assumptions and inputs shown above; this is not a certified pipeline design tool.")
