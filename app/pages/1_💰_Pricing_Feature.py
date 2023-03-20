import pandas as pd
import pymysql
from sqlalchemy import create_engine
import streamlit as st
from secretsfile import secrets
import visuals

## connecting to database
endpoint = secrets.get('DATABASE_ENDPOINT')
user = secrets.get('DATABASE_USER')
password = secrets.get('DATABASE_PASSWORD')
port = secrets.get('DATABASE_PORT')
database = secrets.get('DATABASE_NAME')

engine = create_engine(f'mysql+pymysql://{user}:{password}@{endpoint}:{port}/{database}', pool_recycle=3600);



st.set_page_config(layout="wide", page_title='And That Means Comfort', page_icon='https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f9d9-200d-2642-fe0f.png',
                   menu_items={
                       'About': "Check out our Github page at "
                   }
                   )

## adding title to streamlit.io
st.title(":blue[And That Means Comfort: Optimizing Airbnb Listings]")

states_list = ['NC', 'FL', 'MA', 'IL', 'NV', 'OH', 'CO', 'TX', 'HI', 'TN', 'LA', 'NY', 'NJ', 'RI', 'OR', 'CA',
               'WA', 'MN', 'DC']
areas_dict = {'NC': ['---', 'asheville'], 'FL': ['---', 'broward-county'], 'MA': ['---', 'boston', 'cambridge'],
              'HI': ['---', 'hawaii'],
              'IL': ['---', 'chicago'], 'NV': ['---', 'clark-county-nv'], 'OH': ['---', 'columbus'],
              'CO': ['---', 'denver'],
              'TX': ['---', 'austin', 'dallas', 'fort-worth'], 'TN': ['---', 'nashville'], 'LA': ['---', 'new-orleans'],
              'NY': ['---', 'new-york-city'], 'NJ': ['---', 'jersey-city', 'newark'], 'MN': ['---', 'twin-cities-msa'],
              'RI': ['---', 'rhode-island'], 'OR': ['---', 'portland', 'salem-or'],
              'CA': ['---', 'los-angeles', 'oakland', 'pacific-grove', 'san-diego', 'san-francisco',
                     'san-mateo-county', 'santa-clara-county', 'santa-cruz-county'], 'WA': ['---', 'seattle'],
              'DC': ['---', 'washington-dc']
              }

states_list = sorted(states_list)
states_list.insert(0, '---')

## STREAMLIT
st.subheader("Choose your state")

# creating state/area select boxes
state = st.selectbox('Available states:', states_list)
if state == '---':
    st.error("Please select your state.")
else:
    area = st.selectbox('Available areas:', areas_dict[state])
    if area == '---':
        st.error("Please select your area.")

    else:
        clicked = st.button('Submit area')
        if clicked:
            st.header("Pricing")
            st.subheader("How should you price your home? Select your setup.")

            def load_pricing(area):
                area_quotes = "'" + area + "'"
                query = f'SELECT amenity, score FROM {database}.pricing_features WHERE scrape_city={area_quotes};'
                pricing = pd.read_sql_query(query, engine)

                remove_list = ['bathrooms_text', 'accommodates', 'bedrooms', 'beds', 'room_type', 'number_of_reviews',
                               'minimum_nights', 'host_acceptance_rate', 'host_response_rate', 'host_response_time']

                pricing = pricing[pricing.amenity.isin(remove_list) == False]
                return pricing


            data_load_state = st.text('Please wait while we load the pricing data...')
            pricing = load_pricing(area)
            data_load_state.text('Loading pricing data...done!')

            with st.form(key='my_form'):
                amen = st.multiselect(label='What amenities do you provide?', options=pricing.amenity)
                click2 = st.form_submit_button('Submit amenities')


            # with st.form(key='my_2_form'):
            #     c1, c2, c3, c4 = st.columns(4)
            #     with c1:
            #         rooms = st.number_input('How many bedrooms?', step=1, format='%d')
            #     with c2:
            #         baths = st.number_input('How many bathrooms?', step=0.5, format='%1f')
            #     with c3:
            #         beds = st.number_input('How many beds?', step=1, format='%d')
            #     with c4:
            #         ppl = st.number_input('Accommodates how many people?', step=1, format='%d')
            #
            #
            #     submit = st.form_submit_button(label='Submit listing details', on_click=submitted)
            #
            # if 'submitted' in st.session_state:
            #     def load_pricing(area):
            #         area_quotes = "'" + area + "'"
            #         query = f'SELECT amenity, score FROM {database}.pricing_features WHERE scrape_city={area_quotes};'
            #         pricing = pd.read_sql_query(query, engine)
            #         return pricing
            #     if st.session_state.submitted == True:
            #         st.dataframe(load_pricing(area))
            
            
st.text(' ')
st.text(' ')
st.text(' ')
st.text(' ')
st.text(' ')
st.text('*Results are meant to enhance listings, not guarantee income.')
