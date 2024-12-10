from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    is_active = db.Column(db.Boolean, default=True)  # New column to track if the user is active

    def __repr__(self):
        return f'<User {self.username}>'


    def get_id(self):
        return str(self.id)


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String, nullable=False)
    bmi = db.Column(db.Integer, nullable=False)
    children = db.Column(db.Integer, nullable=False)
    charges = db.Column(db.Integer, nullable=False)
    region = db.Column(db.String(100), nullable=False)

    # Foreign Key relationship with User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
