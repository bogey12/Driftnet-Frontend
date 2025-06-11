import plotly.express as px
import numpy as np

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

def get_cmap(max_priority_col):
    if max_priority_col == "climate factors_score":
        return "Blues"
    elif max_priority_col == "land_score":
        return "Greens"
    elif max_priority_col == "regulations_score":
        return "Purples"
    elif max_priority_col == "fiber_score":
        return "Viridis"
    elif max_priority_col == "power_score":
        return "Inferno"
    elif max_priority_col == "future scalability_score":
        return "Teal"
    else:
        return "Viridis"

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
    # Use color_val which is set by the checkbox logic above
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

def make_zoomed_choropleth(df_marked, max_priority, county_geojson, region_name, core_market_fips_dict, color_theme="Viridis"):
    # Get FIPS list for selected region
    region_fips = core_market_fips_dict[region_name]
    
    # Filter dataframe to only selected region's FIPS
    df_filtered = df_marked[df_marked["fips"].isin(region_fips)]
    
    # Plot the choropleth without `scope='usa'` so that it zooms to selected region
    choropleth = px.choropleth(
        df_filtered,
        geojson=county_geojson,
        locations="fips",
        color="color_val",
        color_continuous_scale=color_theme,
        range_color=(0, 100),
        labels={"color_val": f"{max_priority}"},
    )
    
    choropleth.update_geos(
        fitbounds="locations",  # automatically zoom to the included counties
        #visible=False           # remove base map (optional)
    )
    
    choropleth.update_layout(
        title=f"{region_name} - {max_priority} Score",
        template='plotly',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=30, b=0),
        height=500
    )
    return choropleth

def census_blockgroup_choropleth(gdf, max_priority, core_market, cmap, thresholds, core_market_fips_dict):
    # Get rows of the core market
    columb_gdf_proj = gdf[gdf['statecounty_fips'].isin(core_market_fips_dict[core_market])]
    columb_gdf_proj = filter_master_df(columb_gdf_proj, thresholds)
    columb_gdf_proj['color_val'] = columb_gdf_proj[max_priority] * columb_gdf_proj['passes']
    # Clean invalid geometries
    columb_gdf_proj = columb_gdf_proj.to_crs(epsg=4326)
    #st.markdown(f"### {len(columb_gdf_proj)}")

    # Use projected centroid and convert back to EPSG:4326
    center = {
        "lat": columb_gdf_proj.geometry.centroid.to_crs(epsg=4326).y.mean(),
        "lon": columb_gdf_proj.geometry.centroid.to_crs(epsg=4326).x.mean()
    }

    # Use new choropleth_map function
    fig = px.choropleth_map(
        columb_gdf_proj,
        geojson=columb_gdf_proj.__geo_interface__,
        locations=columb_gdf_proj.index,
        color="color_val",
        color_continuous_scale=cmap,
        zoom=9,
        center=center,
        opacity=0.6,
        labels={"color_val": f"{max_priority}"}
    )

    fig.update_layout(
        template='plotly',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=500
    )
    return fig