#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

import seaborn as sns
import os
from scipy import stats
import pickle

from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

RANDOM_STATE = 42


# In[2]:


data = pd.read_csv("./concrete_dataset.csv")


data = data.reindex(sorted(data.columns), axis=1)
data = data[(np.abs(stats.zscore(data)) < 3).all(axis=1)]


y = data['strength'].to_numpy()
x = data.drop('strength', axis=1).to_numpy()


# In[12]:


x_train, x_test, y_train, y_test = train_test_split(x, y, train_size = 0.8, test_size = 0.2, random_state=RANDOM_STATE)


rf = RandomForestRegressor(n_estimators=150)
rf.fit(x_train, y_train)


# In[14]:


rf_preds = rf.predict(x_test[0:])
rf_error = np.abs(y_test.reshape(-1,1) - rf_preds.reshape(-1,1))

print("Total number of samples:", len(rf_error))
print("Mean of ground truth is:", np.mean(y_test))
print("Mean absolute error:",np.mean(rf_error))
print("Maximum error is: {}, occurred at: {}, relative values are : {} vs {} -> TRUE".format(np.max(rf_error), np.argmax(rf_error), rf_preds[np.argmax(rf_error)], y_test[np.argmax(rf_error)]))
print("Minimum error is: ",np.min(rf_error))
print("Standard deviation of error is: ",np.std(rf_error))
print("Median of error is: ",np.median(rf_error))
print("99th percentile of error is: ",np.percentile(rf_error, 99))


# In[15]:


plt.hist(rf_error)


# In[20]:


pickle.dump(rf, open("./model.pickle", "wb"));


# In[21]:


print(x_test[0])


# In[ ]:




