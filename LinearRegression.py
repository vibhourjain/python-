# Importing pandas, numpy and plotting libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# Suppress warnings
import warnings
warnings.filterwarnings('ignore')
# Import library
from sklearn.model_selection import train_test_split
# Normalization method
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import sklearn.metrics as metrics
# Import Ridge regression module, Grid Serach CV and KFold
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import Ridge
# Importing Lasso module
from sklearn.linear_model import Lasso
# Commented out IPython magic to ensure Python compatibility.
pd.set_option('display.max_columns', None)
# %matplotlib inline

###############################
##Step: Read the data
###############################


f=r'/content/train.csv'
df = pd.read_csv(f)
df.head()
df.describe()
df.shape
df.info()

###############################
##Step: Data Cleanisation
###############################
#Feature Engineering
# Age of the house 
df['AgeHouse'] = df['YrSold'] - df['YearBuilt']
df.head()

# Removing columns
df.drop(['YearBuilt', 'YearRemodAdd', 'GarageYrBlt', 'YrSold', 'MoSold'], axis=1, inplace=True)

# Converting column type for categorical variable from numeric to object
df['MSSubClass'] = df['MSSubClass'].astype('object')
df['OverallQual'] = df['OverallQual'].astype('object')
df['OverallCond'] = df['OverallCond'].astype('object')


