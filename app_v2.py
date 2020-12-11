import pandas as pd
import streamlit as st
import re
import pydeck as pdk

def to_coords(coord_str):
    try:
        matches = re.search(r'\((\d{2}\.\d+),\s(-*\d+\.\d+)\)', coord_str)
        lat = float(matches.group(1))
        lon = float(matches.group(2))
        return (lat, lon)
    except:
        return 'failed'



def clean_amount(data, col='Amount'):
    data[col] = data[col].str.strip('$').replace('?', '0')
    data[col] = data[col].str.replace(',', '')
    data[col] = data[col].astype('float')
    return data

def load_applicants():
    applicants = pd.read_csv('./applicants.csv')
    applicants['Grant'] = applicants.Round
    applicants['Round'] = applicants.Round.str[-4:].astype('int')
    applicants = clean_amount(applicants, col='Funding Request')
    applicants = clean_amount(applicants, col='Project Cost')
    return applicants

def load_grants():
    grants = pd.read_csv('tiger_grants_2016.csv')
    grants = grants.rename(columns={' Amount ': 'Amount',
                                      'Capital vs Planning':'cap_plan',
                                      'Location 1': 'coord'
                                     })
    grants.drop('Location Precision', axis=1, inplace=True)
    grants['Round'] = pd.to_datetime(grants.Round).dt.year
    grants['lat'], grants['lon'] = zip(*[to_coords(coord) for coord in list(grants.coord)])
    return grants


applicants = load_applicants()
grants = load_grants()

lat_midpoint = grants['lat'].median()
lon_midpoint = grants['lon'].median()

min_grant, max_grant, med_grant = int(grants.Amount.min()), int(grants.Amount.max()), int(grants.Amount.median())


st.title('TIGER Applicants and Awards')
# st.subheader('Applicants')
# st.write(applicants)
# st.subheader('Grants Awarded')
# st.write(grants)
# min_grant_size = st.slider('Minimum Grant Size', min_grant, max_grant, med_grant)
# n_grants = len(grants[grants.Amount >= min_grant_size])
# st.write(f'{n_grants} grants awarded in amounts of at least {min_grant_size}')
# st.subheader('Grants Awarded Map (Guam Excluded)')
# st.map(grants[(grants.lon < 0) & (grants.Amount >= min_grant_size)])
st.pydeck_chart(pdk.Deck(
     map_style='mapbox://styles/mapbox/light-v9',
     layers=[
         pdk.Layer(
            'HexagonLayer',
            data=grants,
            get_position='[lon, lat]',
            radius=25000,
            elevation_scale=50,
            elevation_range=[0, 9000],
            pickable=True,
            extruded=True,
         ),
         pdk.Layer(
             'ScatterplotLayer',
             data=grants,
             get_position='[lon, lat]',
             get_color='[200, 30, 0, 160]',
             get_radius=200,
         ),
     ],
 ))