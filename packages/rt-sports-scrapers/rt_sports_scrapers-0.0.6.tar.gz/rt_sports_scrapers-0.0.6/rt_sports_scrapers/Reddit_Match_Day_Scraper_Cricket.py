import requests
import pandas as pd
from smack_gsheets import Google_Sheet as gs



def Get_Subreddit(self):
        
    sh=gs.Open_Gsheets("Subreddit_Links")
    wrks=gs.Open_Worksheet(sh,'MatchThreads')
    df=gs.Read_Gsheet(wrks)
    urls=df['URLS'].values
    urls_cleaned = [item for item in urls if not (pd.isnull(item)) == True]
    print(urls_cleaned[0])
    for i in urls_cleaned:
        
        score=[]
        comment=[]
        Link=[]
        subreddit=[]
        
        r=requests.get(i,headers={'User-agent': 'Chrome'})
        body=r.json()
        content1=body[0]
        content2=body[1]

        dt=content1['data']
        children_list1=dt['children']
        t3=children_list1[0]
        t3_data=t3['data']
        selftext=t3_data['selftext']
        title=selftext.split("\n")
        title=title[0]

        data=content2['data']
        children_list=data['children']
        print(children_list[1].keys())

        for j in children_list:
            thread_data=j
            match_data=thread_data['data']
            print(match_data.keys())

            try:
                comment.append(match_data['body'])
                score.append(match_data['score'])
                Link.append(match_data['permalink'])
                subreddit.append(match_data['subreddit'])
            except:
                comment.append("NA")
                score.append('NA')
                Link.append('NA')
                subreddit.append('NA')
                
        results={"Subreddit":subreddit,"Comment":comment,"Score":score,"URL":Link}
        df=pd.DataFrame(results)
        df['Match_Thread']=title
        sheet=gs.Open_Gsheets("Reddit_Match_Thread_Data")
        fname=subreddit[0]+"_"+title
        rows=len(df['Comment'].values)
        try:
            newsheet=gs.Create_Gsheet(df,fname,rows,sheet)
            gs.Update_Gsheet(newsheet,df)
        except:
            worksheet=gs.Open_Worksheet(sheet,fname)
            gs.Update_Gsheet(worksheet,df)

    
