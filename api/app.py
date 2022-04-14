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
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/test.db'
db = SQLAlchemy(app)

def JsonBuilder(obj):
    retValue = {}
    retValue['XGCSWGS84'] = obj.XGCSWGS84
    retValue['YGCSWGS84'] = obj.YGCSWGS84
    retValue['IstRad'] = obj.IstRad
    retValue['IstPKW'] = obj.IstPKW
    retValue['IstFuss'] = obj.IstFuss
    retValue['IstKrad'] = obj.IstKrad
    return retValue

@app.route('/', methods=['GET', 'POST'])
def start_page(): 
    df = pd.read_csv(("api/data/Regierungsbezirke.csv").replace('_', ''),delimiter=';')
    df['Name'] = df['Name'].str.replace(r"[\']", r"") 
    if request.method == 'POST':
        value = request.form['input_city']
        df_res = df.loc[df['Name'] == value]
        land = df_res['Land'].iloc[0]
        req = df_res['RB'].iloc[0]
        kreis = df_res['Kreis'].iloc[0]
        gem = df_res['Gem'].iloc[0]
        return redirect(url_for('incident', land=land, reg=req, kreis=kreis, gem=gem))

    df_dict = df['Name'].to_dict()
    cities = json.dumps(df_dict)
    return render_template('startpage.html', cities=cities) 


@app.route('/incident/<string:land>/<string:reg>/<string:kreis>/<string:gem>/')
def incident(land,reg,kreis,gem):
    print("string")
    #region validate input
    if not(land == "*" or land.isnumeric()):
        return jsonify("Error: invalid expression in land")
    if not(reg == "*" or reg.isnumeric()):
        return jsonify("Error: invalid expression in reg")
    if not(kreis == "*" or kreis.isnumeric()):
        return jsonify("Error: invalid expression in kreis")
    if not(gem == "*" or gem.isnumeric()):
        return jsonify("Error: invalid expression in gem")
    #endregion

    #region add filter

    filterList= []
    if land.isnumeric():
        filterList.append("ULAND=" + land)
    if reg.isnumeric():
        filterList.append("UREGBEZ=" + reg) 
    if kreis.isnumeric():
        filterList.append("UKREIS=" + kreis)
    if gem.isnumeric():
        filterList.append("UGEMEINDE=" + gem)
    filterst = ""
    for fil in filterList:
        filterst += fil + " and "  
    filterst = filterst[:-4]
    #endregion

    incidents = Incident.query.filter(text(filterst)).all()
    
    locations = {}
    for i in range(len(incidents)):
        locations['{}'.format(i)] = JsonBuilder(incidents[i])
    locations = json.dumps(locations)

    #region do stats
    
    count_all = len(incidents)
    statList = []
    count_IstRad =0
    count_IstPKW = 0
    count_IstFuss = 0
    count_IstKrad = 0
    try:
        for i in incidents:
            count_IstFuss = count_IstFuss + i.IstFuss
            count_IstRad = count_IstRad + i.IstRad
            count_IstKrad = count_IstKrad + i.IstKrad
            count_IstPKW = count_IstPKW + i.IstPKW
        statList.append(round((count_IstFuss / count_all)*100,2))
        statList.append(round((count_IstRad / count_all)*100,2))
        statList.append(round((count_IstKrad / count_all)*100,2))
        statList.append(round((count_IstPKW / count_all)*100,2)) 
    except ZeroDivisionError: 
        return jsonify("Nothing Found, Please enter Valid Numbers")
    
    #endregion
    XGCSWGS84 =[]
    YGCSWGS84 =[]
    for incident in incidents:
        XGCSWGS84.append(incident.XGCSWGS84)
        YGCSWGS84.append(incident.YGCSWGS84)
    df = np.array([YGCSWGS84,XGCSWGS84])
    dbscan(df,0.5,1)
    filtering = ["Land: "+land,"Regierung: "+reg,"Kreis: "+kreis,"Gemeinde: "+gem]
    return render_template('index.html', incidents=incidents, count_all=count_all, statList=statList, filtering=filtering, locations=locations)

def dbscan(X, eps, min_samples):
    db = DBSCAN(eps=eps, min_samples=min_samples)
    db.fit(X)
    y_pred = db.fit_predict(X)
    print(y_pred)
    plt.scatter(X[:,0], X[:,1],c=y_pred, cmap='Paired')
    plt.title("DBSCAN")
    plt.savefig('books_read.png')

if __name__ == "__main__":
  
    app.run(debug=True)
     