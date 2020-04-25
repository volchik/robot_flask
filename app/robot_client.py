import logging
import serial
from serial import SerialException
import time
import sys

logger = logging.getLogger(__name__)

############################################
#  Класс связи с аппаратной частью робота  #
############################################

class Robot:
    def __init__(self, port, baudrate, timeout =0.1):
        self.port     = port
        self.baudrate = baudrate
        self.timeout  = timeout
        self.connect()

    def connect(self):
        try:
            self.busy = False
            self.last_error = ''
            #Открытие порта
            self.serial = serial.Serial(self.port, self.baudrate, timeout = self.timeout)
            #Ожидание инициализации...
            time.sleep(2)
            if self.serial.isOpen():
                logger.info('Подключен к устройству: %s' % self.port)
            else:
                self.last_error = 'Подключение к устройству %s не установлено' %  self.port
                logger.error(self.last_error)
        except SerialException:
            self.serial     = None
            self.last_error = 'Ошибка подключения к %s' % self.port
            logger.error(self.last_error)
        except:
            self.serial     = None
            self.last_error = 'Ошибка подключения: %s' % sys.exc_info()[1]
            logger.error(self.last_error)

    def close(self):
        self.last_error = ''
        if self.serial and self.serial.isOpen():
            self.serial.close()
        logger.info('Подключение к %s закрыто' % self.port)

    def reconnect(self):
        self.close()
        self.connect()

    def invoke(self, command, check=True):
        #Неопределен serial, вероятно была ошибка
        if not self.serial:
            return self.last_error

        #Выход если порт не открыт
        if not self.serial.isOpen():
            return self.last_error

        #Ждем пока не освободится
        while (self.busy):
            pass

        #Установим флаг занятости
        self.busy = True
        try:
            logger.debug('Отправка комманды: %s' % command)
            self.serial.write(command+'\r')
            logger.debug('Отправлена комманда: %s' % command)
            result = self.serial.readline().replace('\n', '').replace('\r', '')
            logger.debug('Получено: %s' % result)
        except:
            logger.error('Ошибка отправки/получения: "%s"' % sys.exc_info()[1])
            result = sys.exc_info()[1]
        #Снимем флаг зянятости
        self.busy = False
        if check and result[:len(command)] != command:
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

    def get(self, command):
        result = self.invoke(command)
        if result[:len(command)] == command:
            return result[len(command):]
        #Вернем прочерк
        return '--'

    def get_temperature(self):
        return self.get('TG')

    def get_pressure(self):
        return self.get('PG')

    def get_light(self):
        result = self.get('LG')
        if result == '1':
            return True
        return False

    def get_realvolts(self):
        return self.get('VG')

if __name__ == '__main__':
    pass
