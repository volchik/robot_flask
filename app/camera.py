#!/usr/bin/env python
# coding: utf-8
import os
import time
import cv2
import logging

logger = logging.getLogger(__name__)

class Camera(object):
    def __init__(self, cam_num, cam_mode=1, cam_fps=-1, cam_quality=70, cam_put_date=False):
        self.cv_version = cv2.__version__
        logger.debug('OpenCV version %s' % (self.cv_version))

        (self.cv_version_major, self.cv_version_minor, _) = self.cv_version.split(".")

        if self.cv_version_major == '2':
            self.capture = cv2.cv.CaptureFromCAM(cam_num)
        else:
            self.capture = cv2.VideoCapture(cam_num)

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
        if self.cv_version_major == '2':
            cv2.cv.SetCaptureProperty(self.capture, cv2.cv.CV_CAP_PROP_FRAME_WIDTH, value)
        else:
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, value)

        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if self.cv_version_major == '2':
            cv2.cv.SetCaptureProperty(self.capture, cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, value)
        else:
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, value)

        self._height = value

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, value):
        if self.cv_version_major == '2':
            cv2.cv.SetCaptureProperty(self.capture, cv2.cv.CV_CAP_PROP_FPS, value)
        else:
            self.capture.set(cv2.CAP_PROP_FPS, value)

        self._fps = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        if self.cv_version_major == '2':
            self.font  = cv2.cv.InitFont(cv2.cv.CV_FONT_HERSHEY_SIMPLEX, 0.5*(self.mode+1), 0.5*(self.mode+1), 0, self.mode+1, 8)
        else:
            self.font  = cv2.FONT_HERSHEY_SIMPLEX

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

        if self.cv_version_major == '2':
            textColor = cv2.cv.RGB(red, green, blue)
            img = cv2.cv.QueryFrame(self.capture)

            #Задержка для нормализации периодического процесса захвата (см. документацию)
            #По непонятной причине из-за cv2.cv.WaitKey вылетает сервер
            #с ошибкой "Ошибка сегментирования (сделан дамп памяти)" после смены размера картинки
            #cv2.cv.WaitKey(10)

            if put_date:
                text = time.strftime('%d/%m/%Y %H:%M:%S',time.localtime())
                textSize, baseline = cv2.cv.GetTextSize(text, self.font)
                cv2.cv.PutText(img, text, (textSize[1],2*textSize[1]), self.font, textColor)

            if frameSpeed:
                text = str(frameSpeed) + 'kb/s  ' + str(frameFps) + 'fps'
                textSize, baseline = cv2.cv.GetTextSize(text, self.font)
                cv2.cv.PutText(img, text, (self.width - textSize[0] - textSize[1], self.height - textSize[1]), self.font, textColor)

            cv2mat = cv2.cv.EncodeImage('.jpeg', img, (cv2.cv.CV_IMWRITE_JPEG_QUALITY, self.quality))
        else:
            textColor = self.textColor
            ret, img = self.capture.read()

            #Задержка для нормализации периодического процесса захвата (см. документацию)
            #По непонятной причине из-за cv2.WaitKey вылетает сервер
            #с ошибкой "Ошибка сегментирования (сделан дамп памяти)" после смены размера картинки
            #cv2.WaitKey(10)

            if put_date:
                text = time.strftime('%d/%m/%Y %H:%M:%S',time.localtime())
                textSize, baseline = cv2.getTextSize(text, self.font, 0.5*(self.mode+1), self.mode+1)
                cv2.putText(img, text, (textSize[1],2*textSize[1]), self.font, 0.5*(self.mode+1), textColor, self.mode+1)

            if frameSpeed:
                text = str(frameSpeed) + 'kb/s  ' + str(frameFps) + 'fps'
                textSize, baseline = cv2.getTextSize(text, self.font, 0.5*(self.mode+1), self.mode+1)
                cv2.putText(img, text, (self.width - textSize[0] - textSize[1], self.height - textSize[1]), self.font, 0.5*(self.mode+1), textColor, self.mode+1)

            ret, cv2mat = cv2.imencode('.jpeg', img, (cv2.IMWRITE_JPEG_QUALITY, self.quality))

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
