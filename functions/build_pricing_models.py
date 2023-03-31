def create_pickle(city):
    import pickle
    #Connect to DB
    connect= mysql.connector.connect(host=endpoint, database='Capstone', user=user, password=password)
    cursor = connect.cursor()

    #pull data for current city
    query_text = "SELECT * FROM recent_listings_occup WHERE scrape_city = '" + city +"'"
    sql_query = pd.read_sql_query(query_text, connect)

    df = pd.DataFrame(sql_query)

    #Pare down to user-controllable
    df = df[['listing_id', 'room_type', 'accommodates',
       'bathrooms_text', 'bedrooms', 'beds', 'amenities', 'price',
       'number_of_reviews', 'license', 'instant_bookable',
       'scrape_city','avg_occup']]
    df['amenities']=[c.strip('[]\' ""') for c in df['amenities']]
    df['room_type']=df['room_type'].map({'Entire home/apt':1, 'Private room':2, 'Shared room':3, 'Hotel room':4})
    df['bathrooms_text']=df['bathrooms_text'].str.extract(r'(\d(?:.\d)?)').fillna(0)

    #create boolean df of amenities
    new_df = df.amenities.str.get_dummies(sep=', ')
    
    #Pull list of city-specific pricing features
    pricing_featues = pd.read_sql_query ("SELECT * FROM pricing_features WHERE scrape_city = '" + city +"'", connect)
    
    #merge dfs together
    df2 = pd.concat((df, new_df), axis=1)
    df2 = df2[list(pricing_featues['amenity'])]

    

    #determine which model provides best scoring for city
    #select from linear regression or kNN with varying k                           
    max_score = [0,0]
    for i in range(5,21):
        X_train, X_test, y_train, y_test = train_test_split(df2[df2.columns[:i]], df['price'], test_size=0.2, random_state =15)
        lin_reg = LinearRegression().fit(X_train, y_train)
        lin_reg_score = lin_reg.score(X_test, y_test)
        #print(i,lin_reg_score)
        if lin_reg_score > max_score[0]:
            max_score[0] = lin_reg_score
            max_score[1] = i
        scores = {}
        for j in range(25):
            knn_reg = KNeighborsRegressor(n_neighbors = j+1, weights = 'distance').fit(X_train, y_train)
            scores[j] = knn_reg.score(X_test, y_test)
            if scores[j] > max_score[0]:
                max_score[0] = scores[j]
                max_score[1] = i,j
    print(max_score)

    print(city)
    if type(max_score[1]) is int:
        X = df2[df2.columns[:max_score[1]]]
        y = df['price']
        model =  LinearRegression().fit(X, y)
        print('lin_reg',max_score[1])
    else:
        X = df2[df2.columns[:max_score[1][0]]]
        y = df['price']
        model = KNeighborsRegressor(n_neighbors = max_score[1][1]+1).fit(X, y)
        print('knn',max_score[1][0], max_score[1][1])
    
    pkl_file = city + '.pkl'
    pickle.dump(model, open(pkl_file, 'wb'))