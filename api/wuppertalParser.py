from msilib.schema import tables
from operator import imod
from os import defpath
from traceback import print_tb
import urllib.request
import json
import numpy as np
import pandas as pd
import sqlite3
import calendar
import datetime
from datetime import date, datetime

from regex import P
from sqlalchemy import null
from services.osm_service import get_node_info
from services.historical_weather_service import get_hist_weather


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

def ray_tracing_method(x: float, y: float, poly: list):
    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(n+1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

def allWeekdaysInMonth(year: int, month: int, weekday: int) -> list:
    days = calendar.monthrange(year, month)[1]
    date_list = []
    for day in range(1, days):
        date_day = date(year, month, day)
        if date_day.weekday() == weekday-1:
            date_list.append(date_day.day)
    return date_list

def createWeatherDataframeWuppertal(table_list: list) -> pd.DataFrame: 
    df_weather_list = []
    for incident in table_list:
        days = allWeekdaysInMonth(incident[2], incident[3], incident[5])
        df_list = []
        for day in days:
            date_string = str(incident[3]) + "-" + str(day) + "-" + str(incident[2])
            time_string = str(incident[4]) + ":00:00"
            weather = get_hist_weather(str(incident[0]), str(incident[1]), date_string, time_string)
            filter = datetime(year=incident[2], month=incident[3], day=day, hour=incident[4])    
            df_temp = weather[weather.index.to_pydatetime() == filter]
            df_list.append(df_temp)
        df_combined = df_list[0]
        for i in range(1, len(df_list)): 
            df_combined = df_combined.append(df_list[i])
        weather_data = pd.DataFrame(df_combined.mean()).transpose()
        weather_data['incident_ID'] = incident[6]
        df_weather_list.append(weather_data)

    df_weather = df_weather_list[0]
    for i in range(1, len(df_weather_list)):
        df_weather = df_weather.append(df_weather_list[i])
    df_weather = df_weather.round(decimals=2)
    return df_weather

def createStreetInfoDataframeWuppertal(table_list: list) -> pd.DataFrame:
    df_street_info_list = []
    for incident in table_list[1000:]:
        street_info = get_node_info(incident[1], incident[0])
        # Generate dict from object
        street_info_dict = street_info.__dict__
        # Delete unnecessary keys
        key = next(iter(street_info_dict))
        street_info_dict.pop(key)
        street_info_dict.pop('speed')
        street_info_dict.pop('cycleway')
        street_info_dict.pop('footway')
        street_info_dict.pop('overtaking')
        street_info_dict.pop('material')
        # Build Dataframe from dict and add info
        street_info_dict = {k:[v] for k,v in street_info_dict.items()}
        df_temp = pd.DataFrame.from_dict(street_info_dict)
        df_temp['incident_ID'] = incident[6]
        df_street_info_list.append(df_temp)

    # Build complete Dataframe
    df_street_info = df_street_info_list[0]
    for i in range(1, len(df_street_info_list)):
        df_street_info = df_street_info.append(df_street_info_list[i])
    df_street_info.to_csv('test_3.csv')
    return df_street_info


if __name__ == '__main__':
    slowZones = get30Zones()
    schools = getSchools()
    bicycleWay = getBicycleWay()
    oneWay = getOneWay()

    # creating file path
    dbfile = 'api/data/test.db'
    # Create a SQL connection to our SQLite database
    con = sqlite3.connect(dbfile)
    # creating cursor
    cur = con.cursor()
    df = [a for a in cur.execute(
        "SELECT Land, RB, Kreis, Gem FROM stateinfo WHERE Name = 'Wuppertal, Stadt'")]

    land = str(df[0][0])
    reg = str(df[0][1])
    kreis = str(df[0][2])
    gem = str(df[0][3])

    filterList = []

    filterList.append("ULAND=" + land)
    filterList.append("UREGBEZ=" + reg)
    filterList.append("UKREIS=" + kreis)
    filterList.append("UGEMEINDE=" + gem)
    filterst = ""
    for fil in filterList:
        filterst += fil + " and "
    filterst = filterst[:-4]

    # reading all table names for aplying filters
    table_list = [a for a in cur.execute("SELECT XGCSWGS84, YGCSWGS84, UJAHR, UMONAT, USTUNDE, UWOCHENTAG, ID FROM incident WHERE " + filterst)]
    # df_weather = createWeatherDataframeWuppertal(table_list)
    # df_weather.to_csv('weather_wuppertal.csv')
    # street_info = createStreetInfoDataframeWuppertal(table_list)
    #     # for i in table_list:
        #     inSlowZone = False
        #     for key in slowZones:
        #         if ray_tracing_method(i[0], i[1], slowZones[key]):
        #             inSlowZone = True
        #     print(inSlowZone)
