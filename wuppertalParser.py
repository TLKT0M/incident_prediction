from os import defpath
import urllib.request, json 
import numpy as np
import pandas as pd
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from api.classes.incident import Incident
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api/data/test.db'
db = SQLAlchemy(app)

def get30Zones():
    with urllib.request.urlopen("https://daten.wuppertal.de/Transport_Verkehr/Tempo30-Zonen_EPSG4326_JSON.json") as url:
        data = json.loads(url.read().decode())

    idList = {}
    for i in range(len(data['features'])):
        id = data['features'][i]['properties']['Id']
        coordinates = data['features'][i]['geometry']['coordinates'][0]
        type = data['features'][i]['geometry']['type']
        if id in idList or type == 'MultiPolygon':
            continue
        idList[id] = coordinates

    return idList

def getSchools():
    with urllib.request.urlopen("https://daten.wuppertal.de/Soziales/Schulen_EPSG4326_JSON.json") as url:
        data = json.loads(url.read().decode())
    idList = {}
    for i in range(len(data['features'])):
        id = data['features'][i]['properties']['ID']
        name = data['features'][i]['properties']['Name']
        coordinates = data['features'][i]['geometry']['coordinates']
        idList[id] = [name, coordinates]

    return idList

def getBicycleWay():
    with urllib.request.urlopen("https://daten.wuppertal.de/Transport_Verkehr/Radwege_EPSG4326_JSON.json") as url:
        data = json.loads(url.read().decode())
    idList = {}
    for i in range(len(data['features'])):
        id = data['features'][i]['properties']['STR_NR']
        coordinates = data['features'][i]['geometry']['coordinates']
        lighted = data['features'][i]['properties']['BELEUCHT']

        temp = []
        for i in coordinates:
            if i[2] != 0:
                del i[-1]
                temp.append(i)
        coordinates = temp
        idList[id] = [lighted, coordinates]
    return idList

def getOneWay():
    with urllib.request.urlopen("https://daten.wuppertal.de/Transport_Verkehr/Einbahnstrassen_EPSG4326_JSON.json") as url:
        data = json.loads(url.read().decode())
    idList = {}
    for i in range(len(data['features'])):
        id = data['features'][i]['properties']['STR_NR']
        coordinates = data['features'][i]['geometry']['coordinates']
        name = data['features'][i]['properties']['STR_NAME']
        bicyleFree = data['features'][i]['properties']['RAD_FREI']

        for i in coordinates:
            del i[-1]
        idList[id] = [name, coordinates, bicyleFree]
    return idList    

def ray_tracing_method(x:float, y:float ,poly:list):
    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

if __name__ == '__main__':
    slowZones = get30Zones()
    schools = getSchools()
    bicycleWay = getBicycleWay()
    oneWay = getOneWay()
    
    x = 7.06338478300006 
    y = 51.2309223930001

    df = pd.read_csv(("api/data/Regierungsbezirke.csv").replace('_', ''),delimiter=';')

    df['Name'] = df['Name'].str.replace(r"[\']", r"") 
    df_res = df.loc[df['Name'] == 'Wuppertal, Stadt']
    if not df_res.empty:    
        land = str(df_res['Land'].iloc[0])
        reg = str(df_res['RB'].iloc[0])
        kreis = str(df_res['Kreis'].iloc[0])
        gem = str(df_res['Gem'].iloc[0])
    
        filterList= []
        
        filterList.append("ULAND=" + land)
        
        filterList.append("UREGBEZ=" + reg) 

        filterList.append("UKREIS=" + kreis)

        filterList.append("UGEMEINDE=" + gem)
        filterst = ""
        for fil in filterList:
            filterst += fil + " and "  
        filterst = filterst[:-4]
      
        incidents = Incident.query.filter(text(filterst)).all()
        print(incidents)

    # inSlowZone = False
    # for i in slowZones:
    #     if ray_tracing_method(x, y, slowZones[i]):
    #         inSlowZone = True
    # print(inSlowZone)