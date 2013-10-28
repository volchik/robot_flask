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
        self.log_filename = config.get('log_filename', 'log/server.log')
        self.log_filename = os.path.abspath(os.path.join(config_dir, self.log_filename))
        self.log_dir      = os.path.dirname(self.log_filename)
        self.log_level    = logging.getLevelName(config.get('log_level', 'info').upper())
        self.pid_filename = config.get('pid_filename', 'pid/server.pid')
        self.pid_filename = os.path.abspath(os.path.join(config_dir, self.pid_filename))
        self.db_url       = config.get('db_url', 'app.db')
        self.db_url       = os.path.abspath(os.path.join(config_dir, self.db_url))

    def __getattr__(self, name):
        return None

    def create_dirs(self):
        for f in (self.log_filename, self.pid_filename):
            d = os.path.dirname(f)
            if not os.path.isdir(d):
                os.makedirs(d)

if __name__ == '__main__':
    pass
