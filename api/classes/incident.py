from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from api.app import db

class Incident(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    ULAND = db.Column(db.Integer, nullable=True)
    UREGBEZ = db.Column(db.Integer, nullable=True)
    UKREIS = db.Column(db.Integer, nullable=True)
    UGEMEINDE = db.Column(db.Integer, nullable=True)
    UJAHR = db.Column(db.Integer, nullable=True)
    UMONAT = db.Column(db.Integer, nullable=True)
    USTUNDE = db.Column(db.Integer, nullable=True)
    UWOCHENTAG = db.Column(db.Integer, nullable=True)
    UKATEGORIE = db.Column(db.Integer, nullable=True)
    UART = db.Column(db.Integer, nullable=True)
    UTYP1 = db.Column(db.Integer, nullable=True)
    ULICHTVERH = db.Column(db.Integer, nullable=True)
    IstRad = db.Column(db.Integer, nullable=True)
    IstPKW = db.Column(db.Integer, nullable=True)
    IstFuss = db.Column(db.Integer, nullable=True)
    IstKrad = db.Column(db.Integer, nullable=True)
    IstSonstige = db.Column(db.Integer, nullable=True)
    XGCSWGS84 = db.Column(db.Float, nullable=True)
    YGCSWGS84 = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return "Land"+ str(self.ULAND)

