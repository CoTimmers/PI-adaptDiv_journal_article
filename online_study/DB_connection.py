import os
from dotenv import load_dotenv
load_dotenv()

import sqlite3
import pandas as pd


local_path =  os.getenv("LOCAL_PATH")


class DB_connection():

    def __init__(self, phase):
        if phase == 'training':
            self.connection = sqlite3.connect(local_path + "/online_study/data/training_phase/"+"database.db", check_same_thread=False)
        elif phase == 'experiment':
            self.connection = sqlite3.connect(local_path + "/online_study/data/experiment_phase/"+"database.db", check_same_thread=False)

    def save_table_in_db(self,df,table_name):
        df.to_sql(table_name,self.connection, if_exists='replace',index=False)

    def close(self):
        self.connection.close()



