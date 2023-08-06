# Still rely on L_model_forward

import numpy as np
import matplotlib.pyplot as plt

def plot_decision_boundary(model, X, y): #**model depends from MultilayerPerceptron.py
    # Set min and max values and give it some padding
    x_min, x_max = X[0, :].min() - 1, X[0, :].max() + 1  #Intrapolation
    y_min, y_max = X[1, :].min() - 1, X[1, :].max() + 1
    h = 0.01
    # Generate a grid of points with distance h between them
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    # Predict the function value for the whole grid
    Z = model(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    # Plot the contour and training examples
    plt.contourf(xx, yy, Z, cmap=plt.cm.Spectral)
    plt.ylabel('x2')
    plt.xlabel('x1')
    plt.scatter(X[0, :], X[1, :], c=y, cmap=plt.cm.Spectral)
    plt.show()
    
    
def predict_dec(model , X):
    """
    Used for plotting decision boundary.
    
    Arguments:
    model -- expecting model to contain parameter and its activation function 
             where python dictionary containing your param 
    X -- input data of size (m, K)
    
    Returns
    predictions -- vector of predictions of our model (red: 0 / blue: 1)
    """
    
    # Predict using forward propagation and a classification threshold of 0.5
    #param = model.param
    #forward_activation_function = model.forward_activation_function
    #last_forward_activation_function = model.last_forward_activation_function
    
    #a3, cache = L_model_forward(X, param , forward_activation_function, last_forward_activation_function)
    A, cache = model.predict(X,threshold=0.5)
    #predictions = (a3 >0.5 ) #Default as 0.5 
    
    return predictions