import itertools
import numpy as np
from collections import Counter
from scipy.sparse import coo_matrix

from DB_connection import DB_connection


def most_viewed_news(behaviors, topn):
    histories = list(behaviors['History'])
    hist      = []
    for i in range(len(histories)):
        #print(i)
        if (type(histories[i]) == str):
            user_hist = histories[i].split(" ")
            hist.append(user_hist)
    
    hist = list(itertools.chain(*hist))
    counter = Counter(hist)
    
    most_viewed_news = []
    for tuples in counter.most_common()[0:topn]:
        most_viewed_news.append(tuples[0])
    return  most_viewed_news

 

def build_user_item_matrix(filter_acitve_users = False,history_len = 15, nbr_interaction = 15 ):
    db_connection = DB_connection()
    if filter_acitve_users:
        active_users = db_connection.get_active_users(history_len,nbr_interaction)
    if filter_acitve_users:
        select_query = "SELECT user_id FROM Users WHERE user_id IN ('{}')".format("','".join(active_users))
    else:
        select_query = "SELECT user_id FROM Users"
    users = db_connection.select(select_query)
    dic_int_to_userID = users.to_dict()["user_id"] 
    dic_userID_to_int = {value: key for key, value in dic_int_to_userID.items()}


    select_query = "SELECT NewsID FROM news" 
    news = db_connection.select(select_query)
    dic_int_to_newsID = news.to_dict()["NewsID"]
    dic_newsID_to_int = {value: key for key, value in dic_int_to_newsID.items()}

    if filter_acitve_users:
        select_query = "SELECT user_id,item_id FROM UserItem_Matrix WHERE user_id IN ('{}')".format("','".join(active_users))
    else:
        select_query = "SELECT user_id,item_id FROM UserItem_Matrix"
    user_item_df = db_connection.select(select_query)
    user_ids = list(user_item_df['user_id'])
    item_ids = list(user_item_df['item_id'])

    rows = []
    cols = []
    for i in range(len(user_ids)):
        try :
            cols.append(dic_newsID_to_int[item_ids[i]])
            rows.append(dic_userID_to_int[user_ids[i]])

        except:
            pass
    vals = np.ones(len(rows))
    return (coo_matrix((np.array(vals),(np.array(rows),np.array(cols)))),
            dic_int_to_userID,dic_userID_to_int,dic_int_to_newsID,dic_newsID_to_int)