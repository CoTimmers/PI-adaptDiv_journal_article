import numpy as np

def percentiles(data,nbr_percentiles,min = 0,max = 1):
    result = [min]
    step = 100/nbr_percentiles
    for i in range(1,nbr_percentiles):
        result.append(np.percentile(data,i * step))
    result.append(max)
    return result

def Max_normalization(list):
    maximum = max(list)
    normalized_list = []
    for elem in list:
        normalized_list.append(elem/maximum)
    return normalized_list

def MinMax_normalization(list):
    minimum = min(list)
    maximum = max(list)
    normalized_list = []
    for elem in list:
        normalized_list.append((elem - minimum)/(maximum-minimum))
    return normalized_list