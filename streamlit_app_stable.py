#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import json
import numpy as np


#######################
# Page configuration
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)

#######################
# Data Processing
def broadband_processing(df):
    # Convert 'year' to string for better handling in Altair
    df_county = df[df["geography_type"] == "County"]
    df_county['fips'] = df_county['geography_id'].astype(str).str.zfill(5)
    return df_county

def water_processing(df):
    # Convert 'year' to string for better handling in Altair
    df['fips'] = df['county_fips'].astype(str).str.zfill(5)
    return df

def gen_random_data(df):
    N = len(df)

    # Create random data for dummy data
    new_df = pd.DataFrame({
        "fips": df['fips'],
        "Dummy": np.random.rand(N)
    })
    input_col = "Dummy"
    return new_df

#######################
# Load data
df_unemp = pd.read_csv('data/us_county_unemp.csv')
df_fixed_broadband = pd.read_csv("data/bdc_us_fixed_broadband_summary_by_geography_D24_27may2025.csv")
df_fixed_broadband = broadband_processing(df_fixed_broadband)
df_mobile_broadband = pd.read_csv("data/bdc_us_mobile_broadband_summary_by_geography_D24_27may2025.csv")
df_mobile_broadband = broadband_processing(df_mobile_broadband)

df_water = pd.read_csv("data/county_water_availability_full.csv")
df_water = water_processing(df_water)

random_df = gen_random_data(df_water)

with open('data/us_county_fips.json', 'r') as f:
    geofips_county_json = json.load(f)

#######################
# Plots

# Heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap

# Choropleth map
def get_data_by_selection(category, subcategory):
    # This function would typically filter the data based on user selections
    # For now, we will return the full dataset
    if category == "Fiber":
        if subcategory == "Fixed Broadband":
            df = df_fixed_broadband
            input_col = "speed_02_02"
            df = (
                df
                .groupby("fips", as_index=False)[input_col]
                .mean()
            )
        else:
            df = df_mobile_broadband
            input_col = "mobilebb_4g_area_st_pct"
        cmap = "viridis"
    elif category == "Water":
        if subcategory == "Water Availability":
            df = df_water
            input_col = "availability_score"
        else:
            df = df_water
            input_col = "availability_score" # Change when data is available
        cmap = "blues"
    elif category == "Land":
        df = random_df
        input_col = "Dummy"
        cmap = "earth"
    elif category == "Zoning":
        df = random_df
        input_col = "Dummy"
        cmap = "prgn"
    elif category == "Power":
        df = random_df
        input_col = "Dummy"
        cmap = "inferno"
    else:
        df = random_df
        input_col = "Dummy"
        cmap = "viridis"

    return df, input_col, cmap

def make_choropleth_county(input_df, input_col, input_label, geo_json, min_value, max_value, color_theme="Viridis"):
    choropleth = px.choropleth(input_df, geojson=geo_json, locations='fips', color=input_col,
                           color_continuous_scale=color_theme,
                           range_color=(min_value, max_value),
                           scope="usa",
                           labels={input_col:input_label}
                          )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

#######################
# User Requirements Summary Function
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

#######################
# Define tabs
maps, requirements, requirments_summary, results = st.tabs(["Map", "Requirements", "Requirements Summary", "Results"])

with maps:
    col = st.columns((1.5, 6.5), gap='medium')
    selected_sub_cat = None
    with col[0]:
        st.markdown('### Constraints Explorer')
        st.markdown('Visualize data for data center planning')
        main_categories = ["Power", "Water", "Land", "Fiber", "Zoning"]
        selected_cat = st.radio('Data Type', main_categories, index=1)
        if selected_cat == "Fiber":
            sub_categories = ["Fixed Broadband", "Mobile Broadband"]
            selected_sub_cat = st.selectbox('Select Broadband Type', sub_categories)
        elif selected_cat == "Zoning":
            sub_categories = ["Zoning Compatibility", "Permitting Ease", "Permitting Timeline", "Environmental Restrictions", "Building Code Complexity"]
            selected_sub_cat = st.selectbox('Select Zoning Type', sub_categories)
        elif selected_cat == "Power":
            sub_categories = ["Electricity Rates", "Transmission Capacity", "Grid Reliability", "Marginal Emissions Rate", "Energy Incentives", "Power Quality", "Power Outage Risk"]
            selected_sub_cat = st.selectbox('Select Power Type', sub_categories)
        elif selected_cat == "Water":
            sub_categories = ["Water Availability", "Water Quality", "Water Regulations"]
            selected_sub_cat = st.selectbox('Select Water Type', sub_categories)
        else:
            sub_categories = ["Land Availability", "Land Use Regulations", "Land Cost"]
            selected_sub_cat = st.selectbox('Select Land Type', sub_categories)

    with col[1]:
        df, input_col, cmap = get_data_by_selection(selected_cat, selected_sub_cat)
        constraints_name = selected_cat + " - " + selected_sub_cat if selected_sub_cat else selected_cat
        st.markdown("## " + constraints_name)
        if input_col == "Dummy":
            choropleth = make_choropleth_county(df, input_col, constraints_name + " (Fake Data)", geofips_county_json, 0, 1, color_theme=cmap)
        else:
            choropleth = make_choropleth_county(df, input_col, constraints_name, geofips_county_json, 0, df[input_col].max(), color_theme=cmap)
        st.plotly_chart(choropleth, use_container_width=True)

with requirements:
    st.header("Requirements")
    region = st.radio("Preferred Region", ["None", "West Coast", 'Northeast', 'Southwest', 'Midwest', 'Southeast'])
    st.markdown("#### Select Sites and Cities")
    city = st.text_input("Add specific cities or sites you'd like to consider", "None")
    st.markdown("#### Proximity Importance")
    proximity = st.slider("How important is proximity to your existing infrastructure or customer base? (scale of 0 - 100)", 0, 100, 50)
    st.markdown("#### Netowork Latency Importance")
    network_latency = st.radio(
        "How important is network latency for your workloads?",
        ["Not Important", "Somewhat Important", "Important", "Very Important"],
        index=2  # Default to "Important"
    )
    
    st.markdown("#### Data Center Type")
    data_center_type = st.radio("Select the type of data center", ["Enterprise", "Colocation", 'Hyperscaler', 'Cloud', 
                                                         'Edge', 'Micro', 'Managed', 'Crypto', "Mid-sized/Traditional"])
    st.markdown("#### Total Power Capacity (MW)")
    power_cap = st.slider("What is the total power capacity of your data center in MW?", 0, 100, 10)
    redundancy_levels = ["N (Basic)", "N+1 (Standard)", "2N (Full Redundancy)", "2N+1 (Enhanced)"]
    st.markdown("#### Redundancy Level")
    redundancy = st.selectbox('Select the required level of redundancy', redundancy_levels)
    st.markdown("#### Power Density")
    power_density = st.slider("Expected power density per rack (kW/rack)", 5, 50, 10)
    st.markdown("#### Cooling Method")
    cooling_method = st.radio("Select your preferred cooling method", ["Air Cooling", "Liquid Cooling", "Immersion Cooling", "Hybrid Cooling"])
    st.markdown("#### AI/ML Hardware Requirements")
    ai_ml_hardware = st.checkbox("Do you require specialized AI/ML hardware?")
    st.markdown("#### Workload Flexibility")
    st.markdown("##### Inflexible Workloads (0h)")
    inflexible_pct = st.slider(
        "What percentage of workloads must run at specific times (0h flexibility)?",
        min_value=0,
        max_value=100,
        value=17  # scaled from original 12/70 to sum to 100
    )

    st.markdown("##### Short-term Flexible (4h)")
    short_term_pct = st.slider(
        "What percentage of workloads can be shifted up to 4 hours?",
        min_value=0,
        max_value=100,
        value=43  # scaled from original 30/70 to sum to 100
    )

    st.markdown("##### Medium-term Flexible (12h)")
    medium_term_pct = st.slider(
        "What percentage of workloads can be shifted up to 12 hours?",
        min_value=0,
        max_value=100,
        value=17  # scaled from original 12/70 to sum to 100
    )

    st.markdown("##### Long-term Flexible (24h+)")
    long_term_pct = st.slider(
        "What percentage of workloads can be shifted by a day or more?",
        min_value=0,
        max_value=100,
        value=23  # scaled from original 16/70 to sum to 100
    )

    # Compute total
    total_pct = inflexible_pct + short_term_pct + medium_term_pct + long_term_pct
    st.markdown("##### Total Percentage")
    st.write(f"**{total_pct}%**")

    # Warn if the sliders do not sum to 100%
    if total_pct != 100:
        st.error("❌ The percentages must add up to 100%. Please adjust the sliders accordingly.")
    else:
        st.success("✅ The percentages add up to 100%!")
    
    st.markdown("#### Peak Usage Hours")
    peak_usage = st.radio(
        "When do you expect peak usage of your data center?",
        ["Morning (6 AM - 12 PM)", "Afternoon (12 PM - 6 PM)",
         "Evening (6 PM - 12 AM)", "Night (12 AM - 6 AM)"],
        index=1  # Default to Afternoon
    )
    
    st.markdown("#### Workload Mix")
    st.markdown("##### AI/ML Processing")
    ai_ml_pct = st.slider(
        "What percentage of workloads are dedicated to AI/ML processing?",
        min_value=0,
        max_value=100,
        value=30
    )

    st.markdown("##### Databases")
    databases_pct = st.slider(
        "What percentage of workloads are database workloads?",
        min_value=0,
        max_value=100,
        value=30
    )

    st.markdown("##### Web Services")
    web_services_pct = st.slider(
        "What percentage of workloads are web services?",
        min_value=0,
        max_value=100,
        value=20
    )

    st.markdown("##### Media/Streaming")
    media_streaming_pct = st.slider(
        "What percentage of workloads are media/streaming?",
        min_value=0,
        max_value=100,
        value=20
    )

    # Compute total
    total_pct = ai_ml_pct + databases_pct + web_services_pct + media_streaming_pct
    st.markdown("##### Total Percentage")
    st.write(f"**{total_pct}%**")

    # Validate that the sliders sum to 100%
    if total_pct != 100:
        st.error("❌ The percentages must add up to 100%. Please adjust the sliders accordingly.")
    else:
        st.success("✅ The percentages add up to 100%!")
    
    st.markdown("#### Latency Sensitivity")
    latency_sensitivity = st.selectbox(
        "How sensitive are your workloads to latency?",
        ["Low (Batch processing, backups)", 
         "Medium (Web services, databases)", 
         "High (Real-time applications, AI/ML processing)"],
        index=1  # Default to Medium
    )

    st.markdown("#### Seasonality")
    seasonality = st.selectbox(
        "How much does your workload vary throughout the year?",
        ["Low (Consistent usage year-round)",
         "Medium (Some seasonal peaks, e.g., holidays)", 
         "High (Significant seasonal variation, e.g., retail)"],
        index=0  # Default to Low
    )
    
    st.markdown("#### Preferred Renewable Energy")
    renewable_perc = st.slider(
        "Target percentage of renewable energy (preferred, not required)",
        min_value=0,
        max_value=100,
        value=50,  # Default to 50%
        step=1
    )

    importance_options = [
        "No Importance",
        "Low Importance",
        "Medium Importance",
        "High Importance",
        "Very Important"
    ]

    st.markdown("#### Energy System Characteristics")
    st.markdown("##### Cost Importance")
    cost_importance = st.radio(
        "Select how important cost is:",
        options=importance_options,
        index=2  # Default to "Medium Importance"
    )

    st.markdown("##### Reliability Importance")
    reliability_importance = st.radio(
        "Select how important reliability is:",
        options=importance_options,
        index=2
    )

    st.markdown("##### Sustainability Importance")
    sustainability_importance = st.radio(
        "Select how important sustainability is:",
        options=importance_options,
        index=2
    )

    col = st.columns((4, 4), gap='medium')
    with col[0]:
        st.markdown("#### Preferred Generation Sources")
        generation_sources = st.multiselect(
            "Select preferred generation sources",
            options=["Solar", "Wind", "Hydroelectric", "Geothermal", "Biomass", "Natural Gas", "Nuclear"],
            default=["Solar", "Wind"]
        )
    with col[1]:
        st.markdown("#### Preferred Storage Technologies")
        storage_technologies = st.multiselect(
            "Select preferred storage technologies",
            options=["Battery Storage", "Pumped Hydro", "Hydrogen", "Thermal Storage"],
            default=["Battery Storage"]
        )
    
    st.markdown("#### Water Usage Constraints")
    water_constraints = st.selectbox(
        "Select water usage constraints",
        options=["None", "Low Water Usage", "Moderate Water Usage", "High Water Usage"],
        index=0  # Default to "None"
    )

    st.markdown("#### Land Constraints")
    land_constraints = st.selectbox(
        "Select land constraints",
        options=["None", "Low (Prefer efficient use land use)", 
                 "Moderate (Significant land constraints)", 
                 "High (Minimal land footprint required)"],
        index=0  # Default to "None"
    )

    st.markdown("#### Custom Constraints")
    custom_constraints = st.text_area(
        "Add any additional constraints or requirements you have for your data center planning.",
        placeholder="e.g., 'Must be within 50 miles of existing infrastructure', 'Prefer urban locations', etc."
    )

with requirments_summary:
    display_results_summary_two_columns(
        region=region,
        city=city,
        proximity=proximity,
        network_latency=network_latency,
        latency_sensitivity=latency_sensitivity,
        peak_usage=peak_usage,
        seasonality=seasonality,
        data_center_type=data_center_type,
        power_cap=power_cap,
        redundancy=redundancy,
        power_density=power_density,
        cooling_method=cooling_method,
        ai_ml_hardware=ai_ml_hardware,
        inflexible_pct=inflexible_pct,
        ai_ml_pct=ai_ml_pct,
        renewable_perc=renewable_perc,
        cost_importance=cost_importance,
        reliability_importance=reliability_importance,
        sustainability_importance=sustainability_importance,
        generation_sources=generation_sources,
        storage_technologies=storage_technologies,
        water_constraints=water_constraints,
        land_constraints=land_constraints,
        custom_constraints=custom_constraints,
    )

with results:
    st.header("Performance Metrics")

    # --- Show three key metrics side by side ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Time Saved", value="8 months")
        st.caption("Estimated time saved in development and deployment")

    with col2:
        st.metric(label="Lifetime Cost Savings", value="$42.7 M")
        st.caption("Projected cost savings over 10-year lifetime")

    with col3:
        st.metric(label="Reliability", value="99.99 %")
        st.caption("Projected uptime based on location and infrastructure")


    st.markdown("---")  # horizontal rule to separate sections

    # ---------------------
    # Generation & Storage
    # ---------------------
    st.subheader("Generation and Storage Mix")

    # 1) Build two small DataFrames for the pie charts
    gen_data = pd.DataFrame({
        "Source": ["Solar", "Wind", "Hydro", "Geothermal", "Nuclear"],
        "Percentage": [45, 35, 10, 5, 5]
    })

    storage_data = pd.DataFrame({
        "Storage Type": ["Battery Storage", "Pumped Hydro", "Hydrogen", "Thermal Storage"],
        "Percentage": [60, 20, 10, 10]
    })

    # 2) Create pie charts with Plotly Express
    fig_gen = px.pie(
        gen_data,
        names="Source",
        values="Percentage",
        title="Generation Mix",
        hole=0.3  # optional: makes it a donut chart instead of a full pie
    )
    fig_storage = px.pie(
        storage_data,
        names="Storage Type",
        values="Percentage",
        title="Storage Systems",
        hole=0.3
    )

    # 3) Display them side by side
    col4, col5 = st.columns(2)
    with col4:
        st.plotly_chart(fig_gen, use_container_width=True)
    with col5:
        st.plotly_chart(fig_storage, use_container_width=True)


    st.markdown("---")  # separate again

    # ----------------------
    # System Characteristics
    # ----------------------
    st.subheader("System Characteristics")

    # We can show each as a small metric
    col6, col7, col8 = st.columns(3)
    with col6:
        st.metric(label="Reliability", value="99.99 %")
    with col7:
        st.metric(label="Cost Efficiency", value="$0.052 / kWh")
        st.caption("Levelized cost per kWh")
    with col8:
        st.metric(label="Renewable %", value="95 %")
        st.caption("Of total generation")

    # If you also want to show “Annual uptime” as text under the metrics:
    st.markdown("*Annual uptime based on projected operations and maintenance assumptions*")