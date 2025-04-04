import numpy as np
from scipy.sparse import coo_matrix
from tqdm import tqdm
from DB_connection import DB_connection

db_connection = DB_connection()

def build_user_item_matrix(filter_active_users=False, history_len=15, nbr_interaction=15):
    # Load active users if specified
    if filter_active_users:
        active_users = db_connection.get_active_users(history_len, nbr_interaction)
        active_users = [str(user) for user in active_users]
        select_query = "SELECT user_id FROM users WHERE user_id IN ('{}')".format("','".join(active_users))
    else:
        select_query = "SELECT user_id FROM users"
    
    users = db_connection.select(select_query)
    dic_int_to_userID = users.to_dict()["user_id"]
    dic_userID_to_int = {value: key for key, value in dic_int_to_userID.items()}

    select_query = "SELECT article_id FROM articles"
    news = db_connection.select(select_query)
    dic_int_to_newsID = news.to_dict()["article_id"]
    dic_newsID_to_int = {value: key for key, value in dic_int_to_newsID.items()}

    # Retrieve the user-item interactions
    if filter_active_users:
        select_query = "SELECT user_id, item_id FROM UserItem_Matrix WHERE user_id IN ('{}')".format("','".join(active_users))
    else:
        select_query = "SELECT user_id, item_id FROM UserItem_Matrix"

    user_item_df = db_connection.select(select_query)
    user_ids = list(user_item_df['user_id'])
    item_ids = list(user_item_df['item_id'])

    rows = []
    cols = []
    print("LOAD USER ITEM MATRIX")
    for i in tqdm(range(len(user_ids))):
        try:
            cols.append(dic_newsID_to_int[int(item_ids[i])])
            rows.append(dic_userID_to_int[int(user_ids[i])])
        except KeyError:
            pass
    
    vals = np.ones(len(rows))
    return (coo_matrix((np.array(vals), (np.array(rows), np.array(cols)))),
            dic_int_to_userID, dic_userID_to_int, dic_int_to_newsID, dic_newsID_to_int)