# PI-adaptDiv journal article
This repo aim to reproduce all results present in the article "PI-adaptDiv: an adaptive algorithm to prevent and escape online filter bubbles journal article". All results are present in the different notebooks. Further this repo enables also to make new simulations of user interactions for [EB-NeRD](https://dl.acm.org/doi/10.1145/3687151.3687152) and [MIND](https://msnews.github.io/) datasets for the four different recommendation algorithms presented in the paper. 

## Requirements
  - [Docker](https://www.docker.com/)
  - [Docker-compose](https://docs.docker.com/compose/)
    
## Setup
  1. Build the images:
     ```
     docker-compose build
     ```
  2. Load the data
     ```
     docker-compose up load_data
     ```
## Run notebooks to reproduce results
This can be done trough the notebook service :

     ```
     docker-compose up notebook
     ```
## Run new simulations 
  1. Open offline_study/ebnerd/run_massive_simulations.py and/or offline_study/mind/run_massive_simulations.py
  2. Set True and choose parameters for the recommendation systems you want to run new simulations
     ```
      run_baseline_simulations = False  # Change this to True to run the baseline simulations
      run_mmr_simulations = False # Change this to True to run the MMR simulations
      run_mmr_expected_div_change_simulations = False # Change this to True to run the MMR expected diversity change simulations
      run_adaptative_simulations = False # Change this to True to run the adaptive simulations
      
      if run_baseline_simulations:
          run_baseline_simulations_for_active_users()
      if run_mmr_simulations:
          lambda_ = 0.7 # Change this value to test different lambda values
          run_mmr_simulations_for_active_users(lambda_)
      if run_mmr_expected_div_change_simulations:
          lambda_ = 0.9 # Change this value to test different lambda values
          run_mmr_expected_div_change_simulations_for_active_users(lambda_)
      if run_adaptative_simulations:
          K_p = 10 # Change this value to test different K_p values
          run_adaptative_simulations_for_active_users(K_p)
     ```
  3. Run the run_new_simulations service :
     ```
     docker-compose up run_new_simulations_ebnerd
     docker-compose up run_new_simulations_ebnerd
     ```

