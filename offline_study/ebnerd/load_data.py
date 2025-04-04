import os

import pandas as pd

from DB_connection import DB_connection


# Load data 
local_path =  os.getenv("LOCAL_PATH")


articles            = pd.read_csv(local_path + "/offline_study/ebnerd/data/articles.csv")
behaviors           = pd.read_csv(local_path + "/offline_study/ebnerd/data/behaviors.csv")
parameters_adapt    = pd.read_csv(local_path + "/offline_study/ebnerd/data/parameters_adapt.csv")
parameters_mmr      = pd.read_csv(local_path + "/offline_study/ebnerd/data/parameters_mmr.csv")
simulated_behaviors = pd.read_csv(local_path + "/offline_study/ebnerd/data/simulated_behaviors.csv")
UserItem_Matrix     = pd.read_csv(local_path + "/offline_study/ebnerd/data/UserItem_Matrix.csv")
users               = pd.read_csv(local_path + "/offline_study/ebnerd/data/users.csv")


# Save data to database
db_connection = DB_connection()
db_connection.save_df(articles, 'articles')
db_connection.save_df(behaviors, 'behaviors')
db_connection.save_df(parameters_adapt, 'parameters_adapt')
db_connection.save_df(parameters_mmr, 'parameters_mmr')
db_connection.save_df(simulated_behaviors, 'simulated_behaviors')
db_connection.save_df(UserItem_Matrix, 'UserItem_Matrix')
db_connection.save_df(users, 'users')
db_connection.close()



