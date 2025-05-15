import sklearn
import pandas as pd
import numpy as np
import sklearn.model_selection
import sklearn.preprocessing
import plotly, xgboost, matplotlib

data= pd.read_csv("MDA-Main/oscar_SciProject_metact.csv")
#print(data)

y= data['ecMaxContribution']
x=data[['field', 'country', 'activityType', 'duration', 'fundingScheme']]

x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(x, y, test_size=0.3, random_state=100)

scaling_cat=sklearn.preprocessing.OneHotEncoder(handle_unknown='ignore')
scaling_cat.fit(x_train)
x_train=scaling_cat.transform(x_train)
x_test=scaling_cat.transform(x_test)



