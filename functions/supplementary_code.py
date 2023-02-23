#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import pymysql
from sqlalchemy import create_engine 
import matplotlib.pyplot as plt

from secretsfile import secrets

endpoint = secrets.get('DATABASE_ENDPOINT')
user = secrets.get('DATABASE_USER')
password = secrets.get('DATABASE_PASSWORD')
port = secrets.get('DATABASE_PORT')
database = secrets.get('DATABASE_NAME')

engine = create_engine(f'mysql+pymysql://{user}:{password}@{endpoint}:{port}/{database}', pool_recycle=3600);


################## Choropleth map with count of unique listings by state ##################################################
query = f'SELECT scrape_city, listing_id FROM {database}.listings;'
all_city_listings = pd.read_sql_query(query, engine)

areas_dict= {'NC':['---', 'asheville'], 'FL':['---', 'broward-county'], 'MA':['---', 'boston', 'cambridge'], 'HI':['---', 'hawaii'],
             'IL':['---', 'chicago'], 'NV':['---', 'clark-county'], 'OH': ['---', 'columbus'], 'CO':['---', 'denver'],
             'TX':['---', 'austin', 'dallas', 'fort-worth'], 'TN':['---', 'nashville'], 'LA':['---', 'new-orleans'],
             'NY':['---', 'new-york-city'], 'NJ':['---', 'jersey-city', 'newark'], 'MN':['---', 'twin-cities-msa'],
             'RI':['---', 'rhode-island'],  'OR':['---', 'portland', 'salem-or'],
             'CA':['---', 'los-angeles', 'oakland', 'pacific-grove', 'san-diego', 'san-francisco',
                   'san-mateo-county', 'santa-clara-county', 'santa-cruz-county'], 'WA': ['---', 'seattle'],
             'DC':['---', 'washington-dc']
             }

def get_listings_by_state():
    import pandas as pd
    import plotly.express as px
    
    for v in areas_dict.values():
        if '---' in v:
            v.remove('---')
    inv_areas_dict = {v: k for k, values in areas_dict.items() for v in values}
    unique_listings = pd.DataFrame(all_city_listings.groupby('scrape_city')['listing_id'].nunique()).reset_index()
    unique_listings['state'] = unique_listings['scrape_city'].map(inv_areas_dict)
    
    state_listings = pd.DataFrame(unique_listings.groupby('state')['listing_id'].sum())
    state_listings = state_listings.rename(columns = {'listing_id':'unique_listings'})
    
    fig = px.choropleth(state_listings, locations=state_listings.index, title='Distribution of Airbnb Data Areas',
                    locationmode="USA-states", color='unique_listings', scope="usa",color_continuous_scale='teal')
 
    fig.show()
##################################################################################################




