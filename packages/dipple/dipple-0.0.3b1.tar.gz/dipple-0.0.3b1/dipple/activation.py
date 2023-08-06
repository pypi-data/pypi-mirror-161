"""Dipple Activation Function and its derivative 
                    - Sigmoid
                    - Tanh
                    - ReLU
                    - LeakyReLU
                    - Linear

In Progress :
1. Recheck the correctness of Sigmoid, Tanh, LeakyReLU due to high error gradient approx.
2. Perhap Turn this activation into an object involved both activation and its derivative
"""

################### 

import numpy as np

################### 

def sigmoid(z: np.ndarray) -> np.ndarray:
    assert isinstance(z,np.ndarray)      # temporary : in case z is not numpy array object
    return 1 / (1 + np.exp(-z))

def tanh(z: np.ndarray) -> np.ndarray:
    assert isinstance(z,np.ndarray)
    return (np.exp(z) - np.exp(-z)) / (np.exp(z) + np.exp(-z))

def relu(z: np.ndarray) -> np.ndarray:   # always return numpy array
    return np.where(z >= 0, z, 0)

def leakyrelu(z: np.ndarray) -> np.ndarray: 
    return np.where(z >= 0, z, 0.01 * z)

def linear(z: np.ndarray) -> np.ndarray:
    assert isinstance(z,np.ndarray)
    return z

"""
Derivative of Activation Function wrp. Z
"""

def dsigmoid(z: np.ndarray) -> np.ndarray:
    assert isinstance(z,np.ndarray)
    a = sigmoid(z)
    return a*(1 - a)

def dtanh(z: np.ndarray) -> np.ndarray:
    assert isinstance(z,np.ndarray)
    a = tanh(z)
    return 1 - a ** 2

def drelu(z: np.ndarray) -> np.ndarray:
    return np.where(z >= 0, 1, 0)

def dleakyrelu(z: np.ndarray) -> np.ndarray:
    return np.where(z >= 0, 1, 0.01)

def dlinear():
    return 1
