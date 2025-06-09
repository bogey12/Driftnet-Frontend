import pandas as pd

# Create sample data
data = {
    'fips': ['01001', '01003', '01005', '01007', '01009'],
    'power_demand_growth': [85, 72, 91, 68, 88],
    'zoning_evolution': [80, 75, 89, 65, 83],
    'climate_resilience': [90, 78, 95, 70, 85]
}

df = pd.DataFrame(data)
df.to_parquet('data/future_scalability.parquet', index=False)
print("Parquet file updated!")