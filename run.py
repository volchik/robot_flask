#!/usr/bin/env python
# coding: utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import logging
import sys
import os
import argparse
import functools
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from twisted.internet import reactor
from daemon import Daemon
import app
from config import Config

logger = logging.getLogger('main')

def configure_logging(config):
    root_logger = logging.getLogger()
    root_logger.setLevel(config.log_level)
    formatter = logging.Formatter('%(asctime)-15s %(levelname)-7s %(name)-20s %(message)s')
    if config.log_to_stdout:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        root_logger.addHandler(stdout_handler)
    file_handler = logging.FileHandler(config.log_filename)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def start_server(config):
    configure_logging(config)
    local_app = app.prepare_app(config)

    resource = WSGIResource(reactor,
                            reactor.getThreadPool(),
                            local_app)
    factory = Site(resource)
    endpoint = TCP4ServerEndpoint(reactor, config.server_port)
    d = endpoint.listen(factory)
    logger.info('Старт сервера...')
    d.addCallback(lambda _: logger.info(u'Сервер стартовал...'))
    d.addErrback(lambda failure: (logger.error(u'Ошибка старта: %s' % failure.getErrorMessage()) or
                                  logger.error(u'Stopping reactor...') or
                                  reactor.callLater(0, reactor.stop)))

    reactor.run()


class Server(Daemon):
    def __init__(self, target, pidfile, stdout='/dev/null', stderr='/dev/null'):
        self.target = target
        super(Server, self).__init__(pidfile, '/dev/null', stdout, stderr)

#    def set_config(self, config_filename):
#        self.conf_filename = config_filename

    def run(self):
        self.target()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', nargs='?', choices=['start', 'stop', 'restart'])
    args = parser.parse_args()

    basedir  = os.path.abspath(os.path.dirname(__file__))
    config_filename = 'server.conf'
    config_filename = os.path.join(basedir, config_filename)

    config = Config(config_filename)
    config.create_dirs()
    pid = config.pid_filename
    stdout = os.path.join(config.log_dir, 'stdout.log')
    stderr = os.path.join(config.log_dir, 'stderr.log')

    target = functools.partial(start_server, config)
    server = Server(target, pid, stdout, stderr)

    if args.action == 'start':
        server.start()
    elif args.action == 'stop':
        server.stop()
    elif args.action == 'restart':
        server.restart()
    else:
        target()

