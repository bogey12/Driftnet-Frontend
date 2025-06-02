'''
energy, regulatory, infra = st.tabs(["Energy", "Regulatory", "Infrastructure"])        
with energy:
    energy_categories = ["", 'Electricity Rates', 'Transmission Capacity', 'Grid Reliability', 'Marginal Emissions Rate', 'Energy Incentives', 'Power Quality', 'Power Outage Risk']
    selected_cat = st.selectbox('Energy', energy_categories)

with regulatory:
    regulatory_categories = ["", 'Permitting Ease', "Permitting Timeline", "Tax Incentives", "Environmental Restrictions", "Zoning Compatibility", "Local Government Support", "Building Code Complexity", "Land Use Restrictions"]
    selected_cat = st.selectbox('Regulatory', regulatory_categories)

with infra:
    infrastructure_categories = ["", 'Permitting Ease', "Permitting Timeline", "Tax Incentives", "Environmental Restrictions", "Zoning Compatibility", "Local Government Support", "Building Code Complexity", "Land Use Restrictions"]
    selected_cat = st.selectbox('Infrastructure', regulatory_categories)
'''