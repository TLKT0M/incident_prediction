import pandas as pd
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from classes.incident import Incident
from classes.stateinfo import Stateinfo
from classes.vehicleinfo import Vehicleinfo
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../api/data/test.db'
db = SQLAlchemy(app)
pd.set_option('display.max_columns', None) 


"""Preparing incident data for SQL entry

Return: Clean Incident dataframe 
"""

def get_main_Df():
    dfs = []
    dataFiles = os.listdir("api/data/incident/")
    for filename in dataFiles:
        os.rename("api/data/incident/"+filename, ("api/data/incident/"+filename).replace('_', ''))
        df = pd.read_csv(("api/data/incident/"+filename).replace('_', ''),delimiter=';')
        df = df.rename(columns={'LICHT':'ULICHTVERH','IstSonstig':'IstSonstige'})
        df = df.drop(['FID','OBJECTID','UIDENTSTLA','OBJECTID_1','UIDENTSTLAE','IstGkfz','LINREFX','LINREFY','IstStrasse','STRZUSTAND'], axis=1, errors='ignore')
        dfs.append(df)
        lastdf = df
    new_df = pd.concat(dfs)
    new_df.replace(',','.')
    print(new_df.shape)
    return new_df

def get_location_information():
    df = pd.read_csv(("api/data/Regierungsbezirke.csv").replace('_', ''),delimiter=';')
    return df

def get_vehicle_information():
    df = pd.read_csv(("api/data/pkwanzahl.csv").replace('_', ''),delimiter=';')
    return df

"""Imports Incidents into SQL Database

Keyword arguments:
df -- Incident Dataframe
"""

def import_to_db(df):
    print(df.columns)
    print(df)
    #db.create_all()
    for row in df.itertuples():
        new_incident = Incident(ULAND=row[1],UREGBEZ=row[2],UKREIS=row[3],UGEMEINDE=row[4],UJAHR=row[5],UMONAT=row[6],USTUNDE=row[7],UWOCHENTAG=row[8],UKATEGORIE=row[9],UART=row[10],UTYP1=row[11],ULICHTVERH=row[12],IstRad=row[13],IstPKW=row[14],IstFuss=row[15],IstKrad=row[16],IstSonstige=row[17],XGCSWGS84=float(str(row[18]).replace(',','.')),YGCSWGS84=float(str(row[19]).replace(',','.')))
        db.session.add(new_incident)
        db.session.commit()

"""Imports Stateinfo into SQL Database

Keyword arguments:
df -- Stateinfo Dataframe
"""

def import_stateinfo_to_db(df):
    print(df)
    for row in df.itertuples():
        new_stateinfo = Stateinfo(Land=row[1], RB=row[2], Kreis=row[3], Gem=row[4], Name=str(row[5]).replace("'", ""), Insgesamt=row[6], Mann=row[7], Weibl=row[8], JeKM=row[9], PLZ=row[10], Long=float(str(row[11]).replace(',', '.')), Lat=float(str(row[12]).replace(',', '.')))
        db.session.add(new_stateinfo)
        db.session.commit()

"""Imports Vehicle into SQL Database

Keyword arguments:
df -- Vehicle Dataframe
"""

def import_vehicleinfo_to_db(df):
    print(df)
    for row in df.itertuples():
        new_vehicleinfo = Vehicleinfo(Key=row[1], KRADanzahl=row[2], KRADweibl=row[3], PKW=row[4], PKWproTausendEW=row[5], KFZinsgesamt=row[6], KFZproTausendEW=row[7])
        db.session.add(new_vehicleinfo)
        db.session.commit()

if __name__ == "__main__":
        import_vehicleinfo_to_db(get_vehicle_information())
