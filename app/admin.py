#!/usr/bin/env python
# coding: utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from app import app
from db import db, User
from flask import Response, render_template, redirect, url_for
from flask import request, current_app, stream_with_context, abort
from flask import session
import time
import logging
import os
###############  Авторизация  #########################
from auth import *

logger = logging.getLogger(__name__)

def render_admin_template(template):
    users = User.query.all()
    return render_template("admin/"+template+".html", \
                           main_url = request.args.get('last') or url_for("index"), \
                           active = template, \
                           users = users, \
                           users_count = len(users))


@app.route("/admin/", methods=["GET", "POST"])
@requires_auth
def admin_main():
    args = '&'.join(['='.join(i) for i in request.args.items()])
    logger.info(request.path+'?'+args)
    return render_admin_template("index")


@app.route("/admin/users", methods=["GET", "POST"])
@requires_auth
def admin_users():
    args = '&'.join(['='.join(i) for i in request.args.items()])
    logger.info(request.path+'?'+args)
    return render_admin_template("users")
