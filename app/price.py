def predict_price(city, amenities):
    #import requirements
    import pickle
    import numpy as np

    if len(amenities)<20:
        for i in range(16):
            amenities.append(0)

    #Import city-specific model
    pickle_file = "pkl_files/"+city + ".pkl"
    
    #amenities.append(0)
    
    city_model = pickle.load(open(pickle_file, 'rb'))

    price = city_model.predict(np.array(amenities[:city_model.n_features_in_]).reshape(1, -1))[0]

    #amenities[-1] = 500


    #dummy prices
    review_price = 17
    return price#, review_price
