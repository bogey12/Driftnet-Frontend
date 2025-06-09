import pandas as pd

try:
    df = pd.read_csv("data/doe_grid_constraints.csv")
    print("CSV Columns:", df.columns.tolist())
except Exception as e:
    print("ERROR:", e)

try:
    df = pd.read_parquet("data/future_scalability.parquet")
    print("Parquet Columns:", df.columns.tolist())
except Exception as e:
    print("ERROR:", e)

#with open("data/doe_grid_constraints.csv", "w") as f:
#    f.write("fips,transmission_cap,interconnection_timeline,hv_line_proximity\n")

#with open("data/doe_grid_constraints.csv", "w") as f:
#    f.write("fips,transmission_cap,interconnection_timeline,hv_line_proximity\n")

import pandas as pd
import numpy as np
import json

# Load all FIPS codes from your geojson or another file
with open('data/us_county_fips.json', 'r') as f:
    geojson = json.load(f)
all_fips = [feature['properties']['GEO_ID'][-5:] for feature in geojson['features']]

np.random.seed(42)

# Water/Climate Factors
pd.DataFrame({
    'county_fips': all_fips,
    'availability_score': np.random.normal(75, 15, len(all_fips)).clip(0, 100)
}).to_csv('data/county_water_availability_full.csv', index=False)

# Power Grid
pd.DataFrame({
    'fips': all_fips,
    'transmission_cap': np.random.normal(80, 10, len(all_fips)).clip(0, 100),
    'interconnection_timeline': np.random.normal(70, 20, len(all_fips)).clip(0, 100),
    'hv_line_proximity': np.random.normal(80, 15, len(all_fips)).clip(0, 100)
}).to_csv('data/doe_grid_constraints.csv', index=False)

# Broadband/Fiber
pd.DataFrame({
    'geography_type': ['County']*len(all_fips),
    'geography_id': all_fips,
    'mobilebb_4g_area_st_pct': np.random.beta(3, 1, len(all_fips))
}).to_csv('data/bdc_us_mobile_broadband_summary_by_geography_D24_27may2025.csv', index=False)

# Future Scalability
pd.DataFrame({
    'fips': all_fips,
    'power_demand_growth': np.random.normal(80, 20, len(all_fips)).clip(0, 100),
    'zoning_evolution': np.random.normal(70, 20, len(all_fips)).clip(0, 100),
    'climate_resilience': np.random.normal(75, 15, len(all_fips)).clip(0, 100)
}).to_parquet('data/future_scalability.parquet', index=False)
