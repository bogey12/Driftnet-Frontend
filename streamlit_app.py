#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import numpy as np

# Import our custom modules
from config import CORE_MARKET_FIPS_DICT, PAGE_SETTINGS, ALT_THEME

from data_processing import (
    load_score_data,
    load_geo_data,
)

from requirements_utils import (
    render_region_site,
    render_infrastructure_importance,
    render_data_center_specs,
    render_workload_flexibility,
    render_timing_and_sensitivity,
    render_workload_mix,
    render_renewables_and_importance,
    render_generation_storage,
    render_site_constraints,
    display_results_summary_two_columns
)

from plotting import (
    filter_master_df,
    get_cmap,
    census_blockgroup_choropleth,
    make_choropleth_threshold,
    get_selected_ts, filter_intervals, plot_lmp_map
)

from constraint_utils import (
    render_power_constraints,
    render_land_constraints,
    render_climate_constraints,
    render_fiber_constraints,
    render_future_constraints,
    render_regulatory_constraints,
)


# 1) Page config
st.set_page_config(**PAGE_SETTINGS)
alt.themes.enable(ALT_THEME)

# 2) Load and inject CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#######################
# Load data (wrapper functions with caching)
@st.cache_data
def get_score_data(
    grid_path: str,
    future_path: str,
    water_path: str,
    fiber_path: str
):
    return load_score_data(
        grid_path=grid_path,
        future_path=future_path,
        water_path=water_path,
        fiber_path=fiber_path
    )

@st.cache_data
def get_geo_data(
    blockgroup_path: str,
    county_fips_json: str
):
    return load_geo_data(
        blockgroup_path=blockgroup_path,
        county_fips_json=county_fips_json
    )

@st.cache_data
def load_lmp(lmp_path: str):
    # adjust path if needed
    return pd.read_parquet(lmp_path)

# 2) Then use those cached wrappers in your main code
df_master = get_score_data(
    grid_path="data/doe_grid_constraints.csv",
    future_path="data/future_scalability.parquet",
    water_path="data/county_water_availability_full.csv",
    fiber_path="data/bdc_us_mobile_broadband_summary_by_geography_D24_27may2025.csv"
)

blockgroup_gdf, geofips_county_json = get_geo_data(
    blockgroup_path="data/core_markets_blockgroup.geojson",
    county_fips_json="data/us_county_fips.json"
)

df_lmp = load_lmp(lmp_path="data/gridstatus_lmp_samples.parquet")

#######################
# Define tabs
maps, requirements, requirments_summary, results = st.tabs(["Map", "Requirements", "Requirements Summary", "Results"])

with maps:
    col = st.columns((1.5, 6.5), gap='medium')
    selected_sub_cat = None
    with col[0]:
        st.markdown('### Constraints Explorer')
        st.markdown('Visualize data for data center planning')
        #all_categories = ["Water", "Land", "Regulations", "Fiber", "Power"]
        show_core_only = st.checkbox("Show core connectivity markets only", value=False)
        if show_core_only:
            select_core_market = st.selectbox(
                "Select Core Market",
                options=list(CORE_MARKET_FIPS_DICT.keys()),
                index=0  # Default to first option
            )
        all_categories = ["Power", "Fiber", "Land", "Regulations", "Climate Factors", "Future Scalability"]
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
        show_grid_lmp = False
        for cat in selected_cats:
            col_name = f"{cat.lower()}_score"
            if cat == "Power":
                show_grid_lmp = st.checkbox("Show Grid LMP", value=False, help="Display the local grid's LMP (Locational Marginal Price) for power costs.")
            
            # ADD CATEGORY DESCRIPTIONS
            render_map = {
                "Power": render_power_constraints,
                "Land": render_land_constraints,
                "Climate Factors": render_climate_constraints,
                "Fiber": render_fiber_constraints,
                "Future Scalability": render_future_constraints,
                "Regulations": render_regulatory_constraints,
            }

            if cat in render_map:
                cat_res = render_map[cat]()
                if cat_res and "overall_score" in cat_res:
                    min_thresholds[col_name] = cat_res["overall_score"]
            
            min_val = st.slider(
                label=f"Minimum {cat} score",
                min_value=0,
                max_value=100,
                value=0,
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
        
        if show_core_only:
            # Set color_val to NaN for non-core counties (they will appear white)
            all_fips = [fips for zips in CORE_MARKET_FIPS_DICT.values() for fips in zips]
            df_for_map['color_val'] = np.where(
                df_for_map['fips'].isin(all_fips),
                df_for_map[max_priority_col] * df_for_map['passes'],
                np.nan
            )

        else:
            df_for_map['color_val'] = df_for_map[max_priority_col] * df_for_map['passes']
        cmap = get_cmap(max_priority_col)

    with col[1]:
        st.markdown(f"### {max_priority} Score")
        if show_core_only:
            choro = census_blockgroup_choropleth(blockgroup_gdf, max_priority_col, select_core_market, cmap, min_thresholds, CORE_MARKET_FIPS_DICT)
        elif show_grid_lmp == True:
            selected_date = st.date_input("Date", value=pd.to_datetime("2023-06-01").date())
            selected_hour = st.slider("Hour (UTC)", 0, 23, 0)
            selected_ts = get_selected_ts(selected_date, selected_hour)
            hourly = filter_intervals(df_lmp, selected_ts)
            if hourly.empty:
                st.warning(f"No data for {selected_ts.isoformat()}")
            else:
                st.subheader(f"LMPs for Interval Containing {selected_ts.isoformat()}")
                choro = plot_lmp_map(
                    hourly,
                    title=f"LMPs at {selected_ts.isoformat()}"
                )
        else:
            choro = make_choropleth_threshold(df_for_map, max_priority_col, geofips_county_json, cmap)
        st.plotly_chart(choro, use_container_width=True)

with requirements:
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