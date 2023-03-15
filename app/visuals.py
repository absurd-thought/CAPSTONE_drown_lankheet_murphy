## VISUALS
def get_amenities_visual(amenities_df):#, amen):
    '''
    Uses the listing df to create an ordered heatmap of top 20 recommended amenities
    '''
    import pandas as pd
    import altair as alt

    amenities_df = amenities_df.reset_index()

    chart = alt.Chart(amenities_df).mark_rect().encode(
        y=alt.Y('amenity:N', sort=alt.EncodingSortField(field='score',
                                                        order='descending'),
                title=None,
                axis=alt.Axis(labelLimit=200)),
        color=alt.Color('score:Q', legend=None, scale=alt.Scale(scheme='purplebluegreen'))
    ).properties(width=275, height=600)

    return chart

################################################################################################################
def get_review_wordcloud(terms_df, pos_or_neg):
    '''
    Uses the terms_df to make a word cloud of top (up to) 10 review terms
    pos_or_neg = string of 'pos' or 'neg'
    '''
    import pandas as pd
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt

    terms_dict = terms_df.set_index(pos_or_neg+'_word')[pos_or_neg+'_score'].to_dict()

    # adapted from https://stackoverflow.com/questions/61916096/word-cloud-built-out-of-tf-idf-vectorizer-function
    if pos_or_neg == 'pos':
        cloud = WordCloud(background_color='#0e1117', max_words=10,
                          margin=0, colormap='winter').generate_from_frequencies(terms_dict)
    else:
         cloud = WordCloud(background_color='#0e1117', max_words=10,
                          margin=0, colormap='autumn').generate_from_frequencies(terms_dict)       

    # adapted from https://towardsdatascience.com/simple-wordcloud-in-python-2ae54a9f58e5
    def plot_cloud(wordcloud):
        plt.figure(figsize=(6, 4),)
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.tight_layout(pad=0);

    return plot_cloud(cloud)
