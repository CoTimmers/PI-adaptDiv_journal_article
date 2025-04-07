import numpy as np
import math
import matplotlib.pyplot as plt
from tqdm import tqdm

from DB_connection import db_connection
from diversification_strategies import compute_Ki
from simulation import simulate_baseline,simulate_adaptive_diversification,simulate_mmr, simulate_mmr_expected_div_change
from data.base_mnl_a import base_au_80_80_test_40,entropy_au_80_80
#from data.big_dataset.base_logit_function import bases_active_users_15_35_test_set_10



db_connection.create_simulated_baseline_behaviors_table()
db_connection.create_simulation_parameters_mmr_table()
db_connection.create_simulation_parameters_adapt_table()
active_users  = db_connection.get_active_users(80,80)
bases = base_au_80_80_test_40


##### BASELINE ######

def run_baseline_simulations_for_active_users():
    for i in tqdm(range(0,len(active_users))):
        user = active_users[i]
        base = bases[user]
        #base = 100
    

        simulation_type = 'baseline'
        query = f'''SELECT MAX(simulation_number) FROM simulated_behaviors 
                    WHERE user_id ='{user}'
                    AND simulation_type ='{simulation_type}'
                    AND base ={base}
                 '''
        last_simulation_number = db_connection.select_single_value(query)

        if last_simulation_number == None:
            simulation_number = 1
        else:
            simulation_number = last_simulation_number+1
        
        diversity_evolution, user_choices, all_recommended_items, all_probabilities = simulate_baseline(user,base=base)
        for i in range(len(all_recommended_items)):
            choice = user_choices[i]
            data_point = {
                 'user_id':user,
                 'base':base,
                 'recommended_items': str(all_recommended_items[i]),
                 'probabilities': str(all_probabilities[i]),
                 'chosen_item':choice,
                 'diversity':diversity_evolution[i],
                 'simulation_type': simulation_type,
                 'simulation_number': simulation_number,
                 'parameters_id': None
            }
            db_connection.add_line_in_simulated_behaviors_table(data_point)





def run_adaptative_simulations_for_one_user(user,wanted_diversity , base, coeficients, adapt_user_pref=True,nbr_simulations=1):

    K_p = coeficients[0]
    K_i = coeficients[1]
    K_d = coeficients[2]

    param = f"K_p={K_p}-K_i={K_i}-K_d={K_d}"
    parameters_data_point = {'id': param,
                                 'K_p': K_p,
                                 'K_i': K_i,
                                 'K_d': K_d}
    db_connection.add_line_in_parameters_adapt_table(parameters_data_point)

    if K_i ==0 and K_d == 0:
        coefs = [K_p]
        controller_type = 'P'
    elif K_i !=0 and K_d == 0:
        coefs = [K_p,K_i]
        controller_type = 'PI'
    elif K_i != 0 and K_d !=0:
        coefs = [K_p,K_i,K_d]
        controller_type = 'PID'

    simulation_type = 'adapt'
    for j in range(nbr_simulations):


        query = f'''SELECT MAX(simulation_number) FROM simulated_behaviors 
                    WHERE user_id ='{user}'
                    AND simulation_type ='{simulation_type}'
                    AND base ={base}
                    AND parameters_id = '{param}'
                 '''
        last_simulation_number = db_connection.select_single_value(query)

        if last_simulation_number == None:
            simulation_number = 1
        else:
            simulation_number = last_simulation_number+1
        

        (diversity_evolution,user_choices,
        all_recommended_items,
        all_probabilities) = simulate_adaptive_diversification(user,wanted_diversity,controller_type ,coefs,
                                                               show_stages=False, n_steps=40, base=base, 
                                                               adapt_user_pref=True)
        
        for i in range(len(all_recommended_items)):
            choice = user_choices[i]
            data_point = {
                 'user_id':user,
                 'base':base,
                 'recommended_items': str(all_recommended_items[i]),
                 'probabilities': str(all_probabilities[i]),
                 'chosen_item':choice,
                 'diversity':diversity_evolution[i],
                 'simulation_type': simulation_type,
                 'simulation_number': simulation_number,
                 'parameters_id': param
            }
            db_connection.add_line_in_simulated_behaviors_table(data_point)




def run_adaptative_simulations_for_active_users(K_p):
    for i in tqdm(range(0,len(active_users))):
        user = active_users[i]
        base = bases[user]
        diversity = entropy_au_80_80[user]
        if diversity < 0.5:
            wanted_diversity = 0.65
            K_i = compute_Ki(user,K_p,wanted_diversity,10)
            K_i = round(K_i, 2)
        else:
            wanted_diversity = diversity
            K_i = 0

        run_adaptative_simulations_for_one_user(user,wanted_diversity , base, [K_p,K_i,0])




def run_mmr_simulations_for_one_user(lambda_,user, base,nbr_simulations=1):
    for j in tqdm(range(nbr_simulations)):
        
        param = 'lambda_' + str(lambda_)
        parameters_data_point = {'id': param,
                                 'lambda': lambda_}
        db_connection.add_line_in_parameters_mmr_table(parameters_data_point)


        simulation_type = 'mmr'
        query = f'''SELECT MAX(simulation_number) FROM simulated_behaviors 
                    WHERE user_id ='{user}'
                    AND simulation_type ='{simulation_type}'
                    AND base ={base}
                 '''
        last_simulation_number = db_connection.select_single_value(query)

        if last_simulation_number == None:
            simulation_number = 1
        else:
            simulation_number = last_simulation_number+1
        
        diversity_evolution, user_choices, all_recommended_items, all_probabilities = simulate_mmr(user,lambda_,base=base,adapt_user_pref=True)
        for i in range(len(all_recommended_items)):
            choice = user_choices[i]
            data_point = {
                 'user_id':user,
                 'base':base,
                 'recommended_items': str(all_recommended_items[i]),
                 'probabilities': str(all_probabilities[i]),
                 'chosen_item':choice,
                 'diversity':diversity_evolution[i],
                 'simulation_type': simulation_type,
                 'simulation_number': simulation_number,
                 'parameters_id': param
            }
            db_connection.add_line_in_simulated_behaviors_table(data_point)

#run_mmr_simulations_for_one_user(0.7,'U65795', base=100)


def run_mmr_simulations_for_active_users(lambda_):
    for i in tqdm(range(80,len(active_users))):
        user = active_users[i]
        base = bases[user]


        param = 'lambda_' + str(lambda_)
        parameters_data_point = {'id': param,
                                 'lambda': lambda_}
        db_connection.add_line_in_parameters_mmr_table(parameters_data_point)


        simulation_type = 'mmr'
        query = f'''SELECT MAX(simulation_number) FROM simulated_behaviors 
                    WHERE user_id ='{user}'
                    AND simulation_type ='{simulation_type}'
                    AND base ={base}
                    AND parameters_id = '{param}'
                 '''
        last_simulation_number = db_connection.select_single_value(query)

        if last_simulation_number == None:
            simulation_number = 1
        else:
            simulation_number = last_simulation_number+1
        
        diversity_evolution, user_choices, all_recommended_items, all_probabilities = simulate_mmr(user,lambda_,base=base,adapt_user_pref=True)
        for i in range(len(all_recommended_items)):
            choice = user_choices[i]
            data_point = {
                 'user_id':user,
                 'base':base,
                 'recommended_items': str(all_recommended_items[i]),
                 'probabilities': str(all_probabilities[i]),
                 'chosen_item':choice,
                 'diversity':diversity_evolution[i],
                 'simulation_type': simulation_type,
                 'simulation_number': simulation_number,
                 'parameters_id': param
            }
            db_connection.add_line_in_simulated_behaviors_table(data_point)


def run_mmr_expected_div_change_simulations_for_active_users(lambda_):
    for i in tqdm(range(0,len(active_users))):
        user = active_users[i]
        base = bases[user]


        param = 'lambda_' + str(lambda_)
        parameters_data_point = {'id': param,
                                 'lambda': lambda_}
        db_connection.add_line_in_parameters_mmr_table(parameters_data_point)


        simulation_type = 'mmr_exp_div_change'
        query = f'''SELECT MAX(simulation_number) FROM simulated_behaviors 
                    WHERE user_id ='{user}'
                    AND simulation_type ='{simulation_type}'
                    AND base ={base}
                    AND parameters_id = '{param}'
                 '''
        last_simulation_number = db_connection.select_single_value(query)

        if last_simulation_number == None:
            simulation_number = 1
        else:
            simulation_number = last_simulation_number+1
        
        diversity_evolution, user_choices, all_recommended_items, all_probabilities = simulate_mmr_expected_div_change(user,lambda_,base=base,adapt_user_pref=True)
        for i in range(len(all_recommended_items)):
            choice = user_choices[i]
            data_point = {
                 'user_id':user,
                 'base':base,
                 'recommended_items': str(all_recommended_items[i]),
                 'probabilities': str(all_probabilities[i]),
                 'chosen_item':choice,
                 'diversity':diversity_evolution[i],
                 'simulation_type': simulation_type,
                 'simulation_number': simulation_number,
                 'parameters_id': param
            }
            db_connection.add_line_in_simulated_behaviors_table(data_point)

#run_baseline_simulations_for_active_users()
#run_mmr_simulations_for_active_users(0.2)
#run_mmr_expected_div_change_simulations_for_active_users(0.9)
run_adaptative_simulations_for_active_users(10)





