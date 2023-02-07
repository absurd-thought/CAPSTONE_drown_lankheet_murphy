#!/usr/bin/env python
# coding: utf-8

# In[ ]:


def get_top_review_terms(reviews_df):
    '''
    df must have a 'comments' column
    '''
    from nltk.corpus import stopwords
    from nltk.tokenize import RegexpTokenizer
    from nltk.stem import WordNetLemmatizer
    
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

