import pandas as pd
import streamlit as st
import re
import pydeck as pdk
import numpy as np
import altair as alt

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
    applicants['State'] = applicants.State.str.strip() 
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

# lat_midpoint = grants['lat'].median()
# lon_midpoint = grants['lon'].median()

min_grant, max_grant, med_grant = int(grants.Amount.min()), int(grants.Amount.max()), int(grants.Amount.median())
min_app, max_app = int(applicants['Funding Request'].min()), int(applicants['Funding Request'].max())
app_25, app_75 = int(applicants['Funding Request'].quantile(.25)), int(applicants['Funding Request'].quantile(.75))

st.title('TIGER Applicants and Awards')
st.subheader('Applicants')
applicant_entities = list(applicants.State.unique())
entity_list = st.sidebar.multiselect('Show Applications From:', options=applicant_entities, default=applicant_entities[0])
grant_range = st.sidebar.slider('Select a Range of Values',
                               min_app, max_app, (app_25, app_75))
filtered = applicants[applicants.State.isin(entity_list)]
st.write(f'There are {len(filtered)} applications from the State(s) you selected. This represents {round(100*len(filtered)/len(applicants), 2)} percent of all applications.')

show_variable = st.selectbox('Show Sum of Total:', options=['Funding Request', 'Project Cost'])
hist_values = filtered.groupby(['State', 'Round']).agg('sum')[show_variable].reset_index()
st.write(hist_values)
alt_chart = alt.Chart(hist_values).mark_bar().encode(
    x='State',
    y=show_variable,
    color='State',
    column='Round:O'
)
st.subheader(f'Total {show_variable} by Year')
st.altair_chart(alt_chart)

with st.beta_expander('Raw Data'):
    st.write(applicants[applicants.State.isin(entity_list)])

# st.bar_chart(data=filtered['Applicant Name'].value_counts())

# st.map(filtered)


# st.subheader('Grants Awarded')
# st.write(grants)
# min_grant_size = st.slider('Minimum Grant Size', min_grant, max_grant, med_grant)
# n_grants = len(grants[grants.Amount >= min_grant_size])
# prop_grants = round((1 - (n_grants/len(grants))) * 100, 2)
# st.write(f'{n_grants} grants awarded in amounts of at least {min_grant_size}. {prop_grants} percent of all grants awarded were less than {min_grant_size}.')
# st.subheader('Grants Awarded Map (Guam Excluded)')
# st.map(grants[(grants.lon < 0) & (grants.Amount >= min_grant_size)])


# st.map(applicants[(grants.lon < 0) & (grants.Amount >= min_grant_size)])
# st.pydeck_chart(pdk.Deck(
#      map_style='mapbox://styles/mapbox/light-v9',
#      layers=[
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
#          pdk.Layer(
#              'ScatterplotLayer',
#              data=grants,
#              get_position='[lon, lat]',
#              get_color='[200, 30, 0, 160]',
#              get_radius=200,
#          ),
#      ],
#  ))