import pandas as pd
import streamlit as st
import re
import pydeck as pdk
import numpy as np
import altair as alt


applicants = pd.read_csv('./applicants.csv')
grants = pd.read_csv('./grants.csv')

# lat_midpoint = grants['lat'].median()
# lon_midpoint = grants['lon'].median()

min_grant, max_grant, med_grant = int(grants.Amount.min()), int(grants.Amount.max()), int(grants.Amount.median())
min_app, max_app = int(applicants['Funding Request'].min()), int(applicants['Funding Request'].max())
app_25, app_75 = int(applicants['Funding Request'].quantile(.25)), int(applicants['Funding Request'].quantile(.75))

st.set_page_config(layout='wide')
app_or_grant = st.selectbox(
    'Show Applications or Grants?',
    ('Applications', 'Grants'))

if app_or_grant == 'Applications':
    st.title('TIGER Applications')
    st.subheader('Applicants')


    applicant_entities = list(applicants.State.unique())
    def entity_select():
        return st.multiselect('Show Applications From:', options=applicant_entities, default=applicant_entities[0])
    def slider_select(min_v, max_v, range_v):
        return st.slider('Select a Range of Values', min_v, max_v, range_v)
    def show_select():
        return st.selectbox('Show Sum of Total:', options=['Funding Request', 'Project Cost'])

    with st.sidebar:
        entity_list = entity_select()
        slider = slider_select(0, 3500, (0, 250))
    # grant_range = st.slider('Select a Range of Values',\
    #                                min_app, max_app, (app_25, app_75))
    filtered = applicants[applicants.State.isin(entity_list)]
    st.write(f'There are {len(filtered)} applications from the State(s) you selected. This represents {round(100*len(filtered)/len(applicants), 2)} percent of all applications.')

    left_column, right_column = st.beta_columns((1, 2))
    with left_column:
        
        show_variable = show_select()
        hist_values = filtered.groupby(['State', 'Round']).agg('sum')[show_variable].reset_index()
        st.write(hist_values)


    with right_column:
        alt_chart = alt.Chart(hist_values).\
            mark_bar().encode(
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

elif app_or_grant == 'Grants':
    st.title('TIGER Grants Awarded')
    min_grant_size = st.slider('Minimum Grant Size', min_grant, max_grant, med_grant, step=int((max_grant - min_grant)/100))
    n_grants = len(grants[grants.Amount >= min_grant_size])
    prop_grants = round((1 - (n_grants/len(grants))) * 100, 2)
    st.write(f'{n_grants} grants awarded in amounts of at least {min_grant_size}. {prop_grants} percent of all grants awarded were less than {min_grant_size}.')
    st.subheader('Grants Awarded Map (Guam Excluded)')
    st.map(grants[(grants.lon < 0) & (grants.Amount >= min_grant_size)])
    with st.beta_expander('Raw Data'):
        st.write(grants)


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