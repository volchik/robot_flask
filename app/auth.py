from functools import wraps
from flask import redirect, url_for
from flask import request
from flask import session
import time
import logging

logger = logging.getLogger(__name__)

###############  Авторизация  #########################
def logged():
    if session.get('logged'):
        userexpire = session.get('expire')
        username   = session.get('username','')
        #превышено время действия авторизации
        if userexpire < time.time():
            return False
        return True
    return False


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not logged():
            next = request.path
            #если запрос на главной странице, то не передаем страницу для перехода
            if next == '/':
                return redirect(url_for('login'))
            return redirect(url_for('login')+'?next='+request.path)
        return f(*args, **kwargs)
    return decorated
