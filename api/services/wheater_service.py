import imp
from classes.wheater import Weather
import requests
from datetime import datetime, timedelta
#get_weather("10.621659329","53.7296148","01-03-2016","01:00:00")
def get_weather(long,lat,date, acc_hour):
    key = "2QAUASHFC4YSHTZC6YXVV97NN"
    content_type = "json"
    date_first = datetime.strptime(date, '%d-%m-%Y').date()
    url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"+lat+"%2C"+long+"/"+str(date_first)+"/"+str(date_first)+"?unitGroup=metric&include=hours&key="+key+"&contentType=json"
    response = requests.get(url)
    resp = response.json()
    resp_hours = resp['days'][0]['hours']
    for data in resp_hours:
        if str(data['datetime'])[0:2] == acc_hour[0:2]:
            wea = Weather()
            wea.temp = data['temp']
            wea.datetime = data['datetime']
            wea.feelslike = data['feelslike']
            wea.visibility = data['visibility']
            wea.cloudcover = data['cloudcover']
            wea.snow = data['snow']
            wea.uvindex = data['uvindex']
            
            return wea
    return None       


