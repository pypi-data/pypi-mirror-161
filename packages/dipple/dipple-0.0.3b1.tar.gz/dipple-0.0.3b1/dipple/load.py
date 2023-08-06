"""Load dataset into k-batch 

In progress:


"""
################### 

import pandas as pd

################### 

def data_loader(df,batch_size:int,y:str,seed:int=42) -> list:
    """Shuffle & Partition dataframe
    
    Arguments
    ----------
    df : pd.DataFrame
         Pandas DataFrame containing X, y
         
    batch_size : int
                 Size of batch (Recommended batch size to be a power of 2, eg. 16,32,256,1024...)
                 1. Batch -- Length of DataFrame
                 2. Mini-Batch -- Between 1 and Length of DataFrame
                 3. Stochastic -- 1
                 
    y : str
        response variable column name
    
    seed : int
           random seed for shuffling the rows in df
    Returns
    ----------
    all_batch : list
                a list containing all batchs
    
    """
    
    import warnings
    warnings.filterwarnings("ignore")
    
    m = df.shape[0]
    # Randomly Shuffle
    shuffle_df = df.sample(frac = 1,random_state=seed)
    
    shuffle_y = shuffle_df.loc[:,y]
    shuffle_X = shuffle_df.drop(y, axis=1)
    
    # Partitioning for complete mini batch size
    mini_batches = []
    complete_batch = m // batch_size
    
    
    for batch in range(complete_batch):
        mini_batch_X = shuffle_X.iloc[batch_size*batch : batch_size*(batch+1)]
        mini_batch_y = shuffle_y.iloc[batch_size*batch : batch_size*(batch+1)]
        mini_batch = (mini_batch_X,mini_batch_y)
        
        mini_batches.append(mini_batch)
    
    # Partitioning for last incomplete case (If have)  
    if m % batch_size != 0:
        mini_batch_X = shuffle_X.iloc[batch_size*complete_batch: ]
        mini_batch_y = shuffle_y.iloc[batch_size*complete_batch: ]
        mini_batch = (mini_batch_X,mini_batch_y)
        
        mini_batches.append(mini_batch)
    
    return mini_batches