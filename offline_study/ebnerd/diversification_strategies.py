import numpy as np

from stats import MinMax_normalization, Max_normalization
from diversity_metrics import compute_user_items_per_category, compute_next_shannon_entropy, shannon_entropy, categories
from DB_connection import db_connection



item_df = db_connection.select("SELECT * FROM articles")
itemID_categories_dict_vectors = dict(zip(item_df["article_id"],item_df["vectors"]))
itemID_categories_dict = dict(zip(item_df["article_id"],item_df["category"]))

user_df = db_connection.select("SELECT * FROM Users")
userID_preferences_dict = dict(zip(user_df["user_id"], user_df["user_preference"]))

def compute_prob(vec):
    s = sum(vec)
    p = [vec[i]/s for i in range(len(vec))]
    return p


def compute_Ki(user_id,Kp,wanted_diversity,theta):
    user_history = list(db_connection.select(f"SELECT * FROM users WHERE user_id ='{user_id}'")["initial_history"])[0].split(' ')
    item_per_category = compute_user_items_per_category(user_history)

    H_n = shannon_entropy(compute_prob(item_per_category))
    H_n_wanted = wanted_diversity
    steps = 0
    H_ns = [H_n]
    while (H_n_wanted)-H_n > 0.00000001:
        i = np.argmin(item_per_category)
        H_n = compute_next_shannon_entropy(H_n,item_per_category,i)
        H_ns.append(H_n)
        item_per_category[i] = item_per_category[i] + 1 
        #if H_n > (H_n_wanted-1/Kp):
        steps = steps + 1
    Nmin = steps
    Ki = Kp/(theta*Nmin)
    return Ki
    


def adaptative_diversification_expected_diversity_change(user_history, diversity ,extended_recommendations, theta, probabilities, top_n=10):
    recommended_items = list(extended_recommendations.keys())
    recommended_items_score = extended_recommendations.values()
    normalized_scores = MinMax_normalization(recommended_items_score)

    category_counter = compute_user_items_per_category(user_history)
    max_diversity_change = compute_next_shannon_entropy(diversity,category_counter,np.argmin(category_counter))-diversity
    diversity_difference = []
    for item in recommended_items:
        item_category = itemID_categories_dict[item]
        index = categories.index(item_category)
        shanon_entopy_if_item_choosen = compute_next_shannon_entropy(diversity,category_counter,index)
        diversity_difference.append(probabilities[index]*(shanon_entopy_if_item_choosen-diversity)/max_diversity_change)

    normalized_diversity = Max_normalization(diversity_difference)
    new_score = [(1-theta)*normalized_scores[i] + theta *normalized_diversity[i] for i in range(len(recommended_items))]

    items_new_score_dict = {recommended_items[i]: new_score[i] for i in range(len(recommended_items))}
    sorted_items_new_score_dict = dict(sorted(items_new_score_dict.items(), key=lambda item: item[1], reverse=True))

    return list(sorted_items_new_score_dict.keys())[0:top_n]


def adaptative_diversification(user_history, diversity ,extended_recommendations, theta, top_n=10):
    recommended_items = list(extended_recommendations.keys())
    recommended_items_score = extended_recommendations.values()
    normalized_scores = MinMax_normalization(recommended_items_score)

    category_counter = compute_user_items_per_category(user_history)
    max_diversity_change = compute_next_shannon_entropy(diversity,category_counter,np.argmin(category_counter))-diversity
    diversity_difference = []
    for item in recommended_items:
        item_category = itemID_categories_dict[item]
        shanon_entopy_if_item_choosen = compute_next_shannon_entropy(diversity,category_counter,categories.index(item_category))
        diversity_difference.append(shanon_entopy_if_item_choosen-diversity)

    normalized_diversity = MinMax_normalization(diversity_difference)
    new_score = [(1-theta)*normalized_scores[i] + theta *normalized_diversity[i] for i in range(len(recommended_items))]

    items_new_score_dict = {recommended_items[i]: new_score[i] for i in range(len(recommended_items))}
    sorted_items_new_score_dict = dict(sorted(items_new_score_dict.items(), key=lambda item: item[1], reverse=True))

    return list(sorted_items_new_score_dict.keys())[0:top_n]

    
def mmr_diversification(extended_recommendations, lambda_val=0.5, top_n=10):
    recommended_items = list(extended_recommendations.keys())
    recommended_items_score = extended_recommendations.values()
    normalized_scores = MinMax_normalization(recommended_items_score)
    extended_recommendations = dict(zip(recommended_items,normalized_scores))
 
    items = [(item_id, score) for item_id, score in extended_recommendations.items()]
    selected_item_ids = []

    while items and len(selected_item_ids) < top_n:
        max_mmr = None
        selected_item = None

        for item_id, score in items:
            relevance = score
            diversity = 0
            if selected_item_ids:
                selected_categories = [itemID_categories_dict_vectors[id] for id in selected_item_ids]
                item_category = itemID_categories_dict_vectors[item_id]
                diversity = sum(1 for category in selected_categories if category != item_category) / len(selected_item_ids)
            mmr = lambda_val * relevance - (1 - lambda_val) * (1 - diversity)

            if max_mmr is None or mmr > max_mmr:
                max_mmr = mmr
                selected_item = (item_id, score)
        
        if selected_item:
            items.remove(selected_item)
            selected_item_ids.append(selected_item[0])

    return selected_item_ids








