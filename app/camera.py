#!/usr/bin/env python
# coding: utf-8
import os
import time
from cv2 import cv
import logging

logger = logging.getLogger(__name__)

class Camera(object):
    def __init__(self, cam_num, cam_mode=1, cam_fps=-1, cam_quality=70, cam_put_date=False):
        self.capture = cv.CaptureFromCAM(cam_num)
        self.resolutions = {0: (352,288), 1: (640,480), 2: (1280,720), 3: (1280,1024)}
        self.num     = cam_num
        self.mode    = cam_mode
        self.fps     = cam_fps
        self.quality = cam_quality
        self.put_date= cam_put_date
        self.textColor = (255,255,255)
        logger.debug('Номер камеры: %s' % (self.num))
        logger.debug('Разрешение: %sx%s' % (self.width, self.height))
        logger.debug('Кадров в секунду: %s' % (self.fps))
        logger.debug('Качество: %s' % (self.quality))

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, value)
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT, value)
        self._height = value

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, value):
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FPS, value)
        self._fps = value

    @property 
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        self.font  = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.5*(self.mode+1), 0.5*(self.mode+1), 0, self.mode+1, 8)
        resolution = self.resolutions.get(value)
        if resolution != None:
            self.width  = resolution[0]
            self.height = resolution[1]
        else:
            self.width  = 640
            self.height = 480

    @property
    def textColor(self):
        return self._textColor

    @textColor.setter
    def textColor(self, value):
        self._textColor = value

    def get_image(self, put_date=False, frameSpeed=0, frameFps=0):
        red, green, blue = self.textColor
        textColor = cv.RGB(red, green, blue)
        img = cv.QueryFrame(self.capture)

        #Задержка для нормализации периодического процесса захвата (см. документацию)
        #По непонятной причине из-за cv.WaitKey вылетает сервер 
        #с ошибкой "Ошибка сегментирования (сделан дамп памяти)" после смены размера картинки
        #cv.WaitKey(10)

        if put_date:
            text = time.strftime('%d/%m/%Y %H:%M:%S',time.localtime())
            textSize, baseline = cv.GetTextSize(text,self.font)
            cv.PutText(img, text, (textSize[1],2*textSize[1]),self.font, textColor)

        if frameSpeed:
            text = str(frameSpeed) + 'kb/s  ' + str(frameFps) + 'fps'
            textSize, baseline = cv.GetTextSize(text,self.font)
            cv.PutText(img, text, (self.width - textSize[0] - textSize[1], self.height - textSize[1]), 
                       self.font, textColor)

        cv2mat = cv.EncodeImage('.jpeg', img, (cv.CV_IMWRITE_JPEG_QUALITY, self.quality))
        return cv2mat.tostring()

    def dummy_image(self, filename):
        try:
            f = open(filename)
            image = f.read()
            f.close()
            return image
        except IOError:
            logger.error('Файл не найден: %s' % filename)
            return ''

    def get_resolutions(self):
        return self.resolutions


if __name__ == '__main__':
    pass
