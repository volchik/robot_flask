#!/usr/bin/env python
# coding: utf-8
import os
import time
#import glob
#import itertools
from cv2 import cv


class Camera(object):
    def __init__(self, cam_num, cam_mode=1, cam_fps=-1, cam_quality=70, cam_put_date=False):
        self.capture = cv.CaptureFromCAM(cam_num)
        self.mode    = cam_mode
        self.fps     = cam_fps
        self.quality = cam_quality
        self.put_date= cam_put_date
        self.textColor = cv.RGB(255,255,255)
        self.font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.5*(self.mode+1), 0.5*(self.mode+1), 0, self.mode+1, 8)

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
        if value == 0:
            self.width  = 352
            self.height = 288
        elif value == 1:
            self.width  = 640
            self.height = 480
        elif value == 2:
            self.width  = 1280
            self.height = 1024

    def set_textColor(self, Color):
        red, green, blue = Color
        self.textColor = cv.RGB(red,green,blue)

    def get_image(self, put_date=False, frameSpeed=0, frameFps=0):
        img = cv.QueryFrame(self.capture)
        if put_date:
            text = time.strftime("%d/%m/%Y %H:%M:%S",time.localtime())
            textSize, baseline = cv.GetTextSize(text,self.font)
            cv.PutText(img, text, (textSize[1],2*textSize[1]),self.font, self.textColor)

        if frameSpeed != 0:
            text = str(frameSpeed) + "kb/s  " + str(frameFps) + "fps"
            textSize, baseline = cv.GetTextSize(text,self.font)
            cv.PutText(img, text, (self.width - textSize[0] - textSize[1], self.height - textSize[1]), 
                       self.font, self.textColor)

        cv2mat = cv.EncodeImage(".jpeg", img, (cv.CV_IMWRITE_JPEG_QUALITY, self.quality))
        return cv2mat.tostring()

 

if __name__ == '__main__':
    pass
