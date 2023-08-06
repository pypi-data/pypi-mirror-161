"""
Zinc Sceneviewer Editor Widget

Widget for editing viewing controls for a Sceneviewer.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import math

from PySide2 import QtCore, QtWidgets

from opencmiss.zinc.sceneviewer import Sceneviewer, Sceneviewerevent
from opencmiss.zinc.status import OK as ZINC_OK
from opencmiss.zincwidgets.ui.ui_sceneviewereditorwidget import Ui_SceneviewerEditorWidget


class SceneviewerEditorWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        """
        Call the super class init functions
        """
        QtWidgets.QWidget.__init__(self, parent)
        self._sceneviewer = None
        self._sceneviewernotifier = None
        self._enableUpdates = False
        self._maximumClippingDistance = 1
        # Using composition to include the visual element of the GUI.
        self._ui = Ui_SceneviewerEditorWidget()
        self._ui.setupUi(self)
        self._ui.widget_container.setEnabled(False)
        # Future once enum string conversions added for this type:
        # self._ui.transparency_mode_chooser.setEnumsList(Sceneviewer.TransparencyModeEnumToString, Element.TransparencyModeEnumFromString)
        self._make_connections()

    def _make_connections(self):
        self._ui.region_chooser.currentIndexChanged.connect(self._region_changed)

    def _region_changed(self):
        region = self._ui.region_chooser.getRegion()
        self._sceneviewer.setScene(region.getScene())

    def setZincRootRegion(self, root_region):
        self._ui.region_chooser.setRootRegion(root_region)
        # self.setScene(root_region.getScene())

    def getSceneviewer(self):
        """
        Get the sceneviewer currently in the editor
        """
        return self._sceneviewer

    def setSceneviewer(self, sceneviewer):
        """
        Set the current sceneviewer in the editor
        """
        if not (sceneviewer and sceneviewer.isValid()):
            if self._sceneviewernotifier is not None:
                self._sceneviewernotifier.clearCallback()
                self._sceneviewernotifier = None
            self._sceneviewer = None
            self._ui.widget_container.setEnabled(False)
            return
        self._ui.widget_container.setEnabled(True)
        self._sceneviewer = sceneviewer
        self._maximumClippingDistance = sceneviewer.getFarClippingPlane()
        self._sceneviewernotifier = sceneviewer.createSceneviewernotifier()
        self.setEnableUpdates(self._enableUpdates)
        scene_region = self._sceneviewer.getScene().getRegion()
        self._ui.region_chooser.setRegion(scene_region)
        self._displayAllSettings()

    def setScene(self, scene):
        self._sceneviewer.setScene(scene)

    def setEnableUpdates(self, enableUpdates):
        self._enableUpdates = enableUpdates
        if self._sceneviewernotifier is not None:
            if enableUpdates:
                self._sceneviewernotifier.setCallback(self._sceneviewerChange)
                self._displayViewSettings()
            else:
                self._sceneviewernotifier.clearCallback()

    def _sceneviewerChange(self, event):
        """
        Change to scene viewer; update view widgets if transformation changed
        """
        changeFlags = event.getChangeFlags()
        if changeFlags & Sceneviewerevent.CHANGE_FLAG_TRANSFORM:
            self._displayViewSettings()
        elif changeFlags & Sceneviewerevent.CHANGE_FLAG_FINAL:
            self.setSceneviewer(None)

    def _displayAllSettings(self):
        """
        Show the current scene viewer settings on the view widgets
        """
        self._displayViewSettings()
        self.backgroundColourDisplay()

    def _displayViewSettings(self):
        """
        Show the current view-related scene viewer settings on the view widgets
        """
        self.viewAngleDisplay()
        self.eyePositionDisplay()
        self.lookatPositionDisplay()
        self.upVectorDisplay()
        self.nearClippingDisplay()
        self.farClippingDisplay()
        self.antialiasDisplay()
        self.transparencyModeDisplay()
        self.lightBothSidesDisplay()
        self.perturbLineDisplay()

    def _displayReal(self, widget, value):
        """
        Display real value in a widget
        """
        newText = '{:.5g}'.format(value)
        widget.setText(newText)

    def _displayVector(self, widget, values, numberFormat='{:.5g}'):
        """
        Display real vector values in a widget
        """
        newText = ", ".join(numberFormat.format(value) for value in values)
        widget.setText(newText)

    def _parseVector(self, widget):
        """
        Return real vector from comma separated text in line edit widget
        """
        text = widget.text()
        values = [float(value) for value in text.split(',')]
        if len(values) < 1:
            raise
        return values

    def viewAll(self):
        """
        Change sceneviewer to see all of scene.
        """

        self._sceneviewer.viewAll()
        self._maximumClippingDistance = self._sceneviewer.getFarClippingPlane()
        self._displayViewSettings()

    def perspectiveStateChanged(self, state):
        """
        Set perspective/parallel projection
        """
        if state:
            projectionMode = Sceneviewer.PROJECTION_MODE_PERSPECTIVE
        else:
            projectionMode = Sceneviewer.PROJECTION_MODE_PARALLEL
        self._sceneviewer.setProjectionMode(projectionMode)

    def viewAngleDisplay(self):
        """
        Display the current scene viewer diagonal view angle
        """
        viewAngleRadians = self._sceneviewer.getViewAngle()
        viewAngleDegrees = viewAngleRadians * 180.0 / math.pi
        self._displayReal(self._ui.view_angle, viewAngleDegrees)

    def viewAngleEntered(self):
        """
        Set scene viewer diagonal view angle from value in the view angle widget
        """
        try:
            viewAngleRadians = float(self._ui.view_angle.text()) * math.pi / 180.0
            if ZINC_OK != self._sceneviewer.setViewAngle(viewAngleRadians):
                raise
        except:
            print("Invalid view angle")
        self.viewAngleDisplay()

    def setLookatParametersNonSkew(self):
        """
        Set eye, lookat position and up vector simultaneous in non-skew projection
        """
        eye = self._parseVector(self._ui.eye_position)
        lookat = self._parseVector(self._ui.lookat_position)
        up_vector = self._parseVector(self._ui.up_vector)
        if ZINC_OK != self._sceneviewer.setLookatParametersNonSkew(eye, lookat, up_vector):
            raise

    def eyePositionDisplay(self):
        """
        Display the current scene viewer eye position
        """
        result, eye = self._sceneviewer.getEyePosition()
        self._displayVector(self._ui.eye_position, eye)

    def eyePositionEntered(self):
        """
        Set scene viewer wyw position from text in widget
        """
        try:
            self.setLookatParametersNonSkew()
        except:
            print("Invalid eye position")
            self.eyePositionDisplay()

    def lookatPositionDisplay(self):
        """
        Display the current scene viewer lookat position
        """
        result, lookat = self._sceneviewer.getLookatPosition()
        self._displayVector(self._ui.lookat_position, lookat)

    def lookatPositionEntered(self):
        """
        Set scene viewer lookat position from text in widget
        """
        try:
            self.setLookatParametersNonSkew()
        except:
            print("Invalid lookat position")
            self.lookatPositionDisplay()

    def upVectorDisplay(self):
        """
        Display the current scene viewer eye position
        """
        result, up_vector = self._sceneviewer.getUpVector()
        self._displayVector(self._ui.up_vector, up_vector)

    def upVectorEntered(self):
        """
        Set scene viewer up vector from text in widget
        """
        try:
            self.setLookatParametersNonSkew()
        except:
            print("Invalid up vector")
            self.upVectorDisplay()

    def nearClippingDisplay(self):
        """
        Display the current near clipping plane distance
        """
        near = self._sceneviewer.getNearClippingPlane()
        value = int(10001.0 * near / self._maximumClippingDistance) - 1
        # don't want signal for my change
        self._ui.near_clipping_slider.blockSignals(True)
        self._ui.near_clipping_slider.setValue(value)
        self._ui.near_clipping_slider.blockSignals(False)

    def nearClippingChanged(self, value):
        """
        Set near clipping plane distance from slider
        """
        near = (value + 1) * self._maximumClippingDistance / 10001.0
        self._sceneviewer.setNearClippingPlane(near)

    def farClippingDisplay(self):
        """
        Display the current far clipping plane distance
        """
        value = int(10001.0 * self._sceneviewer.getFarClippingPlane() / self._maximumClippingDistance) - 1
        self._ui.far_clipping_slider.blockSignals(True)
        self._ui.far_clipping_slider.setValue(value)
        self._ui.far_clipping_slider.blockSignals(False)

    def farClippingChanged(self, value):
        """
        Set far clipping plane distance from slider
        """
        far = (value + 1) * self._maximumClippingDistance / 10001.0
        self._sceneviewer.setFarClippingPlane(far)

    def backgroundColourDisplay(self):
        """
        Display the current scene viewer eye position
        """
        result, colourRGB = self._sceneviewer.getBackgroundColourRGB()
        self._displayVector(self._ui.background_colour, colourRGB)

    def backgroundColourEntered(self):
        """
        Set scene viewer diagonal view angle from value in the view angle widget
        """
        try:
            colourRGB = self._parseVector(self._ui.background_colour)
            if ZINC_OK != self._sceneviewer.setBackgroundColourRGB(colourRGB):
                raise
        except:
            print("Invalid background colour")
        self.backgroundColourDisplay()

    def antialiasDisplay(self):
        """
        Display the current scene viewer antialias
        """
        antialiasValue = self._sceneviewer.getAntialiasSampling()
        self._ui.antialias.setText(str(antialiasValue))

    def antialiasEntered(self):
        """
        Set scene viewer diagonal view angle from value in the view angle widget
        """
        try:
            antialiasValue = int(self._ui.antialias.text())
            if ZINC_OK != self._sceneviewer.setAntialiasSampling(antialiasValue):
                raise
        except:
            print("Invalid antialias")
        self.antialiasDisplay()

    TRANSPARENCY_MODE_MAP = [
        ("fast", Sceneviewer.TRANSPARENCY_MODE_FAST),
        ("slow", Sceneviewer.TRANSPARENCY_MODE_SLOW),
        ("order independent", Sceneviewer.TRANSPARENCY_MODE_ORDER_INDEPENDENT)
    ]

    def transparencyModeDisplay(self):
        """
        Display the current scene viewer transparency mode
        """
        transparencyMode = self._sceneviewer.getTransparencyMode()
        # future:
        # self._ui.transparency_mode_chooser.setEnum(transparencyMode)
        self._ui.transparency_mode_comboBox.blockSignals(True)
        self._ui.transparency_mode_comboBox.setCurrentIndex(transparencyMode - Sceneviewer.TRANSPARENCY_MODE_FAST)
        self._ui.transparency_mode_comboBox.blockSignals(False)

    def transparencyModeChanged(self, index):
        """
        Transparency mode combo box changed.
        """
        enumName = str(self._ui.transparency_mode_comboBox.currentText())
        # future:
        # transparencyMode = self._ui.transparency_mode_chooser.getEnum()
        transparencyMode = \
            Sceneviewer.TRANSPARENCY_MODE_FAST if enumName == "fast" else \
            Sceneviewer.TRANSPARENCY_MODE_SLOW if enumName == "slow" else \
            Sceneviewer.TRANSPARENCY_MODE_ORDER_INDEPENDENT if enumName == "order independent" else \
            Sceneviewer.TRANSPARENCY_MODE_INVALID
        self._sceneviewer.setTransparencyMode(transparencyMode)
        if transparencyMode == Sceneviewer.TRANSPARENCY_MODE_ORDER_INDEPENDENT:
            self._sceneviewer.setTransparencyLayers(6)  # a good if conservative default value

    def lightBothSidesDisplay(self):
        flag = self._sceneviewer.isLightingTwoSided()
        if flag:
            self._ui.light_both_sides_checkbox.setCheckState(QtCore.Qt.Checked)
        else:
            self._ui.light_both_sides_checkbox.setCheckState(QtCore.Qt.Unchecked)

    def lightBothSidesStateChanged(self, state):
        """
        Set scene viewer lighting two sided value
        """
        self._sceneviewer.setLightingTwoSided(state)

    def perturbLineDisplay(self):
        flag = self._sceneviewer.getPerturbLinesFlag()
        if flag:
            self._ui.perturbline_checkbox.setCheckState(QtCore.Qt.Checked)
        else:
            self._ui.perturbline_checkbox.setCheckState(QtCore.Qt.Unchecked)

    def perturbLineStateChanged(self, state):
        """
        Set scene viewer perturb lines value
        """
        self._sceneviewer.setPerturbLinesFlag(state)
