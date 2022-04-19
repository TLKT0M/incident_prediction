# loading in modules
import sqlite3
# from crypt import methods
import numpy as np
from pyparsing import col
from scipy.spatial import distance
from sklearn.cluster import DBSCAN
from matplotlib import pyplot as plt
from distutils.log import debug
from get_data import get_main_Df
import json
from sqlalchemy import text
from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
from classes.incident import Incident
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import matplotlib

from sklearn.cluster import DBSCAN


if __name__ == "__main__":
    # creating file path
    dbfile = 'api/data/test.db'
    # Create a SQL connection to our SQLite database
    con = sqlite3.connect(dbfile)

    # creating cursor
    cur = con.cursor()

    # reading all table names5/9/70/044/
    table_list = [a for a in cur.execute("SELECT XGCSWGS84,YGCSWGS84 from incident  ")]
    # here is you table list


    df = np.array(table_list)
    df = pd.DataFrame(table_list, columns=['XGCSWGS84','YGCSWGS84'])


    dbscan=DBSCAN(eps=0.0005,min_samples=3)
    dbscan.fit(df[['XGCSWGS84','YGCSWGS84']])
    df['DBSCAN_labels']=dbscan.labels_ 
    print(df['DBSCAN_labels'])
    # Plotting resulting clusters
    plt.figure(figsize=(10,10))
    plt.scatter(df['XGCSWGS84'],df['YGCSWGS84'],c=df['DBSCAN_labels'],s=15)
    plt.title('DBSCAN Clustering',fontsize=20)
    plt.xlabel('Feature 1',fontsize=14)
    plt.ylabel('Feature 2',fontsize=14)
    plt.show()
    con.close()