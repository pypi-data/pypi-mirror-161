#!/usr/bin/env python
# coding: utf-8

# In[177]:


import twint

import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe

import requests

import pandas as pd


import nest_asyncio


# In[169]:



def Get_Tweets(self,username,no_tweets):
    
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
        self.Get_Tweets(username,no_tweets)
    
    filename="Twitter_Data_"+username
    return(tweets_df,filename)


# In[141]:


def Open_Gsheets(self,name):
    gc = gspread.service_account(filename='mycredentials.json')
    sheet=gc.open(name)
    return(sheet)


# In[135]:


def Open_Worksheet(self,sheets,worksheet_name):
    wrksheet=sheets.worksheet(worksheet_name)
    return wrksheet


# In[96]:


def Create_Gsheet(self,df,fname,rows,sheet):
    cols=len(df.columns)
    newsheet = sheet.add_worksheet(title=fname, rows=rows, cols=cols)
    return(newsheet)


# In[97]:


def Update_Gsheet(self,newsheet,df):
    set_with_dataframe(newsheet, df)
    


# In[157]:


def Read_Gsheet(self,sheets):
    df=get_as_dataframe(sheets)
    return(df)


# In[170]:


def Search(self,filename,Sheets):
    worksheet_list = Sheets.worksheets()
    worksheet_name=[]
    for i in worksheet_list:
        worksheet_obj=str(i)
        splitter=worksheet_obj.split(" ")
        worksheet_filename=splitter[1]
        worksheet=worksheet_filename.split(".")
        worksheet_name.append(worksheet_name[0])
    
    if filename in worksheet:
        return True
    else:
        return False


# In[176]:
def get_data():
    sheets=Open_Gsheets("Journalists")
    wks=sheets.worksheet("Journalists")
    df=Read_Gsheet(wks)
    usernames=df["Usernames"].values.tolist()
    Sheet=Open_Gsheets("Athletic_Tweets")
    for i in usernames:
        tweets_df,fname=Get_Tweets(i,10)
        try:
            newsheet=Create_Gsheet(tweets_df,fname,10,Sheet)
            Update_Gsheet(newsheet,tweets_df)
        except:
            worksheet=Open_Worksheet(Sheet,fname)
            Update_Gsheet(worksheet,tweets_df)





