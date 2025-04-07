import ast
import math
import numpy as np


from DB_connection import DB_connection


db_connection = DB_connection()
item_df = db_connection.select("SELECT * FROM news")
itemID_categories_dict = dict(zip(item_df["NewsID"],item_df["vectors"]))

user_df = db_connection.select("SELECT * FROM Users")
userID_preferences_dict = dict(zip(user_df["user_id"], user_df["user_preference"]))


def compute_user_probability(user_id, recommended_items,base = math.e, incule_no_choice = False, user_pref=None):
    if user_pref == None:
        user_pref =  ast.literal_eval(userID_preferences_dict[user_id])
    sum = 0
    sum_user_satisfaction = 0

    for item in recommended_items:
        item_vector = ast.literal_eval(itemID_categories_dict[item])
        sum = sum + base**(np.dot(user_pref,item_vector))
        sum_user_satisfaction = sum_user_satisfaction + np.dot(user_pref,item_vector)
    if incule_no_choice:
        sum = sum + (base**(1-(5*sum_user_satisfaction)/(len(recommended_items)*max(user_pref))))/3
            

    if sum == 0:
        print('sum equal to 0')
    
    probabilities = []
    for item in recommended_items:
        item_vector = ast.literal_eval(itemID_categories_dict[item])
        probabilities.append((base**(np.dot(user_pref,item_vector)))/sum)
    if incule_no_choice:
        probabilities.append(((base**(1-(5*sum_user_satisfaction)/(len(recommended_items)*max(user_pref))))/sum)/3)


    return probabilities


def compute_user_clicking_probabilities(user_id, base):
    user_pref  =  ast.literal_eval(userID_preferences_dict[user_id])
    sum = 0 
    for i in range(len(user_pref)):
        sum = sum + base**(user_pref[i])
    probabilities = []
    for i in range(len(user_pref)):
        probabilities.append(base**(user_pref[i])/sum)
    return probabilities


def make_user_choice(user_id, recommended_items, base = math.e, include_no_choice = False, user_pref=None):
    probabilities = compute_user_probability(user_id, recommended_items,base, include_no_choice,user_pref)
    #print(probabilities)
    if include_no_choice:
        recommended_items.append('No_choice')
    return np.random.choice(recommended_items,p=probabilities),probabilities


def compute_optimal_base(user_id):
    user_pref =  ast.literal_eval(userID_preferences_dict[user_id])
    optimal_base = minimize(0,10000, user_pref)
    return optimal_base[0]
        

def obj_function(user_pref, base):
    sum = 0
    for j in range(len(user_pref)):
        sum = sum + base**(user_pref[j]) 
    probabilities = []
    for i in range(len(user_pref)):
        probabilities.append(base**(user_pref[i])/sum)
    return np.linalg.norm(np.array(user_pref)-np.array(probabilities))


def minimize(a,b,user_pref,n_steps= 10001):
    x = np.linspace(a,b,n_steps)
    y = []
    for i in x:
        y.append(obj_function(user_pref,i))
    y = np.array(y)
    arg_min = np.argmin(y)

    return x[arg_min],y[arg_min]


    
        
        










