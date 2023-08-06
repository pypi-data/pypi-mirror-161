
from scipy.spatial.distance import cdist
import numpy as np

def _distances(a, b):
    r = np.zeros((a.shape[0], a.shape[1], b.shape[1]))
    for i in range(a.shape[0]):
        r[i, :, :] = cdist(a[i, :, :], b[i, :, :])
    return r