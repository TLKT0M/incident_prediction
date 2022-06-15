from operator import imod
import pandas as pd
from regex import P
from sqlalchemy import text
from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from get_data import get_location_information, get_main_Df, get_vehicle_information
from classes.incident import Incident
from classes.stateinfo import Stateinfo
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import warnings
from keras.models import Sequential
from keras.layers import Dense

warnings.simplefilter(action='ignore', category=FutureWarning) # Distplot will remove in future Version
def preprocess_data():
   df = get_main_Df()
   veh_df = get_vehicle_information()
   state_df = get_location_information()
   df["Key"] = df["ULAND"].astype(str) + df["UREGBEZ"].astype(str) + df["UKREIS"].astype(str) + df["UGEMEINDE"].astype(str)  
   df = df.drop(['ULAND','UREGBEZ','UKREIS','UGEMEINDE'], axis=1, errors='ignore')
   state_df["Key"] = state_df["Land"].astype(str) + state_df["RB"].astype(str) + state_df["Kreis"].astype(str) + state_df["Gem"].astype(str) 
   veh_df['Key'] = veh_df['Key'].astype(str)
   result = pd.merge(df,state_df, how='left',on="Key")
   # print(result)
   return result

"""
df['hhhh'] = df['dddd'].apply()lambda x: ""wert if "wert in str(x) else x")

"""

def explode(df, cols):
   row_count = len(df)
   new_cols = []
   for col in cols:
      unVals = df[col].value_counts()
      unVals = unVals[unVals.values > round(row_count*0.05)]
      for key in unVals.index:
         name = str(col)+"_"+ str(key)
         new_cols.append([col,name,key])
         df[name] = np.nan
   for col,name,key in new_cols:
      df[name] = np.where(df[col] == key,1,0)
   # print(df)
   return df

   
    
if __name__ == "__main__":
   df =preprocess_data()
   df = df.drop(['ULAND','UREGBEZ','UKREIS','UGEMEINDE','YGCSWGS84','XGCSWGS84','UJAHR','Key','Land','RB','Kreis','Gem','Name','PLZ','Long','Lat'], axis=1, errors='ignore')
   #new_df = df[['IstRad','IstPKW','IstFuss','IstKrad','IstSonstige','UKATEGORIE']]
   new_df = df[['ULICHTVERH','UART','UKATEGORIE', 'UWOCHENTAG']]
   new_df = explode(new_df, ['ULICHTVERH','UART', 'UWOCHENTAG'])
   new_df = new_df.drop(['ULICHTVERH', 'UWOCHENTAG', 'UART'], axis=1)
   y = new_df[['UKATEGORIE']].to_numpy()
   real_y = y[1000:11000]
   y = y[0:10000]
   
   new_df = new_df.drop(['UKATEGORIE'], axis=1)
   x = new_df.to_numpy()
   real_x = x[10001:11000]
   x = x[0:10000]
   

   model = Sequential()
   model.add(Dense(12, input_dim=19, activation='relu'))
   model.add(Dense(100, activation='relu'))
   model.add(Dense(1, activation='sigmoid'))
   model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
   model.fit(x, y, epochs=15, batch_size=10)
   
   test_x = np.array([real_x])
   test_y = model.predict(test_x)
   print(real_y)
   print(test_y)
   # sns.heatmap(new_df.corr())
   # plt.show()
   