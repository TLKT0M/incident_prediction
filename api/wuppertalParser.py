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

def allWeekdaysInMonth(year, month, weekday):
    days = calendar.monthrange(year, month)[1]
    date_list = []
    for day in range(1, days):
        date_day = date(year, month, day)
        if date_day.weekday() == weekday-1:
            date_list.append(date_day.day)
    return date_list

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
    table_list = [a for a in cur.execute("SELECT XGCSWGS84, YGCSWGS84, UJAHR, UMONAT, USTUNDE, UWOCHENTAG FROM incident WHERE " + filterst)]
    for incident in table_list:
        # street_info = get_node_info(table_list[0][1], table_list[0][0])
        days = allWeekdaysInMonth(incident[2], incident[3], incident[5])
        df_list = []
        for day in days:
            date_string = str(incident[3]) + "-" + str(day) + "-" + str(incident[2])
            time_string = str(incident[4]) + ":00:00"
            weather = get_hist_weather(str(incident[0]), str(incident[1]), date_string, time_string)
            filter = datetime(year=incident[2], month=incident[3], day=day, hour=incident[4])    
            temp = weather[weather.index.to_pydatetime() == filter]
            df_list.append(temp)
        df_combined = df_list[0]
        for i in range(1, len(df_list)):
            df_combined = df_combined.append(df_list[i])
        average_day_wheater = df_combined.mean()
    #     # for i in table_list:
        #     inSlowZone = False
        #     for key in slowZones:
        #         if ray_tracing_method(i[0], i[1], slowZones[key]):
        #             inSlowZone = True
        #     print(inSlowZone)m 
