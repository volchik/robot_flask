#!/usr/bin/env python
# coding: utf-8

#Создание пользователей

from app import app
from app.db import db, User
from config import Config
import os
from sqlalchemy import Table, Column, Integer, String, MetaData, create_engine

if __name__ == '__main__':
    basedir  = os.path.abspath(os.path.dirname(__file__))
    config_filename = 'server.conf'
    config_filename = os.path.join(basedir, config_filename)

    config = Config(config_filename)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + config.db_url

    users = User.query.all()
    for user in users:
      print user

    print len(users)
