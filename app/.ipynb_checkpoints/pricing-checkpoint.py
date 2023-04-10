def get_numeric_vals(amenities, first_four, select_df, list_type):
    selected_amen = list(select_df.amenity)
    list_type_name = list_type[0]
    list_type_num = [0]
    type_dict = {'Entire home/apt':1, 'Private room':2, 'Shared room':3, 'Hotel room':4}
    if list_type_name in type_dict.keys():
        list_type_num = [type_dict[list_type_name]]

    amen_bool_list = []
    for item in amenities:
        if item in selected_amen:
            amen_bool_list.append(1)
        else:
            amen_bool_list.append(0)

    nested_list = [first_four, list_type_num, amen_bool_list]
    flattened_list = [item for sublist in nested_list for item in sublist]

    return flattened_list


def predict_price(city, amenities):
    # import requirements
    import pickle
    import numpy as np

    if len(amenities) < 20:
        for i in range(16):
            amenities.append(0)

    # Import city-specific model
    pickle_file = "pkl_files/" + city + ".pkl"
    city_model = pickle.load(open(pickle_file, 'rb'))

    price = city_model.predict(np.array(amenities[:city_model.n_features_in_]).reshape(1, -1))[0]

    return price
