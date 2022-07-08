

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/test.db'
db = SQLAlchemy(app)

class Weather(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.String, nullable=True)
    temp = db.Column(db.Float, nullable=True)
    feelslike = db.Column(db.Float, nullable=True)
    snow = db.Column(db.Float, nullable=True)
    visibility = db.Column(db.Float, nullable=True)
    uvindex = db.Column(db.Float, nullable=True)
    cloudcover = db.Column(db.Float, nullable=True)
   
    

    def __repr__(self):
        return "Land"+ str(self.cloudcover)

