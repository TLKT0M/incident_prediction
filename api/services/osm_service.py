
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET


def get_node_info(long,lat):
    para= 0.0001
    maxspeed = None #https://wiki.openstreetmap.org/wiki/DE:Key:maxspeed
    cycleway = None #https://wiki.openstreetmap.org/wiki/DE:Key:cycleway
    footway = None #https://wiki.openstreetmap.org/wiki/Key:foot
    lit = None #https://wiki.openstreetmap.org/wiki/DE:Key:lit
    name = None # https://wiki.openstreetmap.org/wiki/DE:Key:name
    overtaking = None #https://wiki.openstreetmap.org/wiki/Key:overtaking
    surface = None #https://wiki.openstreetmap.org/wiki/DE:Key:surface
    for i in range(0,10):
        para += 0.0002
        x_plus= float(long)+para
        x_min = float(long)-para
        y_plus=float(lat)+para
        y_min =float(lat)-para
        payload = "[bbox:"+str(x_min)+","+str(y_min)+","+str(x_plus)+","+str(y_plus)+"];\nway;\nout body;\n\n"
        headers = {
            'Content-Type': 'text/plain'
        }
    
        url = "https://z.overpass-api.de/api/interpreter"
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            resp = response.text
            root = ET.fromstring(resp)
            for way in root.findall("way"):
                for tag in way.findall("tag"):
                    if maxspeed == None and tag.attrib['k'] == "maxspeed":
                        maxspeed = tag.attrib['v']
                    if cycleway == None and tag.attrib['k'] == "cycleway":
                        cycleway = tag.attrib['v']
                    if footway == None and tag.attrib['k'] == "foot:left" and tag.attrib['k'] == "foot:right":
                        footway = tag.attrib['v']
                    if lit == None and tag.attrib['k'] == "lit":
                        lit = tag.attrib['v']
                    if name == None and tag.attrib['k'] == "name":
                        name = tag.attrib['v']
                    if overtaking == None and tag.attrib['k'] == "overtaking":
                        overtaking = tag.attrib['v']
                    if surface == None and tag.attrib['k'] == "surface":
                        surface = tag.attrib['v']
            
        else:
            raise Exception(response.status_code)
    return name,maxspeed,cycleway,footway,lit,overtaking,surface



if __name__ == "__main__":
    speed = get_node_info("51.313933989000077","7.677151576000028")
    print(speed)