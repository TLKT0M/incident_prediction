# Import Meteostat library and dependencies
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
from meteostat import Point, Daily,Hourly,Stations
from numpy import NaN
def get_station(x,y,count):
    stations = Stations()
    stations = stations.nearby(float(y), float(x))
    stations = stations.fetch(10)
    stations = stations[stations["wmo"] != "<NA>"]
    if len(stations) < count:
        return None
    else:
        return stations.iloc[count]['wmo']
#get_hist_weather("10.621659329","50.7296148","01-03-2016","17:00:00")
def get_hist_weather(x,y,date,time):
    date = date +" "+time
    start = datetime.strptime(date, '%m-%d-%Y %H:%M:%S')
    end = start + timedelta(hours=1)
    count = 0
    found=False
    data= pd.DataFrame()
    while found==False and count <=5:
        station = get_station(x,y,count)
        if station != None:
            data = Hourly(station, start, end)
            data = data.fetch()
            data = data[data['temp'] != NaN]
            if len(data) > 0:
                found=True
        count = count+1
    if found== True:
        return data
    else:
        return None


#if __name__ == "__main__":
#    print(get_hist_weather("10.621659329","50.7296148","01-03-2016","17:00:00"))