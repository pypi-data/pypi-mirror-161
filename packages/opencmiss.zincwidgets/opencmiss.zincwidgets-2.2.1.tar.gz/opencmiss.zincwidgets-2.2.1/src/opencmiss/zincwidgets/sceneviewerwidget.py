"""
   Zinc Sceneviewer Widget

   Implements a Zinc Sceneviewer Widget on Python using PySide2,
   which renders the Zinc Scene with OpenGL and allows interactive
   transformation of the view.
   Widget is derived from QtWidgets.QOpenGLWidget

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

from opencmiss.zinc.sceneviewer import Sceneviewer, Sceneviewerevent
from opencmiss.zinc.sceneviewerinput import Sceneviewerinput
from opencmiss.zinc.scenecoordinatesystem import \
    SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT, \
    SCENECOORDINATESYSTEM_WORLD
from opencmiss.zinc.field import Field
from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.result import RESULT_OK

from opencmiss.zincwidgets.definitions import ProjectionMode, SelectionMode, \
    BUTTON_MAP, modifier_map, SELECTION_GROUP_NAME


class SceneviewerWidget(QtWidgets.QOpenGLWidget):

    graphicsInitialized = QtCore.Signal()
    becameActive = QtCore.Signal()

    # init start
    def __init__(self, parent=None):
        """
        Call the super class init functions, set the  Zinc context and the scene viewer handle to None.
        Initialise other attributes that deal with selection and the rotation of the plane.
        """
        super(SceneviewerWidget, self).__init__(parent)
        # Create a Zinc context from which all other objects can be derived either directly or indirectly.
        self._handle_mouse_events = True
        self._graphicsInitialized = False
        self._context = None
        self._sceneviewer = None
        self._scenepicker = None
        self._use_zinc_mouse_event_handling = False
        self._is_active = False

        # Retina displays require a scaling factor most other devices have a scale factor of 1.
        self._pixel_scale = self.window().devicePixelRatio()

        # Selection attributes
        self._selectionKeyHandling = True  # set to False if parent widget is to handle selection key presses
        self._nodeSelectMode = True
        self._dataSelectMode = True
        self._elemSelectMode = True
        self._selection_mode = SelectionMode.NONE
        self._selectionBox = None  # created and destroyed on demand in mouse events
        self._selectionFilter = None  # Client-specified filter which is used in logical AND with sceneviewer filter in selection
        self._selectTol = 3.0  # how many pixels on all sides to add to selection box when a point is clicked on
        self._selectionKeyPressed = False
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self._selection_position_start = None
        # init end

    def paintEvent(self, event):
        super(SceneviewerWidget, self).paintEvent(event)

        if self._is_active:
            painter = QtGui.QPainter(self)
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.magenta), 2))
            painter.drawRect(QtCore.QRect(1, 1, self.width() - 2, self.height() - 2))

    def focusInEvent(self, event) -> None:
        super(SceneviewerWidget, self).focusInEvent(event)
        if not self._is_active:
            self._is_active = True
            self.becameActive.emit()

    def setActiveState(self, state):
        self._is_active = state
        self.update()

    def setContext(self, context):
        """
        Sets the context for this Zinc Scenviewer widget. Prompts creation of a new Zinc
        Sceneviewer, once graphics are initialised.
        """
        self._context = context
        if self._graphicsInitialized:
            self._createSceneviewer()

    def getContext(self):
        return self._context

    def _createSceneviewer(self):
        # Following throws exception if you haven't called setContext() yet
        self.getContext()
        self._sceneviewernotifier = None

        # From the scene viewer module we can create a scene viewer, we set up the
        # scene viewer to have the same OpenGL properties as the QOpenGLWidget.
        sceneviewermodule = self._context.getSceneviewermodule()
        self._sceneviewer = sceneviewermodule.createSceneviewer(Sceneviewer.BUFFERING_MODE_DOUBLE, Sceneviewer.STEREO_MODE_DEFAULT)
        self._sceneviewer.setProjectionMode(Sceneviewer.PROJECTION_MODE_PERSPECTIVE)
        self._sceneviewer.setViewportSize(self.width() * self._pixel_scale, self.height() * self._pixel_scale)

        # Get the default scene filter, which filters by visibility flags
        scenefiltermodule = self._context.getScenefiltermodule()
        scenefilter = scenefiltermodule.getDefaultScenefilter()
        self._sceneviewer.setScenefilter(scenefilter)

        region = self._context.getDefaultRegion()
        scene = region.getScene()
        self.setScene(scene)

        self._sceneviewernotifier = self._sceneviewer.createSceneviewernotifier()
        self._sceneviewernotifier.setCallback(self._zincSceneviewerEvent)

        self._sceneviewer.viewAll()

    def clearSelection(self):
        """
        If there is a selection group, clears it and removes it from scene.
        """
        selectionGroup = self.getSelectionGroup()
        if selectionGroup is not None:
            selectionGroup.clear()
            selectionGroup = Field()  # NULL
            scene = self._sceneviewer.getScene()
            scene.setSelectionField(selectionGroup)

    def getSelectionGroup(self):
        """
        :return: Valid current selection group field or None.
        """
        scene = self._sceneviewer.getScene()
        selectionGroup = scene.getSelectionField()
        if selectionGroup.isValid():
            selectionGroup = selectionGroup.castGroup()
            if selectionGroup.isValid():
                return selectionGroup
        return None

    def getOrCreateSelectionGroup(self):
        selectionGroup = self.getSelectionGroup()
        if selectionGroup is not None:
            return selectionGroup
        scene = self._sceneviewer.getScene()
        region = scene.getRegion()
        fieldmodule = region.getFieldmodule()
        selectionGroup = fieldmodule.findFieldByName(SELECTION_GROUP_NAME)
        if selectionGroup.isValid():
            selectionGroup = selectionGroup.castGroup()
            if selectionGroup.isValid():
                selectionGroup.setManaged(False)
        if not selectionGroup.isValid():
            fieldmodule.beginChange()
            selectionGroup = fieldmodule.createFieldGroup()
            selectionGroup.setName(SELECTION_GROUP_NAME)
            fieldmodule.endChange()
        scene.setSelectionField(selectionGroup)
        return selectionGroup

    def setScene(self, scene):
        if self._sceneviewer is not None:
            self._sceneviewer.setScene(scene)
            self._scenepicker = scene.createScenepicker()
            self.setSelectionfilter(self._selectionFilter)

    def getSceneviewer(self):
        """
        Get the scene viewer for this ZincWidget.
        """
        return self._sceneviewer

    def setSelectionModeAdditive(self):
        self._selectionAlwaysAdditive = True

    def setSelectionKeyHandling(self, state):
        """
        Set whether widget handles its own selection key events.
        :param state: True if widget handles selection key, false if not (i.e. pass to parent)
        """
        self._selectionKeyHandling = state

    def setSelectModeNode(self):
        """
        Set the selection mode to select *only* nodes.
        """
        self._nodeSelectMode = True
        self._dataSelectMode = False
        self._elemSelectMode = False

    def setSelectModeData(self):
        """
        Set the selection mode to select *only* datapoints.
        """
        self._nodeSelectMode = False
        self._dataSelectMode = True
        self._elemSelectMode = False

    def setSelectModeElement(self):
        """
        Set the selection mode to select *only* elements.
        """
        self._nodeSelectMode = False
        self._dataSelectMode = False
        self._elemSelectMode = True

    def setSelectModeAll(self):
        """
        Set the selection mode to select both nodes and elements.
        """
        self._nodeSelectMode = True
        self._dataSelectMode = True
        self._elemSelectMode = True

    def initializeGL(self):
        """
        The OpenGL context is ready for use. If Zinc Context has been set, create Zinc Sceneviewer, otherwise
        inform client who is required to set Context at a later time.
        """
        self._graphicsInitialized = True
        if self._context:
            self._createSceneviewer()
        self.graphicsInitialized.emit()

    def sizeHint(self):
        return QtCore.QSize(200, 400)

    def minimumSizeHint(self):
        return QtCore.QSize(20, 30)

    def setProjectionMode(self, mode):
        if mode == ProjectionMode.PARALLEL:
            self._sceneviewer.setProjectionMode(Sceneviewer.PROJECTION_MODE_PARALLEL)
        elif mode == ProjectionMode.PERSPECTIVE:
            self._sceneviewer.setProjectionMode(Sceneviewer.PROJECTION_MODE_PERSPECTIVE)

    def getProjectionMode(self):
        if self._sceneviewer.getProjectionMode() == Sceneviewer.PROJECTION_MODE_PARALLEL:
            return ProjectionMode.PARALLEL
        elif self._sceneviewer.getProjectionMode() == Sceneviewer.PROJECTION_MODE_PERSPECTIVE:
            return ProjectionMode.PERSPECTIVE

    def getViewParameters(self):
        result, eye, lookat, up = self._sceneviewer.getLookatParameters()
        if result == RESULT_OK:
            angle = self._sceneviewer.getViewAngle()
            return eye, lookat, up, angle

        return None

    def setViewParameters(self, eye, lookat, up, angle):
        self._sceneviewer.beginChange()
        self._sceneviewer.setLookatParametersNonSkew(eye, lookat, up)
        self._sceneviewer.setViewAngle(angle)
        self._sceneviewer.endChange()

    def setScenefilter(self, scenefilter):
        self._sceneviewer.setScenefilter(scenefilter)

    def getScenefilter(self):
        return self._sceneviewer.getScenefilter()

    def getScenepicker(self):
        return self._scenepicker

    def setScenepicker(self, scenepicker):
        self._scenepicker = scenepicker

    def setPickingRectangle(self, coordinate_system, left, bottom, right, top):
        self._scenepicker.setSceneviewerRectangle(self._sceneviewer, coordinate_system, left, bottom, right, top);

    def setSelectionfilter(self, scenefilter):
        """
        Set filter to be applied in logical AND with sceneviewer filter during selection
        """
        self._selectionFilter = scenefilter
        sceneviewerfilter = self._sceneviewer.getScenefilter()
        if self._selectionFilter is not None:
            scenefiltermodule = self._context.getScenefiltermodule()
            scenefilter = scenefiltermodule.createScenefilterOperatorAnd()
            scenefilter.appendOperand(sceneviewerfilter)
            if self._selectionFilter is not None:
                scenefilter.appendOperand(self._selectionFilter)
        else:
            scenefilter = sceneviewerfilter
        self._scenepicker.setScenefilter(scenefilter)

    def getSelectionfilter(self):
        return self._selectionFilter

    def project(self, x, y, z):
        """
        Project the given point in global coordinates into window pixel coordinates
        with the origin at the window's top left pixel.
        Note the z pixel coordinate is a depth which is mapped so that -1 is
        on the far clipping plane, and +1 is on the near clipping plane.
        """
        in_coords = [x, y, z]
        result, out_coords = self._sceneviewer.transformCoordinates(SCENECOORDINATESYSTEM_WORLD, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT, self._sceneviewer.getScene(),
                                                                    in_coords)
        if result == RESULT_OK:
            return out_coords  # [out_coords[0] / out_coords[3], out_coords[1] / out_coords[3], out_coords[2] / out_coords[3]]

        return None

    def unproject(self, x, y, z):
        """
        Unproject the given point in window pixel coordinates where the origin is
        at the window's top left pixel into global coordinates.
        Note the z pixel coordinate is a depth which is mapped so that -1 is
        on the far clipping plane, and +1 is on the near clipping plane.
        """
        in_coords = [x, y, z]
        result, out_coords = self._sceneviewer.transformCoordinates(SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT, SCENECOORDINATESYSTEM_WORLD, self._sceneviewer.getScene(),
                                                                    in_coords)
        if result == RESULT_OK:
            return out_coords  # [out_coords[0] / out_coords[3], out_coords[1] / out_coords[3], out_coords[2] / out_coords[3]]

        return None

    def getViewportSize(self):
        result, width, height = self._sceneviewer.getViewportSize()
        if result == RESULT_OK:
            return (width, height)

        return None

    def setTumbleRate(self, rate):
        self._sceneviewer.setTumbleRate(rate)

    def _getNearestGraphic(self, x, y, domain_type):
        self._scenepicker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT,
                                                  x - self._selectTol, y - self._selectTol, x + self._selectTol, y + self._selectTol)
        nearest_graphics = self._scenepicker.getNearestGraphics()
        if nearest_graphics.isValid() and nearest_graphics.getFieldDomainType() == domain_type:
            return nearest_graphics

        return None

    def getNearestGraphics(self):
        return self._scenepicker.getNearestGraphics()

    def getNearestGraphicsNode(self, x, y):
        return self._getNearestGraphic(x, y, Field.DOMAIN_TYPE_NODES)

    def getNearestGraphicsPoint(self, x, y):
        """
        Assuming given x and y is in the sending widgets coordinates 
        which is a parent of this widget.  For example the values given 
        directly from the event in the parent widget.
        """
        return self._getNearestGraphic(x, y, Field.DOMAIN_TYPE_POINT)

    def getNearestElementGraphics(self):
        return self._scenepicker.getNearestElementGraphics()

    def getNearestGraphicsMesh3D(self, x, y):
        return self._getNearestGraphic(x, y, Field.DOMAIN_TYPE_MESH3D)

    def getNearestGraphicsMesh2D(self, x, y):
        return self._getNearestGraphic(x, y, Field.DOMAIN_TYPE_MESH2D)

    def getNearestNode(self, x, y):
        self._scenepicker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT,
                                                  x - self._selectTol, y - self._selectTol, x + self._selectTol, y + self._selectTol)
        node = self._scenepicker.getNearestNode()

        return node

    def addPickedNodesToFieldGroup(self, selection_group):
        self._scenepicker.addPickedNodesToFieldGroup(selection_group)

    def setIgnoreMouseEvents(self, value):
        self._handle_mouse_events = not value

    def viewAll(self):
        """
        Helper method to set the current scene viewer to view everything
        visible in the current scene.
        """
        self._sceneviewer.viewAll()

    # paintGL start
    def paintGL(self):
        """
        Render the scene for this scene viewer.  The QOpenGLWidget has already set up the
        correct OpenGL buffer for us so all we need do is render into it.  The scene viewer
        will clear the background so any OpenGL drawing of your own needs to go after this
        API call.
        """
        self._sceneviewer.renderScene()
        # paintGL end

    def _zincSceneviewerEvent(self, event):
        """
        Process a scene viewer event.  The updateGL() method is called for a
        repaint required event all other events are ignored.
        """
        if event.getChangeFlags() & Sceneviewerevent.CHANGE_FLAG_REPAINT_REQUIRED:
            QtCore.QTimer.singleShot(0, self.update)

    #  Not applicable at the current point in time.
    #     def _zincSelectionEvent(self, event):
    #         print(event.getChangeFlags())
    #         print('go the selection change')

    # resizeGL start
    def resizeGL(self, width, height):
        """
        Respond to widget resize events.
        """
        if self._sceneviewer:
            self._sceneviewer.setViewportSize(width * self._pixel_scale, height * self._pixel_scale)
        # resizeGL end

    def keyPressEvent(self, event):
        if self._selectionKeyHandling and (event.key() == QtCore.Qt.Key_S) and (event.isAutoRepeat() == False):
            self._selectionKeyPressed = True
            event.setAccepted(True)
        else:
            event.ignore()

    def keyReleaseEvent(self, event):
        if self._selectionKeyHandling and (event.key() == QtCore.Qt.Key_S) and event.isAutoRepeat() == False:
            self._selectionKeyPressed = False
            event.setAccepted(True)
        else:
            event.ignore()

    def mousePressEvent(self, event):
        """
        Handle a mouse press event in the scene viewer.
        """
        self._use_zinc_mouse_event_handling = False  # Track when zinc should be handling mouse events
        if not self._handle_mouse_events:
            event.ignore()
            return

        event.accept()
        if event.button() not in BUTTON_MAP:
            return

        self._selection_position_start = (event.x() * self._pixel_scale, event.y() * self._pixel_scale)

        if BUTTON_MAP[event.button()] == Sceneviewerinput.BUTTON_TYPE_LEFT \
                and self._selectionKeyPressed and (self._nodeSelectMode or self._elemSelectMode):
            self._selection_mode = SelectionMode.EXCLUSIVE
            if event.modifiers() & QtCore.Qt.SHIFT:
                self._selection_mode = SelectionMode.ADDITIVE
        else:
            scene_input = self._sceneviewer.createSceneviewerinput()
            scene_input.setPosition(event.x() * self._pixel_scale, event.y() * self._pixel_scale)
            scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_PRESS)
            scene_input.setButtonType(BUTTON_MAP[event.button()])
            scene_input.setModifierFlags(modifier_map(event.modifiers()))
            self.makeCurrent()
            self._sceneviewer.processSceneviewerinput(scene_input)
            self._use_zinc_mouse_event_handling = True

    def mouseReleaseEvent(self, event):
        """
        Handle a mouse release event in the scene viewer.
        """
        if not self._handle_mouse_events:
            event.ignore()
            return
        event.accept()

        if event.button() not in BUTTON_MAP:
            return

        if self._selection_mode != SelectionMode.NONE:
            self._removeSelectionBox()

            scenepicker = self.getScenepicker()
            if scenepicker:
                x = event.x() * self._pixel_scale
                y = event.y() * self._pixel_scale
                # Construct a small frustum to look for nodes in.
                scene = self._sceneviewer.getScene()
                region = scene.getRegion()
                region.beginHierarchicalChange()
                if (x != self._selection_position_start[0]) or (y != self._selection_position_start[1]):
                    # box select
                    left = min(x, self._selection_position_start[0])
                    right = max(x, self._selection_position_start[0])
                    bottom = min(y, self._selection_position_start[1])
                    top = max(y, self._selection_position_start[1])
                    scenepicker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT, left, bottom, right, top);
                    if self._selection_mode == SelectionMode.EXCLUSIVE:
                        self.clearSelection()
                    if self._nodeSelectMode or self._dataSelectMode or self._elemSelectMode:
                        selectionGroup = self.getOrCreateSelectionGroup()
                        if self._nodeSelectMode or self._dataSelectMode:
                            scenepicker.addPickedNodesToFieldGroup(selectionGroup)
                        if self._elemSelectMode:
                            scenepicker.addPickedElementsToFieldGroup(selectionGroup)

                else:
                    # point select - get nearest object only
                    scenepicker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT,
                                                        x - self._selectTol, y - self._selectTol, x + self._selectTol, y + self._selectTol)
                    nearestGraphics = scenepicker.getNearestGraphics()
                    if (self._nodeSelectMode or self._dataSelectMode or self._elemSelectMode) \
                            and (self._selection_mode == SelectionMode.EXCLUSIVE) \
                            and not nearestGraphics.isValid():
                        self.clearSelection()

                    if (self._nodeSelectMode and (nearestGraphics.getFieldDomainType() == Field.DOMAIN_TYPE_NODES)) or \
                            (self._dataSelectMode and (nearestGraphics.getFieldDomainType() == Field.DOMAIN_TYPE_DATAPOINTS)):
                        node = scenepicker.getNearestNode()
                        if node.isValid():
                            nodeset = node.getNodeset()
                            selectionGroup = self.getOrCreateSelectionGroup()
                            nodegroup = selectionGroup.getFieldNodeGroup(nodeset)
                            if not nodegroup.isValid():
                                nodegroup = selectionGroup.createFieldNodeGroup(nodeset)
                            group = nodegroup.getNodesetGroup()
                            if self._selection_mode == SelectionMode.EXCLUSIVE:
                                remove_current = (group.getSize() == 1) and group.containsNode(node)
                                selectionGroup.clear()
                                if not remove_current:
                                    # re-find node group lost by above clear()
                                    nodegroup = selectionGroup.getFieldNodeGroup(nodeset)
                                    if not nodegroup.isValid():
                                        nodegroup = selectionGroup.createFieldNodeGroup(nodeset)
                                    group = nodegroup.getNodesetGroup()
                                    group.addNode(node)
                            elif self._selection_mode == SelectionMode.ADDITIVE:
                                if group.containsNode(node):
                                    group.removeNode(node)
                                else:
                                    group.addNode(node)

                    if self._elemSelectMode and \
                            (nearestGraphics.getFieldDomainType() in
                             [Field.DOMAIN_TYPE_MESH1D, Field.DOMAIN_TYPE_MESH2D, Field.DOMAIN_TYPE_MESH3D, Field.DOMAIN_TYPE_MESH_HIGHEST_DIMENSION]):
                        elem = scenepicker.getNearestElement()
                        if elem.isValid():
                            mesh = elem.getMesh()
                            selectionGroup = self.getOrCreateSelectionGroup()
                            elementgroup = selectionGroup.getFieldElementGroup(mesh)
                            if not elementgroup.isValid():
                                elementgroup = selectionGroup.createFieldElementGroup(mesh)
                            group = elementgroup.getMeshGroup()
                            if self._selection_mode == SelectionMode.EXCLUSIVE:
                                remove_current = (group.getSize() == 1) and group.containsElement(elem)
                                selectionGroup.clear()
                                if not remove_current:
                                    # re-find element group lost by above clear()
                                    elementgroup = selectionGroup.getFieldElementGroup(mesh)
                                    if not elementgroup.isValid():
                                        elementgroup = selectionGroup.createFieldElementGroup(mesh)
                                    group = elementgroup.getMeshGroup()
                                    group.addElement(elem)
                            elif self._selection_mode == SelectionMode.ADDITIVE:
                                if group.containsElement(elem):
                                    group.removeElement(elem)
                                else:
                                    group.addElement(elem)
                region.endHierarchicalChange()

            self._selection_mode = SelectionMode.NONE

        elif self._use_zinc_mouse_event_handling:
            scene_input = self._sceneviewer.createSceneviewerinput()
            scene_input.setPosition(event.x() * self._pixel_scale, event.y() * self._pixel_scale)
            scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_RELEASE)
            scene_input.setButtonType(BUTTON_MAP[event.button()])
            # self.makeCurrent()
            self._sceneviewer.processSceneviewerinput(scene_input)
            # self._handle_mouse_events = False
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        """
        Handle a mouse move event in the scene viewer.
        Behaviour depends on modes set in original mouse press event.
        """
        if not self._handle_mouse_events:
            event.ignore()
            return

        event.accept()

        if self._selection_mode != SelectionMode.NONE:
            x = event.x() * self._pixel_scale
            y = event.y() * self._pixel_scale
            xdiff = float(x - self._selection_position_start[0])
            ydiff = float(y - self._selection_position_start[1])
            if abs(xdiff) < 0.0001:
                xdiff = 1
            if abs(ydiff) < 0.0001:
                ydiff = 1
            xoff = float(self._selection_position_start[0]) / xdiff + 0.5
            yoff = float(self._selection_position_start[1]) / ydiff + 0.5
            self._addUpdateSelectionBox(xdiff, ydiff, xoff, yoff)

        elif self._use_zinc_mouse_event_handling:
            scene_input = self._sceneviewer.createSceneviewerinput()
            scene_input.setPosition(event.x() * self._pixel_scale, event.y() * self._pixel_scale)
            scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_MOTION_NOTIFY)
            if event.type() == QtCore.QEvent.Leave:
                scene_input.setPosition(-1, -1)
            self.makeCurrent()
            self._sceneviewer.processSceneviewerinput(scene_input)
        else:
            event.ignore()

    def _addUpdateSelectionBox(self, xdiff, ydiff, xoff, yoff):
        # Using a non-ideal workaround for creating a rubber band for selection.
        # This will create strange visual artifacts when using two scene viewers looking at
        # the same scene.  Waiting on a proper solution in the API.
        # Note if the standard glyphs haven't been defined then the
        # selection box will not be visible
        scene = self._sceneviewer.getScene()
        scene.beginChange()
        if self._selectionBox is None:
            self._selectionBox = scene.createGraphicsPoints()
            self._selectionBox.setScenecoordinatesystem(SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT)
        attributes = self._selectionBox.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_CUBE_WIREFRAME)
        attributes.setBaseSize([xdiff, ydiff, 0.999])
        attributes.setGlyphOffset([xoff, -yoff, 0])
        # self._selectionBox.setVisibilityFlag(True)
        scene.endChange()

    def _removeSelectionBox(self):
        if self._selectionBox is not None:
            scene = self._selectionBox.getScene()
            scene.removeGraphics(self._selectionBox)
            self._selectionBox = None
