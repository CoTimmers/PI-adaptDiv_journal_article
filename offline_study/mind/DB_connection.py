import os

import sqlite3 
import pandas as pd



class DB_connection():
    def __init__(self):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        
        db_path = os.path.join(
            project_root,
            "offline_study", "mind", "data", "database.db"
        )
        self.connection = sqlite3.connect( db_path, timeout=10)
    
    def select(self,query):
        return pd.read_sql_query(query, self.connection)
    
    def select_single_value(self,query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0]
    
    def drop_table(self,table_name):
        delete_bool = input(f"Are you sure you want to delete the table {table_name} ? type yes and enter to continue the process ")
        if delete_bool == 'yes':
            cursor = self.connection.cursor()
            query  = "DROP TABLE IF EXISTS " + table_name
            cursor.execute(query)
            print('Table '+ table_name + ' has been deleted')

    def save_df(self,df,table_name):
        df.to_sql(table_name, self.connection, if_exists="replace", index =False)

    def get_active_users(self,min_history_len, min_nbr_interactions):
        cursor = self.connection.cursor()
        query = '''SELECT UserID FROM behaviors
                    WHERE LENGTH(History)> ?
                    GROUP BY UserID
                    HAVING COUNT(UserID) >?;'''
        cursor.execute(query,(min_history_len*7,min_nbr_interactions,))
        
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
