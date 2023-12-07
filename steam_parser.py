#Steam Parser Api
import requests
import pandas as pd
import numpy as np
import time

"""
API INFO: "steamspy.com/api.php?request=tags&page=1 "
"""

def get_request(url, parameters=None):
    try:
        response = requests.get(url=url, params=parameters)
    except SSLError as s:
        print('SSL Error:', s)
        
        for i in range(5, 0, -1):
            print('\rWaiting... ({})'.format(i), end='')
            time.sleep(1)
        print('\rRetrying.' + ' '*10)
        
        # recusively try again
        return get_request(url, parameters)
    
    if response:
        return response.json()
    else:
        # response is none usually means too many requests. Wait and try again 
        print('No response, waiting 10 seconds...')
        time.sleep(10)
        print('Retrying.')
        return get_request(url, parameters)

url = "https://steamspy.com/api.php"
parameters = {"request": "all"}

# request 'all' from steam spy and parse into dataframe
json_data = get_request(url, parameters=parameters)
game_data = pd.DataFrame.from_dict(json_data, orient='index')
game_id = list(game_data["appid"].drop_duplicates())[0:5]
## Generate the final dataframes for later concatination
df_parser = pd.DataFrame()
df_tags = pd.DataFrame()

## Loop through the Api for every game id (once for review data, once for tag data)
for i in game_id:
    response = requests.get(url=f"https://store.steampowered.com/appreviews/{i}?json=1")
    json_data = response.json()
    #json_data = json_data
    review_data = pd.DataFrame.from_dict(json_data, orient='index')
    this = json_data["reviews"]
    ## Cleaning the reviews
    review_cleaned = pd.DataFrame.from_records(this)
    review_cleaned["appid"] = i
    review_cleaned = review_cleaned.merge(game_data[["appid","name"]], on = "appid")
    
    ## Getting Author Info (dirty fix with the try)
    try:
        that = [review_cleaned["author"][0]]
        author_data = pd.DataFrame.from_dict(that)
        author_data["appid"] = i
        review_cleaned = review_cleaned.merge(author_data[["appid","steamid"]], on = "appid")
    except: None

    ## Concat the review texts and info to the df_parser table
    df_parser = pd.concat([df_parser,review_cleaned], ignore_index=True)

    ## Get the Tag data
    response = requests.get(url=f"https://steamspy.com/api.php?request=appdetails&appid={i}")
    json_data = response.json()
    review_data = pd.DataFrame.from_dict(json_data, orient='index')
    tag_dicts = json_data["tags"]
    tag_data = pd.DataFrame.from_dict(tag_dicts, orient='index').reset_index().rename(columns={"index":"tag"})
    tag_data["appid"] = i
    ## Concat the tag_data to df_tags to aggreagte all the values per appid
    df_tags = pd.concat([df_tags,tag_data[["appid","tag"]]], ignore_index=True)


df_parser = df_parser.drop(columns = "author")

df_api = df_parser.merge(game_data[["appid","price","developer","publisher"]], on = "appid")


