from unittest import main
import numpy as np
import pandas as pd
import os
import csv
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from classes.incident import Incident
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../api/data/test.db'
db = SQLAlchemy(app)
pd.set_option('display.max_columns', None) 

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
    return new_df


def get_location_information():
    df = pd.read_csv(("data/Regierungsbezirke.csv").replace('_', ''),delimiter=';')
    return df

def import_to_db(df):
    print(df.columns)
    print(df)
    #db.create_all()
    for row in df.itertuples():
        new_incident = Incident(ULAND=row[1],UREGBEZ=row[2],UKREIS=row[3],UGEMEINDE=row[4],UJAHR=row[5],UMONAT=row[6],USTUNDE=row[7],UWOCHENTAG=row[8],UKATEGORIE=row[9],UART=row[10],UTYP1=row[11],ULICHTVERH=row[12],IstRad=row[13],IstPKW=row[14],IstFuss=row[15],IstKrad=row[16],IstSonstige=row[17],XGCSWGS84=float(str(row[18]).replace(',','.')),YGCSWGS84=float(str(row[19]).replace(',','.')))
        db.session.add(new_incident)
        db.session.commit()
  
if __name__ == "__main__":
        import_to_db(get_main_Df())
