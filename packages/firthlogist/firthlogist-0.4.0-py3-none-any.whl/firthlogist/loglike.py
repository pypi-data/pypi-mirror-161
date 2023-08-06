import numpy as np
# pythran export loglike(float[], float[])

def loglike(y, preds):
    return np.sum(y * np.log(preds) + (1 - y) * np.log(1 - preds))
