#!/usr/bin/env python
# coding: utf-8

# In[19]:


import plotly.express as px
import pandas as pd
import json

# Load the GeoJSON file
geojson_path = r"C:\Users\hellr\Downloads\georef-switzerland-kanton.geojson"
with open(geojson_path, 'r') as geojson_file:
    geojson = json.load(geojson_file)

# Load the CSV dataset
csv_path = r"C:\Users\hellr\Downloads\renewable_power_plants_CH.csv"
df_renewable = pd.read_csv(csv_path)

# Aggregate the data by canton and energy source
df_detailed = df_renewable.groupby(['canton', 'energy_source_level_2']).size().reset_index(name='count')

# Pivot the data to get energy sources as columns
df_pivot = df_detailed.pivot(index='canton', columns='energy_source_level_2', values='count').fillna(0)

# Aggregate the data by canton for total counts
df_total = df_renewable.groupby('canton').size().reset_index(name='total_count')

# Merge the total count with the pivoted detailed data
df_aggregated = pd.merge(df_total, df_pivot, on='canton')

# Map canton abbreviations to full names
canton_mapping = {
    'AG': 'Aargau',
    'AI': 'Appenzell Innerrhoden',
    'AR': 'Appenzell Ausserrhoden',
    'BE': 'Bern',
    'BL': 'Basel-Landschaft',
    'BS': 'Basel-Stadt',
    'FR': 'Fribourg',
    'GE': 'Genève',
    'GL': 'Glarus',
    'GR': 'Graubünden',
    'JU': 'Jura',
    'LU': 'Luzern',
    'NE': 'Neuchâtel',
    'NW': 'Nidwalden',
    'OW': 'Obwalden',
    'SG': 'St. Gallen',
    'SH': 'Schaffhausen',
    'SO': 'Solothurn',
    'SZ': 'Schwyz',
    'TG': 'Thurgau',
    'TI': 'Ticino',
    'UR': 'Uri',
    'VD': 'Vaud',
    'VS': 'Valais',
    'ZG': 'Zug',
    'ZH': 'Zürich'
}

df_aggregated['canton_full'] = df_aggregated['canton'].map(canton_mapping)

# Define a color scale for the total energy sources
color_scale = px.colors.sequential.Plasma

# Create the choropleth map
fig = px.choropleth_mapbox(
    df_aggregated,
    geojson=geojson,
    locations='canton_full',
    featureidkey="properties.kan_name",
    color='total_count',
    color_continuous_scale=color_scale,
    mapbox_style="carto-positron",
    center={"lat": 46.8, "lon": 8.3},
    zoom=7,
    opacity=0.6,
    labels={'total_count': 'Total Clean Energy Sources'}
)

# Customize hover tooltips
hover_data = [
    'total_count',
    'Bioenergy',
    'Hydro',
    'Solar',
    'Wind'
]

# Ensure all hover data columns are present in the DataFrame, even if they contain NaN values
for col in hover_data:
    if col not in df_aggregated.columns:
        df_aggregated[col] = 0

# Add detailed hover information
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

# Update layout
fig.update_layout(
    title='Clean Energy Sources in Switzerland by Canton',
    title_font_size=18,
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)

# Show the figure
fig.show()


# In[5]:


# Melt the DataFrame to long format for plotting
df_melted = df_aggregated.melt(id_vars=['canton_full', 'total_count'], 
                               value_vars=['Bioenergy', 'Hydro', 'Solar', 'Wind'], 
                               var_name='energy_source', 
                               value_name='count')

# Create the stacked bar chart
fig2 = px.bar(
    df_melted,
    x='canton_full',
    y='count',
    color='energy_source',
    title='Clean Energy Sources in Switzerland by Canton',
    labels={'count': 'Number of Clean Energy Sources', 'canton_full': 'Canton'},
    text='count'
)

# Update layout for better readability
fig2.update_layout(
    barmode='stack',
    xaxis_tickangle=-45,
    xaxis_title='Canton',
    yaxis_title='Number of Clean Energy Sources',
    legend_title='Energy Source',
    title={'x':0.5},
    margin={"r": 0, "t": 50, "l": 0, "b": 0}
)

# Show the figure
fig2.show()


# In[9]:


# Create the Treemap
df_detailed['canton_full'] = df_detailed['canton'].map(canton_mapping)

fig3 = px.treemap(
    df_detailed,
    path=[px.Constant("Switzerland"), 'canton_full', 'energy_source_level_2'],
    values='count',
    color='count',
    color_continuous_scale='Viridis',
    title='Distribution of Clean Energy Sources in Switzerland by Canton and Type',
    labels={'count': 'Number of Energy Sources', 'canton_full': 'Canton', 'energy_source_level_2': 'Energy Source'}
)

# Update layout for better readability
fig3.update_layout(
    title={'x': 0.5},
    margin={"r": 0, "t": 50, "l": 0, "b": 0}
)

# Show the figure
fig3.show()


# In[11]:


# Load the CSV file
csv_path = r"C:\Users\hellr\Downloads\conventional_power_plants_EU_filtered.csv"
df = pd.read_csv(csv_path)

# Get the unique cities from the CSV file
unique_cities = df['city'].unique()
#I fed this to chatgpt and it spend 20minutes making me a conversion file from city to kanton.


# In[38]:


# Load the CSV file
csv_path = r"C:\Users\hellr\Downloads\conventional_power_plants_EU_filtered.csv"
df = pd.read_csv(csv_path)

# Get the unique cities from the CSV file
unique_cities = df['city'].unique()

# Aggregate the count and types of power plants by canton
canton_plant_counts = df_conventional.groupby('canton').agg(
    count=('canton', 'size'),
    types=('energy_source', lambda x: ', '.join(x.unique()))
).reset_index()


# Load the GeoJSON file
with open(r"C:\Users\hellr\Downloads\georef-switzerland-kanton.geojson", 'r') as f:
    geojson = json.load(f)

# Create the choropleth map
fig4 = px.choropleth_mapbox(
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

# Update the layout
fig4.update_layout(
    title='Conventional Power Plants in Switzerland by Canton',
    title_font_size=18,
    margin={"r":0,"t":0,"l":0,"b":0}
)

# Show the figure
fig4.show()


# In[42]:


import pandas as pd
import json
import plotly.express as px

# Load the CSV files
df_conventional = pd.read_csv(r"C:\Users\hellr\Downloads\conventional_power_plants_EU_filtered.csv")
df_renewable = pd.read_csv(r"C:\Users\hellr\Downloads\renewable_power_plants_CH.csv")

# Map cities to cantons for the conventional dataset
df_conventional['canton'] = df_conventional['city'].map(city_to_canton)

# Drop rows where canton could not be mapped
df_conventional = df_conventional.dropna(subset=['canton'])

# Both datasets use MW as the unit for energy capacity

# Extract relevant columns
df_conventional = df_conventional[['canton', 'energy_source', 'capacity']]
df_conventional.rename(columns={'capacity': 'generation_capacity'}, inplace=True)

df_renewable = df_renewable[['canton', 'energy_source_level_2', 'electrical_capacity']]
df_renewable.rename(columns={'energy_source_level_2': 'energy_source', 'electrical_capacity': 'generation_capacity'}, inplace=True)

# Combine the datasets
combined_df = pd.concat([df_conventional, df_renewable], ignore_index=True)

# Aggregate data to calculate total generation capacity and percentages by energy source for each canton
canton_agg = combined_df.groupby('canton').agg(
    total_capacity=('generation_capacity', 'sum')
).reset_index()

energy_source_agg = combined_df.groupby(['canton', 'energy_source']).agg(
    source_capacity=('generation_capacity', 'sum')
).reset_index()

# Calculate percentage capacity per energy source
energy_source_agg = energy_source_agg.merge(canton_agg, on='canton')
energy_source_agg['percentage'] = (energy_source_agg['source_capacity'] / energy_source_agg['total_capacity']) * 100

# Prepare hover data
hover_data = energy_source_agg.groupby('canton').apply(
    lambda x: '<br>'.join([f"{row['energy_source']}: {row['percentage']:.2f}%" for _, row in x.iterrows()])
).reset_index()
hover_data.columns = ['canton', 'hover_text']

# Merge hover data with canton aggregates
canton_agg = canton_agg.merge(hover_data, on='canton')

# Load the GeoJSON file
with open(r"C:\Users\hellr\Downloads\georef-switzerland-kanton.geojson", 'r') as f:
    geojson = json.load(f)

# Create the choropleth map
fig5 = px.choropleth_mapbox(
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

# Update the layout
fig5.update_layout(
    title='Total Generation Capacity by Canton with Energy Source Breakdown',
    title_font_size=18,
    margin={"r":0,"t":0,"l":0,"b":0}
)

# Update hover template
fig5.update_traces(
    hovertemplate="<b>%{location}</b><br>Total Capacity: %{z} MW<br>%{customdata}"
)

# Show the figure
fig5.show()


# In[ ]:




