#!/usr/bin/env python
# coding: utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import logging
import sys
import os
import functools
from twisted.internet.endpoints import TCP4ServerEndpoint, SSL4ServerEndpoint
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from twisted.internet import reactor
from twisted.internet.ssl import DefaultOpenSSLContextFactory
from daemon import Daemon
import app
from config import Config
from command import Command

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


def start_server(config, command):
    configure_logging(config)
    local_app = app.prepare_app(config, command)

    resource = WSGIResource(reactor,
                            reactor.getThreadPool(),
                            local_app)
    factory = Site(resource)
    if config.server_ssl:
        ssl_key = os.path.join(basedir, config.server_ssl_key)
        ssl_crt = os.path.join(basedir, config.server_ssl_crt)
        sslContextFactory = DefaultOpenSSLContextFactory(ssl_key, ssl_crt)
        endpoint = SSL4ServerEndpoint(reactor, config.server_port, sslContextFactory)
    else:
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


    def run(self):
        self.target()


if __name__ == '__main__':

    action = None
    if len(sys.argv) > 1:
        action = sys.argv[1]

    if not action in ('start', 'stop', 'restart', 'run'):
        print 'Запуск: %s start|stop|restart|run' % sys.argv[0]
        exit(1)

    basedir  = os.path.abspath(os.path.dirname(__file__))

    command_filename= 'command.dict'
    command_filename = os.path.join(basedir, command_filename)

    config_filename = 'server.conf'
    config_filename = os.path.join(basedir, config_filename)

    command = Command(command_filename)
    config = Config(config_filename)
    #Если запускаем как демона, то выключаем вывод в stdout
    if not action == 'run':
        config.log_to_stdout = False
    config.create_dirs()
    pid = config.pid_filename
    stdout = os.path.join(config.log_dir, 'stdout.log')
    stderr = os.path.join(config.log_dir, 'stderr.log')

    target = functools.partial(start_server, config, command)
    server = Server(target, pid, stdout, stderr)

    if action == 'start':
        server.start()
    elif action == 'stop':
        server.stop()
    elif action == 'restart':
        server.restart()
    elif action == 'run':
        target()
    else:
        pass

