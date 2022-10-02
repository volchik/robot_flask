#!/usr/bin/env python
# coding: utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from app import app
from app.db import db, User
from functools import wraps
from flask import Response, render_template, redirect, url_for
from flask import request, current_app, stream_with_context, abort
from flask import session
import time
import logging
import os
###############  Авторизация  #########################
from app.auth import *
###############  Админка  #############################
from app.admin import *


logger = logging.getLogger(__name__)


###############  Обработка запросов  ##################
@app.route('/')
@requires_auth
def main():
    #для авторизованного на главную страницу
    #если не авторизован, то на страницу аутентификации
    if logged():
      return redirect(url_for('index'))
    return redirect(url_for('login'))


@app.route('/index')
@requires_auth
def index():
    lighton = current_app.robot.get_light()
    cam_mode = current_app.camera.mode
    resolutions = current_app.camera.get_resolutions()
    logger.debug('Запрос состояния освещения, получено %s' % lighton)
    return render_template("index.html", \
                           title=None, \
                           mjpeg=True, \
                           lighton=lighton, \
                           cam_mode=cam_mode, \
                           resolutions=resolutions)


@app.route('/mobile')
@requires_auth
def mobile():
    lighton = current_app.robot.get_light()
    cam_mode = current_app.camera.mode
    resolutions = current_app.camera.get_resolutions()
    logger.debug('Запрос состояния освещения, получено %s' % lighton)
    return render_template("index.html", \
                           title=None, \
                           mjpeg=False, \
                           lighton=lighton, \
                           cam_mode=cam_mode, \
                           resolutions=resolutions)


@app.route("/login", methods=["GET", "POST"])
def login():
    args = '&'.join(['='.join(i) for i in request.args.items()])
    logger.info(request.remote_addr +' ' + request.path+'?'+args)
    if request.method == 'POST':
        username = request.form.get('username','')
        password = request.form.get('password','')
        remember = request.form.get('remember',False)
        user = User.query.filter_by(username=username).first()
        if user:
            if user.check_password(password):
                logger.info('Вход пользователя %s' % username)
                session['username'] = username
                session['logged']   = True
                session['expire']   = time.time() + current_app.auth_timeout #auth_timeout sec
                session['remember'] = remember
                return redirect(request.args.get('next') or url_for("index"))
        return render_template('login.html', \
                               title = 'Логин/пароль (регистрация)', \
                               error = 'Неправильное имя пользователя или пароль', \
                               username = username, \
                               remember = remember, \
                               next = args)

    #запрос пароля
    username = session.get('username','')
    remember = session.get('remember',False)
    return render_template('login.html', \
                           title = 'Логин/пароль (регистрация)', \
                           error = None, \
                           username = username, \
                           remember = remember, \
                           next = args)


@app.route("/logout")
def logout():
    args = '&'.join(['='.join(i) for i in request.args.items()])
    logger.info(request.remote_addr +' ' + request.path+'?'+args)
    logger.info('Выход пользователя %s' % session.get('username',''))
    session.pop('logged', None)
    session.pop('expire', None)
    if not session.get('remember'):
        session.pop('username', None)

    return redirect(url_for('main'))


@app.route('/mjpeg')
def mjpeg():
    if not logged():
        image = current_app.camera.dummy_image(os.path.join(os.path.dirname(__file__), 'static', 'dummy/401.jpg'))
        logger.debug('Отправка кадра %s байт' % len(image))
        return Response(image, 200, content_type='image/jpeg')

    put_date = current_app.camera.put_date
    if request.args.get('nodate',None) == '1':
        put_date = False

    def jpeg_generator(camera):
        fps   = camera.fps
        if fps > 0:
            delay = 1.0 / fps
        else:
            delay = 0.05
        frameTime = time.time()
        frameCount = 0
        frameFps = 0
        frameSize = 0
        frameSpeed = 0
        frameRefreshTime = 5 #Считать скорость захвата каждые ХХХ секунд
        logger.info('Начало MJPEG потока, задержка: %.2f' % delay)
        last_time = time.time()
        while True:
            image = camera.get_image(put_date, frameSpeed, frameFps)

            if image == '':
                time.sleep(delay)
                continue

            yield "--aaboundary\r\n"
            yield "Content-Type: image/jpeg\r\n"
            yield "Content-length: " + str(len(image)) + "\r\n\r\n"
            yield image
            yield "\r\n\r\n\r\n"
            current_time = time.time()
            wait = delay - (current_time - last_time)
            if wait > 0:
                time.sleep(wait)
            last_time = time.time()
            #Считаем скорость захвата
            frameCount += 1
            if time.time() - frameTime > frameRefreshTime: 
                frameFps = round(frameCount/(time.time() - frameTime),1)
                frameCount = 0
                frameSize = len(image)/1024
                frameSpeed = int(8 * len(image) * frameFps/1024)
                logger.debug('Захват кадров: %s к/с, размер кадра: %s кБ, '\
                             'скорость захвата: %s кб/с' % (frameFps, frameSize, frameSpeed))
                frameTime = time.time()

    return Response(stream_with_context(jpeg_generator(current_app.camera)),
                    content_type='multipart/x-mixed-replace; boundary=--aaboundary')


@app.route('/jpeg')
def jpeg():
    get_logged = False
    if request.method == 'GET' and request.args.get('username'):
        username = request.args.get('username','')
        password = request.args.get('password','')
        user = User.query.filter_by(username=username).first()
        if user:
            if user.check_password(password):
                logger.info('Вход пользователя %s' % username)
                get_logged = True

    if not logged() and not get_logged:
        image = current_app.camera.dummy_image(os.path.join(os.path.dirname(__file__), 'static', 'dummy/401.jpg'))
        logger.debug('Отправка кадра %s байт' % len(image))
        return Response(image, 200, content_type='image/jpeg')

    put_date = current_app.camera.put_date
    if request.args.get('nodate',None) == '1':
        put_date = False
    image = current_app.camera.get_image(put_date)
    logger.debug('Отправка кадра %s байт' % len(image))
    return Response(image, 200, content_type='image/jpeg')


@app.route('/get_temperature')
def get_temperature():
    get_logged = False
    if request.method == 'GET' and request.args.get('username'):
        username = request.args.get('username','')
    get_logged = False
    if request.method == 'GET' and request.args.get('username'):
        username = request.args.get('username','')
        password = request.args.get('password','')
        user = User.query.filter_by(username=username).first()
        if user:
            if user.check_password(password):
                logger.info('Вход пользователя %s' % username)
                get_logged = True

    get_logged = False
    if request.method == 'GET' and request.args.get('username'):
        username = request.args.get('username','')
        password = request.args.get('password','')
        user = User.query.filter_by(username=username).first()
        if user:
            if user.check_password(password):
                logger.info('Вход пользователя %s' % username)
                get_logged = True

        password = request.args.get('password','')
        user = User.query.filter_by(username=username).first()
        if user:
            if user.check_password(password):
                logger.info('Вход пользователя %s' % username)
                get_logged = True

    if not logged() and not get_logged:
        return 'Нет доступа'

    logger.debug('Запрос температуры')
    result = str(current_app.robot.get_temperature())
    logger.debug('Ответ на запрос температуры: %s' % result)
    return result


@app.route('/get_pressure')
def get_pressure():
    get_logged = False
    if request.method == 'GET' and request.args.get('username'):
        username = request.args.get('username','')
        password = request.args.get('password','')
        user = User.query.filter_by(username=username).first()
        if user:
            if user.check_password(password):
                logger.info('Вход пользователя %s' % username)
                get_logged = True

    if not logged() and not get_logged:
        return 'Нет доступа'

    logger.debug('Запрос давления')
    result = current_app.robot.get_pressure()
    #Результат в паскалях, преобразуем в мм.рт.ст.
    try:
        pressure = str(int(float(result)/133.33))
    except:
        logger.debug('Ответ на запрос давления: %s' % result)
        return result
    logger.debug('Ответ на запрос давления: %s' % pressure)
    return pressure


@app.route('/get_realvolts')
def get_realvolts():
    get_logged = False
    if request.method == 'GET' and request.args.get('username'):
        username = request.args.get('username','')
        password = request.args.get('password','')
        user = User.query.filter_by(username=username).first()
        if user:
            if user.check_password(password):
                logger.info('Вход пользователя %s' % username)
                get_logged = True

    if not logged() and not get_logged:
        return 'Нет доступа'

    logger.debug('Запрос напряжения питания')
    result = current_app.robot.get_realvolts()
    logger.debug('Ответ на запрос напряжения питания: %s' % result)
    return result


@app.route('/invoke/<command>', methods=["POST"])
def invoke(command):
    if not logged():
        return 'Нет доступа'

    method = getattr(current_app.robot, command, None)
    if callable(method):
        logger.info('Получена комманда: %s(%s)' % (command, ', '.join(['='.join(i) for i in request.args.items()])))
        result = str(method(**request.args))
        if result:
            logger.debug('Ответ на комманду "%s": %s' % (command, result))
            return app.cmd_dict.getCommandText(result)
        else:
            return '%s - OK???' % command
    else:
        logger.error('Комманда "%s" не найдена' % command)
        abort(404)


@app.route('/set_resolution/<int:mode>', methods=["POST"])
def set_resolution(mode):
    if not logged():
        return 'Нет доступа'

    current_app.camera.mode = mode
    logger.info('Смена режима работы камеры: %sx%s' % (current_app.camera.width, current_app.camera.height))
    return '%sx%s' % (current_app.camera.width, current_app.camera.height)


@app.route('/.well-known/pki-validation/<string:file>')
def get_file(file):
    f = open(os.path.join(os.path.dirname(__file__), 'data', file), 'r')
    data = f.read()
    f.close()
    logger.info('Загрузка файла "%s"' % (file))
    return data

@app.route('/<string:file>')
def get_file_root(file):
    f = open(os.path.join(os.path.dirname(__file__), 'data', file), 'r')
    data = f.read()
    f.close()
    logger.info('Загрузка файла "%s"' % (file))
    return data

@app.errorhandler(401)
def page_access_denied(error):
    return render_template('error_401.html', title='Доступ запрещен'), 401


@app.errorhandler(403)
def page_access_denied(error):
    return render_template('error_401.html', title='Доступ запрещен'), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error_404.html', title='Страница не найдена'), 404


@app.errorhandler(500)
def page_not_found(error):
    return render_template('error_404.html', title='Страница не найдена'), 500

@app.route('/test')
@requires_auth
def test():
    return render_template("test.html")
