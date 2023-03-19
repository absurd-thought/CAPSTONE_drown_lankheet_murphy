## NLP FUNCTIONS

def get_top_amenities(listing_df):
    # correlating amenities with review scores
    # adapted from https://stackoverflow.com/questions/48873233/is-there-a-way-to-get-correlation-with-string-data-and-a-numerical-value-in-pand

    import pandas as pd
    from collections import Counter

    df = listing_df.copy()
    amen_list = list(df['amenities'])

    new_list = [item.strip('[]\' ""').replace(' u2013 ', ': ').replace('u2019', "'").replace('"', '') for item in
                amen_list]

    list_of_lists = []
    for item in new_list:
        new_item = item.split(",")
        list_of_lists.append(new_item)

    flattened = [val for sublist in list_of_lists for val in sublist]
    counts = Counter(flattened)

    high_counts = {k: c for k, c in counts.items() if c >= 500}

    top_amen = list(high_counts.keys())

    full_new_list = []
    for each_list in list_of_lists:
        new_new_list = list(set(top_amen).intersection(set(each_list)))
        full_new_list.append(new_new_list)

    df['amenities'] = full_new_list

    s_corr = pd.DataFrame(df.amenities.str.get_dummies(sep=',').corrwith(
        df.review_scores_value / df.review_scores_value.max()))
    s_corr.reset_index(inplace=True)
    s_corr.rename(columns={'index': 'amenity', 0: 'score'}, inplace=True)

    for idx, item in enumerate(s_corr['amenity']):
        s_corr.at[idx, 'amenity'] = s_corr.at[idx, 'amenity'].lower().strip('[]\' ""')
    s_corr = s_corr.sort_values(by='score', ascending=False)
    s_corr['score'] = s_corr['score'].round(3)

    amenities_df = s_corr.set_index('amenity')[:20]

    return amenities_df


##############################################################################################################
def get_top_review_terms(reviews_df, hostnames):
    '''
    returns df of top 10 terms most correlated with get_value_review score
    '''
    import pandas as pd
    import nltk
    nltk.download('stopwords')
    from nltk.corpus import stopwords
    from nltk.tokenize import RegexpTokenizer
    from nltk.stem import WordNetLemmatizer
    from sklearn.feature_extraction.text import TfidfTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    tokenizer = RegexpTokenizer(r'\w+')
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    tfIdfVectorizer = TfidfVectorizer()
    sid = SentimentIntensityAnalyzer()
    punc = '!"#$%&()*+,-./:;<=>?@[\]^_`{|}~'  # from string.punctuation...removed single quote

    reviews_df = reviews_df.dropna()

    # tokenizing
    tokens = []
    for comment in reviews_df['comments']:
        comment = tokenizer.tokenize(comment.lower().strip().strip(punc))
        tokens.append(comment)

    # removing stopwords
    stop_words.add('br')  # breaks in lines show up as 'br'
    stop_words.add('s')  # 's' is a result of possessives

    new_tokens = []
    for item in tokens:
        new = [i for i in item if not i in stop_words]
        new_no_digits = [i for i in new if not i.isdigit()]  # removing numerals
        new_tokens.append(new_no_digits)

    # lemmatizing
    lemms = []
    for item in new_tokens:
        l = []
        for word in item:
            lemm = lemmatizer.lemmatize(word)
            l.append(lemm)
        lemms.append(l)

    # getting only positive sentiments
    pos_lemms = []
    for each_list in lemms:
        lemms2 = []
        for each_word in each_list:
            if sid.polarity_scores(each_word)['compound'] >= 0.5 or sid.polarity_scores(each_word)['pos'] == 1.0:
                lemms2.append(each_word)
        pos_lemms.append(lemms2)

    reviews_df['lemm'] = pos_lemms
    reviews_df['lemm'] = reviews_df['lemm'].astype(str)

    # getting tfidf terms
    corpus = reviews_df['lemm']

    tfIdf = tfIdfVectorizer.fit_transform(corpus)
    tfidf_df = pd.DataFrame(tfIdf[0].T.todense(), index=tfIdfVectorizer.get_feature_names_out(), columns=["TF-IDF"])
    tfidf_df = tfidf_df.sort_values('TF-IDF', ascending=False)

    tfidf_df = tfidf_df.reset_index()
    tfidf_df.rename(columns={'index': 'word'}, inplace=True)
    tfidf_df = tfidf_df[~tfidf_df['word'].isin(hostnames)]

    return tfidf_df.head(10)