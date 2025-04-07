import os
from dotenv import load_dotenv
load_dotenv

import pandas as pd
from tqdm import tqdm

from DB_connection import DB_connection

local_path =  os.getenv("LOCAL_PATH")

db_connection = DB_connection()

behaviors           = pd.read_csv(local_path + "/offline_study/mind/data/behaviors.csv")
news                = pd.read_csv(local_path + "/offline_study/mind/data/news.csv")
parameters_adapt    = pd.read_csv(local_path + "/offline_study/mind/data/parameters_adapt.csv")
parameters_mmr      = pd.read_csv(local_path + "/offline_study/mind/data/parameters_mmr.csv")
simulated_behaviors = pd.read_csv(local_path + "/offline_study/mind/data/simulated_behaviors.csv")
UserItem_Matrix     = pd.read_csv(local_path + "/offline_study/mind/data/UserItem_Matrix.csv")
Users               = pd.read_csv(local_path + "/offline_study/mind/data/Users.csv")



def process_impression(impression):
    items = []
    chosen_items = []
    not_chosen_tems =[]
    for item in impression.split(' '):
        items.append(item[0:-2])
        if int(item[-1:]) == 1: 
            chosen_items.append(item[0:-2])
        elif int(item[-1:]) == 0:
            not_chosen_tems.append(item[0:-2])
    return chosen_items,items, not_chosen_tems

def process_behaviors():
    behavior = db_connection.select("SELECT * FROM behaviors")
    impressions = behavior['Impressions']
    chosen_items_column = []
    choice_list_column  = []
    not_chosen_items_column = []
    for impression in tqdm(impressions):
        chosen_items,choice_list,not_chosen_tems = process_impression(impression)
        chosen_items_column.append(str(chosen_items))
        choice_list_column.append(str(choice_list))
        not_chosen_items_column.append(str(not_chosen_tems))
    behavior['chosen_items'] = chosen_items_column
    behavior['recommended_items'] = choice_list_column
    behavior['not_chosen_items'] = not_chosen_items_column
    db_connection.save_df(behavior,'behaviors')    

print('Load tables into database')
db_connection.save_df(behaviors,'behaviors')
db_connection.save_df(news,'news')
db_connection.save_df(parameters_adapt,'parameters_adapt')
db_connection.save_df(parameters_mmr,'parameters_mmr')
db_connection.save_df(simulated_behaviors,'simulated_behaviors')
db_connection.save_df(UserItem_Matrix,'UserItem_Matrix')
db_connection.save_df(Users,'Users')

print('Process behaviors')
process_behaviors()
print('Process behaviors done')




