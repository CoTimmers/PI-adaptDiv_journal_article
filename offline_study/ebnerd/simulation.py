import matplotlib.pyplot as plt
import math
import numpy as np
from tqdm import tqdm



#from config import output_path
from DB_connection import db_connection
from diversity_metrics import compute_user_shanon_entropy, categories, compute_user_items_per_category
from controller import P_controller,PI_controller, PID_controller
from recommendation_system import MatrixFactorizationRecommender
from diversification_strategies import  mmr_diversification, adaptative_diversification_expected_diversity_change
from user_behavior import make_user_choice, compute_user_clicking_probabilities


item_df = db_connection.select("SELECT * FROM articles")
item_df = db_connection.select("SELECT * FROM articles")
item_id_categories_dict_vectors = dict(zip(item_df["article_id"],item_df["vectors"]))
item_id_categories_dict = dict(zip(item_df["article_id"],item_df["category"]))

user_df = db_connection.select("SELECT * FROM users")
user_id_preferences_dict = dict(zip(user_df["user_id"], user_df["user_preference"]))



def simulate_adaptive_diversification(user_id,target_diversity,controller_type ,controller_param,
                                       show_stages = False,n_steps = 30, base = math.e, adapt_user_pref=False):
    
    if show_stages:
        print("User preferences: ")
        print(dict(zip(categories, np.array(user_id_preferences_dict[user_id].split(" "), dtype=float))))
        
    #### initialisation ###
    user_history = list(db_connection.select(f"SELECT * FROM users WHERE user_id ='{user_id}'")["initial_history"])[0].split(' ')
    user_prob = compute_user_clicking_probabilities(user_id, base)
    matrix_factorization_RS = MatrixFactorizationRecommender()
    integral_of_error = 0 
    last_error = 0

    diversity_evolution = []
    user_choices = []
    all_recommended_items = []
    all_probabilities = []
    unrelevant_items = [] # items that have been recommended to the user but he doesn't interact with it

    if adapt_user_pref:
        user_pref =  np.array(user_id_preferences_dict[user_id].split(" "), dtype=float)
    else:
        user_pref = None


    for n in tqdm(range(n_steps)):
        
        real_diversity = compute_user_shanon_entropy(user_history)
        diversity_evolution.append(real_diversity)

        # Recommendation System
        matrix_factorization_RS.fit()
        extended_recommendations = matrix_factorization_RS.recommend(user_id,unrelevant_items=unrelevant_items)

        # Controller
        error = target_diversity-real_diversity
        if show_stages: print('error = ' + str(error))  
        if controller_type == 'P':
            K_p = controller_param[0]
            theta = P_controller(error,K_p)
            if show_stages: print('theta = ' + str(theta))
        elif controller_type == 'PI':
            K_p = controller_param[0]
            K_i = controller_param[1]
            theta,integral_of_error = PI_controller(error,last_error,K_p, K_i, integral_of_error)
            if show_stages: 
                print('theta = ' + str(theta))
                print('integral = ' +str(integral_of_error))
        
            last_error = error

        elif controller_type == 'PID':
            K_p = controller_param[0]
            K_i = controller_param[1]
            K_d = controller_param[2]
            theta,integral_of_error = PID_controller(error,last_error,K_p, K_i,K_d, integral_of_error)
            last_error = error

        
        # Diversification strategy
        recommended_items = adaptative_diversification_expected_diversity_change(user_history, real_diversity ,extended_recommendations, theta,user_prob)
        all_recommended_items.append(recommended_items)
        if show_stages: 
            print([item_id_categories_dict[item] for item in recommended_items ])

        # User choice 
        user_choice,probabilities = make_user_choice(user_id,recommended_items, base, include_no_choice=True,user_pref=user_pref)
        user_choices.append(user_choice)
        all_probabilities.append(probabilities)

        if show_stages:
            print(probabilities)
            if user_choice != 'No_choice':
                print(item_id_categories_dict[user_choice])
            else:
                print(user_choice)
            print("  ")

        # Update
        if user_choice != 'No_choice':
            user_history.append(user_choice)
            matrix_factorization_RS.update(user_id, int(user_choice))

            if adapt_user_pref:
                category_counter = compute_user_items_per_category(user_history)
                s = sum(category_counter)
                user_pref = [category_counter[i]/s for i in range(len(category_counter))]
            
        # if the user doesn't choose any of the recommended items won't recommend them to him again
        if user_choice == 'No_choice': 
            unrelevant_items = unrelevant_items + recommended_items[:-1]
 
    return diversity_evolution, user_choices, all_recommended_items, all_probabilities



def simulate_baseline(user_id, n_steps = 30, base = math.e, adapt_user_pref=False):
    # In the baseline there are only 
    user_history = list(db_connection.select(f"SELECT * FROM Users WHERE user_id ='{user_id}'")["initial_history"])[0].split(' ')
    matrix_factorization_RS = MatrixFactorizationRecommender()

    diversity_evolution = []
    user_choices = []
    all_recommended_items = []
    all_probabilities = []
    unrelevant_items = []

    if adapt_user_pref:
        user_pref =  np.array(user_id_preferences_dict[user_id].split(" "), dtype=float)
    else:
        user_pref = None


    for n in tqdm(range(n_steps)):
        real_diversity = compute_user_shanon_entropy(user_history)
        diversity_evolution.append(real_diversity)

        # Recommendation System
        matrix_factorization_RS.fit()
        recommendations = matrix_factorization_RS.recommend(user_id, n_recommendations= 10,unrelevant_items=unrelevant_items)
        recommended_items = list(recommendations.keys())
        all_recommended_items.append(recommended_items)

        # User choice 
        user_choice,probabilities = make_user_choice(user_id,recommended_items,base,include_no_choice=True,user_pref=user_pref)
        user_choices.append(user_choice)
        all_probabilities.append(probabilities)

        #Update
        if user_choice != 'No_choice':
            matrix_factorization_RS.update(user_id, int(user_choice))
            user_history.append(user_choice)

            if adapt_user_pref:
                category_counter = compute_user_items_per_category(user_history)
                s = sum(category_counter)
                user_pref = [category_counter[i]/s for i in range(len(category_counter))]

        # if the user doesn't choose any of the recommended items won't recommend them to him again
        if user_choice == 'No_choice': 
            unrelevant_items = unrelevant_items + recommended_items[:-1]
            
    return diversity_evolution, user_choices, all_recommended_items,all_probabilities


def simulate_mmr(user_id,theta,n_steps=30, base =  math.e, adapt_user_pref = False):
    user_history = list(db_connection.select(f"SELECT * FROM Users WHERE user_id ='{user_id}'")["initial_history"])[0].split(' ')
    matrix_factorization_RS = MatrixFactorizationRecommender()

    diversity_evolution = []
    user_choices = []
    all_recommended_items = []
    all_probabilities = []
    unrelevant_items = []

    if adapt_user_pref:
        user_pref =  np.array(user_id_preferences_dict[user_id].split(" "), dtype=float) 
    else:
        user_pref = None


    for n in tqdm(range(n_steps)):
        real_diversity = compute_user_shanon_entropy(user_history)
        diversity_evolution.append(real_diversity)   
               
        # Recommendation System
        matrix_factorization_RS.fit()
        extended_recommendations = matrix_factorization_RS.recommend(user_id,unrelevant_items=unrelevant_items)   

        # Diversification strategy
        recommended_items = mmr_diversification(extended_recommendations,theta)
        all_recommended_items.append(recommended_items)

        # User choice
        user_choice,probabilities = make_user_choice(user_id,recommended_items, base,include_no_choice=True,user_pref=user_pref)
        user_choices.append(user_choice)
        all_probabilities.append(probabilities)
        

        # Update
        if user_choice != 'No_choice':
            user_history.append(user_choice)
            matrix_factorization_RS.update(user_id, int(user_choice))

            if adapt_user_pref:
                category_counter = compute_user_items_per_category(user_history)
                s = sum(category_counter)
                user_pref = [category_counter[i]/s for i in range(len(category_counter))]

        # if the user doesn't choose any of the recommended items won't recommend them to him again
        if user_choice == 'No_choice': 
            unrelevant_items = unrelevant_items + recommended_items[:-1]

    return diversity_evolution,user_choices,all_recommended_items,all_probabilities



def simulate_mmr_expected_div_change(user_id,theta,n_steps=30, base =  math.e, adapt_user_pref = False):
    user_history = list(db_connection.select(f"SELECT * FROM Users WHERE user_id ='{user_id}'")["initial_history"])[0].split(' ')
    matrix_factorization_RS = MatrixFactorizationRecommender()
    user_prob = compute_user_clicking_probabilities(user_id, base)


    diversity_evolution = []
    user_choices = []
    all_recommended_items = []
    all_probabilities = []
    unrelevant_items = []

    if adapt_user_pref:
        user_pref =  np.array(user_id_preferences_dict[user_id].split(" "), dtype=float)
    else:
        user_pref = None


    for n in tqdm(range(n_steps)):
        real_diversity = compute_user_shanon_entropy(user_history)
        diversity_evolution.append(real_diversity)   
               
        # Recommendation System
        matrix_factorization_RS.fit()
        extended_recommendations = matrix_factorization_RS.recommend(user_id,unrelevant_items=unrelevant_items)   

        # Diversification strategy
        recommended_items = adaptative_diversification_expected_diversity_change(user_history, real_diversity ,extended_recommendations, theta,user_prob)
        all_recommended_items.append(recommended_items)

        # User choice
        user_choice,probabilities = make_user_choice(user_id,recommended_items, base,include_no_choice=True,user_pref=user_pref)
        user_choices.append(user_choice)
        all_probabilities.append(probabilities)
        

        # Update
        if user_choice != 'No_choice':
            user_history.append(user_choice)
            matrix_factorization_RS.update(user_id, int(user_choice))

            if adapt_user_pref:
                category_counter = compute_user_items_per_category(user_history)
                s = sum(category_counter)
                user_pref = [category_counter[i]/s for i in range(len(category_counter))]

        # if the user doesn't choose any of the recommended items won't recommend them to him again
        if user_choice == 'No_choice': 
            unrelevant_items = unrelevant_items + recommended_items[:-1]

    return diversity_evolution,user_choices,all_recommended_items,all_probabilities



