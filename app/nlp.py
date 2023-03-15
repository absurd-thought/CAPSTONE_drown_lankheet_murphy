## NLP FUNCTIONS

##############################################################################################################
def get_top_amenities(listing_df):
    # correlating amenities with review scores
    # adapted from https://stackoverflow.com/questions/48873233/is-there-a-way-to-get-correlation-with-string-data-and-a-numerical-value-in-pand

    import pandas as pd
    from collections import Counter

    df = listing_df.copy()
    amen_list = list(df['amenities'])

    # clean extraneous marks
    new_list = [item.strip('[]\' ""').replace('"', '') for item in amen_list] #.replace(' u2013 ', ': ').replace('u2019', "'")

    # split cleaned ammenities on comma
    list_of_lists = []
    for item in new_list:
        new_item = item.split(",")
        list_of_lists.append(new_item)

    # flatten list of lists, then count number of occurrences
    flattened = [val for sublist in list_of_lists for val in sublist]
    counts = Counter(flattened)

    # get counts that are above 500 too keep correlation above 10%
    high_counts = {k: c for k, c in counts.items() if c >= 500}

    top_amen = list(high_counts.keys())

    # find intersection of top amenities with original list
    full_new_list = []
    for each_list in list_of_lists:
        new_new_list = list(set(top_amen).intersection(set(each_list)))
        full_new_list.append(new_new_list)

    # add column to dataframe
    df['amenities'] = full_new_list

    # get correlation of value review scores and each amenity in new dataframe
    s_corr = pd.DataFrame(df.amenities.str.get_dummies(sep=',').corrwith(
        df.review_scores_value / df.review_scores_value.max()))
    s_corr.reset_index(inplace=True)
    s_corr.rename(columns={'index': 'amenity', 0: 'score'}, inplace=True)

    # clean new dataframe and sort values
    for idx, item in enumerate(s_corr['amenity']):
        s_corr.at[idx, 'amenity'] = s_corr.at[idx, 'amenity'].lower().strip('[]\' ""')
    s_corr = s_corr.sort_values(by='score', ascending=False)
    s_corr['score'] = s_corr['score'].round(3)

    amenities_df = s_corr.set_index('amenity')[:20]

    return amenities_df

##############################################################################################################
def get_top_review_terms(reviews_df, hostnames):
    '''
    returns df of top 10 positive and negative review terms by tf-idf
    '''
    import pandas as pd
    import nltk
    nltk.download('stopwords', quiet=True)	
    nltk.download('wordnet', quiet=True)	
    nltk.download('omw-1.4', quiet=True)
    from nltk.corpus import stopwords
    from nltk.tokenize import RegexpTokenizer
    from nltk.stem import WordNetLemmatizer
    from sklearn.feature_extraction.text import TfidfVectorizer
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    tokenizer = RegexpTokenizer(r'\w+')
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    tfIdfVectorizer = TfidfVectorizer()
    sid = SentimentIntensityAnalyzer()
    punc = '!"#$%&()*+,-./:;<=>?@[\]^_`{|}~'  # from string.punctuation...removed apostrophe

    # adding to stop words
    more_stop_words = ['great', 'nice', 'definitely', 'well', 'good', 'loved', 'enjoyed', 'like', 'wonderful', 'thank',
                       'sure', 'thanks', 'thank', 'love', 'better', 'want', 'cool', 'hope', 'truly', 'appreciate',
                       'wish', 'okay',
                       'save', 'yes', 'no', 'share', 'number', 'br', 's', 'u', 'l', 'ok', 'amaze', 'excellent',
                       'fantastic',
                       'awesome', 'friend', 'kind', 'help']
    for word in more_stop_words:
        stop_words.add(word)

    # tokenizing
    tokens = []
    for comment in reviews_df['comments']:
        comment = tokenizer.tokenize(comment.lower().strip().strip(punc))
        tokens.append(comment)

    # lemmatizing
    lemms = []
    for item in tokens:
        l = [lemmatizer.lemmatize(word, pos='v') for word in item]
        lemms.append(l)

    new_tokens = []
    for item in lemms:
        new = [i for i in item if not i in stop_words]  # removing stop words
        new_no_digits = [i for i in new if not i.isdigit()]  # removing numerals
        new_no_hosts = [i for i in new_no_digits if not i in hostnames2]  # removing hostnames
        new_tokens.append(new_no_hosts)

    # getting positive and negative sentiments
    pos_lemms = []
    neg_lemms = []
    for each_list in new_tokens:
        pos = []
        neg = []
        for each_word in each_list:
            if sid.polarity_scores(each_word)['pos'] == 1.0:
                pos.append(each_word)
            elif sid.polarity_scores(each_word)['neg'] == 1.0:
                neg.append(each_word)
        pos_lemms.append(pos)
        neg_lemms.append(neg)

    # creating dataframe of positive and negative terms
    lemms_df = pd.DataFrame({'pos_lemms': pos_lemms, 'neg_lemms': neg_lemms})
    lemms_df['pos_lemms'] = lemms_df['pos_lemms'].astype(str)
    lemms_df['neg_lemms'] = lemms_df['neg_lemms'].astype(str)

    # performing tf-idf
    # adapted from https://stackoverflow.com/questions/45805493/sorting-tfidfvectorizer-output-by-tf-idf-lowest-to-highest-and-vice-versa

    # getting corpi
    pos_corpus = lemms_df['pos_lemms']
    neg_corpus = lemms_df['neg_lemms']

    ## POSITIVE ##
    # fitting model
    tfIdf = tfIdfVectorizer.fit_transform(pos_corpus)

    # getting vocabulary
    terms = tfIdfVectorizer.get_feature_names_out()

    # finding highest ranked words
    sums = tfIdf.sum(axis=0)
    pos_data = {}
    for col, term in enumerate(terms):
        pos_data[term] = sums[0, col]

    pos_data_sorted = sorted(pos_data, key=pos_data.get, reverse=True)

    pos_ranked = {}
    for r in pos_data_sorted:
        pos_ranked[r] = pos_data[r]
    pos_ranked_df = pd.DataFrame.from_dict(pos_ranked, orient='index').reset_index()
    pos_ranked_df = pos_ranked_df.rename(columns={'index': 'pos_word', 0: 'pos_score'})

    ## NEGATIVE ##
    # fitting model
    tfIdf = tfIdfVectorizer.fit_transform(neg_corpus)

    # getting vocabulary
    terms = tfIdfVectorizer.get_feature_names_out()

    # finding highest ranked words
    sums = tfIdf.sum(axis=0)
    neg_data = {}
    for col, term in enumerate(terms):
        neg_data[term] = sums[0, col]
    neg_data_sorted = sorted(neg_data, key=neg_data.get, reverse=True)

    neg_ranked = {}
    for r in neg_data_sorted:
        neg_ranked[r] = neg_data[r]
    neg_ranked_df = pd.DataFrame.from_dict(neg_ranked, orient='index').reset_index()
    neg_ranked_df = neg_ranked_df.rename(columns={'index': 'neg_word', 0: 'neg_score'})

    result = pd.concat([pos_ranked_df, neg_ranked_df], axis=1, join='inner')

    return result[:10]

##############################################################################################################
