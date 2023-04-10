#!/usr/bin/env python
# coding: utf-8



import pandas as pd
import pymysql
from sqlalchemy import create_engine
import streamlit as st
from secretsfile import secrets
import nlp
import visuals

# setting page configuration
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
st.subheader("Find out which amenities add the most perceived value to your home, explore terms to include in your description,"
             " and predict your best price!*")


states_list = ['NC','FL','MA','IL','NV','OH','CO','TX','HI','TN','LA','NY','NJ','RI','OR','CA',
               'WA','MN','DC']
areas_dict= {'NC':['---', 'asheville'], 'FL':['---', 'broward-county'], 'MA':['---', 'boston', 'cambridge'], 'HI':['---', 'hawaii'],
             'IL':['---', 'chicago'], 'NV':['---', 'clark-county-nv'], 'OH': ['---', 'columbus'], 'CO':['---', 'denver'],
             'TX':['---', 'austin', 'dallas', 'fort-worth'], 'TN':['---', 'nashville'], 'LA':['---', 'new-orleans'],
             'NY':['---', 'new-york-city'], 'NJ':['---', 'jersey-city', 'newark'], 'MN':['---', 'twin-cities-msa'],
             'RI':['---', 'rhode-island'],  'OR':['---', 'portland', 'salem-or'],
             'CA':['---', 'los-angeles', 'oakland', 'pacific-grove', 'san-diego', 'san-francisco',
                   'san-mateo-county', 'santa-clara-county', 'santa-cruz-county'], 'WA': ['---', 'seattle'],
             'DC':['---', 'washington-dc']
             }


states_list=sorted(states_list)
states_list.insert(0, '---')

## STREAMLIT
st.subheader("Choose your state")

# creating state/area select boxes
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
            def load_amenities(area):
                area_quotes = "'" + area + "'"
                query = f'SELECT amenity, score FROM {database}.top_amenities WHERE scrape_city={area_quotes};'
                amenities = pd.read_sql_query(query, engine)
                return amenities


            data_load_state = st.text('Please wait while we load the amenities data...')
            amenities = load_amenities(area)
            data_load_state.text('Loading amenities data...done!')


            ## getting reviews df
            @st.cache_resource
            def load_reviews(area):
                area_quotes = "'" + area + "'"
                query = f'SELECT pos_word, pos_score, neg_word, neg_score FROM {database}.top_reviews WHERE scrape_city={area_quotes};'
                reviews = pd.read_sql_query(query, engine)
                return reviews

            # adding messages so user knows it's working
            data_load_state = st.text('Please wait while we load the reviews data...')
            reviews = load_reviews(area)
            data_load_state.text('Loading reviews data...done!')

            # adding reset button
            import pyautogui
            if st.button("Reset"):
                from streamlit import caching
                caching.clear_cache()
                pyautogui.hotkey("ctrl", "F5")

            # creating tabs
            tab1, tab2, tab3 = st.tabs(["Pricing Influences", "Amenity Additions", "Descriptive Terms"])

            with tab1:
                st.header("Pricing")
                st.text("How should you price your home? These are the top price-influencing factors in your area.")

            with tab2:
                st.header("Amenities")

                data_load_state = st.text('Creating amenities chart...')
                amen_chart = visuals.get_amenities_visual(amenities)
                data_load_state.text('Creating amenities chart...done!')

                st.subheader('Try adding these amenities')
                st.text('These amenities are associated with higher value review scores in your area. By adding them to your listing, you increase your listing\'s perception of value after a stay.**')

                st.altair_chart(amen_chart, use_container_width=False)
                st.text('**Only add amentities that you actually provide!')


            with tab3:
                st.header("Description")

                st.subheader('Try incorporating these terms into your listing description')
                st.text('These terms are associated with positive reviews in your area. By incorporating them into your listing\'s description, you create a psychological connection between good reviews and your property.')
                col1, col2, col3 = st.columns(3)

                data_load_state = st.text('Creating positive terms chart...')
                visuals.get_review_wordcloud(reviews, 'pos')
                data_load_state.text('Creating positive terms chart...done!')

                st.image('cloud.png')

                # adding space
                st.text(' ')
                st.text(' ')
                st.text(' ')
                st.text(' ')
                st.text(' ')
                st.subheader('What do the negative reviews say? These are terms and situations you want to avoid.')
                data_load_state = st.text('Creating negative terms chart...')
                visuals.get_review_wordcloud(reviews, 'neg')
                data_load_state.text('Creating negative terms chart...done!')

                st.image('cloud.png')


# adding space
st.text(' ')
st.text(' ')
st.text(' ')
st.text(' ')
st.text(' ')
st.text('*Results are meant to enhance listings, not guarantee income.')