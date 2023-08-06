"""
Created on July 15, 2015

@author: Richard Christie
"""
from PySide2 import QtCore

from opencmiss.maths import vectorops
from opencmiss.zincwidgets.sceneviewerwidget import SceneviewerWidget


class AlignmentSceneviewerWidget(SceneviewerWidget):

    def __init__(self, parent=None):
        super(AlignmentSceneviewerWidget, self).__init__(parent)
        self._model = None
        self._alignKeyPressed = False
        self._active_button = QtCore.Qt.NoButton
        self._lastMousePos = None

    def setModel(self, model):
        self._model = model

    def keyPressEvent(self, event):
        """
        Holding down the 'A' key performs alignment (if align mode is on)
        """
        if (event.key() == QtCore.Qt.Key_A) and event.isAutoRepeat() is False:
            self._alignKeyPressed = True
            event.setAccepted(True)
        else:
           super(AlignmentSceneviewerWidget, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if (event.key() == QtCore.Qt.Key_A) and event.isAutoRepeat() is False:
            self._alignKeyPressed = False
            event.setAccepted(True)
        else:
           super(AlignmentSceneviewerWidget, self).keyReleaseEvent(event)

    def mousePressEvent(self, event):
        if self._active_button != QtCore.Qt.NoButton:
            return
        if self._model.isStateAlign() and self._alignKeyPressed:
            self._use_zinc_mouse_event_handling = False  # needed as not calling super mousePressEvent
            self._active_button = event.button()
            # shift-Left button becomes middle button, to support Mac
            if (self._active_button == QtCore.Qt.LeftButton) and (event.modifiers() & QtCore.Qt.SHIFT):
                self._active_button = QtCore.Qt.MiddleButton
            self._lastMousePos = [event.x(), event.y()]
        else:
            super(AlignmentSceneviewerWidget, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._model.isStateAlign() and self._alignKeyPressed and (self._lastMousePos is not None):
            pos = [event.x(), event.y()]
            delta = [pos[0] - self._lastMousePos[0], pos[1] - self._lastMousePos[1]]
            result, eye = self._sceneviewer.getEyePosition()
            result, lookat = self._sceneviewer.getLookatPosition()
            result, up = self._sceneviewer.getUpVector()
            lookatToEye = vectorops.sub(eye, lookat)
            eyeDistance = vectorops.magnitude(lookatToEye)
            front = vectorops.div(lookatToEye, eyeDistance)
            right = vectorops.cross(up, front)
            if self._active_button == QtCore.Qt.LeftButton:
                mag = vectorops.magnitude(delta)
                prop = vectorops.div(delta, mag)
                axis = vectorops.add(vectorops.mult(up, prop[0]), vectorops.mult(right, prop[1]))
                angle = mag*0.002
                self._model.rotateModel(axis, angle)
            elif self._active_button == QtCore.Qt.MiddleButton:
                result, l, r, b, t, near, far = self._sceneviewer.getViewingVolume()
                viewportWidth = self.width()
                viewportHeight = self.height()
                if viewportWidth > viewportHeight:
                    eyeScale = (t - b) / viewportHeight
                else:
                    eyeScale = (r - l) / viewportWidth
                offset = vectorops.add(vectorops.mult(right, eyeScale * delta[0]), vectorops.mult(up, -eyeScale * delta[1]))
                self._model.offsetModel(offset)
            elif self._active_button == QtCore.Qt.RightButton:
                factor = 1.0 + delta[1]*0.0005
                if factor < 0.9:
                    factor = 0.9
                self._model.scaleModel(factor)
            self._lastMousePos = pos
        else:
            super(AlignmentSceneviewerWidget, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._lastMousePos is not None:
            pass
        else:
            super(AlignmentSceneviewerWidget, self).mouseReleaseEvent(event)
        self._active_button = QtCore.Qt.NoButton
        self._lastMousePos = None
