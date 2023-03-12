## NLP FUNCTIONS

##############################################################################################################
def get_top_amenities(listing_df):
    # correlating amenities with review scores
    # adapted from https://stackoverflow.com/questions/48873233/is-there-a-way-to-get-correlation-with-string-data-and-a-numerical-value-in-pand

    import pandas as pd
    from collections import Counter

    df = listing_df.copy()
    amen_list = list(df['amenities'])

    new_list = [item.strip('[]\' ""').replace('"', '') for item in amen_list] #.replace(' u2013 ', ': ').replace('u2019', "'")

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
    returns df of top 10 review terms by frequency
    '''
    import pandas as pd
    import nltk
    from collections import Counter
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    from nltk.corpus import stopwords
    from nltk.tokenize import RegexpTokenizer
    from nltk.stem import WordNetLemmatizer
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    tokenizer = RegexpTokenizer(r'\w+')
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    sid = SentimentIntensityAnalyzer()
    punc = '!"#$%&()*+,-./:;<=>?@[\]^_`{|}~'  # from string.punctuation...removed apostrophe

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
        new_no_hosts = [i for i in new_no_digits if not i in hostnames]  # removing hostnames
        new_tokens.append(new_no_hosts)

    # lemmatizing
    lemms = []
    for item in new_tokens:
        l = []
        for word in item:
            lemm = lemmatizer.lemmatize(word)
            l.append(lemm)
        lemms.append(l)

    # getting only positive sentiments
    pos_tokens = []
    for each_list in lemms:
        tok2 = []
        for each_word in each_list:
            if sid.polarity_scores(each_word)['compound'] >= 0.5 or sid.polarity_scores(each_word)['pos'] == 1.0:
                tok2.append(each_word)
        pos_tokens.append(tok2)

    flat_list_corpus = [item for sublist in pos_tokens for item in sublist]
    c = Counter(flat_list_corpus)
    data = c.most_common(10)
    df = pd.DataFrame.from_records(data, columns=['term', 'freq'])

    return df

##############################################################################################################
