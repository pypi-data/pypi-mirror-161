from PySide2 import QtCore

from math import cos, sin, sqrt, acos, pi

from opencmiss.maths import vectorops
from opencmiss.maths.vectorops import normalize, sub, cross, mult, add
from opencmiss.zincwidgets.errors import HandlerError
from opencmiss.zincwidgets.handlers.keyactivatedhandler import KeyActivatedHandler


class ModelAlignment(KeyActivatedHandler):

    def __init__(self, key_code):
        super(ModelAlignment, self).__init__(key_code)
        self._model = None
        self._active_button = QtCore.Qt.NoButton
        self._lastMousePos = None

    def set_model(self, model):
        if hasattr(model, 'scaleModel') and hasattr(model, 'rotateModel') and hasattr(model, 'offsetModel'):
            self._model = model
        else:
            raise HandlerError('Given model does not have the required API for alignment')

    def enter(self):
        pass

    def leave(self):
        pass

    def mouse_press_event(self, event):
        self._active_button = event.button()
        if self._active_button == QtCore.Qt.LeftButton and event.modifiers() & QtCore.Qt.SHIFT:
            self._active_button = QtCore.Qt.MiddleButton
        pixel_scale = self._scene_viewer.get_pixel_scale()
        self._lastMousePos = [event.x() * pixel_scale, event.y() * pixel_scale]

    def mouse_move_event(self, event):
        if self._lastMousePos is not None:
            pixel_scale = self._scene_viewer.get_pixel_scale()
            pos = [event.x() * pixel_scale, event.y() * pixel_scale]
            delta = [pos[0] - self._lastMousePos[0], pos[1] - self._lastMousePos[1]]
            mag = vectorops.magnitude(delta)
            if mag <= 0.0:
                return
            result, eye = self._zinc_sceneviewer.getEyePosition()
            result, lookat = self._zinc_sceneviewer.getLookatPosition()
            result, up = self._zinc_sceneviewer.getUpVector()
            lookatToEye = vectorops.sub(eye, lookat)
            eyeDistance = vectorops.magnitude(lookatToEye)
            front = vectorops.div(lookatToEye, eyeDistance)
            right = vectorops.cross(up, front)
            viewportWidth = self._scene_viewer.width()
            viewportHeight = self._scene_viewer.height()
            if self._active_button == QtCore.Qt.LeftButton:
                prop = vectorops.div(delta, mag)
                axis = vectorops.add(vectorops.mult(up, prop[0]), vectorops.mult(right, prop[1]))
                angle = mag * 0.002
                self._model.rotateModel(axis, angle)
            elif self._active_button == QtCore.Qt.MiddleButton:
                result, l, r, b, t, near, far = self._zinc_sceneviewer.getViewingVolume()
                if viewportWidth > viewportHeight:
                    eyeScale = (t - b) / viewportHeight
                else:
                    eyeScale = (r - l) / viewportWidth
                offset = vectorops.add(vectorops.mult(right, eyeScale * delta[0]), vectorops.mult(up, -eyeScale * delta[1]))
                self._model.offsetModel(offset)
            elif self._active_button == QtCore.Qt.RightButton:
                factor = 1.0 + delta[1] * 0.0005
                if factor < 0.9:
                    factor = 0.9
                self._model.scaleModel(factor)
            self._lastMousePos = pos

    def mouse_release_event(self, event):
        self._active_button = QtCore.Qt.NoButton
        self._lastMousePos = None
