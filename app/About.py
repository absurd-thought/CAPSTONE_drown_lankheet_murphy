#!/usr/bin/env python
# coding: utf-8

import streamlit as st

# setting page configuration
st.set_page_config(layout="wide", page_title='And That Means Comfort', page_icon='https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f9d9-200d-2642-fe0f.png',
                   menu_items={
                       'About': "A UMSI Capstone project"
                   }
                   )


## adding title to streamlit.io
st.title(":blue[And That Means Comfort: Optimizing Airbnb Listings]")

st.markdown(
    """
    ### A dynamic Airbnb tool for hosts.
    Find out which amenities add the most perceived value to your home, explore terms to include in your description, and predict your best price!
    
    **👈 Select a feature from the sidebar** to help create your listing
    
    ### Want to learn more?
    - Check out the full report of how we did it at [our blog post](https://medium.com/@gdrown/and-that-means-comfort-optimizing-airbnb-listings-fbc0ce1e052d)
    - Create your own Airbnb web app like this with our [GitHub](https://github.com/absurd-thought/CAPSTONE_drown_lankheet_murphy)
"""
)
