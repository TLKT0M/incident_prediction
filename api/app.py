# from crypt import methods
from audioop import add
from email.policy import default
import numpy as np
from distutils.log import debug
from get_data import get_main_Df
import json
from sqlalchemy import text
from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from classes.incident import Incident
from classes.prediction import Prediction
from classes.stateinfo import Stateinfo
from classes.dataenums import Crashcase, Crashtype, Month, Weekday
import pandas as pd
from clustering import get_clusters
from classes.cluster import Cluster
from services.wheater_service import get_weather
from services.osm_service import get_node_info
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
    retValue['ID'] = obj.ID
    return retValue

@app.route('/pred/',methods=['GET', 'POST'])
def pred_interface():
    if request.method == 'POST':
        print(request.form)
        return redirect(url_for('prediction',lat=request.form['lat'],long=request.form['long'], additionals=request.form['additionals']))
    return render_template("predform.html")

@app.route('/prediction/<string:lat>/<string:long>/<string:additionals>/', methods=['GET', 'POST'])
def prediction(lat,long,additionals):
    pred_class = Prediction()
    pred_class.lat=lat
    pred_class.additionals=additionals
    pred_class.long=long
    date = datetime.today().strftime('%d-%m-%Y')
    dt_string = datetime.today().strftime('%d-%m-%Y') 
    weather_dataset = get_weather(long=long,lat=lat,date=dt_string,acc_hour=datetime.now().strftime("%H:%M:%S"))
    print(weather_dataset)
    street= get_node_info(long=long,lat=lat)
    
    return render_template("predpage.html",predictions=[pred_class],weather=weather_dataset, street=street)

@app.route('/incidentdetail/<int:id>/<string:city_name>/', methods=['GET','POST'])
def incidentdetails(id, city_name):
    filters = " ID = " + str(id)
    incidents = Incident.query.filter(text(filters)).all()

    if request.method == 'POST':
        return redirect(url_for('incident', land=incidents[0].ULAND, reg=incidents[0].UREGBEZ, kreis=incidents[0].UKREIS, gem=incidents[0].UGEMEINDE, city_name=city_name))

    for i in range(len(incidents)):
        incidents[i].UMONAT = Month(incidents[i].UMONAT).label
        incidents[i].UART = Crashcase(incidents[i].UART).label
        incidents[i].UTYP1 = Crashtype(incidents[i].UTYP1).label
        incidents[i].UWOCHENTAG = Weekday(incidents[i].UWOCHENTAG).label
    
    return render_template("detailpage.html", incidents=incidents)

@app.route('/', methods=['GET', 'POST'])
def start_page():
    df = pd.read_csv(("api/data/Regierungsbezirke.csv").replace('_', ''),delimiter=';')

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
    incidents = Incident.query.filter(text(filterst)).all()
     
    clusters = get_clusters(filterst) 
    clusters.columns = clusters.columns.droplevel()
    clusters.columns = ['x', 'y', 'count'] 
    clust = clusters.to_json(orient='records')

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
    filtering = ["Land: "+land,"Regierung: "+reg,"Kreis: "+kreis,"Gemeinde: "+gem]
    return render_template('index.html', incidents=incidents, count_all=count_all, statList=statList, filtering=filtering, locations=locations, clusters=clust, city_name=city_name)


if __name__ == "__main__":
    app.run(debug=True)