import math
import numpy as np

from DB_connection import db_connection



item_df = db_connection.select("SELECT * FROM articles")
item_id_categories_dict = dict(zip(item_df["article_id"],item_df["vectors"]))

user_df = db_connection.select("SELECT * FROM users")
user_id_preferences_dict = dict(zip(user_df["user_id"], user_df["user_preference"]))


def compute_user_probability(user_id, recommended_items,base = math.e, incule_no_choice = False, user_pref=None):
    if user_pref is None:
        user_pref =  np.array(user_id_preferences_dict[user_id].split(" "), dtype=float)
    sum = 0
    sum_user_satisfaction = 0

    for item in recommended_items:
        item_vector = np.array(item_id_categories_dict[item].split(" "), dtype=float)
        sum = sum + base**(np.dot(user_pref,item_vector))
        sum_user_satisfaction = sum_user_satisfaction + np.dot(user_pref,item_vector)
    if incule_no_choice:
        sum = sum + (base**(1-(5*sum_user_satisfaction)/(len(recommended_items)*max(user_pref))))/3
            

    if sum == 0:
        print('sum equal to 0')
    
    probabilities = []
    for item in recommended_items:
        item_vector = np.array(item_id_categories_dict[item].split(" "), dtype=float)
        probabilities.append((base**(np.dot(user_pref,item_vector)))/sum)
    if incule_no_choice:
        probabilities.append(((base**(1-(5*sum_user_satisfaction)/(len(recommended_items)*max(user_pref))))/sum)/3)


    return probabilities


def compute_user_clicking_probabilities(user_id, base):
    user_pref =  np.array(user_id_preferences_dict[user_id].split(" "), dtype=float)
    sum = 0 
    for i in range(len(user_pref)):
        sum = sum + base**(user_pref[i])
    probabilities = []
    for i in range(len(user_pref)):
        probabilities.append(base**(user_pref[i])/sum)
    return probabilities


def make_user_choice(user_id, recommended_items, base = math.e, include_no_choice = False, user_pref=None):
    probabilities = compute_user_probability(user_id, recommended_items,base, include_no_choice,user_pref)
    if include_no_choice:
        recommended_items.append('No_choice')
    return np.random.choice(recommended_items,p=probabilities),probabilities
