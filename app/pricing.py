def get_numeric_vals(amenities, first_four, select_df):
    selected_amen = list(select_df.amenity)

    amen_bool_list = []
    for item in amenities:
        if item in selected_amen:
            amen_bool_list.append(1)
        else:
            amen_bool_list.append(0)

    nested_list = [first_four, amen_bool_list]
    flattened_list = [item for sublist in nested_list for item in sublist]

    return flattened_list



def predict_price(city, amenities):
    # import requirements
    import pickle
    import numpy as np

    # Import city-specific model
    pickle_file = "pkl_files/" + city + ".pkl"

    city_model = pickle.load(open(pickle_file, 'rb'))

    price = city_model.predict(np.array(amenities[:city_model.n_features_in_]).reshape(1, -1))[0]

    return price
