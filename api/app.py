from crypt import methods
from distutils.log import debug
import json
from sqlalchemy import text
from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
from classes.incident import Incident
import pandas as pd
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/test.db'
db = SQLAlchemy(app)


@app.route('/incident/<string:land>/<string:reg>/<string:kreis>/<string:gem>/')
def incident(land,reg,kreis,gem):

    #region validate input
    if not(land == "*" or land.isnumeric()):
        return jsonify("Error: invalid expression in land")
    if not(reg == "*" or reg.isnumeric()):
        return jsonify("Error: invalid expression in reg")
    if not(kreis == "*" or kreis.isnumeric()):
        return jsonify("Error: invalid expression in kreis")
    if not(gem == "*" or gem.isnumeric()):
        return jsonify("Error: invalid expression in gem")
    #endregion

    #region add filter

    filterList= []
    if land.isnumeric():
        filterList.append("ULAND=" + land)
    if reg.isnumeric():
        filterList.append("UREGBEZ=" + reg)
    if kreis.isnumeric():
        filterList.append("UKREIS=" + kreis)
    if gem.isnumeric():
        filterList.append("UGEMEINDE=" + gem)
    filterst = ""
    for fil in filterList:
        filterst += fil + " and "
    filterst = filterst[:-4]
    #endregion

    incidents = Incident.query.filter(text(filterst)).all()
    #region do stats
    
    count_all = len(incidents)
    statList = []
    count_IstRad =0
    count_IstPKW = 0
    count_IstFuss = 0
    count_IstKrad = 0
    try:
        for i in incidents:
            count_IstFuss = count_IstFuss + i.IstFuss
            count_IstRad = count_IstRad + i.IstRad
            count_IstKrad = count_IstKrad + i.IstKrad
            count_IstPKW = count_IstPKW + i.IstPKW
        statList.append(round((count_IstFuss / count_all)*100,2))
        statList.append(round((count_IstRad / count_all)*100,2))
        statList.append(round((count_IstKrad / count_all)*100,2))
        statList.append(round((count_IstPKW / count_all)*100,2))
    except ZeroDivisionError:
        return jsonify("Nothing Found, Please enter Valid Numbers")
    #endregion
    filtering = ["Land: "+land,"Regierung: "+reg,"Kreis: "+kreis,"Gemeinde: "+gem]
    return render_template('index.html', incidents=incidents, count_all=count_all, statList=statList, filtering=filtering )


if __name__ == "__main__":
    app.run(debug=True)
    