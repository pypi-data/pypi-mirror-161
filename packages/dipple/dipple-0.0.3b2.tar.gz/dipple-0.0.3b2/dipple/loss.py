"""Loss functions for Backpropagation

        - Binary Cross Entropy
        - Cross Entropy (Soon)

In Progress :


"""

################### 

import numpy as np

################### 

def binary_cross_entropy_loss(a: np.ndarray, y: np.ndarray) -> np.ndarray :
    return -((y * np.log(a)) + ((1 - y) * np.log(1 - a)))

def cross_entropy_loss(a: np.ndarray, y: np.ndarray) -> np.ndarray :
    # ...
    pass