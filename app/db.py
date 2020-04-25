#!/usr/bin/env python
# coding: utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash

db = SQLAlchemy(app)

#Модель базы
class User(db.Model):
    __tablename__ = 'users'
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    pwdhash  = db.Column(db.String())
    email    = db.Column(db.String(120), unique=True)

    def __init__(self, username, password, email):
        self.username = username
        self.pwdhash  = generate_password_hash(password)
        self.email    = email

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def __repr__(self):
        return '<id: %s, User: %s>' % (self.id, self.username)

