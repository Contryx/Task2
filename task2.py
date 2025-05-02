import base64
import streamlit as st
import pandas as pd
import plotly.express as px
import math

st.set_page_config(layout="wide")

#Load and background image
with open("212.jpg", "rb") as img_file:
    b64 = base64.b64encode(img_file.read()).decode()

st.markdown(
    f"""
    <style>
    .main {{
        transform: scale(0.95);
        transform-origin: 0 0;
        width: 100%;
        margin: 0 auto;
    }}
    .stApp {{
        background: url("data:image/jpg;base64,{b64}") no-repeat center center fixed;
        background-size: cover;
    }}
    section[data-testid="stSidebar"] {{
        background-color: rgba(255,255,255,0.8);
    }}
    .stPlotlyChart {{
        height: 250px !important;
        margin-bottom: 20px;
    }}
    .stPlotlyChart h3 {{
        font-size: 14px !important;
    }}
    .stAxis, .stLegend {{
        font-size: 10px !important;
    }}
    .reportview-container, 
    .main .block-container {{
        padding-top: 0px;
        padding-bottom: 0px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

#Load dataset
df = pd.read_csv('cleaned_global_water_consumption.csv')

#Title
st.markdown(
    "<h1 style='text-align: center; font-size: 25px;'>Global Water Consumption Dashboard</h1>",
    unsafe_allow_html=True
)

# Sidebar hint and filters
st.sidebar.markdown("**Hover over the data points on the charts to get more detailed information!**")
default_countries = ['China', 'India', 'Indonesia', 'Canada', 'Australia']
countries = st.sidebar.multiselect('Select Country', df['Country'].unique(), default=default_countries)
years = st.sidebar.slider('Select Year Range',
                          int(df['Year'].min()), int(df['Year'].max()),
                          (2010, 2014))

#Sector use sliders
ag_max = math.ceil(df['Agricultural Water Use (%)'].max())
hh_max = math.ceil(df['Household Water Use (%)'].max())
ind_max = math.ceil(df['Industrial Water Use (%)'].max())

agricultural_water_use = st.sidebar.slider(
    'Agricultural Water Use (%) Range',
    int(df['Agricultural Water Use (%)'].min()), ag_max,
    (int(df['Agricultural Water Use (%)'].min()), ag_max), step=1
)
household_water_use = st.sidebar.slider(
    'Household Water Use (%) Range',
    int(df['Household Water Use (%)'].min()), hh_max,
    (int(df['Household Water Use (%)'].min()), hh_max), step=1
)
industrial_water_use = st.sidebar.slider(
    'Industrial Water Use (%) Range',
    int(df['Industrial Water Use (%)'].min()), ind_max,
    (int(df['Industrial Water Use (%)'].min()), ind_max), step=1
)

#Filter dataset
filtered_df = df[
    (df['Country'].isin(countries)) &
    (df['Year'].between(years[0], years[1])) &
    (df['Agricultural Water Use (%)'].between(*agricultural_water_use)) &
    (df['Household Water Use (%)'].between(*household_water_use)) &
    (df['Industrial Water Use (%)'].between(*industrial_water_use))
]


#First Row
col1, col2 = st.columns([1, 1])

with col1:
    fig1 = px.bar(
        filtered_df,
        x='Year',
        y='Total Water Consumption (Billion Cubic Meters)',
        color='Country',
        text='Total Water Consumption (Billion Cubic Meters)',
        title="Total Water Consumption Over Time"
    )
    fig1.update_traces(texttemplate='%{text:.1f}', textposition='inside', marker=dict(line=dict(width=0)))
    fig1.update_layout(
        title_x=0.0,
        yaxis_title='Total Water Consumption',
        margin=dict(t=50, l=40, r=40, b=40),
        height=350,
        xaxis=dict(showgrid=False, title_font=dict(size=14), tickfont=dict(size=12)),
        yaxis=dict(showgrid=False, title_font=dict(size=14), tickfont=dict(size=12))
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    long_df = (
        filtered_df
        .groupby('Country', as_index=False)[[
            'Agricultural Water Use (%)',
            'Industrial Water Use (%)',
            'Household Water Use (%)'
        ]]
        .mean()
        .melt(id_vars='Country', var_name='Sector', value_name='Water Use (%)')
    )
    fig2 = px.bar(
        long_df,
        x='Country',
        y='Water Use (%)',
        color='Sector',
        barmode='stack',
        text='Water Use (%)',
        title="Water Use Breakdown by Sector"
    )
    fig2.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
    fig2.update_layout(
        title_x=0.0,
        margin=dict(t=50, l=40, r=40, b=40),
        height=350,
        xaxis=dict(showgrid=False, title_font=dict(size=14), tickfont=dict(size=12)),
        yaxis=dict(showgrid=False, title_font=dict(size=14), tickfont=dict(size=12))
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)


#Second row
col3, col4, col5 = st.columns([1, 1, 1])

with col3:
    filtered_df['Water Use Text'] = filtered_df['Per Capita Water Use (Liters per Day)'].map(lambda x: f"{x:.1f}")
    fig3 = px.bar(
        filtered_df,
        x='Year',
        y='Per Capita Water Use (Liters per Day)',
        color='Country',
        text='Water Use Text',
        title="Per Capita Water Use by Year"
    )
    fig3.update_traces(textposition='inside')
    fig3.update_layout(
        title_x=0.0,
        margin=dict(t=50, l=40, r=40, b=40),
        height=350,
        xaxis=dict(showgrid=False, title_font=dict(size=14), tickfont=dict(size=12)),
        yaxis=dict(showgrid=False, title_font=dict(size=14), tickfont=dict(size=12))
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    fig4 = px.scatter(
        filtered_df,
        x='Rainfall Impact (Annual Precipitation in mm)',
        y='Agricultural Water Use (%)',
        color='Country',
        title="Rainfall Impact vs Agricultural Water Use",
        hover_data={'Country': True, 'Year': True}
    )
    fig4.update_traces(marker=dict(size=10, opacity=0.7))
    fig4.update_layout(
        title_x=0.0,
        margin=dict(t=50, l=40, r=40, b=40),
        height=350,
        xaxis=dict(showgrid=True, gridcolor='lightgrey', title_font=dict(size=14), tickfont=dict(size=12)),
        yaxis=dict(showgrid=True, gridcolor='lightgrey', title_font=dict(size=14), tickfont=dict(size=12))
    )
    st.plotly_chart(fig4, use_container_width=True)

with col5:
    scarcity_counts = filtered_df['Water Scarcity Level'].value_counts()
    fig5 = px.pie(
        names=scarcity_counts.index,
        values=scarcity_counts.values,
        title="Water Scarcity Levels by Selected Countries"
    )
    fig5.update_traces(textinfo='percent', insidetextorientation='radial')
    fig5.update_layout(title_x=0.0, margin=dict(t=50, l=40, r=40, b=40), height=350)
    st.plotly_chart(fig5, use_container_width=True)

    high_count     = scarcity_counts.get('High', 0)
    moderate_count = scarcity_counts.get('Moderate', 0)
    low_count      = scarcity_counts.get('Low', 0)

    st.markdown(
        f"""
        <div style="text-align: right; margin-top: -1.5em; font-weight: bold;">
          High levels: {high_count}<br/>
          Moderate levels: {moderate_count}<br/>
          Low levels: {low_count}
        </div>
        """,
        unsafe_allow_html=True
    )
