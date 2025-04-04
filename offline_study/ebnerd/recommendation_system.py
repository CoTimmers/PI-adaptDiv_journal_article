import numpy as np
from scipy.sparse.linalg import svds


from build_user_item_matrix import build_user_item_matrix
from scipy.sparse import coo_matrix


class MatrixFactorizationRecommender:
    def __init__(self, n_factors=8):
        self.n_factors = n_factors  
        self.user_factors = None  
        self.item_factors = None  

        (user_item_matrix, dic_int_to_userID,dic_userID_to_int,dic_int_to_newsID,
         dic_newsID_to_int)= build_user_item_matrix(filter_active_users=True,history_len=80,nbr_interaction=80)
        
        self.ratings_matrix = user_item_matrix

        # Dictionaries for mapping
        self.dic_int_to_userID = dic_int_to_userID
        self.dic_userID_to_int = dic_userID_to_int
        self.dic_int_to_newsID = dic_int_to_newsID
        self.dic_newsID_to_int = dic_newsID_to_int


    def fit(self):
        # Perform matrix factorization using SVD
        u, s, vt = svds(self.ratings_matrix, k=self.n_factors)
        s_diag_matrix = np.diag(s)
        self.user_factors = np.dot(u, s_diag_matrix)
        self.item_factors = vt.T


    def update(self, user_id, item_id):
        """Update the model with new data without full retraining."""
        # Assuming new_data is a sparse matrix of new user/item interactions

        row = int(self.dic_userID_to_int.get(user_id))
        col = int(self.dic_newsID_to_int.get(item_id))

        rows = list(self.ratings_matrix.row) + [row]
        cols = list(self.ratings_matrix.col) + [col]
        data = list(self.ratings_matrix.data) + [1]
        
        self.ratings_matrix = coo_matrix((np.array(data),(np.array(rows),np.array(cols))))



    def predict_rating(self, user_id, item_id):
        # Convert user_id and item_id to internal indices
        user_index = self.dic_userID_to_int[user_id]
        item_index = self.dic_newsID_to_int[item_id]

        # Predict the rating by dot product of the user and item factors
        predicted_rating = np.dot(self.user_factors[user_index, :], self.item_factors[item_index, :])
        return predicted_rating

    def recommend(self, user_id, n_recommendations=2000, unrelevant_items = []):
        user_index = self.dic_userID_to_int.get(user_id)
        if user_index is None:
            raise ValueError("User ID not found in the dataset")

        predicted_ratings = np.dot(self.user_factors[user_index, :], self.item_factors.T)
        
        # Exclude already interacted items
        interacted_items = set(self.ratings_matrix.getrow(user_index).nonzero()[1])
        items_to_exclude = list(interacted_items) + [self.dic_newsID_to_int[item] for item in unrelevant_items]
        recommendations = [(item_idx, rating) for item_idx, rating in enumerate(predicted_ratings) if item_idx not in items_to_exclude]

        # Sort the predictions by rating in descending order and take the top N
        recommendations.sort(key=lambda x: x[1], reverse=True)
        top_recommendations = recommendations[:n_recommendations]

        # Convert item indices back to IDs
        recommended_item_ids = {self.dic_int_to_newsID[item_idx]: rating for item_idx, rating in top_recommendations}
        return recommended_item_ids
    