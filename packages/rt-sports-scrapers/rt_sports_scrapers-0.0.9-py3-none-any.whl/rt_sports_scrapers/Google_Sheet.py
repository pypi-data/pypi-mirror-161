#!/usr/bin/env python
# coding: utf-8

# In[1]:


import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe


# In[2]:

def Open_Gsheets(name):
    gc = gspread.service_account(filename="D:\Work\Internship\Smack\mycredentials.json")
    sheet=gc.open(name)
    return(sheet)


# In[3]:


def Open_Worksheet(self,sheets,worksheet_name):
    wrksheet=sheets.worksheet(worksheet_name)
    return wrksheet


# In[4]:


def Create_Gsheet(self,df,fname,rows,sheet):
    cols=len(df.columns)
    newsheet = sheet.add_worksheet(title=fname, rows=rows, cols=cols)
    return(newsheet)


# In[5]:


def Update_Gsheet(self,newsheet,df):
    set_with_dataframe(newsheet, df)
    


# In[6]:


def Read_Gsheet(self,sheets):
    df=get_as_dataframe(sheets)
    return(df)


# In[ ]:




