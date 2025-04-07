from math import log2

from DB_connection import DB_connection

db_connection = DB_connection()

categories = list(db_connection.select('SELECT DISTINCT Category FROM news')["Category"])


def compute_user_items_per_category(user_history,categories=categories):
    distribution = [0] * len(categories)
    categorical_history = db_connection.select( "SELECT Category FROM news WHERE NewsID IN ('{}')".format("','".join(user_history)))["Category"]
    for item_category in categorical_history:
        distribution[categories.index(item_category)] += 1
    return distribution

def compute_next_shannon_entropy(H_n,vec,i):
    X_j = vec[i]
    n = sum(vec)
    m = len(vec) 
    if X_j>0:
        H_np1 = n/(n+1)*H_n - (log2(n/(n+1)) +(X_j+1)/(n+1)*log2((X_j+1)/X_j) + 1/(n+1) * log2(X_j/n))/log2(m)
    if X_j==0:
        H_np1 = n/(n+1)*H_n - (log2(n/(n+1)) + 1/(n+1) * log2(1/n))/log2(m)
    return H_np1


def compute_user_history_distribution(user_history,categories=categories):
    distribution = [0] * len(categories)
    categorical_history = db_connection.select( "SELECT Category FROM news WHERE NewsID IN ('{}')".format("','".join(user_history)))["Category"]
    for item_category in categorical_history:
        distribution[categories.index(item_category)] += 1

    total_sum = sum(distribution)
    for i in range(len(distribution)):
        distribution[i] =   distribution[i] / total_sum
    return distribution
    
    
def shanon_entropy(distribution, normalize = True):
    entropy = 0
    for p in distribution:
        if p>0:
            entropy = entropy - p*log2(p)
    if normalize:
        return (entropy/log2(len(distribution)))
    else:
        return entropy


def compute_user_shanon_entropy(user_history):
    distribution = compute_user_history_distribution(user_history,categories)
    return shanon_entropy(distribution)
    

