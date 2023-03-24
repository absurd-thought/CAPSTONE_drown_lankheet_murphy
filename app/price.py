def predict_price(city, amenities):
    #import requirements


    #Import city-specific model
    pickle_file = city + ".pkl"
    
    #amenities.append(0)
    
    #city_model = pickle.load(open('model.pkl', 'rb'))
    #price = city_model.predict(X_test)

    #amenities[-1] = 500
    #review_price = city_model.predict(X_test)

    #dummy prices
    price = 10000
    review_price = 17
    return price, review_price