#!/usr/bin/env python
# coding: utf-8
import os
import logging
from configobj import ConfigObj


class Config(object):
    def __init__(self, filename):
        config = ConfigObj(filename, unrepr=True)
        self.__dict__.update(config)
        config_dir = os.path.abspath(os.path.dirname(filename))

        self.server_host  = config.get('server.host',  '127.0.0.1')
        self.server_port  = config.get('server.port',  8080)
        self.server_debug = config.get('server.debug', False)

        log_filename      = config.get('log.filename', 'log/www.log')
        self.log_filename = os.path.join(config_dir, log_filename)
        self.log_dir = os.path.dirname(self.log_filename)
        self.log_level    = logging.getLevelName(config.get('log.level', 'info').upper())
        self.log_to_stdout = config.get('log.to_stdout', False)

        pid_filename      = config.get('pid.filename', 'pid/www.pid')
        self.pid_filename = os.path.join(config_dir, pid_filename)

        self.robot_port     = config.get('robot.port',     '/dev/ttyUSB0')
        self.robot_baudrate = config.get('robot.baudrate', 9600)

        self.cam_num     = config.get('cam.num',  6)
        self.cam_mode    = config.get('cam.mode', 1)
        self.cam_fps     = config.get('cam.fps', -1)
        self.cam_quality = config.get('cam.quality', 70)
        self.cam_put_date= config.get('cam.put_date', False)

    def create_dirs(self):
        for f in (self.log_filename, self.pid_filename):
            d = os.path.dirname(f)
            if not os.path.isdir(d):
                os.makedirs(d)

if __name__ == '__main__':
    pass

