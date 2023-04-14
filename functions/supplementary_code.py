
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
############################################################################################################
# Choropleth map with count of unique listings by state
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
##################################################################################################################
# Horizontal bar chart showing Reviews sentiments percents (Example: Boston, MA)
query = f"SELECT comments FROM {database}.reviews WHERE scrape_city='boston'"
reviews = pd.read_sql_query(query, engine)

def get_reviews_sentiments(reviews_df, full_area_name):
    '''
    full_area_name should be a string with city, state. Example: 'Boston, MA'
    '''
    import pandas as pd
    from collections import Counter

    scores_dict_list = []
    for each_list in reviews_df['comments']:
        scores_dict_list.append(sid.polarity_scores(each_list))

    counter = Counter()
    for d in scores_dict_list:
        counter.update(d)

    result = dict(counter)
    source = pd.DataFrame.from_dict(result, orient='index').reset_index()
    source = source.rename(columns={'index': 'sentiment', 0: 'value'})

    chart = alt.Chart(source, title=f'Review Sentiments for {full_area_name}').transform_joinaggregate(
        TotalValue='sum(value)',
    ).transform_calculate(
        PercentOfTotal="datum.value / datum.TotalValue"
    ).mark_bar(color='#057775').encode(
        alt.X('PercentOfTotal:Q', axis=alt.Axis(format='.0%')),
        y='sentiment:N'
    )

    return chart

get_reviews_sentiments(reviews, 'Boston, MA')
