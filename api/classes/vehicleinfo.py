
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/test.db'
db = SQLAlchemy(app)



class Vehicleinfo(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    Key= db.Column(db.Integer, nullable=True)
    KRADanzahl= db.Column(db.Integer, nullable=True)
    KRADweibl= db.Column(db.Integer, nullable=True)
    PKW= db.Column(db.Integer, nullable=True)
    PKWproTausendEW= db.Column(db.Integer, nullable=True)
    KFZinsgesamt= db.Column(db.Integer, nullable=True)
    KFZproTausendEW= db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<vehicleInfo %r>' % self.id