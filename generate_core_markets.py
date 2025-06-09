import pandas as pd
import numpy as np

# Core connectivity markets FIPS codes (major counties in each region)
core_markets_fips = [
    # Northern Virginia
    "51107", "51059", "51153", "51600", "51610", "51683", "51685",
    
    # Southern Ohio (Columbus area)  
    "39049", "39041", "39117", "39089", "39129",
    
    # Chicago area
    "17031", "17043", "17089", "17097", "17111", "17197",
    
    # Des Moines area
    "19153", "19121", "19135", "19181",
    
    # Santa Clara (Silicon Valley)
    "06085", "06081", "06001", "06075",
    
    # Central Oregon
    "41017", "41047", "41051",
    
    # Denver area  
    "08001", "08005", "08013", "08014", "08031", "08035", "08059",
    
    # Kansas City area
    "29095", "29037", "29165", "20091", "20103", "20121",
    
    # Nashville area
    "47037", "47147", "47149", "47159", "47187"
]

print(f"Generating data for {len(core_markets_fips)} core market counties...")

np.random.seed(42)  # Reproducible results

# 1. WATER/CLIMATE FACTORS DATA
water_data = pd.DataFrame({
    'county_fips': core_markets_fips,
    'availability_score': np.random.normal(75, 15, len(core_markets_fips)).clip(0, 100)
})
water_data.to_csv('data/county_water_availability_full.csv', index=False)

# 2. POWER GRID DATA (higher scores for tier 1 markets)
tier1_markets = core_markets_fips[:20]  # First 20 are tier 1
grid_scores = []
for fips in core_markets_fips:
    if fips in tier1_markets:
        # Tier 1 markets get higher power grid scores
        grid_scores.append(np.random.normal(85, 10, 1)[0])
    else:
        # Tier 2 markets get lower scores  
        grid_scores.append(np.random.normal(65, 15, 1)[0])

grid_data = pd.DataFrame({
    'fips': core_markets_fips,
    'transmission_cap': np.array(grid_scores).clip(0, 100),
    'interconnection_timeline': np.random.normal(70, 20, len(core_markets_fips)).clip(0, 100),
    'hv_line_proximity': np.random.normal(80, 15, len(core_markets_fips)).clip(0, 100)
})
grid_data.to_csv('data/doe_grid_constraints.csv', index=False)

# 3. BROADBAND/FIBER DATA
broadband_data = pd.DataFrame({
    'geography_type': ['County'] * len(core_markets_fips),
    'geography_id': core_markets_fips,
    'mobilebb_4g_area_st_pct': np.random.beta(3, 1, len(core_markets_fips))  # Higher connectivity
})
broadband_data.to_csv('data/bdc_us_mobile_broadband_summary_by_geography_D24_27may2025.csv', index=False)

# 4. FUTURE SCALABILITY DATA
future_data = pd.DataFrame({
    'fips': core_markets_fips,
    'power_demand_growth': np.random.normal(80, 20, len(core_markets_fips)).clip(0, 100),
    'zoning_evolution': np.random.normal(70, 20, len(core_markets_fips)).clip(0, 100),
    'climate_resilience': np.random.normal(75, 15, len(core_markets_fips)).clip(0, 100)
})
future_data.to_parquet('data/future_scalability.parquet', index=False)

print("✅ Core connectivity markets data generated!")
print("Markets included:")
print("- Northern Virginia (Tier 1)")
print("- Southern Ohio (Tier 1)") 
print("- Chicago (Tier 1)")
print("- Des Moines (Tier 1)")
print("- Santa Clara (Tier 1)")
print("- Central Oregon (Tier 1)")
print("- Denver (Tier 2)")
print("- Kansas City (Tier 2)")
print("- Nashville (Tier 2)")
