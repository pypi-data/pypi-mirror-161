"""
   Copyright 2015 University of Auckland

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from PySide2 import QtCore, QtGui, QtWidgets

from opencmiss.zinc.field import Field
from opencmiss.zinc.graphics import Graphics

from opencmiss.zincwidgets.ui.ui_sceneeditorwidget import Ui_SceneEditorWidget

"""
Zinc Scene Editor Widget

Allows a Zinc Scene object to be edited in Qt / Python.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""


class SceneEditorWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        """
        Call the super class init functions
        """
        QtWidgets.QWidget.__init__(self, parent)
        self._scene = None
        # Using composition to include the visual element of the GUI.
        self._ui = Ui_SceneEditorWidget()
        self._ui.setupUi(self)
        self._make_connections()

    def _make_connections(self):
        self._ui.region_chooser.currentIndexChanged.connect(self._region_changed)

    def _region_changed(self, index):
        region = self._ui.region_chooser.getRegion()
        self.setScene(region.getScene())

    def setZincRootRegion(self, root_region):
        self._ui.region_chooser.setRootRegion(root_region)
        self.setScene(root_region.getScene())

    def getScene(self):
        """
        Get the scene currently in the editor
        """
        return self._scene

    def setScene(self, scene):
        """
        Set the current scene in the editor

        :param scene: zinc.scene
        """
        if not (scene and scene.isValid()):
            self._scene = None
        else:
            self._scene = scene
        self._ui.graphics_editor.setScene(scene)
        if self._scene:
            self._ui.graphics_editor.setGraphics(self._scene.getFirstGraphics())
        self._buildGraphicsList()

    def _getDefaultCoordinateField(self):
        """
        Get the first coordinate field from the current scene
        """
        if self._scene:
            fielditer = self._scene.getRegion().getFieldmodule().createFielditerator()
            field = fielditer.next()
            while field.isValid():
                if field.isTypeCoordinate() and (field.getValueType() == Field.VALUE_TYPE_REAL) and \
                        (field.getNumberOfComponents() <= 3) and field.castFiniteElement().isValid():
                    return field
                field = fielditer.next()
        return None

    def _getGraphicsDisplayName(self, graphics):
        """
        Build a display name from the graphics graphics_type and domain
        """
        graphics_type = graphics.getType()
        fieldDomainType = graphics.getFieldDomainType()
        if graphics_type == Graphics.TYPE_POINTS:
            if fieldDomainType == Field.DOMAIN_TYPE_POINT:
                return "point"
            if fieldDomainType == Field.DOMAIN_TYPE_NODES:
                return "node points"
            if fieldDomainType == Field.DOMAIN_TYPE_DATAPOINTS:
                return "data points"
            return "element points"
        elif graphics_type == Graphics.TYPE_LINES:
            return "lines"
        elif graphics_type == Graphics.TYPE_SURFACES:
            return "surfaces"
        elif graphics_type == Graphics.TYPE_CONTOURS:
            return "contours"
        elif graphics_type == Graphics.TYPE_STREAMLINES:
            return "streamlines"

    def _buildGraphicsList(self):
        """
        Fill the graphics list view with the list of graphics for current region/scene
        """
        if self._ui.graphics_listWidget is not None:
            self._ui.graphics_listWidget.clear()  # Must clear or holds on to graphics references
        if self._scene:
            selectedGraphics = self._ui.graphics_editor.getGraphics()
            graphics = self._scene.getFirstGraphics()
            index = 0
            while graphics and graphics.isValid():
                name = self._getGraphicsDisplayName(graphics)
                item = QtWidgets.QListWidgetItem(name)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                visible = graphics.getVisibilityFlag()
                item.setCheckState(QtCore.Qt.Checked if visible else QtCore.Qt.Unchecked)
                self._ui.graphics_listWidget.addItem(item)
                if graphics == selectedGraphics:
                    self._ui.graphics_listWidget.setCurrentItem(item)
                graphics = self._scene.getNextGraphics(graphics)
                index += 1
        self._ui.graphics_listWidget.registerDropCallback(self._onGraphicsListItemChanged)
        self._ui.graphics_listWidget.show()

    def _onGraphicsListItemChanged(self, prevRow, newRow):
        """
        For the drag and drop event.
        Update the order of graphics in scene.
        """ 
        if newRow != prevRow:
            movingGraphics = self._scene.getFirstGraphics()
            refGraphics = self._scene.getFirstGraphics()
            while prevRow > 0 or newRow > 0 and movingGraphics.isValid():
                if prevRow > 0:
                    movingGraphics = self._scene.getNextGraphics(movingGraphics)
                    prevRow -= 1
                if newRow > 0:
                    refGraphics = self._scene.getNextGraphics(refGraphics)
                    newRow -= 1
            self._scene.moveGraphicsBefore(movingGraphics, refGraphics)
            self.graphicsListItemClicked(self._ui.graphics_listWidget.currentItem())

    def graphicsListItemClicked(self, item):
        """
        Either changes visibility flag or selects current graphics
        """
        clickedIndex = self._ui.graphics_listWidget.row(item)
        graphics = self._scene.getFirstGraphics()
        tempIndex = clickedIndex
        while tempIndex > 0 and graphics.isValid():
            graphics = self._scene.getNextGraphics(graphics)
            tempIndex -= 1
        visibilityFlag = item.checkState() == QtCore.Qt.Checked
        graphics.setVisibilityFlag(visibilityFlag)
        selectedModelIndex = self._ui.graphics_listWidget.currentIndex()
        if clickedIndex == selectedModelIndex.row():
            self._ui.graphics_editor.setGraphics(graphics)

    def addGraphicsEntered(self, name):
        """
        Add a new chosen graphics type

        :param name: string
        """
        if not self._scene:
            return
        graphicsType = Graphics.TYPE_INVALID
        fieldDomainType = Field.DOMAIN_TYPE_INVALID
        # name = str(combobox1.currentText())
        if name == "point":
            graphicsType = Graphics.TYPE_POINTS
            fieldDomainType = Field.DOMAIN_TYPE_POINT
        elif name == "node points":
            graphicsType = Graphics.TYPE_POINTS
            fieldDomainType = Field.DOMAIN_TYPE_NODES
        elif name == "data points":
            graphicsType = Graphics.TYPE_POINTS
            fieldDomainType = Field.DOMAIN_TYPE_DATAPOINTS
        elif name == "element points":
            graphicsType = Graphics.TYPE_POINTS
            fieldDomainType = Field.DOMAIN_TYPE_MESH_HIGHEST_DIMENSION
        elif name == "lines":
            graphicsType = Graphics.TYPE_LINES
        elif name == "surfaces":
            graphicsType = Graphics.TYPE_SURFACES
        elif name == "contours":
            graphicsType = Graphics.TYPE_CONTOURS
        elif name == "streamlines":
            graphicsType = Graphics.TYPE_STREAMLINES
        else:
            pass
        if graphicsType != Graphics.TYPE_INVALID:
            self._scene.beginChange()
            graphics = self._scene.createGraphics(graphicsType)
            if fieldDomainType != Field.DOMAIN_TYPE_INVALID:
                graphics.setFieldDomainType(fieldDomainType)
            if fieldDomainType != Field.DOMAIN_TYPE_POINT:
                coordinateField = self._getDefaultCoordinateField()
                if coordinateField is not None:
                    graphics.setCoordinateField(coordinateField)
            self._scene.endChange()
            self._ui.graphics_editor.setGraphics(graphics)
            self._buildGraphicsList()
        self._ui.add_graphics_combobox.setCurrentIndex(0)

    def deleteGraphicsClicked(self):
        """
        Delete the current graphics type
        """
        if not self._scene:
            return
        graphics = self._ui.graphics_editor.getGraphics()
        if graphics:
            nextGraphics = self._scene.getNextGraphics(graphics)
            if not (nextGraphics and nextGraphics.isValid()):
                nextGraphics = self._scene.getPreviousGraphics(graphics)
            if not (nextGraphics and nextGraphics.isValid()):
                nextGraphics = self._scene.getFirstGraphics()
            if nextGraphics == graphics:
                nextGraphics = None
            self._ui.graphics_editor.setGraphics(nextGraphics)
            self._scene.removeGraphics(graphics)
            self._buildGraphicsList()
