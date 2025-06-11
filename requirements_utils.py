import streamlit as st
import numpy as np

# --- 1. Region & Site ---
def render_region_site():
    st.subheader("Region & Site")
    region = st.radio(
        "Preferred Region",
        ["None", "West Coast", "Northeast", "Southwest", "Midwest", "Southeast"]
    )
    city = st.text_input(
        "Add specific cities or sites you'd like to consider",
        "None"
    )
    return region, city

# --- 2. Infrastructure Importance ---
def render_infrastructure_importance():
    st.subheader("Infrastructure Importance")
    proximity = st.slider(
        "How important is proximity to your existing infrastructure or customer base? (0–100)",
        0, 100, 50
    )
    network_latency = st.radio(
        "How important is network latency for your workloads?",
        ["Not Important", "Somewhat Important", "Important", "Very Important"],
        index=2
    )
    return proximity, network_latency

# --- 3. Data Center Specifications ---
def render_data_center_specs():
    st.subheader("Data Center Specifications")
    data_center_type = st.radio(
        "Select the type of data center",
        ["Enterprise", "Colocation", "Hyperscaler", "Cloud",
         "Edge", "Micro", "Managed", "Crypto", "Mid-sized/Traditional"]
    )
    power_cap = st.slider(
        "What is the total power capacity of your data center in MW?",
        0, 100, 10
    )
    redundancy = st.selectbox(
        "Select the required level of redundancy",
        ["N (Basic)", "N+1 (Standard)", "2N (Full Redundancy)", "2N+1 (Enhanced)"]
    )
    power_density = st.slider(
        "Expected power density per rack (kW/rack)",
        5, 50, 10
    )
    cooling_method = st.radio(
        "Select your preferred cooling method",
        ["Air Cooling", "Liquid Cooling", "Immersion Cooling", "Hybrid Cooling"]
    )
    ai_ml_hardware = st.checkbox("Do you require specialized AI/ML hardware?")
    return data_center_type, power_cap, redundancy, power_density, cooling_method, ai_ml_hardware

# --- 4. Workload Flexibility ---
def render_workload_flexibility():
    st.subheader("Workload Flexibility")
    inflexible_pct = st.slider(
        "What percentage of workloads must run at specific times (0h flexibility)?",
        0, 100, 17
    )
    short_term_pct = st.slider(
        "What percentage of workloads can be shifted up to 4 hours?",
        0, 100, 43
    )
    medium_term_pct = st.slider(
        "What percentage of workloads can be shifted up to 12 hours?",
        0, 100, 17
    )
    long_term_pct = st.slider(
        "What percentage of workloads can be shifted by a day or more?",
        0, 100, 23
    )
    total_pct = inflexible_pct + short_term_pct + medium_term_pct + long_term_pct
    st.markdown("**Total: {}%**".format(total_pct))
    if total_pct != 100:
        st.error("❌ The percentages must add up to 100%. Please adjust the sliders accordingly.")
    else:
        st.success("✅ The percentages add up to 100%!")
    return inflexible_pct, short_term_pct, medium_term_pct, long_term_pct

# --- 5. Peak Hours, Latency & Seasonality ---
def render_timing_and_sensitivity():
    st.subheader("Timing & Sensitivity")
    peak_usage = st.radio(
        "When do you expect peak usage of your data center?",
        ["Morning (6 AM - 12 PM)", "Afternoon (12 PM - 6 PM)",
         "Evening (6 PM - 12 AM)", "Night (12 AM - 6 AM)"],
        index=1
    )
    latency_sensitivity = st.selectbox(
        "How sensitive are your workloads to latency?",
        ["Low (Batch processing, backups)",
         "Medium (Web services, databases)",
         "High (Real-time applications, AI/ML processing)"],
        index=1
    )
    seasonality = st.selectbox(
        "How much does your workload vary throughout the year?",
        ["Low (Consistent usage year-round)",
         "Medium (Some seasonal peaks, e.g., holidays)",
         "High (Significant seasonal variation, e.g., retail)"],
        index=0
    )
    return peak_usage, latency_sensitivity, seasonality

# --- 6. Workload Mix ---
def render_workload_mix():
    st.subheader("Workload Mix")
    ai_ml_pct = st.slider("Percentage AI/ML processing", 0, 100, 30)
    databases_pct = st.slider("Percentage databases", 0, 100, 30)
    web_services_pct = st.slider("Percentage web services", 0, 100, 20)
    media_streaming_pct = st.slider("Percentage media/streaming", 0, 100, 20)
    total = ai_ml_pct + databases_pct + web_services_pct + media_streaming_pct
    st.markdown("**Total: {}%**".format(total))
    if total != 100:
        st.error("❌ The percentages must add up to 100%.")
    else:
        st.success("✅ The percentages add up to 100%!")
    return ai_ml_pct, databases_pct, web_services_pct, media_streaming_pct

# --- 7. Renewables & Importance ---
def render_renewables_and_importance():
    st.subheader("Renewables & Priorities")
    renewable_perc = st.slider("Target renewable energy (%)", 0, 100, 50)
    importance_options = ["No Importance","Low Importance","Medium Importance","High Importance","Very Important"]
    cost_importance = st.radio("Cost importance", importance_options, index=2)
    reliability_importance = st.radio("Reliability importance", importance_options, index=2)
    sustainability_importance = st.radio("Sustainability importance", importance_options, index=2)
    return renewable_perc, cost_importance, reliability_importance, sustainability_importance

# --- 8. Generation & Storage Preferences ---
def render_generation_storage():
    st.subheader("Generation & Storage")
    generation_sources = st.multiselect("Select preferred generation sources",
        ["Solar","Wind","Hydroelectric","Geothermal","Biomass","Natural Gas","Nuclear"],
        default=["Solar","Wind"])
    storage_technologies = st.multiselect("Select preferred storage technologies",
        ["Battery Storage","Pumped Hydro","Hydrogen","Thermal Storage"],
        default=["Battery Storage"])
    return generation_sources, storage_technologies

# --- 9. Site Constraints ---
def render_site_constraints():
    st.subheader("Site Constraints")
    water_constraints = st.selectbox("Water usage constraints",
        ["None","Low Water Usage","Moderate Water Usage","High Water Usage"], index=0)
    land_constraints = st.selectbox("Land constraints",
        ["None","Low","Moderate","High"], index=0)
    custom_constraints = st.text_area("Custom constraints", "")
    return water_constraints, land_constraints, custom_constraints

def display_results_summary_two_columns(
    region,
    city,
    proximity,
    network_latency,
    latency_sensitivity,
    peak_usage,
    seasonality,
    data_center_type,
    power_cap,
    redundancy,
    power_density,
    cooling_method,
    ai_ml_hardware,
    inflexible_pct,
    ai_ml_pct,
    renewable_perc,
    cost_importance,
    reliability_importance,
    sustainability_importance,
    generation_sources,
    storage_technologies,
    water_constraints,
    land_constraints,
    custom_constraints=None,
):
    st.header("Results Summary")
    col1, col2 = st.columns(2)

    # Left Column
    with col1:
        st.subheader("Region & Site")
        st.markdown(f"- **Preferred Region:** {region}")
        st.markdown(f"- **Selected City/Site:** {city}")

        st.subheader("Priorities & Sensitivities")
        st.markdown(f"- **Proximity Importance (0–100):** {proximity}")
        st.markdown(f"- **Network Latency Importance:** {network_latency}")
        st.markdown(f"- **Latency Sensitivity:** {latency_sensitivity}")
        st.markdown(f"- **Peak Usage Hours:** {peak_usage}")
        st.markdown(f"- **Seasonality:** {seasonality}")

        st.subheader("Data Center Specifications")
        st.markdown(f"- **Type:** {data_center_type}")
        st.markdown(f"- **Power Capacity:** {power_cap} MW")
        st.markdown(f"- **Redundancy Level:** {redundancy}")

    # Right Column
    with col2:
        st.subheader("Data Center Specifications (cont’d)")
        st.markdown(f"- **Power Density:** {power_density} kW/rack")
        st.markdown(f"- **Cooling Method:** {cooling_method}")
        st.markdown(f"- **AI/ML Hardware Required:** {'Yes' if ai_ml_hardware else 'No'}")

        st.subheader("Workload & Flexibility")
        st.markdown(f"- **Inflexible Workloads (0h):** {inflexible_pct}%")
        st.markdown(f"- **AI/ML Workload %:** {ai_ml_pct}%")

        st.subheader("Renewables & Goals")
        st.markdown(f"- **Renewable Energy Target:** {renewable_perc}%")

    st.markdown("---")
    st.subheader("Energy System Characteristics")
    col3, col4 = st.columns(2)

    # Energy System Left
    with col3:
        st.markdown(f"- **Cost Importance:** {cost_importance}")
        st.markdown(f"- **Reliability Importance:** {reliability_importance}")
        st.markdown(f"- **Sustainability Importance:** {sustainability_importance}")

    # Energy System Right
    with col4:
        st.markdown(f"- **Gen. Sources:** {', '.join(generation_sources)}")
        st.markdown(f"- **Storage Techs:** {', '.join(storage_technologies)}")
        st.markdown(f"- **Water Usage Constraints:** {water_constraints}")
        st.markdown(f"- **Land Constraints:** {land_constraints}")
        st.markdown(f"- **Custom Constraints:** {custom_constraints or 'None'}")

if __name__ == "__main__":
    # --- Main requirements tab ---
    st.header("Requirements")
    region, city = render_region_site()
    proximity, network_latency = render_infrastructure_importance()
    data_center_type, power_cap, redundancy, power_density, cooling_method, ai_ml_hardware = \
        render_data_center_specs()
    inflexible_pct, short_term_pct, medium_term_pct, long_term_pct = render_workload_flexibility()
    peak_usage, latency_sensitivity, seasonality = render_timing_and_sensitivity()
    ai_ml_pct, databases_pct, web_services_pct, media_streaming_pct = render_workload_mix()
    renewable_perc, cost_importance, reliability_importance, sustainability_importance = \
        render_renewables_and_importance()
    generation_sources, storage_technologies = render_generation_storage()
    water_constraints, land_constraints, custom_constraints = render_site_constraints()
