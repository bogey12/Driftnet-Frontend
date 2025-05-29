#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import json


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
# Load data
df_unemp = pd.read_csv('data/us-unemployment-2010-2019.csv')
geofips_county_json = json.load('data/us-population-geofips-county.csv')


#######################
# Sidebar
with st.sidebar:
    st.title('🏂 US Population Dashboard')

    #energy_categories = ['Electricity Rates', 'Transmission Capacity', 'Grid Reliability', 'Marginal Emissions Rate', 'Energy Incentives', 'Power Quality', 'Power Outage Risk']
    #selected_energy = st.selectbox('Energy data', energy_categories)
    #st.write('Energy constraints')
    #option_1 = st.checkbox('Electricity ')
    #option_2 = st.checkbox('final velocity (v)')
    #option_3 = st.checkbox('acceleration (a)')
    #option_4 = st.checkbox('time (t)')



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
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="USA-states",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(df_selected_year.population)),
                               scope="usa",
                               labels={'population':'Population'}
                              )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

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
# Dashboard Main Panel
col = st.columns((1.5, 6.5), gap='medium')

with col[0]:
    st.markdown('TEST HERE')

with col[1]:
    st.markdown('#### Total Population')

    choropleth = make_choropleth_county(df_unemp, 'unemp', 'unemployment rate', geofips_county_json, 0, 12)
    st.plotly_chart(choropleth, use_container_width=True)
