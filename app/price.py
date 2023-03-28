def predict_price(city, amenities):
    #import requirements
    import pickle
    import numpy as np

    #Import city-specific model
    pickle_file = "pkl_files/"+city + ".pkl"
    
    #amenities.append(0)
    
    city_model = pickle.load(open(pickle_file, 'rb'))

    #print(city_model.n_features_in_)
    price = city_model.predict(np.array(amenities[:city_model.n_features_in_]).reshape(1, -1))[0]

    #amenities[-1] = 500
    #review_price = city_model.predict(X_test)

    #dummy prices
    #price = 10000
    review_price = 17
    return price#, review_price

city = 'san-mateo-county'
amenities = [4,3,4,1,0,1,1,0,1,0,1,0,1,1,0,1,0,1,0,1,1,0,1]
predict_price(city, amenities)
