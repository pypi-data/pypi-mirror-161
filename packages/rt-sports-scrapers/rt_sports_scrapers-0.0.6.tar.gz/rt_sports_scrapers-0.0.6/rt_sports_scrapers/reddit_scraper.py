import requests
import pandas as pd
from smack_gsheets import Google_Sheet as gs
#from reddit.json_trial.Google_Sheet import Open_Gsheets



def get_subreddit_data(self):
    
    sh=gs.Open_Gsheets("Subreddit_Links")
    wrks=gs.Open_Worksheet(sh,'Urls')
    df=gs.Read_Gsheet(wrks)
    urls=df['URLs'].values
    pages=df['No:Pages']
    urls_cleaned = [item for item in urls if not (pd.isnull(item)) == True]
    pages_cleaned=[item for item in pages if not(pd.isnull(item)) == True]
    
    for i in urls_cleaned:
        tag=[]
        name=[]
        title=[]
        down_vote=[]
        up_vote=[]
        subreddit_link=[]
        comments=[]
        videos=[]
        media_url=[]
        count=0
        df=pd.DataFrame()
        next_page=''
        after=""

        for k in pages_cleaned:
            url=i+after
            r = requests.get(url, headers={'User-agent': 'Chrome'})
            body = r.json()
            data=body['data']
            next_page=data['after']
            rows=data['dist']
            after=""
            after="?after="+next_page
            children=data['children']
            
            for j in children:
                print(url)
                children_data=j['data']
                name.append(children_data['subreddit'])
                try:
                    tag_dictionary=children_data['link_flair_richtext'][-1]
                    tag.append(tag_dictionary['t'])
                except:
                    tag.append("")
                title.append(children_data['title'])
                up_vote.append(children_data['ups'])
                down_vote.append(children_data['downs'])
                subreddit_link.append(children_data['permalink'])
                comments.append(children_data['num_comments'])
                is_video=children_data['is_video']
                if(is_video):
                    reddit_video=children_data['secure_media']
                    video_data=reddit_video['reddit_video']
                    video_url=video_data['fallback_url']
                    videos.append(video_url)
                    print(video_url)
                else:
                    videos.append(is_video)
                
                try:
                    media_url.append(children_data['url'])
                except:
                    media_url.append("NA")
            
            consolidated_data={'Name':name,'Tags':tag,'Title':title,'Up_Votes':up_vote,'Down_Votes':down_vote,'url':subreddit_link,
                                "Media_URL":media_url,"Videos":videos,"comments":comments}
            
            df=pd.DataFrame(consolidated_data)

            sheet=gs.Open_Gsheets("Reddit_Data")
            fname=name[0]+"_"+"Data"
            
            try:
                newsheet=gs.Create_Gsheet(df,fname,rows*k,sheet)
                gs.Update_Gsheet(newsheet,df)
            except:
                worksheet=gs.Open_Worksheet(sheet,fname)
                gs.Update_Gsheet(worksheet,df)
            "?after="+next_page
