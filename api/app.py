# from crypt import methods
from email.policy import default
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
from classes.stateinfo import Stateinfo
from classes.dataenums import Crashcase, Crashtype, Month
import pandas as pd
from clustering import get_clusters
from classes.cluster import Cluster
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/test.db'
db = SQLAlchemy(app)

def JsonBuilder(obj: Incident):
    retValue = {}
    retValue['XGCSWGS84'] = obj.XGCSWGS84
    retValue['YGCSWGS84'] = obj.YGCSWGS84
    retValue['IstRad'] = obj.IstRad
    retValue['IstPKW'] = obj.IstPKW
    retValue['IstFuss'] = obj.IstFuss
    retValue['IstKrad'] = obj.IstKrad
    retValue['UJAHR'] = obj.UJAHR
    retValue['UMONAT'] = Month(int(obj.UMONAT)).label 
    retValue['UART'] = Crashcase(int(obj.UART)).label
    retValue['UTYP1'] = Crashtype(int(obj.UTYP1)).label
    return retValue

@app.route('/', methods=['GET', 'POST'])
def start_page():
    # Todo Replace with sql  
    df = pd.read_csv(("api/data/Regierungsbezirke.csv").replace('_', ''),delimiter=';')
    # stateinfos = Stateinfo.query.all()
    # print(pd.read_sql(Stateinfo.query.all(), db.engine))  
    df['Name'] = df['Name'].str.replace(r"[\']", r"") 
    if request.method == 'POST':
        city_name = request.form['input_city']
        df_res = df.loc[df['Name'] == city_name]
        if not df_res.empty:    
            land = df_res['Land'].iloc[0]
            req = df_res['RB'].iloc[0]
            kreis = df_res['Kreis'].iloc[0]
            gem = df_res['Gem'].iloc[0]
            return redirect(url_for('incident', land=land, reg=req, kreis=kreis, gem=gem, city_name=city_name))

    df_dict = df['Name'].to_dict()
    cities = json.dumps(df_dict)
    return render_template('startpage.html', cities=cities) 


@app.route('/incident/<string:land>/<string:reg>/<string:kreis>/<string:gem>/', defaults={'city_name': None})
@app.route('/incident/<string:land>/<string:reg>/<string:kreis>/<string:gem>/<string:city_name>/')
def incident(land,reg,kreis,gem, city_name):
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
    print(filterst)
    incidents = Incident.query.filter(text(filterst)).all()
    
    clusters = get_clusters(filterst)
    cluster = pd.DataFrame(clusters, columns=['x','y','count'])
    cluster['x'] = clusters[['XGCSWGS84_agg']]
    cluster['y'] = clusters[['YGCSWGS84_agg']]
    cluster['count'] = clusters[['count']]
    clust = cluster.to_json(orient='records')
    print(clust)
    # clust = {}
    locations = {}
    for i in range(len(incidents)):
        locations['{}'.format(i)] = JsonBuilder(incidents[i])
    locations = json.dumps(locations)
    #print(locations)
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
    filtering = ["Land: "+land,"Regierung: "+reg,"Kreis: "+kreis,"Gemeinde: "+gem]
    return render_template('index.html', incidents=incidents, count_all=count_all, statList=statList, filtering=filtering, locations=locations, clusters=clust, city_name=city_name)


if __name__ == "__main__":
  
    app.run(debug=True)
     
