import urllib.request, json 
import numpy as np

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
    test = getOneWay()
    print(test)
    # x = 7.20
    # y = 51.27476788705908

    # for i in test:
    #     print(i)
    #     print(ray_tracing_method(x, y, test[i]))