"""Metrics 

In progress:


"""

from copy import deepcopy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dipple.interpret import plot_decision_boundary,predict_dec

def binary_accuracy(X,Y,model,plot = False,**kwargs): #**model depends from MultilayerPerceptron.py
    """Retrieve the Pandas dataframe of X and Y 
    
    Arguments
    -------------------
    X --- pd.DataFrame
            Dataframe of predictors
    Y --- pd.Series
            Series of class            
    
    Returns
    ------------------
    accuracy --- float
    """
    df_X = deepcopy(X)
    df_Y = deepcopy(Y)
    length = Y.shape[0]
    
    Y_pred = model.predict(X.T)
    Y = Y.values.T
    
    array = Y-Y_pred
    
    accuracy = np.count_nonzero(array==0) / length

    if plot:
        
        if 'title' in kwargs:           # Model with random initialization with Dropout Regularization
            title = kwargs['title']
            plt.title(f'{title}\n Accuracy : {accuracy}')
        
        axes = plt.gca()
        plot_decision_boundary(lambda x: predict_dec(model, x.T), df_X.values.T, df_Y.values)

    return accuracy

