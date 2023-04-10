#!/usr/bin/env python
# coding: utf-8

# In[36]:


## Lets import our requirements
import boto3
import pandas as pd
#import psycopg2
import pymysql
from sqlalchemy import create_engine
import os
import sqlite3
import sys
parentDirectory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.insert(0,parentDirectory)
from secrets import secrets
import mysql.connector

import re
import gzip
import shutil
import urllib


# In[ ]:





# In[62]:


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)


# In[63]:


#connections
#def create_connection():
endpoint = 'drown-murphy-lankheet.cluster-ceswqg9qwa9i.us-east-1.rds.amazonaws.com'#secrets.get('DATABASE_ENDPOINT')
user = secrets.get('DATABASE_USER')
password = secrets.get('DATABASE_PASSWORD')
port=secrets.get('DATABASE_PORT')
connection = create_engine(f'mysql+pymysql://{user}:{password}@{endpoint}:{port}/Capstone', pool_recycle=3600,  connect_args={'connect_timeout': 10});
    
connect=mysql.connector.connect(host=endpoint, database='Capstone', user=user, password=password)
cursor = connect.cursor()
    #return cursor
#cursor=create_connection()


# In[17]:





# In[39]:


def handle_listing(listing_detail, city):
    listing_detail.rename(columns={'id':'listing_id', 'name':'listing_name'}, inplace=True)
    listing_detail['price']=pd.to_numeric(listing_detail['price'].str[1:].str.replace(',','')) #changing price column to numeric field
    listing_detail['host_acceptance_rate']=pd.to_numeric(listing_detail['host_acceptance_rate'].str[:-1])/100#.apply(pd.to_numeric)/100 #change to numeric
    listing_detail['host_response_rate']=pd.to_numeric(listing_detail['host_response_rate'].str[:-1])/100#.apply(pd.to_numeric)/100

    #converting to datetime
    listing_detail[['last_scraped', 'host_since','calendar_last_scraped','first_review','last_review']]=listing_detail[['last_scraped', 'host_since','calendar_last_scraped','first_review','last_review']].apply(pd.to_datetime)
    
    #converting to 1/0 (better for modeling and summarization)
    listing_detail[['host_is_superhost','host_has_profile_pic','host_identity_verified','has_availability','instant_bookable']]=listing_detail[['host_is_superhost','host_has_profile_pic','host_identity_verified','has_availability','instant_bookable']].replace('t',1).replace('f',0)
    listing_detail['scrape_city']=city
    
    #Removing source as it is not always present
    listing_detail.drop(['source'],axis=1, errors='ignore',inplace=True)
    
    #Inserting into database
    listing_detail.to_csv('data.csv', index=False)
    sql_query = "LOAD DATA LOCAL INFILE 'data.csv' INTO TABLE listing_detail_stage FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES;"
    cursor.execute(sql_query)
    connect.commit()

    #used to first create the database table
    #listing_detail.to_sql('listing_detail_stage',con=connection, if_exists='replace',index=False, chunksize=1000, method='multi')


# In[28]:


def handle_calendar(calendar, scrapedate, city):
    calendar['price']=pd.to_numeric(calendar['price'].str[1:].str.replace(',','')) #changing price column to numeric field
    calendar['adjusted_price']=pd.to_numeric(calendar['adjusted_price'].str[1:].str.replace(',','')) #changing price column to numeric field
    calendar['date']=pd.to_datetime(calendar['date'],infer_datetime_format=True)
    calendar['available']=calendar['available'].replace('t',1).replace('f',0)
    calendar.rename(columns={'date':'calendar_date'},inplace=True)
    calendar['scrape_date']=pd.to_datetime(scrapedate,infer_datetime_format=True)
    calendar['scrape_city']=city
    
    #checking to see if columns match for database insert
    #if list(calendar.columns)==['listing_id', 'calendar_date', 'available', 'price', 'adjusted_price','minimum_nights', 'maximum_nights', 'scrape_date', 'scrape_city']:
    
    #Inserting into database
    calendar.to_csv('data.csv', index=False)
    sql_query = "LOAD DATA LOCAL INFILE 'data.csv' INTO TABLE calendar_stage FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES;"
    cursor.execute(sql_query)
    connect.commit()
    
    #used to first create the database table
    #calendar.to_sql('calendar_stage',con=connection, if_exists='replace',index=False, chunksize=1000, method='multi')


# In[40]:


def handle_reviews(reviews, city):
    reviews['date']=reviews['date'].apply(pd.to_datetime)
    reviews.rename(columns={'date':'review_date'}, inplace=True)
    reviews.to_csv('data.csv', index=False)
    reviews['scrape_city']=city
    
    reviews.to_csv('data.csv', index=False)
    sql_query = "LOAD DATA LOCAL INFILE 'data.csv' INTO TABLE reviews_stage FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES;"
    cursor.execute(sql_query)
    connect.commit()
    
    #used to first create the database table
    #reviews.to_sql('reviews_stage',con=connection, if_exists='replace',index=False)


# In[ ]:





# In[59]:


filelist = ['http://data.insideairbnb.com/united-states/nc/asheville/2022-12-21/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/nc/asheville/2022-12-21/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/nc/asheville/2022-12-21/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/nc/asheville/2022-09-14/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/nc/asheville/2022-09-14/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/nc/asheville/2022-06-11/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/nc/asheville/2022-06-11/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/nc/asheville/2022-03-19/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/nc/asheville/2022-03-19/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/tx/austin/2022-12-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/tx/austin/2022-12-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/tx/austin/2022-12-15/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/tx/austin/2022-09-12/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/tx/austin/2022-09-12/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/tx/austin/2022-06-08/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/tx/austin/2022-06-08/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/tx/austin/2022-03-12/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/tx/austin/2022-03-12/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ma/boston/2022-12-21/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ma/boston/2022-12-21/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ma/boston/2022-12-21/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ma/boston/2022-09-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ma/boston/2022-09-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ma/boston/2022-06-13/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ma/boston/2022-06-13/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ma/boston/2022-03-20/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ma/boston/2022-03-20/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/fl/broward-county/2022-12-28/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/fl/broward-county/2022-12-28/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/fl/broward-county/2022-12-28/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/fl/broward-county/2022-09-21/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/fl/broward-county/2022-09-21/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/fl/broward-county/2022-06-17/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/fl/broward-county/2022-06-17/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/fl/broward-county/2022-03-24/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/fl/broward-county/2022-03-24/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ma/cambridge/2022-12-29/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ma/cambridge/2022-12-29/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ma/cambridge/2022-12-29/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ma/cambridge/2022-09-22/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ma/cambridge/2022-09-22/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ma/cambridge/2022-06-22/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ma/cambridge/2022-06-22/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ma/cambridge/2022-03-27/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ma/cambridge/2022-03-27/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/il/chicago/2022-12-20/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/il/chicago/2022-12-20/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/il/chicago/2022-12-20/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/il/chicago/2022-09-14/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/il/chicago/2022-09-14/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/il/chicago/2022-06-10/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/il/chicago/2022-06-10/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/il/chicago/2022-03-17/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/il/chicago/2022-03-17/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/nv/clark-county-nv/2022-12-21/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/nv/clark-county-nv/2022-12-21/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/nv/clark-county-nv/2022-12-21/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/nv/clark-county-nv/2022-09-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/nv/clark-county-nv/2022-09-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/nv/clark-county-nv/2022-06-13/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/nv/clark-county-nv/2022-06-13/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/nv/clark-county-nv/2022-03-20/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/nv/clark-county-nv/2022-03-20/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/oh/columbus/2022-12-28/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/oh/columbus/2022-12-28/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/oh/columbus/2022-12-28/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/oh/columbus/2022-09-21/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/oh/columbus/2022-09-21/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/oh/columbus/2022-06-20/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/oh/columbus/2022-06-20/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/oh/columbus/2022-03-25/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/oh/columbus/2022-03-25/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/tx/dallas/2023-01-07/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/tx/dallas/2023-01-07/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/tx/dallas/2023-01-07/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/tx/dallas/2022-09-14/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/tx/dallas/2022-09-14/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/tx/dallas/2022-06-10/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/tx/dallas/2022-06-10/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/tx/dallas/2022-03-17/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/tx/dallas/2022-03-17/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/co/denver/2022-12-30/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/co/denver/2022-12-30/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/co/denver/2022-12-30/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/co/denver/2022-09-26/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/co/denver/2022-09-26/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/co/denver/2022-06-27/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/co/denver/2022-06-27/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/co/denver/2022-03-29/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/co/denver/2022-03-29/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/tx/fort-worth/2022-12-13/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/tx/fort-worth/2022-12-13/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/tx/fort-worth/2022-12-13/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/tx/fort-worth/2022-09-11/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/tx/fort-worth/2022-09-11/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/tx/fort-worth/2022-06-08/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/tx/fort-worth/2022-06-08/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/hi/hawaii/2022-12-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/hi/hawaii/2022-12-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/hi/hawaii/2022-12-15/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/hi/hawaii/2022-09-12/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/hi/hawaii/2022-09-12/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/hi/hawaii/2022-06-08/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/hi/hawaii/2022-06-08/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/hi/hawaii/2022-03-12/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/hi/hawaii/2022-03-12/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/nj/jersey-city/2022-12-24/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/nj/jersey-city/2022-12-24/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/nj/jersey-city/2022-12-24/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/nj/jersey-city/2022-09-18/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/nj/jersey-city/2022-09-18/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/nj/jersey-city/2022-06-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/nj/jersey-city/2022-06-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/nj/jersey-city/2022-03-23/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/nj/jersey-city/2022-03-23/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/los-angeles/2022-12-06/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/los-angeles/2022-12-06/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/los-angeles/2022-12-06/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ca/los-angeles/2022-09-09/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/los-angeles/2022-09-09/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/los-angeles/2022-06-06/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/los-angeles/2022-06-06/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/los-angeles/2022-03-08/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/los-angeles/2022-03-08/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/tn/nashville/2022-12-21/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/tn/nashville/2022-12-21/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/tn/nashville/2022-12-21/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/tn/nashville/2022-09-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/tn/nashville/2022-09-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/tn/nashville/2022-06-13/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/tn/nashville/2022-06-13/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/tn/nashville/2022-03-20/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/tn/nashville/2022-03-20/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/la/new-orleans/2022-12-06/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/la/new-orleans/2022-12-06/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/la/new-orleans/2022-12-06/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/la/new-orleans/2022-09-09/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/la/new-orleans/2022-09-09/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/la/new-orleans/2022-06-05/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/la/new-orleans/2022-06-05/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/la/new-orleans/2022-03-08/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/la/new-orleans/2022-03-08/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ny/new-york-city/2022-12-04/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ny/new-york-city/2022-12-04/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ny/new-york-city/2022-12-04/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ny/new-york-city/2022-09-07/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ny/new-york-city/2022-09-07/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ny/new-york-city/2022-06-03/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ny/new-york-city/2022-06-03/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ny/new-york-city/2022-03-05/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ny/new-york-city/2022-03-05/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/nj/newark/2022-12-30/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/nj/newark/2022-12-30/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/nj/newark/2022-12-30/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/nj/newark/2022-09-28/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/nj/newark/2022-09-28/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/nj/newark/2022-06-27/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/nj/newark/2022-06-27/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/nj/newark/2022-03-31/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/nj/newark/2022-03-31/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/oakland/2022-12-24/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/oakland/2022-12-24/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/oakland/2022-12-24/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ca/oakland/2022-09-18/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/oakland/2022-09-18/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/oakland/2022-06-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/oakland/2022-06-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/oakland/2022-03-23/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/oakland/2022-03-23/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-12-31/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-12-31/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-12-31/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-09-28/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-09-28/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-12-31/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-12-31/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-03-05/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-03-05/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-12-23/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-12-23/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-12-23/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-09-16/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-09-16/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-06-14/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-06-14/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-03-21/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-03-21/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-12-31/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-12-31/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-12-31/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-09-28/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-09-28/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-06-29/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-06-29/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-03-31/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-03-31/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-12-27/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-12-27/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-12-27/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-09-19/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-09-19/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-06-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-06-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-03-23/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-03-23/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-12-24/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-12-24/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-12-24/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-09-18/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-09-18/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-06-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-06-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-03-23/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-03-23/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-francisco/2022-12-04/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-francisco/2022-12-04/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-francisco/2022-12-04/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-francisco/2022-09-07/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-francisco/2022-09-07/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-francisco/2022-06-03/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-francisco/2022-06-03/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-12-27/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-12-27/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-12-27/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-09-19/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-09-19/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-06-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-06-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-03-23/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-03-23/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-12-27/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-12-27/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-12-27/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-09-19/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-09-19/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-06-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-06-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-03-23/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-03-23/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-12-30/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-12-30/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-12-30/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-09-28/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-09-28/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-06-27/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-06-27/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-03-31/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-03-31/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-12-24/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-12-24/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-12-24/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-09-18/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-09-18/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-06-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-06-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-03-23/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-03-23/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-12-23/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-12-23/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-12-23/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-09-16/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-09-16/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-06-14/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-06-14/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-03-21/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-03-21/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-12-20/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-12-20/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-12-20/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-09-14/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-09-14/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-06-11/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-06-11/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-03-19/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-03-19/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/oakland/2022-12-24/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ca/oakland/2022-09-18/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/oakland/2022-09-18/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/oakland/2022-06-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/oakland/2022-06-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/oakland/2022-03-23/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/oakland/2022-03-23/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-12-31/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-12-31/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-12-31/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-09-28/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-09-28/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-12-31/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-12-31/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-03-05/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/pacific-grove/2022-03-05/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-12-23/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-12-23/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-12-23/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-09-16/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-09-16/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-06-14/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-06-14/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-03-21/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/or/portland/2022-03-21/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-12-31/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-12-31/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-12-31/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-09-28/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-09-28/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-06-29/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-06-29/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-03-31/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ri/rhode-island/2022-03-31/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-12-27/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-12-27/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-12-27/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-09-19/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-09-19/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-06-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-06-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-03-23/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/or/salem-or/2022-03-23/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-12-24/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-12-24/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-12-24/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-09-18/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-09-18/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-06-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-06-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-03-23/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-diego/2022-03-23/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-francisco/2022-12-04/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-francisco/2022-12-04/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-francisco/2022-12-04/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-francisco/2022-09-07/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-francisco/2022-09-07/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-francisco/2022-06-03/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-francisco/2022-06-03/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-12-27/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-12-27/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-12-27/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-09-19/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-09-19/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-06-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-06-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-03-23/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/san-mateo-county/2022-03-23/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-12-27/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-12-27/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-12-27/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-09-19/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-09-19/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-06-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-06-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-03-23/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-clara-county/2022-03-23/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-12-30/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-12-30/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-12-30/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-09-28/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-09-28/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-06-27/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-06-27/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-03-31/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/ca/santa-cruz-county/2022-03-31/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-12-24/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-12-24/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-12-24/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-09-18/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-09-18/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-06-15/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-06-15/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-03-23/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/wa/seattle/2022-03-23/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-12-23/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-12-23/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-12-23/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-09-16/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-09-16/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-06-14/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-06-14/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-03-21/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/mn/twin-cities-msa/2022-03-21/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-12-20/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-12-20/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-12-20/data/reviews.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-09-14/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-09-14/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-06-11/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-06-11/data/calendar.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-03-19/data/listings.csv.gz',
'http://data.insideairbnb.com/united-states/dc/washington-dc/2022-03-19/data/calendar.csv.gz']


# In[65]:


##download files, call dataloading functions

for file in filelist:
    file_split = file[46:].split("/")
    file_name = file_split[0]+'_'+file_split[1]+'_'+file_split[3]
    city=file_split[0] #Getting city name to add to sql tables
    scrapedate=file_split[1]
    urllib.request.urlretrieve(file, file_name)

    with gzip.open(file_name, 'rb') as f_in:
        with open(file_name[:-3], 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
            print(file_name)
            df = pd.read_csv(file_name)
            if "listing" in file_name:
                handle_listing(df, city)
            if "calendar" in file_name:
                handle_calendar(df, scrapedate, city)
            if "review" in file_name:
                handle_reviews(df,city)
connect.close()

