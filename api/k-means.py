from matplotlib import pyplot as plt
import numpy as np
from scipy.spatial import distance
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets import make_blobs
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

def dbscan(X, eps, min_samples):
    dbs = DBSCAN(eps=eps, min_samples=min_samples)
    dbs.fit(X)
    y_pred = dbs.fit_predict(X)
    plt.scatter(X[:,0], X[:,1],c=y_pred, cmap='Paired')
    plt.title("DBSCAN")
    plt.show()

if __name__ == "__main__":
    db.
   