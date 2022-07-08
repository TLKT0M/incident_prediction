import urllib.request
import json
import pandas as pd
import sqlite3
import calendar
import datetime
from datetime import date, datetime

from services.osm_service import get_node_info
from services.historical_weather_service import get_hist_weather

"""Parse json format and extract polygons with 30 Zones in Wuppertal

Keyword arguments:
Return: List of polygons for 30 Zones in Wuppertal
"""

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

"""Parse json format and extract coordinates with schools in Wuppertal

Keyword arguments:
Return: List of coordinates and names for schools in Wuppertal
"""

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

"""Parse json format and extract collection of points with bicycleways in Wuppertal

Keyword arguments:
Return: List of multiple coordinates for bicycle ways in Wuppertal
"""

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

"""Parse json format and extract collection of points with One way Streets in Wuppertal

Keyword arguments:
Return: List of multiple coordinates for One Way Streets in Wuppertal
"""

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

"""Point in Polygon

Keyword arguments:
x -- Coordinats
y -- Coordinates
poly -- List of Coordinates which include a polygon
Return: Returns if given point is a given polygon or not
"""
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

"""Builds list with days for given weekday

Keyword arguments:
year -- Int for year
month -- Int between 1 and 12
weekday -- Int between 0 and 6
Return: List of days which are in the year and month and have the given weekday
"""

def allWeekdaysInMonth(year: int, month: int, weekday: int) -> list:
    days = calendar.monthrange(year, month)[1]
    date_list = []
    for day in range(1, days):
        date_day = date(year, month, day)
        if date_day.weekday() == weekday-1:
            date_list.append(date_day.day)
    return date_list

"""Creates Weather Dataframe for given incidents from city

Keyword arguments:
table_list -- A list with needed attributes, like coordinates of every incident
Return: A dataframe with weather data for every incident 
"""

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

"""Creates OSM Dataframe for given incidents from city

Keyword arguments:
table_list -- A list with needed attributes, like coordinates of every incident
Return: A dataframe with OSM data for every incident 
"""

def createStreetInfoDataframeWuppertal(table_list: list) -> pd.DataFrame:
    df_street_info_list = []
    for incident in table_list:
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
    df_street_info.to_csv('test_5.csv')
    return df_street_info

"""Gets Incident Data and builds table_list for other functions

Keyword arguments:
city_name -- Name of the city which data you want to get
Return: List including: Coordinates, year, month, weekday, hour and id for every incident in the city
"""

def getData(city_name: str):
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
        "SELECT Land, RB, Kreis, Gem FROM stateinfo WHERE Name = ' " + city_name + " '")]

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

    # reading all table names for applying filters
    table_list = [a for a in cur.execute("SELECT XGCSWGS84, YGCSWGS84, UJAHR, UMONAT, USTUNDE, UWOCHENTAG, ID FROM incident WHERE " + filterst)]
    return table_list

if __name__ == '__main__':
    table_list = getData(city_name="Karlsruhe, Stadt")
    df_weather = createWeatherDataframeWuppertal(table_list)
    street_info = createStreetInfoDataframeWuppertal(table_list)
    # for i in table_list:
    #     inSlowZone = False
    #     onBicyleWay = False
    #     # for key in slowZones:
    #     #     if ray_tracing_method(i[0], i[1], slowZones[key]):
    #     #         inSlowZone = True
        
    #     for key in oneWay:
    #         print(oneWay[key])
