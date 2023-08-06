import numpy as np

"""
For Bi-Deep L layer Classification
"""


def binary_cutoff_threshold(A, thr):
    return np.where(A >= thr, 1, 0)

