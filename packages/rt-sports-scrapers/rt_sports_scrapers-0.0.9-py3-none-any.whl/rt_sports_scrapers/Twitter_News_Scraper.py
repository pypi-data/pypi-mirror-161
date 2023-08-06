#!/usr/bin/env python
# coding: utf-8

# In[177]:


import twint

from smack_gsheets import Google_Sheet as gs

import requests

import pandas as pd


import nest_asyncio


# In[169]:



def Get_Tweets(username,no_tweets):
    
    tweets_df=pd.DataFrame()
    try:
        c = twint.Config()
        c.Username = username
        c.Limit = no_tweets
        c.Store_csv = True
        c.Pandas=True
        twint.run.Search(c)
        tweets_df = twint.storage.panda.Tweets_df
    except:
        nest_asyncio.apply()
        Get_Tweets(username,no_tweets)
    
    filename="Twitter_Data_"+username
    return(tweets_df,filename)





def get_data():
    sheets=gs.Open_Gsheets("Journalists")
    wks=gs.Open_Worksheet(sheets,"Journalists")
    df=gs.Read_Gsheet(wks)
    usernames=df["Usernames"].values.tolist()
    Sheet=gs.Open_Gsheets("Athletic_Tweets")
    for i in usernames:
        tweets_df,fname=Get_Tweets(i,10)
        try:
            newsheet=gs.Create_Gsheet(tweets_df,fname,10,Sheet)
            gs.Update_Gsheet(newsheet,tweets_df)
        except:
            worksheet=gs.Open_Worksheet(Sheet,fname)
            gs.Update_Gsheet(worksheet,tweets_df)





