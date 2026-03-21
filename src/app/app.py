"""
Microgrid Optimization Simulator
Challenge 3 - Streamlit Interface

This application allows users to configure a microgrid with various loads, 
PV generators, and battery storage, then optimize the system for cost or 
emissions minimization.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.optimization.microgrid import Microgrid
from src.config.data_config import DATASETS
from src.config.pricing_config import ENERGY_RATES, DEMAND_CHARGES

# Page configuration
st.set_page_config(
    page_title="Microgrid Optimization Simulator",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
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
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">Microgrid Optimization Simulator</p>', unsafe_allow_html=True)

# Initialize session state
if 'optimization_results' not in st.session_state:
    st.session_state.optimization_results = None
if 'microgrid' not in st.session_state:
    st.session_state.microgrid = None

# Sidebar - Microgrid Configuration
st.sidebar.title("Microgrid Configuration")

# Organize datasets by type for easier selection
load_assets = [name for name, info in DATASETS.items() if info['type'] in ['load', 'loadwev']]
pv_assets = [name for name, info in DATASETS.items() if info['type'] == 'pv']
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

# Date Range Selection
st.sidebar.markdown("### Simulation Period")
st.sidebar.info("Available data: 2018-01-01 to 2019-12-31")

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

# Validate date range
if start_date >= end_date:
    st.sidebar.error("End date must be after start date")
    st.stop()

simulation_days = (end_date - start_date).days
if simulation_days > 31:
    st.sidebar.warning(f"Long simulation period ({simulation_days} days) may take several minutes to optimize.")

# Optimization Settings
st.sidebar.markdown("### Optimization Settings")

objective_type = st.sidebar.radio(
    "Optimization Objective:",
    options=["cost", "emissions", "weighted"],
    format_func=lambda x: {
        "cost": "Minimize Cost",
        "emissions": "Minimize Emissions",
        "weighted": "Weighted Multi-Objective"
    }[x],
    help="Choose the primary objective for optimization"
)

# Advanced Settings (Expandable)
with st.sidebar.expander("Advanced Settings"):
    round_trip_efficiency = st.slider(
        "Battery Round-Trip Efficiency",
        min_value=0.70,
        max_value=1.00,
        value=0.95,
        step=0.01,
        help="Energy efficiency during charge/discharge cycles (typically 0.85-0.95)"
    )
    
    include_soc_penalty = st.checkbox(
        "Include SOC Soft Constraints",
        value=True,
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
            min_value=1.0,
            max_value=1000.0,
            value=10.0 if objective_type == "cost" else 1000.0,
            step=10.0,
            help="Higher values enforce SOC limits more strictly"
        )
    else:
        soc_min, soc_max, soc_penalty_weight = 0.20, 0.80, None

    # Weighted objective weights — only shown when weighted is selected
    if objective_type == "weighted":
        st.markdown("**Weighted Objective Weights**")
        st.caption("Weights control the trade-off between cost and emissions. They do not need to sum to 1.")
        cost_weight = st.slider("Cost Weight (α)", 0.0, 1.0, 0.5, 0.05)
        emissions_weight = st.slider("Emissions Weight (β)", 0.0, 1.0, 0.5, 0.05)
    else:
        cost_weight = 0.5
        emissions_weight = 0.5

    verbose_optimization = st.checkbox(
        "Show Solver Output",
        value=False,
        help="Display detailed optimization solver logs"
    )

# Objective label helper used across all tabs
obj_label = {
    "cost": "Minimize Cost",
    "emissions": "Minimize Emissions",
    "weighted": f"Weighted Multi-Objective (α={cost_weight}, β={emissions_weight})"
}

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["Configuration Summary", "Run Optimization", "Results", "About"])

with tab1:
    st.markdown('<p class="sub-header">Microgrid Configuration Summary</p>', unsafe_allow_html=True)
    
    if not selected_loads:
        st.warning("Please select at least one building load from the sidebar to configure the microgrid.")
    else:
        # Create summary columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Loads")
            if selected_loads:
                for load in selected_loads:
                    st.write(f"- {load}")
            else:
                st.write("None selected")
        
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
        
        # Simulation details
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
        
        # Pricing information
        st.markdown("---")
        st.markdown("#### Pricing Information (SDG&E TOU-DR1)")
        
        pricing_df = pd.DataFrame({
            'Period': ['On-Peak', 'Off-Peak', 'Super Off-Peak'],
            'Energy Rate ($/kWh)': [
                f"${ENERGY_RATES['on_peak']:.3f}",
                f"${ENERGY_RATES['off_peak']:.3f}",
                f"${ENERGY_RATES['super_off_peak']:.3f}"
            ],
            'Time of Day': [
                '4 PM - 9 PM',
                '6 AM - 4 PM, 9 PM - midnight',
                'midnight - 6 AM'
            ]
        })
        st.table(pricing_df)
        
        st.write(f"**Maximum Demand Charge:** ${DEMAND_CHARGES['maximum_demand']:.2f}/kW")
        st.write(f"**On-Peak Demand Charge:** ${DEMAND_CHARGES['on_peak_demand']:.2f}/kW")

with tab2:
    st.markdown('<p class="sub-header">Run Optimization</p>', unsafe_allow_html=True)
    
    if not selected_loads:
        st.warning("Please select at least one building load from the sidebar before running optimization.")
    else:
        # Show configuration summary
        st.markdown("#### Current Configuration")
        config_summary = f"""
        - **Loads:** {len(selected_loads)} building(s)
        - **PV Generators:** {len(selected_pvs)} system(s)
        - **Battery Storage:** {len(selected_batteries)} system(s)
        - **Simulation Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} ({simulation_days} days)
        - **Objective:** {obj_label[objective_type]}
        """
        st.markdown(config_summary)

        # Extra callout for weighted objective so user understands the weights
        if objective_type == "weighted":
            st.info(
                f"**Weighted objective:** α={cost_weight} × Cost + β={emissions_weight} × Emissions. "
                "Because cost (dollars) and emissions (gCO₂e) are on different scales, "
                "adjusting the weights changes which objective dominates rather than splitting them equally."
            )
        
        # Run optimization button
        if st.button("Run Optimization", type="primary", use_container_width=True):
            with st.spinner("Building microgrid model..."):
                try:
                    # Create microgrid object
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
            
            with st.spinner(f"Running optimization for {simulation_days} days... This may take a few minutes."):
                try:
                    # Run optimization
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
                    st.success("Optimization completed successfully!")
                    
                    # Display quick summary
                    st.markdown("#### Quick Results Summary")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        total_cost = results['cost_breakdown']['total_cost']
                        st.metric("Total Cost", f"${total_cost:,.2f}")
                    
                    with col2:
                        total_emissions = results['total_emissions_gco2'] / 1000  # Convert to kg
                        st.metric("Total Emissions", f"{total_emissions:,.2f} kg CO2")
                    
                    with col3:
                        status = results['status']
                        st.metric("Solver Status", status)
                    
                    st.info("Switch to the 'Results' tab to see detailed visualizations and analysis.")
                    
                except Exception as e:
                    st.error(f"Optimization failed: {str(e)}")
                    if verbose_optimization:
                        st.exception(e)

with tab3:
    st.markdown('<p class="sub-header">Optimization Results</p>', unsafe_allow_html=True)
    
    if st.session_state.optimization_results is None:
        st.info("No results yet. Please run the optimization from the 'Run Optimization' tab.")
    else:
        results = st.session_state.optimization_results
        
        # Results Summary
        st.markdown("### Summary Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_cost = results['cost_breakdown']['total_cost']
            energy_charges = results['cost_breakdown']['energy_charges']
            st.metric(
                "Total Cost",
                f"${total_cost:,.2f}",
                delta=f"Energy: ${energy_charges:,.2f}"
            )
        
        with col2:
            demand_charges = results['cost_breakdown']['demand_charges']
            max_demand = results['cost_breakdown']['max_demand']
            st.metric(
                "Demand Charges",
                f"${demand_charges:,.2f}",
                delta=f"Peak: {max_demand:.1f} kW"
            )
        
        with col3:
            total_emissions_kg = results['total_emissions_gco2'] / 1000
            st.metric("Total Emissions", f"{total_emissions_kg:,.1f} kg CO2")
        
        with col4:
            total_energy = np.sum(results['grid_import'])
            st.metric("Grid Import", f"{total_energy:,.1f} kWh")
        
        # Cost Breakdown
        st.markdown("---")
        st.markdown("### Cost Breakdown")
        
        cost_data = pd.DataFrame({
            'Category': ['Energy Charges', 'Demand Charges', 'Total Cost'],
            'Amount ($)': [
                results['cost_breakdown']['energy_charges'],
                results['cost_breakdown']['demand_charges'],
                results['cost_breakdown']['total_cost']
            ]
        })

        if not results['cost_breakdown'].get('demand_charges_applied', True):
            st.info(
        "**Demand charges not applied** — demand charges are a monthly billing concept "
        "and are only included in simulations of 28 days or more. "
        "Try running a full month to see how demand charges affect the optimization."
         )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.dataframe(cost_data, use_container_width=True, hide_index=True)
        
        with col2:
            # Pie chart of cost breakdown
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Energy Charges', 'Demand Charges'],
                values=[
                    results['cost_breakdown']['energy_charges'],
                    results['cost_breakdown']['demand_charges']
                ],
                hole=.3
            )])
            fig_pie.update_layout(title="Cost Distribution", height=300)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Time Series Plots
        st.markdown("---")
        st.markdown("### Time Series Analysis")
        
        # Convert timestamps to datetime
        timestamps = pd.to_datetime(results['timestamps'], unit='s')
        
        # Get microgrid data for context
        microgrid = st.session_state.microgrid
        load_profile = microgrid.get_total_load(start_date, end_date)
        pv_profile = microgrid.get_total_pv_generation(start_date, end_date)
        
        # Create subplots
        fig = make_subplots(
            rows=4, cols=1,
            subplot_titles=(
                'Power Flow (kW)',
                'Battery Power (kW)',
                'Battery State of Charge (kWh)',
                'Grid Import Cost ($/hour)'
            ),
            vertical_spacing=0.08,
            row_heights=[0.25, 0.25, 0.25, 0.25]
        )
        
        # Plot 1: Power Flow
        fig.add_trace(
            go.Scatter(x=timestamps, y=load_profile, name='Load', 
                      line=dict(color='red', width=2)),
            row=1, col=1
        )
        if pv_profile is not None and len(pv_profile) > 0:
            fig.add_trace(
                go.Scatter(x=timestamps, y=pv_profile, name='PV Generation',
                          line=dict(color='orange', width=2)),
                row=1, col=1
            )
        fig.add_trace(
            go.Scatter(x=timestamps, y=results['grid_import'], name='Grid Import',
                      line=dict(color='blue', width=2)),
            row=1, col=1
        )
        
        # Plot 2: Battery Power
        fig.add_trace(
            go.Scatter(x=timestamps, y=results['battery_power'], name='Battery Power',
                      line=dict(color='green', width=2),
                      fill='tozeroy'),
            row=2, col=1
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
        
        # Plot 3: SOC
        battery_kw, battery_kwh = microgrid.get_total_battery_storage()
        soc_timestamps = pd.to_datetime(
            np.append(results['timestamps'], results['timestamps'][-1] + 3600),
            unit='s'
        )
        
        fig.add_trace(
            go.Scatter(x=soc_timestamps, y=results['soc'], name='SOC',
                      line=dict(color='purple', width=2)),
            row=3, col=1
        )
        
        # Add SOC limit lines
        if include_soc_penalty:
            fig.add_hline(y=soc_min * battery_kwh, line_dash="dash", 
                         line_color="red", opacity=0.5, row=3, col=1,
                         annotation_text=f"Min SOC ({soc_min*100:.0f}%)")
            fig.add_hline(y=soc_max * battery_kwh, line_dash="dash",
                         line_color="red", opacity=0.5, row=3, col=1,
                         annotation_text=f"Max SOC ({soc_max*100:.0f}%)")
        
        # Plot 4: Hourly Cost
        from src.optimization.pricing import get_price_array
        energy_prices = get_price_array(results['timestamps'])
        hourly_costs = results['grid_import'] * energy_prices
        
        fig.add_trace(
            go.Scatter(x=timestamps, y=hourly_costs, name='Hourly Cost',
                      line=dict(color='darkblue', width=2),
                      fill='tozeroy'),
            row=4, col=1
        )
        
        # Update layout
        fig.update_xaxes(title_text="Time", row=4, col=1)
        fig.update_yaxes(title_text="Power (kW)", row=1, col=1)
        fig.update_yaxes(title_text="Power (kW)", row=2, col=1)
        fig.update_yaxes(title_text="Energy (kWh)", row=3, col=1)
        fig.update_yaxes(title_text="Cost ($)", row=4, col=1)
        
        fig.update_layout(
            height=1200,
            showlegend=True,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Battery Performance Analysis
        st.markdown("---")
        st.markdown("### Battery Performance")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_charging = np.sum(np.maximum(0, results['battery_power']))
            st.metric("Total Charging", f"{total_charging:,.1f} kWh")
        
        with col2:
            total_discharging = np.sum(np.maximum(0, -results['battery_power']))
            st.metric("Total Discharging", f"{total_discharging:,.1f} kWh")
        
        with col3:
            cycles = total_charging / battery_kwh if battery_kwh > 0 else 0
            st.metric("Equivalent Cycles", f"{cycles:.2f}")
        
        # SOC Statistics
        soc_min_actual = np.min(results['soc'])
        soc_max_actual = np.max(results['soc'])
        soc_avg = np.mean(results['soc'])
        
        st.write(f"**SOC Range:** {soc_min_actual:.1f} - {soc_max_actual:.1f} kWh "
                f"({soc_min_actual/battery_kwh*100:.1f}% - {soc_max_actual/battery_kwh*100:.1f}%)")
        st.write(f"**Average SOC:** {soc_avg:.1f} kWh ({soc_avg/battery_kwh*100:.1f}%)")
        
        # Download Results
        st.markdown("---")
        st.markdown("### Export Results")
        
        # Create DataFrame for export
        results_df = pd.DataFrame({
            'Timestamp': timestamps,
            'Load_kW': load_profile,
            'PV_Generation_kW': pv_profile if pv_profile is not None else 0,
            'Grid_Import_kW': results['grid_import'],
            'Battery_Power_kW': results['battery_power'],
            'SOC_kWh': results['soc'][:-1],  # Exclude last SOC value
            'Energy_Price_$/kWh': energy_prices,
            'Hourly_Cost_$': hourly_costs
        })
        
        csv = results_df.to_csv(index=False)
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name=f"microgrid_results_{start_date}_{end_date}.csv",
            mime="text/csv"
        )

with tab4:
    st.markdown('<p class="sub-header">About This Tool</p>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Purpose
    
    This Microgrid Optimization Simulator is designed for **Challenge 3** of the microgrid 
    optimization educational project. It demonstrates centralized control optimization for 
    grid-connected microgrids with:
    
    - Building load profiles
    - Solar PV generation
    - Battery energy storage systems
    
    ### Features
    
    **Optimization Objectives:**
    - **Cost Minimization**: Minimize total electricity costs including energy charges and demand charges
    - **Emissions Minimization**: Minimize CO2 emissions from grid electricity
    - **Weighted Multi-Objective**: Minimize α × Cost + β × Emissions, allowing user-controlled trade-off between the two objectives
    
    **Key Capabilities:**
    - Real building load data from UCSD campus
    - Actual solar PV generation profiles
    - SDG&E time-of-use (TOU) pricing with demand charges
    - Quarterly carbon intensity profiles
    - Battery storage optimization with configurable efficiency
    - SOC management with soft constraints
    
    ### Optimization Formulation
    
    **Decision Variables:**
    - Grid import power at each time step
    - Battery charge/discharge power
    - Battery state of charge (SOC)
    
    **Constraints:**
    - Power balance: Grid + Battery + PV = Load
    - Battery power limits (+-rating)
    - Battery energy limits (0 to capacity)
    - Battery dynamics (SOC evolution)
    - Non-negativity of grid imports
    
    **Objective Functions:**
    
    *Cost Minimization:*
    ```
    minimize: sum(energy_price x grid_import) + 
              max_demand x demand_charge_rate +
              on_peak_max x on_peak_demand_rate +
              SOC_penalty
    ```
    
    *Emissions Minimization:*
    ```
    minimize: sum(carbon_intensity x grid_import x 3.6) + SOC_penalty
    ```

    *Weighted Multi-Objective:*
    ```
    minimize: α × cost_objective + β × emissions_objective + SOC_penalty
    ```
    where α and β are user-defined weights controlling the cost/emissions trade-off.
    Note: because cost (dollars) and emissions (gCO₂e) are on different scales,
    the weights are relative rather than absolute — increasing α makes cost dominate.
    
    ### Usage Tips
    
    1. **Start Small**: Begin with a short simulation period (1-7 days) to understand the tool
    2. **Compare Objectives**: Run the same configuration with both cost and emissions objectives
    3. **Try Weighted**: Use the weighted objective and vary α/β to explore the cost-emissions trade-off
    4. **Battery Sizing**: Try different battery configurations to see their impact
    5. **SOC Constraints**: Experiment with SOC penalty weights to see battery behavior changes
    6. **Seasonal Variation**: Compare summer vs. winter optimization results
    
    ### Data Sources
    
    - **Building Loads**: UCSD Microgrid Database
    - **PV Generation**: UCSD campus solar installations
    - **Pricing**: SDG&E TOU-DR1 tariff (2018-2019)
    - **Carbon Intensity**: CAISO quarterly average values
    
    ### Technical Details
    
    - **Optimization Solver**: CVXPY with ECOS solver
    - **Time Resolution**: Hourly intervals
    - **Battery Model**: Simple energy balance with round-trip efficiency
    - **Pricing Model**: Time-of-use energy charges + demand charges
    
    ### System Requirements
    
    This tool requires:
    - Python 3.8+
    - CVXPY (convex optimization)
    - Streamlit (web interface)
    - Plotly (interactive visualizations)
    
    """)
    

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 1rem;'>
    Microgrid Optimization Simulator | Powered by CVXPY & Streamlit
    </div>
    """,
    unsafe_allow_html=True
)