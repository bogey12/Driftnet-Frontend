import pandas as pd
import numpy as np
import geopandas as gpd
import json

def broadband_processing(df):
    # Convert 'year' to string for better handling in Altair
    df_county = df[df["geography_type"] == "County"]
    df_county['fips'] = df_county['geography_id'].astype(str).str.zfill(5)
    df_county['fiber_score'] = 100 * df_county['mobilebb_4g_area_st_pct'].fillna(0)
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

def load_score_data(
    grid_path: str,
    future_path: str,
    water_path: str,
    fiber_path: str,
    county_geojson_path: str = None
) -> pd.DataFrame:
    """
    Load and merge all score datasets into a master DataFrame.

    Parameters
    ----------
    grid_path : str
        Path to DOE grid constraints CSV.
    future_path : str
        Path to future scalability Parquet.
    water_path : str
        Path to county water availability CSV.
    fiber_path : str
        Path to broadband summary CSV.
    county_geojson_path : str, optional
        Path to county FIPS JSON, if needed elsewhere.

    Returns
    -------
    DataFrame
        A master DataFrame with all composite scores.
    """
    # Load new datasets
    df_grid = pd.read_csv(grid_path)[["fips", "transmission_cap", "interconnection_timeline", "hv_line_proximity"]]
    df_future = pd.read_parquet(future_path)[["fips", "power_demand_growth", "zoning_evolution", "climate_resilience"]]

    # Load original datasets
    df_water = water_processing(pd.read_csv(water_path))
    df_fiber = broadband_processing(pd.read_csv(fiber_path))

    # Generate dummy data
    df_land = gen_random_data(df_water, "land_score")
    df_zoning = gen_random_data(df_water, "zoning_score")
    df_power = gen_random_data(df_water, "power_score")

    # Ensure fips column formatting
    for df_ in [df_water, df_land, df_zoning, df_fiber, df_power, df_grid, df_future]:
        df_["fips"] = df_["fips"].astype(str).str.zfill(5)

    # Merge into master
    df_master = df_water[["fips","water_score"]]
    for df_ in [df_land, df_zoning, df_fiber, df_power, df_grid, df_future]:
        df_master = df_master.merge(df_, on="fips", how="outer")

    df_master = df_master.fillna(0)

    # Composite scores
    df_master["power_score"] = (
        df_master["transmission_cap"] * 0.4
        + df_master["interconnection_timeline"] * 0.3
        + df_master["hv_line_proximity"] * 0.3
    )
    df_master["future scalability_score"] = (
        df_master["power_demand_growth"] * 0.5
        + df_master["zoning_evolution"] * 0.3
        + df_master["climate_resilience"] * 0.2
    )

    # Rename and map to final schema
    df_master = df_master.rename(
        columns={
            "fiber_score": "fiber_score",
            "land_score": "land_score",
            "zoning_score": "regulations_score",
            "water_score": "climate factors_score"
        }
    )
    df_master["fips"] = df_master["fips"].astype(str).str.zfill(5)
    return df_master

def load_geo_data(
    blockgroup_path: str,
    county_fips_json: str
) -> tuple:
    """
    Load geographic data for plotting.

    Parameters
    ----------
    blockgroup_path : str
        Path to blockgroup GeoJSON.
    county_fips_json : str
        Path to county FIPS JSON.

    Returns
    -------
    tuple
        A tuple (blockgroup GeoDataFrame, county FIPS JSON dict).
    """
    blockgroup_gdf = gpd.read_file(blockgroup_path)
    with open(county_fips_json, 'r') as f:
        geofips_county_json = json.load(f)
    return blockgroup_gdf, geofips_county_json

if __name__ == "__main__":
    # Example usage
    df_master = load_score_data(
        grid_path="data/doe_grid_constraints.csv",
        future_path="data/future_scalability.parquet",
        water_path="data/county_water_availability_full.csv",
        fiber_path="data/bdc_us_mobile_broadband_summary_by_geography_D24_27may2025.csv"
    )

    blockgroup_gdf, geofips_county_json = load_geo_data(
        blockgroup_path="data/core_markets_blockgroup.geojson",
        county_fips_json="data/us_county_fips.json"
    )