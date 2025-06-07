#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import json
import numpy as np
#import folium
#from streamlit_folium import st_folium



#######################
# Page configuration
st.set_page_config(
    page_title="US Data Center Constraints Explorer",
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
    df_county['fibre_score'] = 100 * df_county['mobilebb_4g_area_st_pct'].fillna(0)
    return df_county

def water_processing(df):
    # Convert 'year' to string for better handling in Altair
    df['fips'] = df['county_fips'].astype(str).str.zfill(5)
    df['water_score'] = df['availability_score']
    return df

def gen_random_data(df, col_name):
    N = len(df)
    # Create random data for dummy data
    new_df = pd.DataFrame({
        "fips": df['fips'],
        col_name: 100 * np.random.rand(N)
    })
    return new_df

@st.cache_data
def load_score_data():
    # Replace file paths & column names with your actual CSV/Parquet/etc. files
    df_water = water_processing(pd.read_csv("data/county_water_availability_full.csv")) # fips, water_score
    df_land = gen_random_data(df_water, "land_score")    # fips, land_score
    df_zoning = gen_random_data(df_water, "zoning_score") # fips, zoning_score
    df_fiber = broadband_processing(pd.read_csv("data/bdc_us_mobile_broadband_summary_by_geography_D24_27may2025.csv"))   # fips, fiber_score
    df_power = gen_random_data(df_water, "power_score")  # fips, power_score
    return df_water, df_land, df_zoning, df_fiber, df_power

#######################
# Load data
df_master = pd.read_csv("testdata/county_scores.csv")
df_master["fips"] = df_master["fips"].astype(str).str.zfill(5)
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

def make_choropleth_threshold(df_marked, max_priority, county_geojson, color_theme="Viridis"):
    df_marked["color_val"] = df_marked["passes"] * df_marked[max_priority]

    # Pass 'color_val' into your choropleth.  Rows with color_val=0 will appear unlit.
    choropleth = px.choropleth(
        df_marked,
        geojson=county_geojson,
        locations="fips",
        color="color_val",
        color_continuous_scale=color_theme,
        range_color=(0, 100),
        scope="usa",
        labels={"color_val": f"{max_priority}"},
    )
    choropleth.update_layout(
        template='plotly',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=500
    )
    return choropleth

def make_folium_map(df, geojson_path, colormap="Viridis", key_on="feature.properties.GEO_ID"):
    """
    df: DataFrame with 'fips' and 'color_val' columns
    geojson_path: path to your counties GeoJSON
    key_on: how to match GeoJSON features to df['fips'] (often 'feature.properties.GEOID')
    """
    # Center roughly on contiguous US:
    m = folium.Map(location=[37.8, -96], zoom_start=4, tiles="CartoDB dark_matter")

    folium.Choropleth(
        geo_data=geojson_path,
        name="choropleth",
        data=df,
        columns=["fips", "color_val"],
        key_on=key_on,
        fill_color=colormap,         # any built‐in color palette (YlOrRd, Viridis, etc.)
        fill_opacity=0.7,
        line_opacity=0.2,
        nan_fill_color="lightgrey",   # <— counties with NaN get grey
        legend_name="Priority Score",
        highlight=True
    ).add_to(m)

    # Add a tooltip that shows FIPS and color_val on hover
    folium.GeoJson(
        geojson_path,
        style_function=lambda feature: {
            "fillOpacity": 0,
            "color": "transparent"
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["GEO_ID"],  # or whatever the property is in your GeoJSON
            aliases=["FIPS:"],
            labels=True,
            sticky=False
        )
    ).add_to(m)

    return m

def get_cmap(max_priority_col):
    """
    Return a color map based on the max_priority_col.
    This is used to set the color intensity of the choropleth map.
    """
    if max_priority_col == "water_score":
        return "Blues"
    elif max_priority_col == "land_score":
        return "Greens"
    elif max_priority_col == "zoning_score":
        return "Purples"
    elif max_priority_col == "fiber_score":
        return "Viridis"
    elif max_priority_col == "power_score":
        return "Inferno"
    else:
        return "Viridis"

def filter_master_df(df, thresholds: dict):
    """
    Return a new DataFrame in which each 'fips' row passes
    ALL of the thresholds in the dictionary.
    thresholds: {"water_score": 80, "land_score": 70, ...}
    """
    df["passes"] = 1

    for col, min_val in thresholds.items():
        # Any row where col < min_val (or is NaN) should be marked 0
        mask_fails = df[col].fillna(-1) < min_val
        df.loc[mask_fails, "passes"] = np.nan
    return df

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
        all_categories = ["Water", "Land", "Regulations", "Fiber", "Power"]
        st.markdown("1) Select categories to filter (you can pick 1–5)")
        selected_cats = st.multiselect(
            "",
            options=all_categories
        )

        if not selected_cats:
            st.warning("▶️ Pick at least one category above to continue.")
            st.stop()

        # 4b) For each chosen category, ask for a minimum‐score:
        min_thresholds = {}  # e.g. {"Water": 80, "Land": 70, ...}

        st.markdown("2) For each selected category, set a minimum score (0–100)")

        for cat in selected_cats:
            # We know our DataFrames had columns named "<cat>_score"
            col_name = f"{cat.lower()}_score"
            # Provide a slider or number_input for the user
            min_val = st.slider(
                label=f"Minimum {cat} score",
                min_value=0,
                max_value=100,
                value=0,               # default
                key=f"min_{col_name}"
            )
            min_thresholds[col_name] = min_val
        st.markdown("3) Choose a category as Max Priority")
        max_priority = st.selectbox(
            "Max Priority ➤",
            options=selected_cats,
            index=0
        )
        max_priority_col = f"{max_priority.lower()}_score"
        df_for_map = filter_master_df(df_master, min_thresholds)
        cmap = get_cmap(max_priority_col)

    with col[1]:
        st.markdown(f"### {max_priority} Score")
        #st.markdown(f"### Water Availability")
        choro = make_choropleth_threshold(df_for_map, max_priority_col, geofips_county_json, cmap)
        st.plotly_chart(choro, use_container_width=True)
        #df_for_map['color_val'] = df_for_map[max_priority_col] * df_for_map['passes']
        #county_map = make_folium_map(df_for_map, "data/us_county_fips.json", cmap)
        #st_data = st_folium(county_map, width="100%", height=600)

with requirements:
    st.header("Requirements")
    region = st.radio("Preferred Region", ["None", "West Coast", 'Northeast', 'Southwest', 'Midwest', 'Southeast'])
    st.markdown("#### Select Sites and Cities")
    city = st.text_input("Add specific cities or sites you'd like to consider", "None")
    st.markdown("#### Proximity Importance")
    proximity = st.slider("How important is proximity to your existing infrastructure or customer base? (scale of 0 - 100)", 0, 100, 50)
    st.markdown("#### Network Latency Importance")
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





    

