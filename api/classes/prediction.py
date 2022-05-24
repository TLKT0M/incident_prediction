
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/test.db'
db = SQLAlchemy(app)

class Prediction(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float, nullable=True)
    long = db.Column(db.Float, nullable=True)
    additionals = db.Column(db.Integer, nullable=True)
    

    def __repr__(self):
        return "Land"+ str(self.additionals)

