import logging
import os
from flask import Flask

logger = logging.getLogger(__name__)
app = Flask(__name__)

import views
from app import camera
from app import robot_client

def prepare_app(config, command):
    global app
    app.debug = config.server_debug
    app.auth_timeout = config.auth_timeout
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + config.db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.urandom(24)
    assert not hasattr(app, 'camera')
    assert not hasattr(app, 'robot')
    assert not hasattr(app, 'cmd_dict')
    app.camera = camera.Camera(config.cam_num, config.cam_mode, 
                               config.cam_fps, config.cam_quality, 
                               config.cam_put_date)
    app.robot = robot_client.Robot(config.robot_port, config.robot_baudrate)
    app.cmd_dict = command
    return app

