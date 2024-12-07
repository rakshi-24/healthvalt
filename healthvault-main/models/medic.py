from pickle import FALSE

from utils.db import db


class Patients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String, nullable=False)
    bmi = db.Column(db.Integer, nullable=False)
    children = db.Column(db.Integer, nullable=False)
    charges = db.Column(db.Integer, nullable=False)
    region = db.Column(db.String(100), nullable=False)
