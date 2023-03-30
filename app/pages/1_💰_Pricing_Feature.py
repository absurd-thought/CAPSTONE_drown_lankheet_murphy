import pandas as pd
import pymysql
from sqlalchemy import create_engine
import streamlit as st
from secretsfile import secrets
import pricing
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

# Functions
def load_pricing(area):
    area_quotes = "'" + area + "'"
    query = f'SELECT amenity, score FROM {database}.pricing_features WHERE scrape_city={area_quotes};'
    pricing = pd.read_sql_query(query, engine)

    remove_list = ['bathrooms_text', 'accommodates', 'bedrooms', 'beds', 'room_type', 'number_of_reviews',
                   'minimum_nights', 'host_acceptance_rate', 'host_response_rate', 'host_response_time']

    pricing = pricing[pricing.amenity.isin(remove_list) == False]
    return pricing


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
        # clicked = st.button('Submit area')
        # if clicked:
        # st.header("Pricing")
        st.subheader("How should you price your home? Select your setup.")

        c1, c2, c3, c4 = st.columns(4)

        placeholder = st.empty()
        with c1:
            placeholder1 = st.empty()
            rooms = placeholder1.number_input('How many bedrooms?', step=1, format='%d')
        with c2:
            placeholder2 = st.empty()
            baths = placeholder2.number_input('How many bathrooms?', step=0.5, format='%1f')
        with c3:
            placeholder3 = st.empty()
            beds = placeholder3.number_input('How many beds?', step=1, format='%d')
        with c4:
            placeholder4 = st.empty()
            ppl = placeholder4.number_input('Accommodates how many people?', step=1, format='%d')

        # adding reset button
        click_clear = st.button('Reset', key='clear')
        if click_clear:
            rooms = placeholder1.number_input('How many bedrooms?', value=0, key='rooms')
            baths = placeholder2.number_input('How many bathrooms?', step=0.5, format='%1f', value=0.0, key='baths')
            beds = placeholder3.number_input('How many beds?', value=0, key='beds')
            ppl = placeholder4.number_input('Accommodates how many people?', value=0, key='ppl')

        with st.form("price_form"):
        # getting list of first 4 config spots
            first_four = [rooms, baths, beds, ppl]


            # loading pricing data
            data_load_state = st.text('Please wait while we load the pricing data...')
            pricing_data = load_pricing(area)
            data_load_state.text('Loading pricing data...done!')

            amenities_list = pricing_data.sort_values(by='amenity')
            amen = st.multiselect(label='What amenities do you provide?', options=amenities_list.amenity)
            submitted = st.form_submit_button("Submit setup")

        if submitted:
            select_df = pricing_data[pricing_data.amenity.isin(amen) == True]
            # select_df = select_df.set_index('amenity')

            amenities_for_pricing = pricing.get_numeric_vals(amen, first_four, select_df)
            price = pricing.predict_price(area, amenities_for_pricing)


            # showing pricing
            st.metric(label="Suggested price", value='$'+str(round(price))+' / night')



st.text(' ')
st.text(' ')
st.text(' ')
st.text(' ')
st.text(' ')
st.text('*Results are meant to enhance listings, not guarantee income.')
