#!/usr/bin/env python
# coding: utf-8

# status : Try Adding Optimizer 

from time import time
import math
from copy import deepcopy
from .initializer import *
from .activation import * 
from .loss import *
from .load import *
from .metrics import *
from .interpret import *
from .utils.classification_utils import binary_cutoff_threshold
from .utils.py_util import dictionary_to_vector, vector_to_dictionary, gradients_to_vector

#External modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# ---

# In[6]:



def dropout_unit(A,keep_prob):
    """Implement dropout to activation node output
    
    Arguments
    -------------------
    A --- Activation node output
    keep_prob --- The proportion of non-shut-off units in the layer
    
    Returns
    -------------------
    A --- Filtered Activation node output by Dropout filter
    """
    
    D = np.random.rand(A.shape[0],A.shape[1]) < keep_prob   # Dropout filter
    A = np.multiply(A,D)
    
    A /= keep_prob #Inverted dropout
    
    return A


# In[9]:


"""
Forward Propagation Unit Component
"""


def linear_forward(A_prev, W, b):
    """Linear Forward unit
    
    Argument
    ----------    
    1. A_prev --- Activation node of the previous layer A[l-1]
    2. W --- Weight of layer l
    3. b --- Bias of layer l

    Return
    ----------
    1. Z --- Output Z of layer l 
    2. caches --- cache of Linear forward Unit
    """
    Z = np.dot(W, A_prev) + b
    
    assert(Z.shape == (W.shape[0], A_prev.shape[1]))
    cache = (A_prev,W,b)      # A :for dZ, W for dA & to get updating, b for updating , dA for dZ
    
    return Z, cache


def linear_activation_forward(A_prev, W, b, activation_function):
    """Linear Forward unit
    
    Argument
    ----------    
    1. A_prev --- Activation node of the previous layer A[l-1]
    2. W --- Weight of layer l
    3. b --- Bias of layer l

    Return
    ----------
    1. Z --- Output Z of layer l 
    2. caches --- cache of Linear forward Unit and Activation function
    """
    allowed_activation_function = {'sigmoid' : sigmoid,
                                  'tanh': tanh,
                                  'relu':relu,
                                  'leakyrelu' : leakyrelu,
                                  'linear' : linear}
    
    Z, linear_cache = linear_forward(A_prev, W, b)
    g = allowed_activation_function[activation_function]
    A = g(Z)
    
    activation_cache = Z
    
    assert (A.shape == (W.shape[0], A_prev.shape[1]))
    cache = (activation_cache, linear_cache)  # (Z, (A_prev,W,b))

    return A, cache


def L_model_forward(X, param, activation_function, last_activation_function,**kwargs):   # Matter on Dropout
    """Forward propagation model from input to output layer
       Apply parameter to the input X to return the Activation Output 
    
    Argument
    ----------    
    1. X --- Input denoted as A[0]
    2. param --- Weight and Bias of every layer
    3. activation_function --- the activation function for hidden layer 
    4. last_activation_function --- the activation function for output layer 
                                    Binary Classication : sigmoid
                                    Regression : linear
  
    Keyword Argument
    ----------   
    1. keep_prob_sequence --- When the regularization technique is dropout
    
    
    Return
    ----------
    1. AL --- Output A[L] from the propagation (Z[L] with sigmoid activation function)
    2. caches --- the cache of every layer l 
    """

    A = X
    L = (len(param) // 2)  # param stores the weight and bias for L layer, hence len(param) = 2L

    caches = []
    
    if 'keep_prob_sequence' in kwargs:                     #For dropout
        keep_prob_sequence = kwargs['keep_prob_sequence']
        
    # For Hidden Layer [1,2..,L-1]
    for l in range(1,L):  # l = 1,2,..,L-1
        A_prev = A
        W = param["W" + str(l)]
        b = param["b" + str(l)]
        A, cache = linear_activation_forward(A_prev, W, b, activation_function)
        
        if 'keep_prob_sequence' in kwargs:                #For dropout
            A = dropout_unit(A,keep_prob_sequence[l])
            
        caches.append(cache)  # append cache at layer l
    
    # For Output layer [L]
    
    A_prev = A
    W = param["W" + str(L)]
    b = param["b" + str(L)]
    AL, cache = linear_activation_forward(A_prev, W, b, last_activation_function)
    
    if 'keep_prob_sequence' in kwargs:     #For dropout
        A = dropout_unit(A,keep_prob_sequence[l])
        
    caches.append(cache)

    
    assert(AL.shape == (1, X.shape[1]))

    return AL, caches


# In[10]:


def L2_norm(W):
    """ 
    Compute L2 or Frebonius norm of weight matrix 
    
    Arguments:
    ---
    W : np.array
        Weight matrix of each layer
        
    Returns:
    ---
    Norm : float
        The weight norm of that layer
    """
    l2_norm = np.sum(np.square(W))
    return l2_norm


# In[11]:


def compute_cost(AL, Y , **kwargs):
    """
    Compute the cost function with respect to tAL
    cost function : Binary cross entropy
    
    Arguments:
    -----------------------------------------
    A --- predicted value from L-Forward model
    y --- actual output
    
    Keyword Arguments:
    -----------------------------------------
    regularization --- regularization method [L2,dropout]
    lambd --- Regularization parameter for L2 Regularization 
    param --- Parameter for L2 Regularization (Especially weight)
    """
    
    #Setup
    allowed_kwargs = {'regularization','lambd','param'}
    for kwarg in kwargs.keys():
        assert kwarg in allowed_kwargs, 'Invalid keyword argument: ' + kwarg
    
    regularization = kwargs.get('regularization',None)
    if regularization == 'L2':
        assert {'lambd','param'} <= set(kwargs), 'L2 Regularization lacks of keyword argument lambd or param'
        lambd = kwargs['lambd']
        param = kwargs['param']
        
    m = Y.shape[1]
    loss = binary_cross_entropy_loss(AL, Y)
    cost = np.divide(loss, m)  # No significant difference in speed when compare to '/' though
    cost = np.sum(cost, axis=1)
    
    # Regularization
    if regularization:
        if regularization == 'L2':
            L = len(param) // 2

            # L2 Regularization cost
            L2_regularization_cost = 0
            for l in range(1,L+1):    #summation of square of L2 weight norm for every layer
                W = param['W'+str(l)]
                L2_regularization_cost += np.sum(np.square(W))        

            L2_regularization_cost = (lambd / (2*m) ) * L2_regularization_cost
            cost += L2_regularization_cost
    return cost


# In[12]:


"""
Backward Propagation Unit
"""

def linear_backward(dZ, cache):
    """Use dZ from the layer l to obtain dW,dB,dA_prev
    Arguments
    ----------
      dZ -- Gradient of the cost with respect to the linear output (of current layer l)
      cache -- tuple of values (Z,(A_prev, W, b)) coming from the forward propagation in the current layer (We use only linear cache anyway)

    Returns
    ----------
      dA_prev --- Gradient of the cost with respect to the activation node at the previous layer
      dW --- Gradient of the cost with the weight in this layer
      db --- Gradient of the cost with the bias in this layer
    """
    _, linear_cache = cache  # We use only linear cache
    (A_prev, W, b) = linear_cache  # We do not use b to obtain those 3 gradients

    m = dZ.shape[1]  

    dW = (1 / m) * np.dot(dZ, A_prev.T)
    db = (1 / m) * np.sum(dZ, axis=1, keepdims=True)

    dA_prev = np.dot(W.T, dZ)
    
    assert (dA_prev.shape == A_prev.shape)
    assert (dW.shape == W.shape)
    assert (db.shape == b.shape)
    
    return dA_prev, dW, db


def linear_activation_backward(dA, cache, activation_function):
    """Input dA to find dZ, then use dZ to obtain dW,dB,dA_prev
    Arguments
    ----------
      dZ -- Gradient of the cost with respect to the linear output (of current layer l)
      cache -- tuple of values (Z,(A_prev, W, b)) coming from the forward propagation in the current layer (We use only linear cache anyway)
    
    Returns
    ----------
      dA_prev --- Gradient of the cost with respect to the activation node at the previous layer
      dW --- Gradient of the cost with the weight in this layer
      db --- Gradient of the cost with the bias in this layer
    """
    
    allowed_activation_function = {'sigmoid' : dsigmoid,
                                  'tanh': dtanh,
                                  'relu':drelu,
                                  'leakyrelu' : dleakyrelu,
                                  'linear' : 1}
    
    activation_cache, _ = cache  # We use only activation cache
    Z = activation_cache
    
    g_ = allowed_activation_function[activation_function]
    dZ = dA * g_(Z)
    dA_prev, dW, db = linear_backward(dZ, cache)
    
    return dA_prev, dW, db


''' FROZEN
def linear_activation_backward(dA, cache, activation_function):
    """Input dA to find dZ, then use dZ to obtain dW,dB,dA_prev
    Arguments
    ----------
      dZ -- Gradient of the cost with respect to the linear output (of current layer l)
      cache -- tuple of values (Z,(A_prev, W, b)) coming from the forward propagation in the current layer (We use only linear cache anyway)
    
    Returns
    ----------
      dA_prev --- Gradient of the cost with respect to the activation node at the previous layer
      dW --- Gradient of the cost with the weight in this layer
      db --- Gradient of the cost with the bias in this layer
    """
    if activation_function == "relu":
        g_ = drelu
    elif activation_function == "leakyrelu":
        g_ = dleakyrelu
    elif activation_function == "tanh":
        g_ = dtanh
    elif activation_function == "sigmoid":
        g_ = dsigmoid
    else:
        print(f"The activation function {activation_function} not found, relu as default")
        g_ = drelu
    
    activation_cache, _ = cache  # We use only activation cache
    Z = activation_cache

    dZ = dA * g_(Z)
    dA_prev, dW, db = linear_backward(dZ, cache)
    
    return dA_prev, dW, db
'''

def L_model_backward(AL, Y, cache, activation_function, last_activation_function):
    """
    Backward propagation model from output AL to the parameter gradient of all layers
    Apply parameter to the input X to return the Activation Output 
    
    Arguments:
    A --- A at the layer L
    y --- an actual output
    cache --- cache from the forward propagation
    activation_function --- activation function for the hidden layer
    Return:
     grads  -- A dictionary with the gradients
               grads["dA" + str(l)] = ...
               grads["dW" + str(l)] = ...
               grads["db" + str(l)] = ...
    """
    L = len(cache)  # cache for each layer
    grads = {}
    
    # For Output layer
    dAL = np.divide(1 - Y, 1 - AL) - np.divide(Y, AL)  # dA_[L] : Input for the first linear activation backward
                                                        # Loss : Binary Cross Entropy
    
    current_cache = cache[-1] 
    dA_prev, dW, db = linear_activation_backward(dAL,current_cache,last_activation_function)
    grads["dW" + str(L)] = dW
    grads["db" + str(L)] = db
    
    dA = dA_prev
    
    
    # For Hidden layer [L-1, L-2...,1]
    for l in reversed(range(1,L)): 

        current_cache = cache[l-1] 
        (activation_cache, linear_cache) = current_cache
        
        Z = activation_cache
        a_prev, W, b = linear_cache  # Start with Z_[L] , A_[L-1], W_[L], b_[L]
        
        dA_prev, dW, db = linear_activation_backward(dA, current_cache, activation_function)

        grads["dW" + str(l)] = dW
        grads["db" + str(l)] = db
        
        dA = dA_prev

    return grads


# In[14]:


def update_param(param, grads, lr=1e-4, **kwargs):
    """Update parameter 
    Arguments
    ----------------------------------------------------------------
    1. param -- The current parameter (W1,W2,...,WL,b1,b2,...bL)
    2. grads -- the dictionary of gradient that was obtained from L_model_backward function
    3. lr (default=1e-4) : Learning rate
    
    Keyword Arguments
    ----------------------------------------------------------------
    1. regularization -- The regularization technique 
                            ['L2']
    2. lambd -- Regularization parameter for regularization L2 
    3. m --- the number of observations (Future : obtain da[1].shape from grad)
    4. v --- Exponentially weighted average of gradient
    5. beta_1 --- the weight for v_(t-1)
    6. is_nesterov --- Enable nesterov accelerated to momentum ? (True,False)
    7. epsilon --- an error to prevent dividing learning rate by zero to obtain adaptive learning rate
    8. s --- Exponentially weighted average of squared gradient
    9. beta_2 --- the weight for S_(t-1)
    10. t --- The iteration t (Purposely: for Bias correction)
    
    Returns:
    1. updated_param -- The parameter that got updated
    """
    
    
    
    """Setup"""
    allowed_kwargs = {'regularization','lambd','m',
                     'v','beta_1','is_nesterov','epsilon',
                      's','beta_2', 't'}
    for kwarg in kwargs.keys():
        assert kwarg in allowed_kwargs, 'Invalid keyword argument: ' + kwarg
    
    regularization = kwargs.get('regularization',None)
    
    if regularization:
        #update_param_with_regularization(param, grads, lr=lr, regularization = regularization, **kwargs)
        if regularization == 'L2':
            assert {'lambd','m'} <= set(kwargs), 'L2 Regularization lacks of keyword argument lambd or m'
            lambd = kwargs['lambd']
            m = kwargs['m']
    
    # Setup for optimizer case
    optimizer = kwargs.get('optimizer',None)
    if optimizer:
        if optimizer == 'adagrad':
            assert {'s','epsilon'} <= set(kwargs), 'Adagrad lacks of keyword s (squared gradient) or epsilon'
            s = kwargs['s']
            epsilon = kwargs['epsilon']
            
        elif optimizer == 'rmsprop':
            assert {'s','beta_2','epsilon','t'} <= set(kwargs), 'RMSProp lacks of some of this keyword {s (squared gradient),beta_2, epsilon'
            s = kwargs['s']
            beta_2 = kwargs['beta_2']  
            epsilon = kwargs['epsilon']  
            t = kwargs['t']  
            
        elif optimizer == 'momentum':
            is_nesterov = kwargs.get('is_nesterov',None)
            assert {'v','beta_1','t'} <= set(kwargs), 'Momentum lacks of keyword v (gradient) or beta_1'
            v = kwargs['v']    
            beta_1 = kwargs['beta_1'] 
            t = kwargs['t']
            
        elif optimizer == 'adam':
            assert {'v','beta_1','s','beta_2','epsilon','t'} <= set(kwargs), 'RMSProp lacks of keyword s (squared gradient) or beta_2 or epsilon'
            v = kwargs['v']    
            beta_1 = kwargs['beta_1']  
            s = kwargs['s']
            beta_2 = kwargs['beta_2']  
            epsilon = kwargs['epsilon']  
            t = kwargs['t']  
            
        elif optimizer == 'nadam':
            assert {'v','beta_1','s','beta_2','epsilon','t'} <= set(kwargs), 'RMSProp lacks of keyword s (squared gradient) or beta_2 or epsilon'
            v = kwargs['v']    
            beta_1 = kwargs['beta_1']  
            s = kwargs['s']
            beta_2 = kwargs['beta_2']  
            epsilon = kwargs['epsilon']  
            t = kwargs['t']  
            is_nesterov = True
            
            
    """Start Computing"""
    L = len(param) // 2  # number of layers in the neural network (int)
    
    if not optimizer: #No optimizer
        for l in range(1,L+1): # Update rule for each parameter. Use a for loop.
            param["W" + str(l)] -= lr * grads["dW" + str(l)]
            param["b" + str(l)] -= lr * grads["db" + str(l)]
    
    else: # Have optimizer
        if optimizer == 'adagrad':
            for l in range(1,L+1): # Update rule for each parameter. Use a for loop.
                s["W" + str(l)] += grads["dW" + str(l)]**2;
                s["b" + str(l)] += grads["db" + str(l)]**2;
                
                adaptive_lr_W = lr / (np.sqrt(s["W" + str(l)]) + epsilon)
                adaptive_lr_b = lr / (np.sqrt(s["b" + str(l)]) + epsilon)
                
                param["W" + str(l)] -= adaptive_lr_W * grads["dW" + str(l)]
                param["b" + str(l)] -= adaptive_lr_b * grads["db" + str(l)]
                
        elif optimizer == 'rmsprop':
            for l in range(1,L+1): # Update rule for each parameter. Use a for loop.
                s["W" + str(l)] =  beta_2 * s["W" + str(l)] + (1-beta_2) * grads["dW" + str(l)]**2
                s["b" + str(l)] = grads["db" + str(l)]**2;
                                                                                          
                adaptive_lr_W = lr/s["W" + str(l)]
                adaptive_lr_b = lr/s["b" + str(l)]
                
                param["W" + str(l)] -= adaptive_lr_W * grads["dW" + str(l)]
                param["b" + str(l)] -= adaptive_lr_b * grads["db" + str(l)]
    
    # Update parameters other than a vanila gradient descent
    if regularization:    
        if regularization == 'L2':
            for l in range(1,L+1): # For L2 (subtract by weight decay)
                param["W" + str(l)] -= lr * ((lambd/m) * param["W" + str(l)])
    
    return param


# In[15]:


def update_param_with_optimizer(param, grads, lr, **kwargs):
    """
    Case for optimizer
    """
    pass


# In[16]:


def update_param_with_regularization(param, grads, lr, regularization, **kwargs):
    """
    Case for regularization
    """
    
    if regularization == 'L2':
        assert {'lambd','m'} <= set(kwargs), 'L2 Regularization lacks of keyword argument lambd or m'
        lambd = kwargs['lambd']
        m = kwargs['m']
        
    pass

# In[17]:


def gradient_check_n(parameters, gradients, X, Y,  activation_function, last_activation_function , epsilon = 1e-7):
    
    parameters_values, _ = dictionary_to_vector(parameters) #len(parameter_value) = all_parameter
    grad = gradients_to_vector(parameters,gradients)                   # same len 
    num_parameters = parameters_values.shape[0]             # simply len(parameter_value)
    
    J_plus = np.zeros((num_parameters, 1))                  # + epsilon
    J_minus = np.zeros((num_parameters, 1))                 # - epsilon
    gradapprox = np.zeros((num_parameters, 1))              # d..
    
    # Compute gradapprox for every SINGLE parameter
    for i in range(num_parameters):        
       
        thetaplus = np.copy(parameters_values)              # deepcopy
        thetaplus[i][0] = thetaplus[i][0] + epsilon
        AL, caches = L_model_forward(X = X,
                                     param = vector_to_dictionary(thetaplus,parameters), #FIXED
                                     activation_function = activation_function,
                                     last_activation_function = last_activation_function)
        J_plus[i] = compute_cost(AL, Y)
        
        thetaminus = np.copy(parameters_values)
        thetaminus[i][0] = thetaminus[i][0] - epsilon
        AL, caches = L_model_forward(X = X,
                                     param = vector_to_dictionary(thetaminus,parameters),
                                     activation_function = activation_function,
                                     last_activation_function = last_activation_function)
        J_minus[i] = compute_cost(AL,Y)
        
        gradapprox[i] = (J_plus[i]-J_minus[i])/(2*epsilon) # grad of SINGLE param
    
    
    numerator = np.linalg.norm(gradapprox-grad)                   # L2 norm
    denominator = np.linalg.norm(gradapprox)+np.linalg.norm(grad) 
    difference = numerator/denominator

    if difference > 2*epsilon:
        print ("\033[93m" + "⚠️ Probably, there is a mistake in the backward propagation! difference = " + str(difference) + "\033[0m")
    else:
        print ("\033[92m" + "✔️ Your backward propagation works perfectly fine! difference = " + str(difference) + "\033[0m")
    
    return difference


# In[18]:


class MultilayerPerceptron:
    """
    A Deep neural network with L layers
    - Able to fit with the predictors (X) and the response (Y)
    - Able to predict_proba and predict with threshold
    To see the last fit model parameter, uses self.param where self refer to the fit model
    """

    def __init__(self, hyperparam: dict):
        """
        Launch the Deep_L_layer with the given hyperparameter
        
        Arguments:
        hyperparam: A dictionary with key:
         L --- Number of Layers (Hidden layer(s) + Output layer)
         layer_dims --- Number of units of that L layer
         lr --- Learning rate
         forward_activation_function --- Activation function for all hidden layer(s) in forward model (relu,leakyrelu,tanh,sigmoid)
         last_forward_activation_function --- Activation function for all hidden layer(s) in forward model (sigmoid,linear)
          {"L" : 5,
          "layer_dims" : [nrow,8,6,4,2,1],
          "lr" : 1e-5,
          "forward_activation_function" : 'tanh' ,
          "last_forward_activation_function" : 'sigmoid' }
          
        Supported activation
        """
        self.hyperparam = hyperparam  # assume include nrow in dict

        # Required hyperparameter attributes
        self.L = hyperparam["L"]
        self.layer_dims = hyperparam['layer_dims']
        self.lr = hyperparam["lr"]  
        self.forward_activation_function = hyperparam["forward_activation_function"]
        self.last_forward_activation_function = hyperparam["last_forward_activation_function"]
        self.regularization = None
        
        
    def compiles(self, loss='binary_cross_entropy_loss', initialization = 'random' ,regularization = None ,
                 optimizer = None, **kwargs):
        """Compile options for training Deep-L layer Neural network
        
        Arguments
        ------------------------
        loss --- loss function of the predicted value and the observation
                 (default : binary_cross_entropy_loss_function)
        initialization --- weight initialization technique
                 ['zero','random','Xavier','He']
                 (default:random)
        regularization --- regularization technique
                 [None,'L2','dropout']
                 (default:None)
        
        Keyword Arguments
        ------------------------
        lambd ---   L2 Regularization parameter
                    *When regularization is 'L2'
        
        keep_prob_sequence --- Keep probability of the nodes for every layer
                                *When regularization is 'Dropout' 
        """
        
        self.initialization = initialization
        self.optimizer = optimizer
        self.loss = loss
        self.regularization = regularization
        
        allowed_kwargs = {'lambd','keep_prob_sequence',
                         'beta1','use_nesterov','beta2'}
        for kwarg in kwargs.keys():
            assert kwarg in allowed_kwargs, 'Invalid keyword argument: ' + kwarg
        
        if self.regularization:
            if self.regularization == 'L2': # Validate case for L2 regularization
                assert {'lambd'} <= set(kwargs), 'L2 Regularization needs lambd'
                self.lambd = kwargs['lambd']

            elif self.regularization == 'dropout':
                assert {'keep_prob_sequence'} <= set(kwargs), 'Dropout Regularization needs keep_prob_sequence'
                self.keep_prob_sequence = kwargs['keep_prob_sequence']
        
        if self.optimizer:
            if self.optimizer == 'momentum': #add beta but adam:beta1 beta2
                beta1
            
        
    def fit(
        self,
        X: pd.DataFrame,
        Y: pd.Series,
        Epochs: int,
        batch_size:int=32 ,
        seed:int = 42,
        report_cost: bool = True,
        grad_check:bool = False,
        warmup: bool = False
    ):
        """
        Fit the launched Deep L layer with the given data X , Y

        Arguments:
         X --- Pandas Dataframe of predictors
         Y --- Pandas Series of response (0 : negative, 1:positive)
         Epoch --- number of epochs 
         batch_size --- Size of batch (Stochastic:1,Mini batch:around 1 and m, Batch: m) 
         seed --- Random seed for shuffling the row in DataFrame (for non-batch gradient descent)
         report_cost --- report the cost epochs every 1000 epoch
         grad_check --- Numerically test on the precision of backprop gradient
         warmup --- update param and save the parameter
        """

        ## First, we initiate the attributes
        df = pd.concat([X,Y],axis=1)
        mini_batches = data_loader(df,batch_size,Y.columns)
        
        # Assign class attribute
        self.param = initiate_param(layer_dims = self.layer_dims,
                                        initialization = self.initialization)

        self.cost_list = []
        for epoch in range(1,Epochs+1):    # Start fitting
            cost = 0                   # initial cost for every epoch
            for batch in range(len(mini_batches)):
                
                mini_batch = mini_batches[batch]
                mini_batch_X , mini_batch_y = mini_batch[0], mini_batch[1]
                
                # We turn Dataframe into Numpy format
                mini_batch_X = mini_batch_X.to_numpy().T
                mini_batch_y = mini_batch_y.to_numpy().T
                self.m = mini_batch_y.shape[1]; # Size of each batch
                nrow = np.shape(mini_batch_X)[0] # Number of feature
                
                # Forward Prop
                if self.regularization == 'dropout':                # For Dropout
                    AL, cache = L_model_forward(mini_batch_X, self.param, 
                                               activation_function=self.forward_activation_function,
                                              last_activation_function=self.last_forward_activation_function,
                                                keep_prob_sequence = self.keep_prob_sequence )

                else:
                    AL, cache = L_model_forward(mini_batch_X, self.param, 
                                               activation_function=self.forward_activation_function,
                                              last_activation_function=self.last_forward_activation_function )
                
                # Compute cost function 
                
                if self.regularization == 'L2':                # For L2        
                    cost += compute_cost(AL, mini_batch_y,
                                       param = self.param, 
                                        regularization = 'L2',
                                        lambd = self.lambd)
                else:
                    cost += compute_cost(AL, mini_batch_y)

                # Backward Prop ## 
                self.grads = L_model_backward(AL, mini_batch_y, cache,                       #Obtain gradient # + turn grad to .self.grad
                                         self.forward_activation_function,
                                        self.last_forward_activation_function)

                #Gradient checking
                if (grad_check and epoch % 1000 == 0):
                    gradient_check_n(self.param , self.grads, mini_batch_X, mini_batch_y , 
                                     activation_function = self.forward_activation_function,
                                    last_activation_function=self.last_forward_activation_function )
                    

                # Update paramater by gradient
                if self.regularization:
                    if self.regularization == 'L2':
                        self.param = update_param(param = self.param, 
                                                  grads = self.grads, 
                                                  lr=self.lr,
                                                  regularization='L2',
                                                  lambd=self.lambd,
                                                  m=self.m)
                
                if self.optimizer:
                    if self.optimizer == 'adagrad':
                        pass
                else:
                    self.param = update_param(self.param, self.grads, lr=self.lr)
                
            
            self.cost_list.append(np.squeeze(cost)/self.m)
            if (report_cost and epoch % 1000 == 0):
                print(f"Epoch {epoch}/{Epochs} : ===Cost=== : {np.squeeze(cost)/len(mini_batches)}")
        
        if report_cost:
            plt.plot(self.cost_list ,)       
            plt.xlabel("Epoch")
            plt.ylabel("Cost function")
            plt.show()
    
    def predict(self, X: pd.DataFrame, threshold: float = 0.5,predict_proba=False):
        """Predict the observation given input X
        
        Arguments:
         X --- Pandas Dataframe or Series of predictors
        """
        
        A_prob, _ = L_model_forward(X, self.param, 
                            activation_function=self.forward_activation_function,
                            last_activation_function=self.last_forward_activation_function
                           )
        
        
        if not predict_proba:
            A_pred = binary_cutoff_threshold(A_prob, threshold)
        else:
            A_pred = A_prob
        return A_pred

    def __repr__(self):
        return f"Deep_L_Layer({self.hyperparam})"

    def __str__(self):
        return f"A Deep {self.L} Neural network with learning rate = {self.lr} (Forward activation :{self.forward_activation_function},Backward activation :{self.backward_activation_function})"



