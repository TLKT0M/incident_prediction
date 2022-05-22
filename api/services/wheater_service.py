
import requests
from datetime import datetime, timedelta

def get_weather(long,lat,date, acc_hour):
    key = "2QAUASHFC4YSHTZC6YXVV97NN"
    content_type = "json"
    date_first = datetime.strptime(date, '%m-%d-%Y').date()
   
    url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"+lat+"%2C"+long+"/"+str(date_first)+"/"+str(date_first)+"?unitGroup=metric&include=hours&key="+key+"&contentType=json"
    response = requests.get(url)
    resp = response.json()
    resp_hours = resp['days'][0]['hours']
    for hour in resp_hours:
        if str(hour['datetime']) == acc_hour:
            print("moinsen")
            print(hour)
            

if __name__ == "__main__":
    get_weather("10.621659329","53.7296148","01-03-2016","01:00:00")
