"""
File: app.py
Description: Streamlit app for microgrid optimization simulation for challenge 3
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.optimization.microgrid import Microgrid
from src.config.data_config import DATASETS
from src.config.pricing_config import ENERGY_RATES, DEMAND_CHARGES


st.write("DEBUG PANDAS:", pd.__version__)

st.set_page_config(
    page_title="Microgrid Optimization Simulator",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.write("DEBUG APP PATH:", os.getcwd())
st.write("DEBUG FILE:", os.path.dirname(__file__))

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0497a7;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-header">Microgrid Optimization Simulator</p>', unsafe_allow_html=True)

#  Theme colors 
COLOR_LOAD   = '#e760b8'
COLOR_GRID   = '#0497a7'
COLOR_PV     = '#f4a442'
COLOR_SOC    = '#7c5cbf'
COLOR_COST   = '#1a6b75'

#  Helper: pink-themed info box 
def pink_info(text: str, sidebar: bool = False):
    html = (
        "<div style='background-color:#fdf0f9; padding:0.5rem 0.75rem; "
        "border-left: 4px solid #e760b8; border-radius: 0.25rem; "
        "color: #2c3e50; font-size: 0.875rem; margin: 0.5rem 0;'>"
        f"{text}</div>"
    )
    if sidebar:
        st.sidebar.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)

#  Helper: x-axis tick format based on simulation length 
def xaxis_format(simulation_days: int) -> dict:
    if simulation_days <= 3:
        return dict(tickformat='%b %d %H:%M', dtick=3600000 * 6)
    elif simulation_days <= 14:
        return dict(tickformat='%b %d', dtick=3600000 * 24)
    else:
        return dict(tickformat='%b %d', dtick=3600000 * 24 * 3)

#  Session state 
if 'optimization_results' not in st.session_state:
    st.session_state.optimization_results = None
if 'microgrid' not in st.session_state:
    st.session_state.microgrid = None
if 'comparison_runs' not in st.session_state:
    st.session_state.comparison_runs = []  # list of dicts, each a saved run

#  Sidebar 
st.sidebar.title("Microgrid Configuration")

load_assets    = [name for name, info in DATASETS.items() if info['type'] in ['load', 'loadwev']]
pv_assets      = [name for name, info in DATASETS.items() if info['type'] == 'pv']
battery_assets = [name for name, info in DATASETS.items() if info['type'] == 'battery']

st.sidebar.markdown("### Building Loads")
selected_loads = st.sidebar.multiselect(
    "Select building loads:",
    options=load_assets,
    default=["CenterHall", "GeiselLibrary"],
    help="Choose one or more building loads to include in the microgrid"
)

st.sidebar.markdown("### PV Generators")
selected_pvs = st.sidebar.multiselect(
    "Select PV generators:",
    options=pv_assets,
    default=["BioEngineeringPV", "GilmanParkingPV"],
    help="Choose solar PV generators to include in the microgrid"
)

st.sidebar.markdown("### Battery Storage")
selected_batteries = st.sidebar.multiselect(
    "Select battery systems:",
    options=battery_assets,
    default=["BatteryStorage"],
    help="Choose battery storage systems for the microgrid"
)

has_battery = len(selected_batteries) > 0

st.sidebar.markdown("### Simulation Period")
pink_info("Available data: 2018-01-01 to 2019-12-31", sidebar=True)

col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date",
        value=datetime(2018, 7, 1),
        min_value=datetime(2018, 1, 1),
        max_value=datetime(2019, 12, 31)
    )
with col2:
    end_date = st.date_input(
        "End Date",
        value=datetime(2018, 7, 7),
        min_value=datetime(2018, 1, 1),
        max_value=datetime(2019, 12, 31)
    )

if start_date >= end_date:
    st.sidebar.error("End date must be after start date")
    st.stop()

simulation_days = (end_date - start_date).days
if simulation_days > 31:
    st.sidebar.warning(f"Long simulation period ({simulation_days} days) may take several minutes.")

st.sidebar.markdown("### Optimization Settings")

objective_type = st.sidebar.radio(
    "Optimization Objective:",
    options=["cost", "emissions", "weighted"],
    format_func=lambda x: {
        "cost": "Minimize Cost",
        "emissions": "Minimize Emissions",
        "weighted": "Weighted Multi-Objective"
    }[x],
)

#  Advanced Settings — battery options only shown when battery is selected 
with st.sidebar.expander("Advanced Settings"):

    if has_battery:
        round_trip_efficiency = st.slider(
            "Battery Round-Trip Efficiency",
            min_value=0.70, max_value=1.00, value=0.95, step=0.01,
            help="Energy efficiency during charge/discharge cycles (typically 0.85-0.95)"
        )
        include_soc_penalty = st.checkbox(
            "Include SOC Soft Constraints", value=True,
            help="Add penalty for operating outside preferred SOC range (20%-80%)"
        )
        if include_soc_penalty:
            col1, col2 = st.columns(2)
            with col1:
                soc_min = st.slider("Min SOC", 0.0, 0.5, 0.20, 0.05)
            with col2:
                soc_max = st.slider("Max SOC", 0.5, 1.0, 0.80, 0.05)
            soc_penalty_weight = st.number_input(
                "SOC Penalty Weight",
                min_value=1.0, max_value=1000.0,
                value=10.0 if objective_type == "cost" else 1000.0,
                step=10.0,
                help="Higher values enforce SOC limits more strictly"
            )
        else:
            soc_min, soc_max, soc_penalty_weight = 0.20, 0.80, None
    else:
        round_trip_efficiency = 0.95
        include_soc_penalty   = False
        soc_min, soc_max, soc_penalty_weight = 0.20, 0.80, None
        st.caption("Battery settings are disabled — no battery selected.")

    if objective_type == "weighted":
        st.markdown("**Weighted Objective Weights**")
        st.caption("Weights control the trade-off between cost and emissions.")
        cost_weight      = st.slider("Cost Weight (α)", 0.0, 1.0, 0.5, 0.05)
        emissions_weight = st.slider("Emissions Weight (β)", 0.0, 1.0, 0.5, 0.05)
    else:
        cost_weight, emissions_weight = 0.5, 0.5

    verbose_optimization = st.checkbox("Show Solver Output", value=False)

obj_label = {
    "cost":     "Minimize Cost",
    "emissions":"Minimize Emissions",
    "weighted": f"Weighted (α={cost_weight}, β={emissions_weight})"
}

#  Helper: build a results plot 
def build_results_figure(results, microgrid, start, end, include_soc_penalty, soc_min, soc_max):
    from src.optimization.pricing import get_price_array

    timestamps    = pd.to_datetime(results['timestamps'], unit='s')
    load_profile  = microgrid.get_total_load(start, end)
    pv_profile    = microgrid.get_total_pv_generation(start, end)
    energy_prices = get_price_array(results['timestamps'])
    hourly_costs  = results['grid_import'] * energy_prices
    sim_days      = (end - start).days if hasattr(end, 'year') else (end - start).days

    has_batt = microgrid.get_total_battery_storage()[1] > 0

    # Rows: Power Flow | SOC (if battery) | Hourly Cost
    n_rows         = 3 if has_batt else 2
    row_heights    = [0.4, 0.35, 0.25] if has_batt else [0.6, 0.4]
    subplot_titles = (
        ('Power Flow (kW)', 'Battery State of Charge (kWh)', 'Grid Import Cost ($/hour)')
        if has_batt else
        ('Power Flow (kW)', 'Grid Import Cost ($/hour)')
    )

    fig = make_subplots(
        rows=n_rows, cols=1,
        subplot_titles=subplot_titles,
        vertical_spacing=0.14,
        row_heights=row_heights
    )

    xticks = xaxis_format(sim_days)

    # Row 1: Power flow
    fig.add_trace(go.Scatter(x=timestamps, y=load_profile, name='Load',
                             line=dict(color=COLOR_LOAD, width=2)), row=1, col=1)
    if pv_profile is not None and len(pv_profile) > 0:
        fig.add_trace(go.Scatter(x=timestamps, y=pv_profile, name='PV Generation',
                                 line=dict(color=COLOR_PV, width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=timestamps, y=results['grid_import'], name='Grid Import',
                             line=dict(color=COLOR_GRID, width=2)), row=1, col=1)

    cost_row = 2
    if has_batt:
        # Row 2: SOC only (battery power row removed)
        _, battery_kwh = microgrid.get_total_battery_storage()
        soc_timestamps = pd.to_datetime(
            np.append(results['timestamps'], results['timestamps'][-1] + 3600), unit='s'
        )
        fig.add_trace(go.Scatter(x=soc_timestamps, y=results['soc'], name='SOC',
                                 line=dict(color=COLOR_SOC, width=2)), row=2, col=1)
        if include_soc_penalty:
            fig.add_hline(y=soc_min * battery_kwh, line_dash="dash", line_color=COLOR_LOAD,
                         opacity=0.5, row=2, col=1,
                         annotation_text=f"Min SOC ({soc_min*100:.0f}%)")
            fig.add_hline(y=soc_max * battery_kwh, line_dash="dash", line_color=COLOR_LOAD,
                         opacity=0.5, row=2, col=1,
                         annotation_text=f"Max SOC ({soc_max*100:.0f}%)")
        cost_row = 3

    # Last row: Hourly cost
    fig.add_trace(go.Scatter(x=timestamps, y=hourly_costs, name='Hourly Cost',
                             line=dict(color=COLOR_COST, width=2), fill='tozeroy'),
                  row=cost_row, col=1)

    # Apply x-axis formatting to all rows
    for row in range(1, n_rows + 1):
        fig.update_xaxes(tickformat=xticks['tickformat'], dtick=xticks['dtick'],
                         tickangle=-45, row=row, col=1)

    fig.update_xaxes(title_text="Time", row=cost_row, col=1)
    fig.update_yaxes(title_text="Power (kW)", row=1, col=1)
    if has_batt:
        fig.update_yaxes(title_text="Energy (kWh)", row=2, col=1)
    fig.update_yaxes(title_text="Cost ($)", row=cost_row, col=1)
    fig.update_layout(height=380 * n_rows, showlegend=True, hovermode='x unified')

    return fig, energy_prices, hourly_costs, load_profile, pv_profile


# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Configuration Summary", "Run Optimization", "Results", "Comparison"
])

# ── Tab 1: Configuration Summary ─────────────────────────────────────────────
with tab1:
    st.markdown('<p class="sub-header">Microgrid Configuration Summary</p>', unsafe_allow_html=True)

    if not selected_loads:
        st.warning("Please select at least one building load from the sidebar.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("#### Loads")
            for load in selected_loads:
                st.write(f"- {load}")
        with col2:
            st.markdown("#### PV Generators")
            if selected_pvs:
                for pv in selected_pvs:
                    st.write(f"- {pv}")
            else:
                st.write("None selected")
        with col3:
            st.markdown("#### Batteries")
            if selected_batteries:
                for bat in selected_batteries:
                    bat_info = DATASETS[bat]
                    st.write(f"- {bat}")
                    st.write(f"  - Power: {bat_info['rating_kw']} kW")
                    st.write(f"  - Capacity: {bat_info['rating_kwh']} kWh")
            else:
                st.write("None selected")

        st.markdown("---")
        st.markdown("#### Simulation Settings")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Start Date:** {start_date.strftime('%Y-%m-%d')}")
            st.write(f"**End Date:** {end_date.strftime('%Y-%m-%d')}")
            st.write(f"**Duration:** {simulation_days} days ({simulation_days * 24} hours)")
        with col2:
            st.write(f"**Objective:** {obj_label[objective_type]}")
            st.write(f"**Battery Efficiency:** {round_trip_efficiency * 100:.0f}%")
            st.write(f"**SOC Penalty:** {'Enabled' if include_soc_penalty else 'Disabled'}")

        st.markdown("---")
        st.markdown("#### Pricing Information (SDG&E TOU-DR1)")
        pricing_df = pd.DataFrame({
            'Period':              ['On-Peak', 'Off-Peak', 'Super Off-Peak'],
            'Energy Rate ($/kWh)': [f"${ENERGY_RATES['on_peak']:.3f}",
                                    f"${ENERGY_RATES['off_peak']:.3f}",
                                    f"${ENERGY_RATES['super_off_peak']:.3f}"],
            'Time of Day':         ['4 PM - 9 PM', '6 AM - 4 PM, 9 PM - midnight', 'midnight - 6 AM']
        })
        st.table(pricing_df)
        st.write(f"**Maximum Demand Charge:** ${DEMAND_CHARGES['maximum_demand']:.2f}/kW (applied for simulations ≥ 28 days)")
        st.write(f"**On-Peak Demand Charge:** ${DEMAND_CHARGES['on_peak_demand']:.2f}/kW (applied for simulations ≥ 28 days)")

#  Tab 2: Run Optimization
with tab2:
    st.markdown('<p class="sub-header">Run Optimization</p>', unsafe_allow_html=True)

    if not selected_loads:
        st.warning("Please select at least one building load from the sidebar before running.")
    else:
        st.markdown("#### Current Configuration")
        st.markdown(f"""
        - **Loads:** {len(selected_loads)} building(s)
        - **PV Generators:** {len(selected_pvs)} system(s)
        - **Battery Storage:** {len(selected_batteries)} system(s)
        - **Simulation Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} ({simulation_days} days)
        - **Objective:** {obj_label[objective_type]}
        """)

        if objective_type == "weighted":
            pink_info(
                f"<b>Weighted objective:</b> α={cost_weight} × Cost + β={emissions_weight} × Emissions."
            )

        if simulation_days < 28:
            pink_info("<b>Demand charges</b> are a monthly billing concept and will not be applied for this simulation period. Run ≥ 28 days to include them.")

        if st.button("Run Optimization", type="primary", use_container_width=True):
            with st.spinner("Building microgrid model..."):
                try:
                    microgrid = Microgrid(
                        loads=selected_loads,
                        pv_generators=selected_pvs if selected_pvs else None,
                        batteries=selected_batteries if selected_batteries else None
                    )
                    st.session_state.microgrid = microgrid
                    st.success("Microgrid model created successfully")
                except Exception as e:
                    st.error(f"Error creating microgrid: {str(e)}")
                    st.stop()

            with st.spinner(f"Running optimization for {simulation_days} days..."):
                try:
                    results = microgrid.optimize(
                        start_date=start_date,
                        end_date=end_date,
                        objective_type=objective_type,
                        round_trip_efficiency=round_trip_efficiency,
                        include_soc_penalty=include_soc_penalty,
                        soc_min=soc_min,
                        soc_max=soc_max,
                        soc_penalty_weight=soc_penalty_weight,
                        cost_weight=cost_weight,
                        emissions_weight=emissions_weight,
                        verbose=verbose_optimization
                    )
                    st.session_state.optimization_results = results
                    st.write("DEBUG TS RAW:", results['timestamps'][:5])
                    st.success("Optimization completed successfully!")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Cost", f"${results['cost_breakdown']['total_cost']:,.2f}")
                    with col2:
                        st.metric("Total Emissions", f"{results['total_emissions_gco2']/1000:,.2f} kg CO2")
                    with col3:
                        st.metric("Solver Status", results['status'])

                    pink_info("Switch to the 'Results' tab to see detailed visualizations.")
                except Exception as e:
                    st.error(f"Optimization failed: {str(e)}")
                    if verbose_optimization:
                        st.exception(e)

#  Tab 3: Results 
with tab3:
    st.markdown('<p class="sub-header">Optimization Results</p>', unsafe_allow_html=True)

    if st.session_state.optimization_results is None:
        pink_info("No results yet. Please run the optimization from the 'Run Optimization' tab.")
    else:
        results   = st.session_state.optimization_results
        microgrid = st.session_state.microgrid

        # Summary metrics
        st.markdown("### Summary Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Cost", f"${results['cost_breakdown']['total_cost']:,.2f}",
                      delta=f"Energy: ${results['cost_breakdown']['energy_charges']:,.2f}")
        with col2:
            st.metric("Demand Charges", f"${results['cost_breakdown']['demand_charges']:,.2f}",
                      delta=f"Peak: {results['cost_breakdown']['max_demand']:.1f} kW")
        with col3:
            st.metric("Total Emissions", f"{results['total_emissions_gco2']/1000:,.1f} kg CO2")
        with col4:
            st.metric("Grid Import", f"{np.sum(results['grid_import']):,.1f} kWh")

        if not results['cost_breakdown'].get('demand_charges_applied', True):
            pink_info("<b>Demand charges not applied</b> — run ≥ 28 days to include monthly demand charges.")

        # Cost breakdown
        st.markdown("---")
        st.markdown("### Cost Breakdown")
        cost_data = pd.DataFrame({
            'Category':   ['Energy Charges', 'Demand Charges', 'Total Cost'],
            'Amount ($)': [results['cost_breakdown']['energy_charges'],
                           results['cost_breakdown']['demand_charges'],
                           results['cost_breakdown']['total_cost']]
        })
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(cost_data, use_container_width=True, hide_index=True)
        with col2:
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Energy Charges', 'Demand Charges'],
                values=[results['cost_breakdown']['energy_charges'],
                        results['cost_breakdown']['demand_charges']],
                marker=dict(colors=[COLOR_GRID, COLOR_LOAD]),
                hole=.3
            )])
            fig_pie.update_layout(title="Cost Distribution", height=300)
            st.plotly_chart(fig_pie, use_container_width=True)

        # Time series
        st.markdown("---")
        st.markdown("### Time Series Analysis")
        st.write("DEBUG:", pd.to_datetime(results['timestamps'][0], unit='s'), pd.to_datetime(results['timestamps'][-1], unit='s'), len(results['timestamps']))
        
        fig, energy_prices, hourly_costs, load_profile, pv_profile = build_results_figure(
            results, microgrid, start_date, end_date, include_soc_penalty, soc_min, soc_max
        )
        st.plotly_chart(fig, use_container_width=True)

        # Battery performance (only if battery present)
        _, battery_kwh = microgrid.get_total_battery_storage()
        if battery_kwh > 0 and has_battery:
            st.markdown("---")
            st.markdown("### Battery Performance")
            col1, col2 = st.columns(2)
            total_charging    = np.sum(np.maximum(0,  results['battery_power']))
            total_discharging = np.sum(np.maximum(0, -results['battery_power']))
            with col1:
                st.metric("Total Charging",    f"{total_charging:,.1f} kWh")
            with col2:
                st.metric("Total Discharging", f"{total_discharging:,.1f} kWh")

            soc = results['soc']
            st.write(f"**SOC Range:** {soc.min():.1f} – {soc.max():.1f} kWh "
                     f"({soc.min()/battery_kwh*100:.1f}% – {soc.max()/battery_kwh*100:.1f}%)")
            st.write(f"**Average SOC:** {soc.mean():.1f} kWh ({soc.mean()/battery_kwh*100:.1f}%)")

        # Export
        st.markdown("---")
        st.markdown("### Export Results")
        timestamps = pd.to_datetime(results['timestamps'], unit='s')
        results_df = pd.DataFrame({
            'Timestamp':         timestamps,
            'Load_kW':           load_profile,
            'PV_Generation_kW':  pv_profile if pv_profile is not None else 0,
            'Grid_Import_kW':    results['grid_import'],
            'Battery_Power_kW':  results['battery_power'],
            'SOC_kWh':           results['soc'][:-1],
            'Energy_Price_$/kWh':energy_prices,
            'Hourly_Cost_$':     hourly_costs
        })
        st.download_button(
            label="Download Results as CSV",
            data=results_df.to_csv(index=False),
            file_name=f"microgrid_results_{start_date}_{end_date}.csv",
            mime="text/csv"
        )

        # Save to comparison
        st.markdown("---")
        run_label = st.text_input(
            "Label for this run (used in Comparison tab):",
            value=f"{obj_label[objective_type]} | {start_date} – {end_date}"
        )
        if st.button("Save to Comparison"):
            st.session_state.comparison_runs.append({
                'label':       run_label,
                'results':     results,
                'microgrid':   microgrid,
                'start':       start_date,
                'end':         end_date,
                'objective':   objective_type,
                'loads':       selected_loads,
                'pvs':         selected_pvs,
                'batteries':   selected_batteries,
            })
            st.success(f"Saved '{run_label}' to Comparison tab.")

# Tab 4: Comparison 
with tab4:
    st.markdown('<p class="sub-header">Scenario Comparison</p>', unsafe_allow_html=True)

    runs = st.session_state.comparison_runs

    if not runs:
        pink_info("No runs saved yet. Run an optimization and click <b>Save to Comparison</b> in the Results tab.")
    else:
        # Clear button
        if st.button("Clear All Runs"):
            st.session_state.comparison_runs = []
            st.rerun()

        # Summary table
        st.markdown("### Summary Table")
        summary_rows = []
        for r in runs:
            cb = r['results']['cost_breakdown']
            summary_rows.append({
                'Run':              r['label'],
                'Objective':        r['objective'],
                'Loads':            ", ".join(r['loads']),
                'Batteries':        ", ".join(r['batteries']) if r['batteries'] else "None",
                'Period':           f"{r['start']} – {r['end']}",
                'Total Cost ($)':   round(cb['total_cost'], 2),
                'Energy ($)':       round(cb['energy_charges'], 2),
                'Demand ($)':       round(cb['demand_charges'], 2),
                'Emissions (kg)':   round(r['results']['total_emissions_gco2'] / 1000, 1),
                'Grid Import (kWh)':round(np.sum(r['results']['grid_import']), 1),
            })
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

        # Grid import comparison chart
        st.markdown("---")
        st.markdown("### Grid Import Comparison")
        fig_gi = go.Figure()
        for r in runs:
            timestamps = pd.to_datetime(r['results']['timestamps'], unit='s')
            fig_gi.add_trace(go.Scatter(
                x=timestamps, y=r['results']['grid_import'],
                name=r['label'], mode='lines'
            ))
        fig_gi.update_layout(
            height=400, hovermode='x unified',
            yaxis_title="Grid Import (kW)", xaxis_title="Time"
        )
        st.plotly_chart(fig_gi, use_container_width=True)

        # Battery SOC comparison (only runs with batteries)
        battery_runs = [r for r in runs if r['batteries']]
        if battery_runs:
            st.markdown("---")
            st.markdown("### Battery SOC Comparison")
            fig_soc = go.Figure()
            for r in battery_runs:
                _, battery_kwh = r['microgrid'].get_total_battery_storage()
                soc_ts = pd.to_datetime(
                    np.append(r['results']['timestamps'], r['results']['timestamps'][-1] + 3600),
                    unit='s'
                )
                fig_soc.add_trace(go.Scatter(
                    x=soc_ts, y=r['results']['soc'],
                    name=r['label'], mode='lines'
                ))
            fig_soc.update_layout(
                height=400, hovermode='x unified',
                yaxis_title="SOC (kWh)", xaxis_title="Time"
            )
            st.plotly_chart(fig_soc, use_container_width=True)

        # Cost breakdown comparison bar chart
        st.markdown("---")
        st.markdown("### Cost Breakdown Comparison")
        fig_cost = go.Figure()
        labels = [r['label'] for r in runs]
        fig_cost.add_trace(go.Bar(name='Energy Charges',
                                  x=labels,
                                  y=[r['results']['cost_breakdown']['energy_charges'] for r in runs],
                                  marker_color=COLOR_GRID))
        fig_cost.add_trace(go.Bar(name='Demand Charges',
                                  x=labels,
                                  y=[r['results']['cost_breakdown']['demand_charges'] for r in runs],
                                  marker_color=COLOR_LOAD))
        fig_cost.update_layout(
            barmode='stack', height=400,
            yaxis_title="Cost ($)", xaxis_title="Run"
        )
        st.plotly_chart(fig_cost, use_container_width=True)

        # Emissions comparison
        st.markdown("---")
        st.markdown("### Emissions Comparison")
        fig_em = go.Figure(go.Bar(
            x=labels,
            y=[r['results']['total_emissions_gco2'] / 1000 for r in runs],
            marker_color=COLOR_LOAD
        ))
        fig_em.update_layout(height=350, yaxis_title="Emissions (kg CO2)", xaxis_title="Run")
        st.plotly_chart(fig_em, use_container_width=True)

        # Download comparison table
        st.markdown("---")
        st.download_button(
            label="Download Comparison Table as CSV",
            data=pd.DataFrame(summary_rows).to_csv(index=False),
            file_name="microgrid_comparison.csv",
            mime="text/csv"
        )

#  Footer 
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; padding: 1rem;'>"
    "Microgrid Optimization Simulator | Powered by CVXPY & Streamlit"
    "</div>",
    unsafe_allow_html=True
)