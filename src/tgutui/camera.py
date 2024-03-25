import os
import logging
from typing import Callable
from dataclasses import dataclass

import cv2
from cv2 import VideoCapture

import tgutui
from tgutui.kit import Kit

@dataclass
class CameraData:
    """
    This is a data class that holds all the camera data
    """
    pan: int = 0
    tilt: int = 0
    zoom: int = 0
    focus: int = 0
    width: int = 0
    height: int = 0
    auto_focus: int = 0

class Camera:
    """
    This class is a wrapper around the OpenCV VideoCapture class
    """
    OUTPUT: str = f"{tgutui.__path__[0]}/camera.png"

    def __init__(self) -> None:
        self._locked: bool = False
        self._cap: VideoCapture = cv2.VideoCapture()
        self._data: CameraData = CameraData()
        self.fetch_all()

    @property
    def locked(self) -> bool:
        """ Return the locked status of the camera"""
        return self._locked

    def fetch_all(self):
        """ Fetch all the camera data """
        self.open()
        self._fetch_focus()
        self._fetch_tilt()
        self._fetch_pan()
        self._fetch_zoom()
        self._fetch_width()
        self._fetch_height()
        self._fetch_auto_focus()
        self.close()

    @property
    def data(self) -> CameraData:
        """ Return the camera data"""
        return self._data

    def lock(fn: Callable):
        """ Decorator to lock the camera"""
        def decorate(self, *args, **kwargs):
            """ Lock the camera """
            self._locked = True
            rtn = fn(self, *args, **kwargs)
            self._locked = False
            return rtn
        return decorate

    @lock
    def _fetch_height(self):
        """ Fetch the height of the camera"""
        self._data.height = self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    @lock
    def _fetch_width(self):
        """ Fetch the width of the camera"""
        self._data.width = self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    @lock
    def _fetch_pan(self):
        """ Fetch the pan of the camera"""
        self._data.pan = self._cap.get(cv2.CAP_PROP_PAN)

    @lock
    def _fetch_tilt(self):
        """ Fetch the tilt of the camera"""
        self._data.tilt = self._cap.get(cv2.CAP_PROP_TILT)

    @lock
    def _fetch_zoom(self):
        """ Fetch the zoom of the camera"""
        self._data.zoom = self._cap.get(cv2.CAP_PROP_ZOOM)

    @lock
    def _fetch_focus(self):
        """ Fetch the focus of the camera"""
        self._data.focus = self._cap.get(cv2.CAP_PROP_FOCUS)

    @lock
    def _fetch_auto_focus(self):
        """ Fetch the auto focus of the camera"""
        self._data.auto_focus = self._cap.get(cv2.CAP_PROP_AUTOFOCUS)

    @lock
    def set_focus(self, value: int):
        """ Set the focus of the camera"""
        self._cap.set(cv2.CAP_PROP_FOCUS, value)
        self._data.focus = value

    @lock
    def set_auto_focus(self, value: int):
        """ Set the auto focus of the camera"""
        self._cap.set(cv2.CAP_PROP_AUTOFOCUS, value)
        self._data.auto_focus = value

    @lock
    def set_pan(self, value: int):
        """ Set the pan of the camera"""
        self._cap.set(cv2.CAP_PROP_PAN, value)
        self._data.pan = value

    @lock
    def set_tilt(self, value: int):
        """ Set the tilt of the camera"""
        self._cap.set(cv2.CAP_PROP_TILT, value)
        self._data.tilt = value

    @lock
    def set_zoom(self, value: int):
        """ Set the zoom of the camera"""
        self._cap.set(cv2.CAP_PROP_ZOOM, value)
        self._data.zoom = value

    def save(self):
        """ Save the camera image"""
        if self._locked:
            return
        ret, frame = self._cap.read()
        if not ret:
            logging.warning("Unable to read frame")
            return
        # Lots of thing can be done here if you've got the processing power
        cv2.imwrite(Camera.OUTPUT, frame)

    def open(self):
        """ Open the camera"""
        if not self._cap.isOpened():
            self._cap.open(index=Kit.CAMERA_DEVICE)
            if not self._cap.isOpened():
                raise RuntimeError("Unable to open webcam")

    def close(self):
        """ Close the camera"""
        self._cap.release()
        if os.path.exists(Camera.OUTPUT):
            os.remove(Camera.OUTPUT)

    def __enter__(self):
        if not self._cap.isOpened():
            self.open()
        return self

    def __exit__(self, *args):
        self.close()
