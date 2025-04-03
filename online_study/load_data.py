import os
from dotenv import load_dotenv
load_dotenv()

import pandas as pd

from DB_connection import DB_connection


local_path =  os.getenv("LOCAL_PATH")

# Load the data for training phase 
rating_df = pd.read_csv(local_path + "/online_study/data/training_phase/rating.csv")
user_df   = pd.read_csv(local_path + "/online_study/data/training_phase/user.csv")
video_df  = pd.read_csv(local_path + "/online_study/data/training_phase/video.csv")

db_connection = DB_connection('training')
db_connection.save_table_in_db(rating_df,'rating')
db_connection.save_table_in_db(user_df,'user')
db_connection.save_table_in_db(video_df,'video')
db_connection.close()


# Load the data for experiment phase
rating_df   = pd.read_csv(local_path + "/online_study/data/experiment_phase/rating.csv")
user_df     = pd.read_csv(local_path + "/online_study/data/experiment_phase/user.csv")
video_df    = pd.read_csv(local_path + "/online_study/data/experiment_phase/video.csv")
behavior_df = pd.read_csv(local_path + "/online_study/data/experiment_phase/behavior.csv")

db_connection = DB_connection('experiment')
db_connection.save_table_in_db(rating_df,'rating')
db_connection.save_table_in_db(user_df,'user')
db_connection.save_table_in_db(video_df,'video')
db_connection.save_table_in_db(behavior_df,'behavior')
db_connection.close()





