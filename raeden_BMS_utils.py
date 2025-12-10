import streamlit as st
import pandas as pd
import numpy as np

def render_requirements_page():
    st.title("🔋 Energy System Requirements")
    st.markdown("Define the operational parameters, financial constraints, and architectural choices for the data center.")
    
    # --- Section 1: Load Profile ---
    st.divider()
    st.header("1. Load Profile Configuration")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        profile_mode = st.radio(
            "Profile Source",
            ["Use Default Profile", "Upload Custom Data"],
            help="Choose between pre-loaded industry standard profiles or upload your own time-series data."
        )
    
    with col2:
        if profile_mode == "Use Default Profile":
            st.selectbox(
                "Select Default Profile",
                ["Hyperscale (Steady Base Load)", "Edge DC (High Variance)", "Enterprise (9-5 Peak)"]
            )
            # Optional: Display a placeholder chart for the selected default
            st.info("💡 Tip: Hyperscale profiles assume 24/7 constant utilization.")
            
        else:
            uploaded_file = st.file_uploader("Upload Load Profile (CSV/Excel)", type=['csv', 'xlsx'])
            if uploaded_file:
                st.success(f"File '{uploaded_file.name}' uploaded successfully.")

    # --- Section 2: Energy System Components ---
    st.divider()
    st.header("2. Allowable Technologies")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.subheader("Renewables")
        st.checkbox("On-site Solar PV")
        st.checkbox("On-site Wind")
        
    with c2:
        st.subheader("Storage & Backup")
        st.checkbox("Battery Storage (BESS)")
        st.checkbox("Hydrogen Storage")
        st.checkbox("Diesel / NG Generator")
        
    with c3:
        st.subheader("Thermal / HVAC")
        st.selectbox("HVAC Architecture", ["Air Cooled", "Water Cooled", "Hybrid"])
        st.checkbox("Thermal Storage")

    # --- Section 3: Project Constraints ---
    st.divider()
    st.header("3. Financial & Operational Constraints")
    
    with st.expander("💰 Financial Inputs (CAPEX/OPEX)", expanded=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            st.number_input("Max CAPEX Budget ($)", min_value=0, step=10000, help="Total capital expenditure limit.")
            st.number_input("Max Land Cost ($/sqm)", min_value=0, step=100)
        with f_col2:
            st.number_input("Max OPEX Limit ($/year)", min_value=0, step=5000)
            st.number_input("Labor Cost ($/hr)", min_value=0, step=10)
        with f_col3:
            st.number_input("Max Project Wait Time (Months)", min_value=0, step=1)

    with st.expander("🛡️ Reliability & Uptime", expanded=True):
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            st.slider("Target Uptime Availability (%)", min_value=99.0, max_value=99.999, value=99.9, step=0.001, format="%.3f")
        with r_col2:
            st.toggle("Require N+1 Redundancy", value=True, help="Ensure at least one backup component is available for critical systems.")

    # --- Section 4: Algorithms ---
    st.divider()
    st.header("4. Optimization & Control")
    
    st.selectbox(
        "Battery Management System (BMS) Algorithm",
        [
            "Naive Schedule (Time-of-Use)",
            "Rule Based Control",
            "MPC Optimization (Model Predictive Control)",
            "MILP (Mixed-Integer Linear Programming)",
            "Lexicographic Optimization",
            "Stochastic MPC"
        ],
        help="Select the control logic for energy dispatch."
    )
    
    st.markdown("---")
    if st.button("Save Requirements & Generate Scenario", type="primary"):
        st.toast("Requirements saved successfully!", icon="✅")

def render_results_page():
    st.title("📊 Optimization Results & Scenarios")
    st.markdown("Comparative analysis of financial performance and asset health across operational strategies.")

    # --- 1. Generate Fake Placeholder Data ---
    # We create a dictionary to simulate the output of your optimization engine
    data = {
        "Scenario": [
            "1. Grid Tied (Baseline)", 
            "2. Grid Tied + On-site Gen", 
            "3. Grid + Gen + Storage", 
            "4. Grid + Gen + Storage + Demand Flex"
        ],
        "Demand Charges ($)": [50000, 42000, 15000, 8000],   # Minimize
        "TOU Energy Charges ($)": [120000, 95000, 85000, 70000], # Minimize
        "Grid Service Revenue ($)": [0, 0, 12000, 25000],    # Maximize
        "Battery Degradation (%)": [0, 0, 1.2, 2.5]          # Minimize (0 for non-battery scenarios)
    }
    
    df = pd.DataFrame(data)
    
    # Calculate Total Net Cost (Cost - Revenue) for easy comparison
    df["Total Net Cost ($)"] = (
        df["Demand Charges ($)"] + 
        df["TOU Energy Charges ($)"] - 
        df["Grid Service Revenue ($)"]
    )

    # --- 2. High Level Metrics (The "Winner") ---
    st.divider()
    st.header("🏆 Recommended Strategy")
    
    # Identify best scenario (lowest Net Cost)
    best_scenario = df.loc[df["Total Net Cost ($)"].idxmin()]
    baseline = df.iloc[0]
    savings = baseline["Total Net Cost ($)"] - best_scenario["Total Net Cost ($)"]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Optimal Configuration", 
            value=best_scenario["Scenario"].split(". ")[1]
        )
    with col2:
        st.metric(
            label="Projected Monthly Net Cost", 
            value=f"${best_scenario['Total Net Cost ($)']:,.0f}",
            delta=f"-${savings:,.0f} vs Baseline",
            delta_color="inverse"
        )
    with col3:
        st.metric(
            label="Est. Battery Impact",
            value=f"{best_scenario['Battery Degradation (%)']}% / yr",
            help="Projected capacity fade based on cycling profile."
        )

    # --- 3. Detailed Data Table ---
    st.divider()
    st.subheader("Scenario Comparison Table")
    
    # REMOVED .background_gradient to fix the ImportError
    st.dataframe(
        df.style.format({
            "Demand Charges ($)": "${:,.0f}",
            "TOU Energy Charges ($)": "${:,.0f}",
            "Grid Service Revenue ($)": "${:,.0f}",
            "Total Net Cost ($)": "${:,.0f}",
            "Battery Degradation (%)": "{:.1f}%"
        }),
        use_container_width=True
    )

    # --- 4. Visualizations ---
    st.divider()
    st.header("📉 Financial Breakdown")
    
    tab1, tab2 = st.tabs(["Cost Stack Analysis", "Battery Health"])
    
    with tab1:
        st.markdown("Breakdown of costs and revenues by scenario.")
        
        # Reshape for stacked bar chart
        chart_df = df.melt(
            id_vars=["Scenario"], 
            value_vars=["Demand Charges ($)", "TOU Energy Charges ($)", "Grid Service Revenue ($)"],
            var_name="Category", 
            value_name="Amount ($)"
        )
        
        # Make revenue negative for visual stacking effect (Cost vs Revenue)
        # Note: Simple bar charts stack positive values. For Net impact, we might keep them distinct.
        # Here we just show the raw components.
        
        st.bar_chart(
            chart_df, 
            x="Scenario", 
            y="Amount ($)", 
            color="Category",
            stack=False # Grouped bars are often better for comparing components
        )
        
    with tab2:
        st.markdown("Projected annual battery health impact.")
        # Filter out scenarios without batteries for clean charting
        batt_df = df[df["Battery Degradation (%)"] > 0]
        
        if not batt_df.empty:
            st.bar_chart(
                batt_df,
                x="Scenario",
                y="Battery Degradation (%)",
                color="#FF4B4B" # Red color to signify 'damage/wear'
            )
        else:
            st.info("No scenarios with battery storage selected.")