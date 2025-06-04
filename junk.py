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

"""
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
"""