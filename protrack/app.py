import streamlit as st
import pandas as pd
import pydeck as pdk

points = pd.read_csv('./ProTrack_Project_Point.csv')

points.rename(columns={'X': 'lon', 'Y':'lat'}, inplace=True)

# st.map(points)

st.pydeck_chart(pdk.Deck(
     map_style='mapbox://styles/mapbox/light-v9',
     layers=[
#          pdk.Layer(
#             'HexagonLayer',
#             data=grants,
#             get_position='[lon, lat]',
#             radius=25000,
#             elevation_scale=5000,
#             elevation_range=[0, 1000],
#             pickable=True,
#             extruded=True,
#          ),
         pdk.Layer(
             'ScatterplotLayer',
             data=points.loc[~points['DESCRIPTION'].isna(),['lon', 'lat', 'DESCRIPTION']],
             get_position='[lon, lat]',
             get_color='[200, 30, 0, 160]',
             get_radius=200,
         ),
     ],
 ))