#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import pymysql
from sqlalchemy import create_engine

import streamlit as st

from secretsfile import secrets
import nlp
import visuals

st.set_page_config(layout="wide", page_title='And That Means Comfort', page_icon='https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f9d9-200d-2642-fe0f.png',
                   menu_items={
                       'About': "Check out our Github page at "
                   }
                   )


## connecting to database
endpoint = secrets.get('DATABASE_ENDPOINT')
user = secrets.get('DATABASE_USER')
password = secrets.get('DATABASE_PASSWORD')
port = secrets.get('DATABASE_PORT')
database = secrets.get('DATABASE_NAME')

engine = create_engine(f'mysql+pymysql://{user}:{password}@{endpoint}:{port}/{database}', pool_recycle=3600);


## adding title to streamlit.io
st.title(":blue[And That Means Comfort: Optimizing Airbnb Listings]")
st.subheader("Find out which amenities add the most value to your home, explore terms to include in your description,"
             " and predict your best price!")



states_list = ['NC','FL','MA','IL','NV','OH','CO','TX','HI','TN','LA','NY','NJ','RI','OR','CA',
               'WA','MN','DC']
areas_dict= {'NC':['---', 'asheville'], 'FL':['---', 'broward-county'], 'MA':['---', 'boston', 'cambridge'], 'HI':['---', 'hawaii'],
             'IL':['---', 'chicago'], 'NV':['---', 'clark-county'], 'OH': ['---', 'columbus'], 'CO':['---', 'denver'],
             'TX':['---', 'austin', 'dallas', 'fort-worth'], 'TN':['---', 'nashville'], 'LA':['---', 'new-orleans'],
             'NY':['---', 'new-york-city'], 'NJ':['---', 'jersey-city', 'newark'], 'MN':['---', 'twin-cities-msa'],
             'RI':['---', 'rhode-island'],  'OR':['---', 'portland', 'salem-or'],
             'CA':['---', 'los-angeles', 'oakland', 'pacific-grove', 'san-diego', 'san-francisco',
                   'san-mateo-county', 'santa-clara-county', 'santa-cruz-county'], 'WA': ['seattle'],
             'DC':['---', 'washington-dc']
             }


states_list=sorted(states_list)
states_list.insert(0, '---')

## FUNCTIONS
def get_hostnames(area):
    area_quotes = "'" + area + "'"
    query = f'SELECT host_name FROM {database}.listings WHERE scrape_city={area_quotes};'
    host_names = pd.read_sql_query(query, engine)
    hostnames = set(host_names.host_name)
    return hostnames
    

## STREAMLIT
st.subheader("Choose your state")

state = st.selectbox('Available states:', states_list)
if state=='---':
    st.error("Please select your state.")
else:
    area = st.selectbox('Available areas:', areas_dict[state])
    if area=='---':
        st.error("Please select your area.")

    else:
        clicked = st.button('Submit area')
        if clicked:
            # getting listings df
            @st.cache_resource
            def load_listings(area):
                area_quotes = "'" + area + "'"
                query = f'SELECT amenities, review_scores_value FROM {database}.listings WHERE scrape_city={area_quotes};'
                listings = pd.read_sql_query(query, engine)
                return listings


            data_load_state = st.text('Please wait while we load the listing data...')
            listings = load_listings(area)
            data_load_state.text('Loading listing data...done!')


            ## getting reviews df
            @st.cache_resource
            def load_reviews(area):
                area_quotes = "'" + area + "'"
                query = f'SELECT comments FROM {database}.reviews WHERE scrape_city={area_quotes};'
                reviews = pd.read_sql_query(query, engine)
                return reviews


            data_load_state = st.text('Please wait while we load the reviews data...')
            reviews = load_reviews(area)
            data_load_state.text('Loading reviews data...done!')

            import pyautogui
            if st.button("Reset"):
                from streamlit import caching
                caching.clear_cache()
                pyautogui.hotkey("ctrl", "F5")
            
            tab1, tab2, tab3 = st.tabs(["Pricing", "Amenities", "Descriptive Terms"])

            with tab1:
                st.header("Pricing")

            with tab2:
                st.header("Amenities")

                data_load_state = st.text('Getting top amenities...')
                amenities_df = nlp.get_top_amenities(listings)
                data_load_state.text('Getting top amenities...done!')

                # amen = st.multiselect("Choose your available amenities from these top 20:", set(df.index))
                # if amen:

                data_load_state = st.text('Creating amenities chart...')
                amen_chart = visuals.get_amenities_visual(amenities_df)
                data_load_state.text('Creating amenities chart...done!')

                st.subheader('Try adding these amenities to increase value')
                st.text('These amenities were associated with higher value review scores in your area.')

                st.altair_chart(amen_chart, use_container_width=False)


            with tab3:
                st.header("Descriptive Terms")

                data_load_state = st.text('Getting top descriptive terms...')
                terms_df = nlp.get_top_review_terms(reviews, area)
                data_load_state.text('Getting top descriptive terms...done!')


                st.subheader('Try incorporating these terms into your listing description to add value')
                st.text('These terms were associated with the top value scores in your area.')
                col1, col2, col3 = st.columns(3)

                data_load_state = st.text('Creating terms chart...')
                terms_chart = visuals.get_review_wordcloud(terms_df)
                data_load_state.text('Creating terms chart...done!')

                st.set_option('deprecation.showPyplotGlobalUse', False)
                col1.pyplot(terms_chart, use_container_width=False)




