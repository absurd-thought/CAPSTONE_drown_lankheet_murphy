#!/usr/bin/env python
# coding: utf-8

# In[ ]:


def get_top_review_terms(reviews_df):
    '''
    df must have a 'comments' column
    '''
    import pandas as pd
    from nltk.corpus import stopwords
    from nltk.tokenize import RegexpTokenizer
    from nltk.stem import WordNetLemmatizer
    from sklearn.feature_extraction.text import TfidfTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    tokenizer = RegexpTokenizer(r'\w+')
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    tfIdfVectorizer=TfidfVectorizer(use_idf=True)

    for idx, comment in enumerate(reviews_df['comments']):
        if comment==None:
            comment = ""
        reviews_df.at[idx, 'comments'] = comment.lower().strip()
        
    # tokenizing
    tokens = []
    for comment in reviews['comments']:
        comment = tokenizer.tokenize(comment)
        tokens.append(comment)

    # removing stopwords
    new_tokens = []
    for item in tokens:
        new = [i for i in item if not i in stop_words]
        new_tokens.append(new)

    # lemmatizing
    lemms = []
    for item in new_tokens:
        l = []
        for word in item:
            lemm = lemmatizer.lemmatize(word.lower())
            l.append(lemm)
        lemms.append(l)

    reviews_df['lemm'] = lemms
    reviews_df['lemm'] = reviews_df['lemm'].astype(str)
    
    # getting tfidf terms
    corpus = reviews_df['lemm']

    tfIdfVectorizer=TfidfVectorizer(use_idf=True)
    tfIdf = tfIdfVectorizer.fit_transform(corpus)
    tfidf_df = pd.DataFrame(tfIdf[0].T.todense(), index=tfIdfVectorizer.get_feature_names_out(), columns=["TF-IDF"])
    tfidf_df = tfidf_df.sort_values('TF-IDF', ascending=False)

    tfidf_df = tfidf_df.head(3)
    
    return list(tfidf_df.index)



def get_top_amenities(listing_detail_df):
    value_amenities = pd.merge(listing_detail_df['amenities'],listing_detail_df['review_scores_value'],
                               left_index=True, right_index=True)
    value_amenities = value_amenities.dropna()
    
    # correlating amenities with review scores
    # from https://stackoverflow.com/questions/48873233/is-there-a-way-to-get-correlation-with-string-data-and-a-numerical-value-in-pand

    s_corr = pd.DataFrame(value_amenities.amenities.str.get_dummies(sep=',').corrwith(value_amenities.review_scores_value/value_amenities.review_scores_value.max()))
    s_corr.reset_index(inplace=True)
    s_corr.rename(columns={'index':'amenity', 0:'corr'}, inplace=True)
    
    review_associated_amenities=list(s_corr.sort_values(by='corr', ascending=False)['amenity'][:20])
    top_20_amenities = [i.strip('[] ""') for i in review_associated_amenities]
    
    return top_20_amenities
