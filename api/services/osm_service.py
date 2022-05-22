
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET


def get_node_info(long,lat):
    para= 0.0001
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
                    if tag.attrib['k'] == "maxspeed":
                        return(tag.attrib['v'])
        else:
            raise Exception(response.status_code)
    return None


if __name__ == "__main__":
    speed = get_node_info("51.313933989000077","7.677151576000028")
    print(speed)