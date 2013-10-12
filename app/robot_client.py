#!/usr/bin/env python
# coding: utf-8

import serial
from serial import SerialException
import time
import sys

#======================================
# Robot class 
#======================================

class Robot:
    def __init__(self, port, baudrate, timeout =0.1):
        self.port     = port
        self.baudrate = baudrate
        self.timeout  = timeout
        self.connected= False
        self.last_error = ''
        self.busy = False
        self.connect()

    def connect(self):
        try:
            self.port = serial.Serial(self.port, self.baudrate, timeout = self.timeout)
            #Ожидание инициализации...
            time.sleep(2) 
            self.busy = False
            self.connected = True
        except SerialException:
            self.last_error = 'Ошибка подключения к %s(%s)' % (self.port, self.baudrate)
            self.connected  = False
        except:
            self.last_error = sys.exc_info()[1]
            self.connected  = False

    def close(self):
        self.port.close()
        self.connected = False

    def reconnect(self):
        self.close()
        self.connect()

    def invoke(self, command, check=True):
        if not self.connected:
            return self.last_error

        #ждем пока busy
        while (self.busy):
            None

        #установим busy
        self.busy = True
        try:
            self.port.write(command+'\r')
            result = self.port.readline().replace('\n', '').replace('\r', '')
        except:
            return sys.exc_info()[1]
        #снимем busy
        self.busy = False
        if check and result[0:len(command)] != command:
            return u'Error: Отправлено: "%s" Получено: "%s"' % (command, result)
        else:
            return result

    def move_forward(self):
        return self.invoke('MU')

    def move_backward(self):
        return self.invoke('MD')

    def move_left(self):
        return self.invoke('ML')

    def move_right(self):
        return self.invoke('MR')

    def cam_up(self):
        return self.invoke('CU')

    def cam_down(self):
        return self.invoke('CD')

    def cam_left(self):
        return self.invoke('CL')

    def cam_right(self):
        return self.invoke('CR')

    def light_on(self):
        return self.invoke('LO')

    def light_off(self):
        return self.invoke('LF')

    def get_temperature(self):
        result = self.invoke('TG', False)
        if result[:2] == 'TG':
            return result[2:]
        else:  #вернуть ошибку
            return result

    def get_pressure(self):
        result = self.invoke('PG', False)
        if result[:2] == 'PG':
            return result[2:]
        else:  #вернуть ошибку
            return result


if __name__ == '__main__':
    pass
