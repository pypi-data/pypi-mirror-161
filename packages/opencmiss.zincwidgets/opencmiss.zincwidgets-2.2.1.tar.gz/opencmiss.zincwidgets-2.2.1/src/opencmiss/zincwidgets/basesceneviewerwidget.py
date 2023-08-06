"""
Zinc Sceneviewer Widget

Implements a Zinc Sceneviewer Widget on Python using PySide or PyQt,
which renders the Zinc Scene with OpenGL and allows interactive
transformation of the view.
Widget is derived from QtOpenGL.QGLWidget.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
# This python module is intended to facilitate users creating their own applications that use OpenCMISS-Zinc
# See the examples at https://svn.physiomeproject.org/svn/cmiss/zinc/bindings/trunk/python/ for further
# information.
from PySide2 import QtCore, QtWidgets

from opencmiss.zinc.sceneviewer import Sceneviewer, Sceneviewerevent
from opencmiss.zinc.sceneviewerinput import Sceneviewerinput
from opencmiss.zinc.scenecoordinatesystem import \
    SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT, \
    SCENECOORDINATESYSTEM_WORLD
from opencmiss.zinc.field import Field
from opencmiss.zinc.result import RESULT_OK

from opencmiss.zincwidgets.handlers.interactionmanager import InteractionManager


class BaseSceneviewerWidget(QtWidgets.QOpenGLWidget, InteractionManager):
    # Create a signal to notify when the OpenGL scene is ready.
    graphics_initialized = QtCore.Signal()

    def __init__(self, parent=None):
        """
        Call the super class init functions, set the  Zinc context and the scene viewer handle to None.
        Initialise other attributes that deal with selection and the rotation of the plane.
        """
        super(BaseSceneviewerWidget, self).__init__(parent)
        InteractionManager.__init__(self)
        # Create a Zinc context from which all other objects can be derived either directly or indirectly.
        self._graphics_initialized = False
        self._context = None
        self._sceneviewer = None
        self._scene_picker = None

        # Retina displays require a scaling factor most other devices have a scale factor of 1.
        self._pixel_scale = self.window().devicePixelRatio()

        # Client-specified filter which is used in logical AND with sceneviewer filter in selection
        self._selection_filter = None
        self._selection_tolerance = 3.0  # Number of pixels to set the selection tolerance to.
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def set_context(self, context):
        """
        Sets the context for this Zinc scene viewer widget. Prompts creation of a new Zinc
        scene viewer, once graphics are initialised.
        """
        self._context = context
        if self._graphics_initialized:
            self._create_sceneviewer()

    def get_context(self):
        if self._context is not None:
            return self._context
        else:
            raise RuntimeError("Zinc context has not been set in base scene viewer widget.")

    def _create_sceneviewer(self):
        # From the scene viewer module we can create a scene viewer, we set up the
        # scene viewer to have the same OpenGL properties as the QGLWidget.
        scene_viewer_module = self._context.getSceneviewermodule()
        self._sceneviewer = scene_viewer_module.createSceneviewer(Sceneviewer.BUFFERING_MODE_DOUBLE,
                                                                  Sceneviewer.STEREO_MODE_DEFAULT)
        self._sceneviewer.setProjectionMode(Sceneviewer.PROJECTION_MODE_PERSPECTIVE)
        pixel_scale = self.window().devicePixelRatio()
        self._sceneviewer.setViewportSize(self.width() * pixel_scale, self.height() * pixel_scale)

        # Get the default scene filter, which filters by visibility flags
        scene_filter_module = self._context.getScenefiltermodule()
        scene_filter = scene_filter_module.getDefaultScenefilter()
        self._sceneviewer.setScenefilter(scene_filter)

        region = self._context.getDefaultRegion()
        scene = region.getScene()
        self._sceneviewer.setScene(scene)

        self._sceneviewer_notifier = self._sceneviewer.createSceneviewernotifier()
        self._sceneviewer_notifier.setCallback(self._zinc_sceneviewer_event)

        self._sceneviewer.viewAll()

    def set_scene(self, scene):
        if self._sceneviewer is not None:
            self._sceneviewer.setScene(scene)
            self._scene_picker = scene.createScenepicker()
            self.set_selectionfilter(self._selection_filter)

    def get_pixel_scale(self):
        return self._pixel_scale

    def get_zinc_sceneviewer(self):
        """
        Get the scene viewer for this ZincWidget.
        """
        return self._sceneviewer

    def initializeGL(self):
        """
        The OpenGL context is ready for use. If Zinc Context has been set, create Zinc Sceneviewer, otherwise
        inform client who is required to set Context at a later time.
        """
        self._graphics_initialized = True
        if self._context:
            self._create_sceneviewer()
        self.graphics_initialized.emit()

    def is_graphics_initialized(self):
        return self._graphics_initialized

    def set_projection_mode(self, mode):
        if mode == ProjectionMode.PARALLEL:
            self._sceneviewer.setProjectionMode(Sceneviewer.PROJECTION_MODE_PARALLEL)
        elif mode == ProjectionMode.PERSPECTIVE:
            self._sceneviewer.setProjectionMode(Sceneviewer.PROJECTION_MODE_PERSPECTIVE)

    def get_projection_mode(self):
        if self._sceneviewer.getProjectionMode() == Sceneviewer.PROJECTION_MODE_PARALLEL:
            return ProjectionMode.PARALLEL
        elif self._sceneviewer.getProjectionMode() == Sceneviewer.PROJECTION_MODE_PERSPECTIVE:
            return ProjectionMode.PERSPECTIVE

    def get_view_parameters(self):
        result, eye, lookat, up = self._sceneviewer.getLookatParameters()
        if result == RESULT_OK:
            angle = self._sceneviewer.getViewAngle()
            return eye, lookat, up, angle

        return None

    def set_view_parameters(self, eye, lookat, up, angle):
        self._sceneviewer.beginChange()
        self._sceneviewer.setLookatParametersNonSkew(eye, lookat, up)
        self._sceneviewer.setViewAngle(angle)
        self._sceneviewer.endChange()

    def set_scenefilter(self, scenefilter):
        self._sceneviewer.setScenefilter(scenefilter)

    def get_scenefilter(self):
        return self._sceneviewer.getScenefilter()

    def get_scenepicker(self):
        return self._scene_picker

    def set_scenepicker(self, scenepicker):
        self._scene_picker = scenepicker

    def set_picking_rectangle(self, coordinate_system, left, bottom, right, top):
        self._scene_picker.setSceneviewerRectangle(self._sceneviewer, coordinate_system, left, bottom, right, top)

    def set_selectionfilter(self, scene_filter):
        """
        Set filter to be applied in logical AND with sceneviewer filter during selection
        """
        self._selection_filter = scene_filter
        scene_viewer_filter = self._sceneviewer.getScenefilter()
        if self._selection_filter is not None:
            scene_filter_module = self._context.getScenefiltermodule()
            scene_filter = scene_filter_module.createScenefilterOperatorAnd()
            scene_filter.appendOperand(scene_viewer_filter)
            if self._selection_filter is not None:
                scene_filter.appendOperand(self._selection_filter)
        else:
            scene_filter = scene_viewer_filter
        self._scene_picker.setScenefilter(scene_filter)

    def get_selectionfilter(self):
        return self._selection_filter

    def project(self, x, y, z):
        """
        Project the given point in global coordinates into window pixel coordinates
        with the origin at the window's top left pixel.
        Note the z pixel coordinate is a depth which is mapped so that -1 is
        on the far clipping plane, and +1 is on the near clipping plane.
        """
        in_coords = [x, y, z]
        result, out_coords = self._sceneviewer.transformCoordinates(SCENECOORDINATESYSTEM_WORLD,
                                                                    SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT,
                                                                    self._sceneviewer.getScene(), in_coords)
        if result == RESULT_OK:
            # [out_coords[0] / out_coords[3], out_coords[1] / out_coords[3], out_coords[2] / out_coords[3]]
            return out_coords

        return None

    def unproject(self, x, y, z):
        """
        Unproject the given point in window pixel coordinates where the origin is
        at the window's top left pixel into global coordinates.
        Note the z pixel coordinate is a depth which is mapped so that -1 is
        on the far clipping plane, and +1 is on the near clipping plane.
        """
        in_coords = [x, y, z]
        result, out_coords = self._sceneviewer.transformCoordinates(SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT,
                                                                    SCENECOORDINATESYSTEM_WORLD,
                                                                    self._sceneviewer.getScene(), in_coords)
        if result == RESULT_OK:
            # [out_coords[0] / out_coords[3], out_coords[1] / out_coords[3], out_coords[2] / out_coords[3]]
            return out_coords

        return None

    def get_viewport_size(self):
        result, width, height = self._sceneviewer.getViewportSize()
        if result == RESULT_OK:
            return width, height

        return None

    def set_tumble_rate(self, rate):
        self._sceneviewer.setTumbleRate(rate)

    def get_picking_volume_centre(self):
        result, centre = self._scene_picker.getPickingVolumeCentre()
        if result == RESULT_OK:
            return centre

        return None

    def _get_nearest_graphic(self, x, y, domain_type):
        self._scene_picker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT,
                                                   x - self._selection_tolerance, y - self._selection_tolerance,
                                                   x + self._selection_tolerance, y + self._selection_tolerance)
        nearest_graphics = self._scene_picker.getNearestGraphics()
        if nearest_graphics.isValid() and nearest_graphics.getFieldDomainType() == domain_type:
            return nearest_graphics

        return None

    def get_nearest_graphics(self):
        return self._scene_picker.getNearestGraphics()

    def get_nearest_graphics_node(self, x, y):
        return self._get_nearest_graphic(x, y, Field.DOMAIN_TYPE_NODES)

    def get_nearest_graphics_point(self, x, y):
        """
        Assuming given x and y is in the sending widgets coordinates
        which is a parent of this widget.  For example the values given
        directly from the event in the parent widget.
        """
        return self._get_nearest_graphic(x, y, Field.DOMAIN_TYPE_POINT)

    def get_nearest_element_graphics(self, x, y):
        self._scene_picker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT,
                                                   x - self._selection_tolerance, y - self._selection_tolerance,
                                                   x + self._selection_tolerance, y + self._selection_tolerance)
        return self._scene_picker.getNearestElementGraphics()

    def get_nearest_element(self, x, y):
        self._scene_picker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT,
                                                   x - self._selection_tolerance, y - self._selection_tolerance,
                                                   x + self._selection_tolerance, y + self._selection_tolerance)
        return self._scene_picker.getNearestElement()

    def get_nearest_graphics_mesh_3d(self, x, y):
        return self._get_nearest_graphic(x, y, Field.DOMAIN_TYPE_MESH3D)

    def get_nearest_graphics_mesh_2d(self, x, y):
        return self._get_nearest_graphic(x, y, Field.DOMAIN_TYPE_MESH2D)

    def get_nearest_node(self, x, y):
        self._scene_picker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT,
                                                   x - self._selection_tolerance, y - self._selection_tolerance,
                                                   x + self._selection_tolerance, y + self._selection_tolerance)
        node = self._scene_picker.getNearestNode()

        return node

    def add_picked_nodes_to_field_group(self, selection_group):
        self._scene_picker.addPickedNodesToFieldGroup(selection_group)

    def view_all(self):
        """
        Helper method to set the current scene viewer to view everything
        visible in the current scene.
        """
        self._sceneviewer.viewAll()

    # paintGL start
    def paintGL(self):
        """
        Render the scene for this scene viewer.  The QGLWidget has already set up the
        correct OpenGL buffer for us so all we need do is render into it.  The scene viewer
        will clear the background so any OpenGL drawing of your own needs to go after this
        API call.
        """
        self._sceneviewer.renderScene()
        # paintGL end

    def _zinc_sceneviewer_event(self, event):
        """
        Process a scene viewer event.  The update() method is called for a
        repaint required event all other events are ignored.
        """
        if event.getChangeFlags() & Sceneviewerevent.CHANGE_FLAG_REPAINT_REQUIRED:
            QtCore.QTimer.singleShot(0, self.update)

    #  Not applicable at the current point in time.
    #     def _zincSelectionEvent(self, event):
    #         print(event.getChangeFlags())
    #         print('go the selection change')

    def resizeGL(self, width, height):
        """
        Respond to widget resize events.
        """
        self._sceneviewer.setViewportSize(width * self._pixel_scale, height * self._pixel_scale)

    def keyPressEvent(self, event):
        self.key_press_event(event)

    def keyReleaseEvent(self, event):
        self.key_release_event(event)

    def enterEvent(self, event):
        self.mouse_enter_event(event)

    def leaveEvent(self, event):
        self.mouse_leave_event(event)

    def mousePressEvent(self, event):
        self.mouse_press_event(event)

    def mouseMoveEvent(self, event):
        self.mouse_move_event(event)

    def mouseReleaseEvent(self, event):
        self.mouse_release_event(event)
