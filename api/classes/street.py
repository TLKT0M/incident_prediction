

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/test.db'
db = SQLAlchemy(app)

class Street(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    speed = db.Column(db.Float, nullable=True)
    cycleway = db.Column(db.Float, nullable=True)
    footway = db.Column(db.Float, nullable=True)
    lit = db.Column(db.Float, nullable=True)
    overtaking = db.Column(db.Float, nullable=True)
    material = db.Column(db.Float, nullable=True)
   
    

    # def __repr__(self):
    #     return "Land"+ str(self.cloudcover)

