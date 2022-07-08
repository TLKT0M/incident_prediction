import requests
import xml.etree.ElementTree as ET
from classes.street import Street
import time

"""Extracts Street Info from Open Street Map API 

Keyword arguments:
lat -- float lat-coordinate
long -- float long-coordinate
Return: A street object with all extracted data
"""
def get_node_info(lat, long):
    para= 0.0001
    maxspeed = None #https://wiki.openstreetmap.org/wiki/DE:Key:maxspeed
    cycleway = None #https://wiki.openstreetmap.org/wiki/DE:Key:cycleway
    footway = None #https://wiki.openstreetmap.org/wiki/Key:foot
    lit = None #https://wiki.openstreetmap.org/wiki/DE:Key:lit
    name = None #https://wiki.openstreetmap.org/wiki/DE:Key:name
    overtaking = None #https://wiki.openstreetmap.org/wiki/Key:overtaking
    surface = None #https://wiki.openstreetmap.org/wiki/DE:Key:surface
    found= False
    street = Street()
    street.name,street.speed,street.cycleway,street.footway,street.overtaking,street.material,street.lit= None,None,None,None,None,None,None
    while found == False:
        para += 0.0002
        x_plus= float(lat)+para
        x_min = float(lat)-para
        y_plus=float(long)+para
        y_min =float(long)-para
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
                    if name == None and tag.attrib['k'] == "name":
                        found=True
                        street.name = tag.attrib['v']
                    if maxspeed == None and tag.attrib['k'] == "maxspeed":
                        maxspeed = tag.attrib['v']
                        found=True
                        street.maxspeed = tag.attrib['v']
                    if cycleway == None and tag.attrib['k'] == "cycleway":
                        cycleway = tag.attrib['v']
                        street.cycleway = tag.attrib['v']
                    if footway == None and tag.attrib['k'] == "foot:left" and tag.attrib['k'] == "foot:right":
                        footway = tag.attrib['v']
                        street.footway = tag.attrib['v']
                    if lit == None and tag.attrib['k'] == "lit":
                        lit = tag.attrib['v']
                        street.lit = tag.attrib['v']
                    if overtaking == None and tag.attrib['k'] == "overtaking":
                        overtaking = tag.attrib['v']
                        street.overtaking = tag.attrib['v']
                    if surface == None and tag.attrib['k'] == "surface":
                        surface = tag.attrib['v']
                        found=True
                        street.surface = tag.attrib['v']
            
        elif response.status_code == 429:
            time.sleep(3)
            get_node_info(lat, long)
        elif response.status_code == 504:
            time.sleep(1)
            get_node_info(lat, long)
        else:
            raise Exception(response)
    return street

