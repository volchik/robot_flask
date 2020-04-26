#!/usr/bin/env python
# coding: utf-8

#Создание пользователей

from app import app
from app.db import db, User
from config import Config
import os


if __name__ == '__main__':
    basedir  = os.path.abspath(os.path.dirname(__file__))
    config_filename = 'server.conf'
    config_filename = os.path.join(basedir, config_filename)

    config = Config(config_filename)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + config.db_url

    db.create_all()

    user = User.query.filter_by(username='admin').first()
    if not user:
        user = User('admin', 'qwerty', 'admin@example.com')
        db.session.add(user)
        db.session.commit()

    user = User.query.filter_by(username='guest').first()
    if not user:
        user = User('guest', '1q2w3e', 'guest@example.com')
        db.session.add(user)
        db.session.commit()

