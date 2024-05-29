# Streamlit live coding script
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy

#mpg_df=pd.read_csv(r"C:\Users\hellr\Downloads\240527_Constructor\Exercises\data\data\mpg.csv")

@st.cache_data #This is a decorator? No idea
def load_data(path):
    df=pd.read_csv(path)
    return df

mpg_df_raw=load_data(path=".\my-first-streamlitapp\data\raw\mpg.csv") #For the speed
mpg_df=deepcopy(mpg_df_raw) #This is for security? I think this cashes the og instead of a copy

#The reason we do this, is we don't just keep re-running the cache, it lets the website keep running every time as a new load

st.title("introductions to Streamlit")
st.header("MPG Data Exploration")

if st.checkbox("Show Dataframe"):
    st.subheader("This is my dataset:")
    st.dataframe(data=mpg_df) #This section makes the displayed data set display only under a checkbox

left_column, right_column= st.columns(2)

left_column, middle_column, right_column= st.columns([3,1,1])

years= ["All"]+sorted(pd.unique(mpg_df['year']))
year=left_column.selectbox("choose a year", years) #On its own this is just a select box. It does nothing on its own.

show_means = middle_column.radio(
    label='Show Class Means', options=['Yes', 'No']) #No idea what radio does. Will need to find out. 



if year== 'All':
    reduced_df=mpg_df
else:
    reduced_df=mpg_df[mpg_df["year"]==year]

means = reduced_df.groupby('class').mean(numeric_only=True)


m_fig, ax = plt.subplots(figsize=(10, 8))
ax.scatter(reduced_df['displ'], reduced_df['hwy'], alpha=0.7)
ax.set_title("Engine Size vs. Highway Fuel Mileage")
ax.set_xlabel('Displacement (Liters)')
ax.set_ylabel('MPG')


if show_means == "Yes":
    ax.scatter(means['displ'], means['hwy'], alpha=0.7,
               color="red", label="Class Means")
    

st.pyplot(m_fig)

p_fig = px.scatter(reduced_df, x='displ', y='hwy', opacity=0.5,
                   range_x=[1, 8], range_y=[10, 50],
                   width=750, height=600,
                   labels={"displ": "Displacement (Liters)",
                           "hwy": "MPG"},
                   title="Engine Size vs. Highway Fuel Mileage")
p_fig.update_layout(title_font_size=22)

st.plotly_chart(p_fig)


#There is also a possiblity of showing maps:

st.subheader("Streamlit Map")
ds_geo = px.data.carshare()



ds_geo['lat'] = ds_geo['centroid_lat']
ds_geo['lon'] = ds_geo['centroid_lon']

st.dataframe(ds_geo.head())

st.map(ds_geo)