#!/usr/bin/env python
# coding: utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from app import app
from functools import wraps
import logging
from flask import  Response, render_template, redirect, url_for, request, current_app, stream_with_context, abort
import time
import logging

logger = logging.getLogger(__name__)


################  Basic Auth  #########################
def check_auth(username, password):
    # Проверка логина и пароля
    return username == 'admin' and password == 'qwerty'

def authenticate():
    # Посслать ответ 401 для вызова Basic Auth
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Robot Page"'})

def logged():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return False
    return True

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not logged():
            return authenticate()
        return f(*args, **kwargs)
    return decorated

###############  Обработка запросов  ##################
@app.route('/')
@requires_auth
def index():
    logger.info(request.path)
    return render_template("index.html", title = None)

@app.route('/logout', methods=['POST', 'GET'])
@requires_auth
def logout():
    logger.info(request.path)
    logger.info(request.authorization)
    return redirect(url_for('index'))

@app.route('/mjpeg')
def mjpeg():
    if not logged():
        abort(404)

    put_date = current_app.camera.put_date
    if request.args.get('nodate',None) == '1':
        put_date = False
   
    def jpeg_generator(camera):
        fps   = camera.fps
        delay = 1 / fps
        frameTime = time.time()
        frameCount = 0
        frameFps = 0
        frameSize = 0
        frameSpeed = 0
        frameRefreshTime = 5 #Считать скорост каждые ХХХ секунд
        logger.info('Начало MJPEG потока, задержка: %.2f' % delay)
        last_time = time.time()
        while True:
            image = camera.get_image(put_date, frameSpeed, frameFps)
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
            # считаем скорость захвата
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
    if not logged():
        abort(404)

    put_date = current_app.camera.put_date
    if request.args.get('nodate',None) == '1':
        put_date = False
    image = current_app.camera.get_image(put_date)
    if logger.levelname.upper() != 'DEBUG':
       logger.info('Отправка кадра %s байт' % len(image))
    logger.debug('Отправка кадра %s байт' % len(image))
    return Response(image, 200, content_type='image/jpeg')


@app.route('/get_temperature')
def get_temperature():
    if not logged():
        return "Нет доступа"

    logger.debug('Запрос температуры')
    result = str(current_app.robot.get_temperature())
    return result


@app.route('/get_pressure')
def get_pressure():
    if not logged():
        return "Нет доступа"

    logger.debug('Запрос давления')
    result = current_app.robot.get_pressure()
    #результат в паскалях, преобразуем в мм.рт.ст.
    try:
        pressure = str(int(float(result)/133.33))
    except:
        return result
    return pressure


@app.route('/invoke/<command>', methods=['POST', 'GET'])
def invoke(command):
    if not logged():
        return "Нет доступа"

    method = getattr(current_app.robot, command, None)
    if callable(method):
        logger.info('Получена комманда: %s(%s)' % (command, ', '.join(['='.join(i) for i in request.args.items()])))
        result = method(**request.args)
        if result:
            return result
        else:
            return '%s - OK!' % command
    else:
        logger.error('Неправильная комманда: %s' % command)
        abort(404)


@app.route('/set_resolution/<int:mode>', methods=['POST', 'GET'])
def set_resolution(mode):
    if not logged():
        return "Нет доступа"

    current_app.camera.mode = mode
    logger.info('Смена режима работы камеры: %sx%s' % (current_app.camera.width, current_app.camera.height))
    return '%sx%s' % (current_app.camera.width, current_app.camera.height)

