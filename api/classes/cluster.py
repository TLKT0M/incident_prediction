
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/test.db'
db = SQLAlchemy(app)

class Cluster(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    XGCSWGS84 = db.Column(db.Float, nullable=True)
    YGCSWGS84 = db.Column(db.Float, nullable=True)
    COUNT = db.Column(db.Integer, nullable=True)
    

    def __repr__(self):
        return "Land"+ str(self.ULAND)

