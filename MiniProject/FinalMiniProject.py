#!/usr/bin/env python
# coding: utf-8

# In[19]:

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import urllib.request
import os

# Function to download the file from GitHub
def download_file(url, save_path):
    if not os.path.exists(save_path):
        urllib.request.urlretrieve(url, save_path)

# Define file URLs
geojson_url = 'https://raw.githubusercontent.com/NikitaTheMesh/My-First_Streamlit/main/MiniProject/json/georef-switzerland-kanton.geojson'
conventional_csv_url = 'https://raw.githubusercontent.com/NikitaTheMesh/My-First_Streamlit/main/MiniProject/data/conventional_power_plants_EU_filtered.csv'
renewable_csv_url = 'https://raw.githubusercontent.com/NikitaTheMesh/My-First_Streamlit/main/MiniProject/data/renewable_power_plants_CH.csv'
conversion_py_url = 'https://raw.githubusercontent.com/NikitaTheMesh/My-First_Streamlit/main/MiniProject/conversion/City_To_Kanton_Conversion.py'

# Define local file paths
geojson_path = 'georef-switzerland-kanton.geojson'
conventional_csv_path = 'conventional_power_plants_EU_filtered.csv'
renewable_csv_path = 'renewable_power_plants_CH.csv'
conversion_py_path = 'City_To_Kanton_Conversion.py'

# Download the files
download_file(geojson_url, geojson_path)
download_file(conventional_csv_url, conventional_csv_path)
download_file(renewable_csv_url, renewable_csv_path)
download_file(conversion_py_url, conversion_py_path)

# Import the downloaded module
import importlib.util

spec = importlib.util.spec_from_file_location("City_To_Kanton_Conversion", conversion_py_path)
city_to_canton = importlib.util.module_from_spec(spec)
spec.loader.exec_module(city_to_canton)

# Now you can use city_to_canton.city_to_canton

# Title for the Streamlit app
st.title('Power Generation Capacity in Switzerland by Canton')

# Dropdown for selecting the figure to display
option = st.selectbox(
    'Select a visualization:',
    [
        'Total Generation Capacity by Canton',
        'Conventional Power Plants in Switzerland by Canton',
        'Clean Energy Sources in Switzerland by Canton',
        'Clean Energy Sources Bar Chart',
        'Clean Energy Sources Treemap'
    ]
)


# Define file paths
geojson_path = r"C:\Users\hellr\Documents\Constructor Academy MiniProject\MiniProject\json\georef-switzerland-kanton.geojson"
conventional_csv_path = r"C:\Users\hellr\Documents\Constructor Academy MiniProject\MiniProject\data\conventional_power_plants_EU_filtered.csv"
renewable_csv_path = r"C:\Users\hellr\Documents\Constructor Academy MiniProject\MiniProject\data\renewable_power_plants_CH.csv"

# Load the CSV datasets
df_conventional = pd.read_csv(conventional_csv_path)
df_renewable = pd.read_csv(renewable_csv_path)

# Map cities to cantons for the conventional dataset
df_conventional['canton'] = df_conventional['city'].map(city_to_canton)

# Drop rows where canton could not be mapped
df_conventional = df_conventional.dropna(subset=['canton'])

# Extract relevant columns and rename for consistency
df_conventional = df_conventional[['canton', 'energy_source', 'capacity']].rename(columns={'capacity': 'generation_capacity'})
df_renewable = df_renewable[['canton', 'energy_source_level_2', 'electrical_capacity']].rename(columns={'energy_source_level_2': 'energy_source', 'electrical_capacity': 'generation_capacity'})

# Combine the datasets
combined_df = pd.concat([df_conventional, df_renewable], ignore_index=True)

# Aggregate data to calculate total generation capacity and individual capacities by energy source for each canton
canton_agg = combined_df.groupby('canton').agg(total_capacity=('generation_capacity', 'sum')).reset_index()
energy_source_agg = combined_df.groupby(['canton', 'energy_source']).agg(source_capacity=('generation_capacity', 'sum')).reset_index()

# Pivot the energy source data for easier merging
energy_source_pivot = energy_source_agg.pivot(index='canton', columns='energy_source', values='source_capacity').fillna(0).reset_index()

# Merge the total capacity with the pivoted energy source data
canton_agg = canton_agg.merge(energy_source_pivot, on='canton', how='left')

# Prepare hover data
hover_data_columns = canton_agg.columns.tolist()
hover_data_columns.remove('canton')
canton_agg['hover_text'] = canton_agg.apply(
    lambda row: '<br>'.join([f"{col}: {row[col]:.2f} MW" for col in hover_data_columns]), axis=1
)

# Load the GeoJSON file
with open(geojson_path, 'r') as f:
    geojson = json.load(f)

# Function to create and display the first choropleth map
def display_total_capacity_choropleth():
    fig = px.choropleth_mapbox(
        canton_agg,
        geojson=geojson,
        locations='canton',
        featureidkey="properties.kan_name",
        color='total_capacity',
        color_continuous_scale="Viridis",
        range_color=(0, canton_agg['total_capacity'].max()),
        mapbox_style="carto-positron",
        zoom=7,
        center={"lat": 46.8, "lon": 8.3},
        opacity=0.6,
        labels={'total_capacity': 'Total Generation Capacity (MW)'},
        hover_data={'hover_text': True, 'canton': False, 'total_capacity': False}
    )
    fig.update_layout(
        title='Total Generation Capacity by Canton with Energy Source Breakdown',
        title_font_size=18,
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    fig.update_traces(
        hovertemplate="<b>%{location}</b><br>Total Capacity: %{z} MW<br>%{customdata}"
    )
    st.plotly_chart(fig)


# Aggregate the count and types of power plants by canton
canton_plant_counts = df_conventional.groupby('canton').agg(
    count=('canton', 'size'),
    types=('energy_source', lambda x: ', '.join(x.unique()))
).reset_index()

# Load the GeoJSON file
with open(geojson_path, 'r') as f:
    geojson = json.load(f)

# Function to create and display the second choropleth map
def display_conventional_plant_counts_choropleth():
    fig = px.choropleth_mapbox(
        canton_plant_counts,
        geojson=geojson,
        locations='canton',
        featureidkey="properties.kan_name",
        color='count',
        color_continuous_scale="Viridis",
        range_color=(0, canton_plant_counts['count'].max()),
        mapbox_style="carto-positron",
        zoom=7,
        center={"lat": 46.8, "lon": 8.3},
        opacity=0.6,
        labels={'count': 'Number of Power Plants'},
        hover_data={'canton': False, 'count': True, 'types': True}
    )
    fig.update_layout(
        title='Conventional Power Plants in Switzerland by Canton',
        title_font_size=18,
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    st.plotly_chart(fig)


# Additional visualizations

# Aggregate renewable data by canton and energy source
df_detailed = df_renewable.groupby(['canton', 'energy_source']).size().reset_index(name='count')
df_pivot = df_detailed.pivot(index='canton', columns='energy_source', values='count').fillna(0)
df_total = df_renewable.groupby('canton').size().reset_index(name='total_count')
df_aggregated = pd.merge(df_total, df_pivot, on='canton')

# Map canton abbreviations to full names
canton_mapping = {
    'AG': 'Aargau', 'AI': 'Appenzell Innerrhoden', 'AR': 'Appenzell Ausserrhoden', 'BE': 'Bern',
    'BL': 'Basel-Landschaft', 'BS': 'Basel-Stadt', 'FR': 'Fribourg', 'GE': 'Genève', 'GL': 'Glarus',
    'GR': 'Graubünden', 'JU': 'Jura', 'LU': 'Luzern', 'NE': 'Neuchâtel', 'NW': 'Nidwalden',
    'OW': 'Obwalden', 'SG': 'St. Gallen', 'SH': 'Schaffhausen', 'SO': 'Solothurn', 'SZ': 'Schwyz',
    'TG': 'Thurgau', 'TI': 'Ticino', 'UR': 'Uri', 'VD': 'Vaud', 'VS': 'Valais', 'ZG': 'Zug', 'ZH': 'Zürich'
}
df_aggregated['canton_full'] = df_aggregated['canton'].map(canton_mapping)

# Function to create and display the third choropleth map
def display_renewable_energy_choropleth():
    fig = px.choropleth_mapbox(
        df_aggregated,
        geojson=geojson,
        locations='canton_full',
        featureidkey="properties.kan_name",
        color='total_count',
        color_continuous_scale=px.colors.sequential.Plasma,
        mapbox_style="carto-positron",
        center={"lat": 46.8, "lon": 8.3},
        zoom=7,
        opacity=0.6,
        labels={'total_count': 'Total Clean Energy Sources'}
    )

    hover_data = ['total_count', 'Bioenergy', 'Hydro', 'Solar', 'Wind']
    for col in hover_data:
        if col not in df_aggregated.columns:
            df_aggregated[col] = 0

    fig.update_traces(
        hovertemplate=(
            '<b>%{properties.kan_name}</b><br>'
            'Total Clean Energy Sources: %{z}<br>'
            'Bioenergy: %{customdata[1]}<br>'
            'Hydro: %{customdata[2]}<br>'
            'Solar: %{customdata[3]}<br>'
            'Wind: %{customdata[4]}<extra></extra>'
        ),
        customdata=df_aggregated[hover_data].values
    )

    fig.update_layout(
        title='Clean Energy Sources in Switzerland by Canton',
        title_font_size=18,
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    st.plotly_chart(fig)


# Stacked bar chart for renewable energy sources
df_melted = df_aggregated.melt(id_vars=['canton_full', 'total_count'],
                               value_vars=['Bioenergy', 'Hydro', 'Solar', 'Wind'],
                               var_name='energy_source',
                               value_name='count')

# Function to create and display the stacked bar chart
def display_renewable_energy_bar_chart():
    fig = px.bar(
        df_melted,
        x='canton_full',
        y='count',
        color='energy_source',
        title='Clean Energy Sources in Switzerland by Canton',
        labels={'count': 'Number of Clean Energy Sources', 'canton_full': 'Canton'},
        text='count'
    )

    fig.update_layout(
        barmode='stack',
        xaxis_tickangle=-45,
        xaxis_title='Canton',
        yaxis_title='Number of Clean Energy Sources',
        legend_title='Energy Source',
        title={'x': 0.5},
        margin={"r": 0, "t": 50, "l": 0, "b": 0}
    )
    st.plotly_chart(fig)


# Function to create and display the treemap
def display_renewable_energy_treemap():
    df_detailed['canton_full'] = df_detailed['canton'].map(canton_mapping)
    fig = px.treemap(
        df_detailed,
        path=[px.Constant("Switzerland"), 'canton_full', 'energy_source'],
        values='count',
        color='count',
        color_continuous_scale='Viridis',
        title='Distribution of Clean Energy Sources in Switzerland by Canton and Type',
        labels={'count': 'Number of Energy Sources', 'canton_full': 'Canton', 'energy_source': 'Energy Source'}
    )
    fig.update_layout(
        title={'x': 0.5},
        margin={"r": 0, "t": 50, "l": 0, "b": 0}
    )
    st.plotly_chart(fig)


# Display the selected figure based on the dropdown selection
if option == 'Total Generation Capacity by Canton':
    display_total_capacity_choropleth()
elif option == 'Conventional Power Plants in Switzerland by Canton':
    display_conventional_plant_counts_choropleth()
elif option == 'Clean Energy Sources in Switzerland by Canton':
    display_renewable_energy_choropleth()
elif option == 'Clean Energy Sources Bar Chart':
    display_renewable_energy_bar_chart()
elif option == 'Clean Energy Sources Treemap':
    display_renewable_energy_treemap()




# In[ ]:




