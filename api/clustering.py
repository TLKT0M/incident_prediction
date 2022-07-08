# loading in modules
import sqlite3
import numpy as np
from sklearn.cluster import DBSCAN
import pandas as pd
 
"""Extract Clusters from data

Keyword arguments:
filters -- filter for finding right data in SQL 
Return: Dataframe with all clusters in data
"""

def get_clusters(filters):
    # creating file path
    dbfile = 'api/data/test.db'
    # Create a SQL connection to our SQLite database
    con = sqlite3.connect(dbfile)

    # creating cursor
    cur = con.cursor()

    # reading all table names for aplying filters
    table_list = [a for a in cur.execute("SELECT XGCSWGS84,YGCSWGS84 from incident Where " + filters)]
    # here is you table list

    df = np.array(table_list)
    df = pd.DataFrame(table_list, columns=['XGCSWGS84','YGCSWGS84'])
    
    dbscan=DBSCAN(eps=0.0005,min_samples=3)
    dbscan.fit(df[['XGCSWGS84','YGCSWGS84']])
    df['DBSCAN_labels']=dbscan.labels_ 
    unique = df['DBSCAN_labels'].unique()
    
    gf = df.groupby(['DBSCAN_labels']).agg({'XGCSWGS84':['sum','count'],'YGCSWGS84':['sum','count']})
    gf = gf.iloc[1: , :]
    gf["XGCSWGS84_agg"] = gf['XGCSWGS84']['sum'] / gf['XGCSWGS84']['count']
    gf["YGCSWGS84_agg"] =  gf['YGCSWGS84']['sum'] / gf['YGCSWGS84']['count']
    result_df = gf[["XGCSWGS84_agg","YGCSWGS84_agg"]]
    result_df['count'] = gf['YGCSWGS84']['count']
    con.close()
    return result_df


if __name__ == "__main__":
    ...