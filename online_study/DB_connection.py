import os

import sqlite3
import pandas as pd




class DB_connection():

    def __init__(self):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        db_path = os.path.join(
            project_root,
            "online_study", "data","experiment_phase", "database.db"
        )
        self.connection = sqlite3.connect(db_path)

    def save_table_in_db(self,df,table_name):
        df.to_sql(table_name,self.connection, if_exists='replace',index=False)

    def select(self,query):
        return pd.read_sql_query(query,self.connection)

    def get_users_by_RS(self):
        recommendation_systems = ['SVD','MMR','PI-adaptDiv','EDC']
        users_by_RS = dict()
        for rs in recommendation_systems:
            query = f'''SELECT id FROM user 
                       WHERE experience_RS = '{rs}'
                       AND q8_answer IS NOT NULL'''
            users = list(self.select(query)['id'])
            users_by_RS[rs] = users
        return users_by_RS
    
    def get_user_ratings(self, user_id):
        experience_history = self.select(f"SELECT * FROM user WHERE id='{user_id}'")["history_experience"][0].split(" ")
        ids = ', '.join(f"'{video_id}'" for video_id in experience_history)
        
        query = f"SELECT rating FROM rating WHERE user_id = '{user_id}' AND video_id in ({ids});"
        ratings_experiment = list(self.select(query)["rating"])

        query = f"SELECT rating FROM rating WHERE user_id = '{user_id}' AND video_id NOT IN ({ids});"
        ratings_training = list(self.select(query)["rating"])
        return ratings_training, ratings_experiment

    def execute_query(self, query):
        self.connection.execute(query)
        self.connection.commit()

    def close(self):
        self.connection.close()



