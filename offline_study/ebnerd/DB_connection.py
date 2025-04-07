import os
from dotenv import load_dotenv
load_dotenv()

import sqlite3
import pandas as pd


local_path =  os.getenv("LOCAL_PATH")



class DB_connection():
    def __init__(self):
        self.connection = sqlite3.connect( "./offline_study/ebnerd/data/database.db", timeout=10)
    
    def select(self,query):
        return pd.read_sql_query(query, self.connection)
    
    def select_single_value(self,query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0]
    
    def save_df(self,df,table_name):
        df.to_sql(table_name, self.connection, if_exists="replace", index =False)

    def get_active_users(self,len_history, min_nbr_interactions):
        cursor = self.connection.cursor()
        query = f'''SELECT b.user_id
                    FROM behaviors b
                    JOIN users u ON b.user_id = u.user_id
                    WHERE LENGTH(u.initial_history) >  {len_history*8} 
                    GROUP BY b.user_id
                    HAVING COUNT(b.user_id) > {min_nbr_interactions}; '''
        
        cursor.execute(query)
        
        active_users = cursor.fetchall()
        active_users_list = [active_users[i][0] for i in range(len(active_users))]

        return active_users_list 
    
    def create_simulated_baseline_behaviors_table(self):
        cursor = self.connection.cursor()
        query = '''CREATE TABLE IF NOT EXISTS simulated_behaviors(
                    id INTEGER PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    base DOUBLE NOT NULL,
                    recommended_items VARCHAR(255) NOT NULL,
                    probabilities VARCHAR(255) NOT NULL,
                    chosen_item VARCHAR(255),
                    diversity DOUBLE,
                    simulation_type VARCHAR(255),
                    simulation_number INT,
                    parameters_id
                    ); '''
        
        cursor.execute(query)
        print('The table simulated_behaviors has been created')

    def add_line_in_simulated_behaviors_table(self,values):
        query = '''INSERT INTO simulated_behaviors 
                   (
                    user_id,
                    base,
                    recommended_items,
                    probabilities,
                    chosen_item,
                    diversity,
                    simulation_type,
                    simulation_number,
                    parameters_id
                   )
                   VALUES 
                   (
                    :user_id,
                    :base,
                    :recommended_items,
                    :probabilities,
                    :chosen_item,
                    :diversity,
                    :simulation_type,
                    :simulation_number,
                    :parameters_id
                   )'''
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, values)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e

    def create_simulation_parameters_mmr_table(self):
        cursor = self.connection.cursor()
        query = '''CREATE TABLE IF NOT EXISTS parameters_mmr
                   (
                    id VARCHAR(255) PRIMARY KEY,
                    lambda DOUBLE
                    );'''
        cursor.execute(query)
        print('The table parameters_mmr has been created')

    def create_simulation_parameters_adapt_table(self):
        cursor = self.connection.cursor()
        query = '''CREATE TABLE IF NOT EXISTS parameters_adapt
                   (
                    id VARCHAR(255) PRIMARY KEY,
                    K_p DOUBLE,
                    K_i DOUBLE,
                    K_d DOUBLE
                    );'''
        cursor.execute(query)
        print('The table parameters_adapt has been created')
    
    def add_line_in_parameters_adapt_table(self,values):
        query = '''INSERT INTO parameters_adapt
                    (
                     id,
                     K_p,
                     K_i,
                     K_d
                    )
                    VALUES 
                    (
                     :id,
                     :K_p,
                     :K_i,
                     :K_d
                    )'''

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, values)
            self.connection.commit()
        except sqlite3.IntegrityError:
            self.connection.rollback()
        except Exception as e:
            self.connection.rollback()
            raise e

    def add_line_in_parameters_mmr_table(self,values):
        query = '''INSERT INTO parameters_mmr
                    (
                     id,
                     lambda
                    )
                    VALUES 
                    (
                     :id,
                     :lambda
                    )'''

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, values)
            self.connection.commit()
        except sqlite3.IntegrityError:
            self.connection.rollback()
        except Exception as e:
            self.connection.rollback()
            raise e
        
        
    def close(self):
        self.connection.close()


db_connection = DB_connection()
