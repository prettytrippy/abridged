import numpy as np

params = [0.9, 0.1, 0.85]

def get_ab_params():
    std = [1e-2, 1e-1, 1e-1]
    a = np.random.normal(params, std)
    b = np.random.normal(params, std)
    a[a < 0] = 0
    b[b < 0] = 0
    a[a > 1] = 1
    b[b > 1] = 1
    return a, b

def store_preference(preferred, dispreferred):
    return