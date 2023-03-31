
def load_city_amenities(city):
    from sklearn.feature_selection import SelectKBest
    from sklearn.feature_selection import f_regression
    import pandas as pd
    import numpy as np
    import mysql.connector
    
    #Connect to DB, clear any previous amenities for selected city
    connect= mysql.connector.connect(host=endpoint, database='Capstone', user=user, password=password)
    cursor = connect.cursor()
    delete_sql = "DELETE FROM pricing_features WHERE scrape_city = '" + city +"'"
    cursor.execute(delete_sql)
    connect.commit()

    #collect all listings for selected city, put in df
    query_text = "SELECT * FROM recent_listings_occup WHERE scrape_city = '" + city +"'"
    sql_query = pd.read_sql_query(query_text, connect)

    df = pd.DataFrame(sql_query)
    df = df[['room_type', 'accommodates', 'bathrooms_text', 'bedrooms', 'beds', 'amenities', 'price', 'number_of_reviews',
       'license', 'instant_bookable', 'scrape_city']]
    
    #clean extra punctuation from amenities
    df['amenities']=[c.strip('[]\' ""') for c in df['amenities']]

    #create data frame of amenities, so each amenity is a column, and each row a 0 or 1 to indicate if that listing had that amenity
    new_df = df.amenities.str.get_dummies(sep=', ')

    df = pd.concat((df, new_df), axis=1)

    #remove pricing and bulk amenity list, map text columns to strings
    pred_columns = list(df.columns)
    pred_columns.remove('price')
    pred_columns.remove('amenities')
    df['room_type']=df['room_type'].map({'Entire home/apt':1, 'Private room':2, 'Shared room':3, 'Hotel room':4})
    df['bathrooms_text']=df['bathrooms_text'].str.extract(r'(\d(?:.\d)?)').fillna(0)
    pred_columns.remove('scrape_city')

    #remove any amenities that are only listed occasionally, outliers can throw off the model
    purge = []
    for i in pred_columns[24:]:
        #print(i, df2[i].value_counts())
        if df[i].value_counts()[1] < 50:
            purge.append(i)
    for i in purge:
        pred_columns.remove(i)
    
    y = df['price']

    #find the 50 pricing features (rental features and amenities) that most affect pricing
    skb_selector = SelectKBest(f_regression, k=50).fit(df[pred_columns], y)    

    scores = -np.log10(skb_selector.pvalues_[skb_selector.pvalues_ != 0])
    scores /= scores.max()

    #trim to top 20 for ease of user interaction
    amenities = []
    scores = sorted(skb_selector.scores_, reverse = True)[:20]
    print(city)
    for i in scores:
        placeloc = np.where(skb_selector.scores_==i)[0][0]
        #print(pred_columns[placeloc], i)
        amenities.append(pred_columns[placeloc])
    
    #Ensure all numerical features are present
    predefined_list = ['bedrooms', 'bathrooms_text', 'beds','accommodates', 'room_type']
    predefined_scores = dict(zip(pred_columns[:5],skb_selector.scores_[:5]))
    for feature in predefined_list:
        if feature not in amenities:
            amenities.insert(0,feature)
            scores.insert(0,predefined_scores[feature])

    #create a table of city, amenity, and score for the top 20, ensure connection to db and push
    amenities_df = pd.DataFrame({'scrape_city': [city] * 20, 'amenity': amenities[:20], 'score' : scores[:20]})


    #sort numerical and boolean
    remains = [word for word in amenities_df['amenity'] if word not in predefined_list]
    sort_order = predefined_list + remains
    amenities_df.sort_values(by="amenity", key=lambda column: column.map(lambda e: sort_order.index(e)), inplace = True)

    insert_sql = "REPLACE INTO pricing_features (scrape_city, amenity, score) VALUES (%s, %s, %s)"
    connect=mysql.connector.connect(host=endpoint, database='Capstone', user=user, password=password)
    cursor = connect.cursor()

    cursor.executemany(insert_sql, list(amenities_df.itertuples(index=False, name = None)))
    connect.commit()



endpoint = secrets.get('DATABASE_ENDPOINT')
user = secrets.get('DATABASE_USER')
password = secrets.get('DATABASE_PASSWORD')
port=secrets.get('DATABASE_PORT')


connect=mysql.connector.connect(host=endpoint, database='Capstone', user=user, password=password)
cursor = connect.cursor()
import pandas as pd
citylist = pd.read_sql_query (''' select distinct scrape_city from listing_detail_stage''', connect)
for city in citylist['scrape_city']:
    load_city_amenities(city)