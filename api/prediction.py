import pandas as pd
from sqlalchemy import text
from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from get_data import get_location_information, get_main_Df, get_vehicle_information
from classes.incident import Incident
from classes.stateinfo import Stateinfo
import get_data
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import warnings

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
   print(result)
   return result

"""
df['hhhh'] = df['dddd'].apply()lambda x: ""wert if "wert in str(x) else x")

"""

def explode(df,cols):
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
   print(df)
   return df

   
    
if __name__ == "__main__":
   df =preprocess_data()
   #df = explode(df,['ULICHTVERH','UART'])
   df = df.drop(['ULAND','UREGBEZ','UKREIS','UGEMEINDE','YGCSWGS84','XGCSWGS84','UJAHR','Key','Land','RB','Kreis','Gem','Name','PLZ','Long','Lat'], axis=1, errors='ignore')
   #new_df = df[['IstRad','IstPKW','IstFuss','IstKrad','IstSonstige','UKATEGORIE']]
   
   new_df = df[['ULICHTVERH','UART','UKATEGORIE']]
   new_df = explode(new_df,['ULICHTVERH','UART'])
   sns.heatmap(new_df.corr())
   plt.show()
   