from crypt import methods
from distutils.log import debug
import json
from sqlalchemy import text
from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
from classes.incident import Incident

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
    
    return render_template('index.html', incidents=Incident.query.filter(text(filterst)).all())


if __name__ == "__main__":
    app.run(debug=True)
    