# loading in modules
import sqlite3
# from crypt import methods
import numpy as np
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
def dbscan(X, eps, min_samples):
   
    #db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
    db = NearestNeighbors(n_neighbors=4, algorithm='ball_tree').fit(X)
    distances, indices = db.kneighbors(X)
    #print(db.labels_)
    print(X[:,0],X[:,1])

    plt.scatter(X[:,0],X[:,1], c=indices)
   
    plt.title("DBSCAN")
    plt.show()
if __name__ == "__main__":
    # creating file path
    dbfile = 'api/data/test.db'
    # Create a SQL connection to our SQLite database
    con = sqlite3.connect(dbfile)

    # creating cursor
    cur = con.cursor()

    # reading all table names5/9/70/044/
    table_list = [a for a in cur.execute("SELECT XGCSWGS84,YGCSWGS84 from incident  WHERE ULAND=5 AND UREGBEZ=9 AND UKREIS=70 AND UGEMEINDE=044 LIMIT(50000)")]
    # here is you table list


    df = np.array(table_list)

    dbscan(df,0.5,1)
   

    # Be sure to close the connection
    con.close()