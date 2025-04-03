import numpy as np
from math import log2

from DB_connection import DB_connection

db_connection = DB_connection()

query = "SELECT * FROM video"
video_df = db_connection.select(query)
dic_video_id_to_cat = dict(zip(list(video_df["video_id"]),list(video_df["category"])))

query = "SELECT DISTINCT category FROM video "
categories = list(db_connection.select(query)["category"])


def shanon_entropy(distribution, normalize=True):
    """
    Compute the Shannon entropy of a distribution.
    Input :
    - distribution [list] : list of probabilities
    - normalize [bool] : if True, normalize the entropy by the log2 of the number of categories
    Output :
    - entropy [float] : Shannon entropy of the distribution
    """
    entropy = 0
    for p in distribution:
        if p > 0:
            entropy = entropy - p * log2(p)
    if normalize:
        return entropy / log2(len(distribution))
    else:
        return entropy
    


def compute_user_entropy(user_id, history_expe=True, rolling_window_size=10000, show_distribution = False):
    """"
    Compute the entropy of the user's history or experience.
    Input :
    - user_id [int] : id of the user
    - history_expe [bool]: if True, compute diversity of the experiment only, else compute the entropy all the history
    - rolling_window_size [int]: size of the rolling window to compute the entropy
    - show_distribution [bool]: if True, show the distribution of the categories
    Output :
    - entropy [float]: entropy of the user's history or experience
    """
    distribution = [0] * len(categories)
    if history_expe:
        query = f"SELECT history_experience FROM user WHERE id = {user_id}"
        user_history = db_connection.select(query)["history_experience"][0]
    else:
        query = f"SELECT history FROM user WHERE id = {user_id}"
        user_history = db_connection.select(query)["history"][0]
    user_history = user_history.split(" ")

    if rolling_window_size < len(user_history):
        user_history = user_history[-rolling_window_size:]

    for item_id in user_history:
        item_category = dic_video_id_to_cat[item_id]
        distribution[categories.index(item_category)] += 1

    total_sum = sum(distribution)
    for i in range(len(distribution)):
        distribution[i] = distribution[i] / total_sum

    if show_distribution:
        print(dict(zip(categories,distribution)))
    
    entropy = shanon_entropy(distribution)
    return entropy


def compute_user_recommended_diversity(user_id):
    """"
    Compute the diversity of the recommended items for a user.
    Input :
    - user_id [int] : id of the user
    Output :
    - entropy [float]: diversity of the recommended items
    """
    query = f"SELECT * FROM behavior WHERE user_id = {user_id}"
    user_behaviors = db_connection.select(query)
    all_recommended_items = []
    for index,row in user_behaviors.iterrows():
        all_recommended_items = all_recommended_items + row["recommended_items"].split(" ")
    
    distribution = [0] * len(categories)
    for item_id in all_recommended_items:
        item_category = dic_video_id_to_cat[item_id]
        distribution[categories.index(item_category)] += 1

    sum_distribution = sum(distribution)
    distribution = [d/sum_distribution for d in distribution ]

    entropy = shanon_entropy(distribution)
    return entropy


def compute_user_diversity_evolution(user_id):
    """
    Compute the diversity evolution of the user's history.
    Input :
    - user_id [int] : id of the user
    Output :
    - diversity_evolution [list] : list of diversity values
    """
    query = f"SELECT * FROM user WHERE id = {user_id}"
    user_df = db_connection.select(query)

    user_hist = user_df["history_experience"][0].split(" ")
    
    hist_evolution = [user_hist[0]]
    diversity_evolution = []
    for i in range(1,len(user_hist)):
        hist_evolution.append((user_hist[i]))
        distribution = [0] * len(categories)
        for item_id in hist_evolution:
            item_category = dic_video_id_to_cat[item_id]
            distribution[categories.index(item_category)] += 1

        total_sum = sum(distribution)
        for i in range(len(distribution)):
            distribution[i] = distribution[i] / total_sum
        diversity_evolution.append(shanon_entropy(distribution))
    return diversity_evolution


def compute_user_pref(user_id):
    """"
    "Compute the user preference for each category.
    Input :
    - user_id [int] : id of the user
    Output :
    - user_pref [list] : list of user preference for each category
    """
    user_pref = [0] * len(categories)
    query = f"SELECT * FROM rating WHERE user_id={user_id} LIMIT 29" #get cold start training 
    ratings = db_connection.select(query)
    avg_rating = np.mean(ratings["rating"])
    for index,row in ratings.iterrows():
        item_category = dic_video_id_to_cat[row["video_id"]]
        user_pref[categories.index(item_category)] += max(row["rating"]-avg_rating,0)
    sum_ratings = sum(user_pref)
    user_pref = [p/sum_ratings for p in user_pref]

    return user_pref

