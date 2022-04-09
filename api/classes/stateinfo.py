
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/test.db'
db = SQLAlchemy(app)
class Stateinfo(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    Land = db.Column(db.String, nullable=True)
    RB= db.Column(db.String, nullable=True)
    Kreis= db.Column(db.String, nullable=True)
    Gem= db.Column(db.String, nullable=True)
    Name= db.Column(db.String, nullable=True)
    Insgesamt= db.Column(db.Integer, nullable=True)
    Mann= db.Column(db.Integer, nullable=True)
    Weibl= db.Column(db.Integer, nullable=True)
    JeKM= db.Column(db.Integer, nullable=True)
    PLZ= db.Column(db.Integer, nullable=True)
    Long= db.Column(db.Float, nullable=True)
    Lat= db.Column(db.Float, nullable=True)

    def __repr__(self):
        return '<vehicleInfo %r>' % self.id