import os

import pandas as pd

from DB_connection import db_connection


# Load data 
print('Load data for ebnerd database')


articles            = pd.read_csv("./offline_study/ebnerd/data/articles.csv")
behaviors           = pd.read_csv("./offline_study/ebnerd/data/behaviors.csv")
parameters_adapt    = pd.read_csv("./offline_study/ebnerd/data/parameters_adapt.csv")
parameters_mmr      = pd.read_csv("./offline_study/ebnerd/data/parameters_mmr.csv")
simulated_behaviors = pd.read_csv("./offline_study/ebnerd/data/simulated_behaviors.csv")
UserItem_Matrix     = pd.read_csv("./offline_study/ebnerd/data/UserItem_Matrix.csv")
users               = pd.read_csv("./offline_study/ebnerd/data/users.csv")

#users['user_id'] = users['user_id'].astype(int)


# Save data to database
db_connection.save_df(articles, 'articles')
db_connection.save_df(behaviors, 'behaviors')
db_connection.save_df(parameters_adapt, 'parameters_adapt')
db_connection.save_df(parameters_mmr, 'parameters_mmr')
db_connection.save_df(simulated_behaviors, 'simulated_behaviors')
db_connection.save_df(UserItem_Matrix, 'UserItem_Matrix')
db_connection.save_df(users, 'users')



