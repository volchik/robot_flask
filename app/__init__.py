import logging
from flask import Flask

logger = logging.getLogger(__name__)
app = Flask(__name__)

import views
from app import camera
from app import robot_client

def prepare_app(config):
    global app
    assert not hasattr(app, 'camera')
    assert not hasattr(app, 'robot')
    app.camera = camera.Camera(config.cam_num, config.cam_mode, 
                               config.cam_fps, config.cam_quality, 
                               config.cam_put_date)
    app.robot = robot_client.Robot(config.robot_port, config.robot_baudrate)
    return app

 
