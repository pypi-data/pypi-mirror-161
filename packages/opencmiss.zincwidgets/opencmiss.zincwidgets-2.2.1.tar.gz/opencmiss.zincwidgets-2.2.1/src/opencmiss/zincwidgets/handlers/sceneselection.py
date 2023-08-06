from opencmiss.zinc.field import Field
from opencmiss.zinc.glyph import Glyph

from opencmiss.zinc.scenecoordinatesystem import SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT
from opencmiss.zinc.sceneviewerinput import Sceneviewerinput

from opencmiss.zincwidgets.definitions import BUTTON_MAP, GraphicsSelectionMode, SelectionMode, SELECTION_GROUP_NAME
from opencmiss.zincwidgets.handlers.keyactivatedhandler import KeyActivatedHandler


class SceneSelection(KeyActivatedHandler):

    def __init__(self, key_code):
        super(SceneSelection, self).__init__(key_code)
        self._start_position = None
        self._selection_box = None
        self._selection_box_description = [-1.0, -1.0, -1.0, -1.0]

        self._selection_mode = SelectionMode.NONE
        self._graphics_selection_mode = GraphicsSelectionMode.ANY
        self._selection_tolerance = 3.0

    def enter(self):
        self._selection_mode = SelectionMode.NONE

    def leave(self):
        pass

    def mouse_press_event(self, event):
        super(SceneSelection, self).mouse_press_event(event)
        if self._processing_mouse_events:
            self._start_position = (event.x(), event.y())
            if BUTTON_MAP[event.button()] == Sceneviewerinput.BUTTON_TYPE_LEFT:
                self._selection_mode = SelectionMode.EXCLUSIVE
            elif BUTTON_MAP[event.button()] == Sceneviewerinput.BUTTON_TYPE_RIGHT:
                self._selection_mode = SelectionMode.ADDITIVE
            else:
                self._selection_mode = SelectionMode.NONE

    def mouse_move_event(self, event):
        super(SceneSelection, self).mouse_move_event(event)
        if self._processing_mouse_events and self._selection_mode != SelectionMode.NONE:
            self._update_selection_box_description(event.x(), event.y())
            self._update_and_or_create_selection_box()

    def mouse_release_event(self, event):
        super(SceneSelection, self).mouse_release_event(event)
        if self._processing_mouse_events and self._selection_mode != SelectionMode.NONE:
            self._remove_selection_box()
            x = event.x()
            y = event.y()
            self._update_selection_box_description(x, y)
            # Construct a small frustum to look for nodes in.
            scene = self._zinc_sceneviewer.getScene()
            region = scene.getRegion()
            region.beginHierarchicalChange()

            scene_picker = self._scene_viewer.get_scenepicker()
            if (x != self._start_position[0]) or (y != self._start_position[1]):
                # box select
                left = min(x, self._start_position[0])
                right = max(x, self._start_position[0])
                bottom = min(y, self._start_position[1])
                top = max(y, self._start_position[1])
                scene_picker.setSceneviewerRectangle(self._zinc_sceneviewer,
                                                     SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT,
                                                     left, bottom, right, top)
                if self._selection_mode == SelectionMode.EXCLUSIVE:
                    self.clear_selection()

                selection_group = self._get_or_create_selection_group()
                if self._selecting_points():
                    scene_picker.addPickedNodesToFieldGroup(selection_group)
                if self._selecting_elements():
                    scene_picker.addPickedElementsToFieldGroup(selection_group)

            else:
                # point select - get nearest object only
                scene_picker.setSceneviewerRectangle(self._zinc_sceneviewer, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT,
                                                    x - self._selection_tolerance,
                                                    y - self._selection_tolerance,
                                                    x + self._selection_tolerance,
                                                    y + self._selection_tolerance)
                nearest_graphics = scene_picker.getNearestGraphics()
                if self._selection_mode == SelectionMode.EXCLUSIVE\
                        and not nearest_graphics.isValid():
                    self.clear_selection()

                if self._selecting_points() and \
                        (nearest_graphics.getFieldDomainType() == Field.DOMAIN_TYPE_NODES or
                         nearest_graphics.getFieldDomainType() == Field.DOMAIN_TYPE_DATAPOINTS):
                    node = scene_picker.getNearestNode()
                    if node.isValid():
                        node_set = node.getNodeset()
                        selection_group = self._get_or_create_selection_group()
                        nodegroup = selection_group.getFieldNodeGroup(node_set)
                        if not nodegroup.isValid():
                            nodegroup = selection_group.createFieldNodeGroup(node_set)
                        group = nodegroup.getNodesetGroup()
                        if self._selection_mode == SelectionMode.EXCLUSIVE:
                            remove_current = (group.getSize() == 1) and group.containsNode(node)
                            selection_group.clear()
                            if not remove_current:
                                # re-find node group lost by above clear()
                                nodegroup = selection_group.getFieldNodeGroup(node_set)
                                if not nodegroup.isValid():
                                    nodegroup = selection_group.createFieldNodeGroup(node_set)
                                group = nodegroup.getNodesetGroup()
                                group.addNode(node)
                        elif self._selection_mode == SelectionMode.ADDITIVE:
                            if group.containsNode(node):
                                group.removeNode(node)
                            else:
                                group.addNode(node)

                if self._selecting_elements() and \
                        (nearest_graphics.getFieldDomainType() in
                         [Field.DOMAIN_TYPE_MESH1D, Field.DOMAIN_TYPE_MESH2D,
                          Field.DOMAIN_TYPE_MESH3D, Field.DOMAIN_TYPE_MESH_HIGHEST_DIMENSION]):
                    elem = scene_picker.getNearestElement()
                    if elem.isValid():
                        mesh = elem.getMesh()
                        selection_group = self._get_or_create_selection_group()
                        element_group = selection_group.getFieldElementGroup(mesh)
                        if not element_group.isValid():
                            element_group = selection_group.createFieldElementGroup(mesh)
                        group = element_group.getMeshGroup()
                        if self._selection_mode == SelectionMode.EXCLUSIVE:
                            remove_current = (group.getSize() == 1) and group.containsElement(elem)
                            selection_group.clear()
                            if not remove_current:
                                # re-find element group lost by above clear()
                                element_group = selection_group.getFieldElementGroup(mesh)
                                if not element_group.isValid():
                                    element_group = selection_group.createFieldElementGroup(mesh)
                                group = element_group.getMeshGroup()
                                group.addElement(elem)
                        elif self._selection_mode == SelectionMode.ADDITIVE:
                            if group.containsElement(elem):
                                group.removeElement(elem)
                            else:
                                group.addElement(elem)

            region.endHierarchicalChange()
            self._selection_mode = SelectionMode.NONE

    def clear_selection(self):
        """
        If there is a selection group, clears it and removes it from scene.
        """
        selection_group = self.get_selection_group()
        if selection_group is not None:
            selection_group.clear()
            selection_group = Field()  # NULL
            scene = self._zinc_sceneviewer.getScene()
            scene.setSelectionField(selection_group)

    def get_selection_box_description(self):
        return self._selection_box_description

    def get_selection_group(self):
        """
        :return: Valid current selection group field or None.
        """
        scene = self._zinc_sceneviewer.getScene()
        selection_group = scene.getSelectionField()
        if selection_group.isValid():
            selection_group = selection_group.castGroup()
            if selection_group.isValid():
                return selection_group
        return None

    def set_graphics_selection_mode(self, mode):
        self._graphics_selection_mode = mode

    def get_graphics_selection_mode(self):
        return self._graphics_selection_mode

    def _get_or_create_selection_group(self):
        selection_group = self.get_selection_group()
        if selection_group is not None:
            return selection_group
        scene = self._zinc_sceneviewer.getScene()
        region = scene.getRegion()
        field_module = region.getFieldmodule()
        selection_group = field_module.findFieldByName(SELECTION_GROUP_NAME)
        if selection_group.isValid():
            selection_group = selection_group.castGroup()
            if selection_group.isValid():
                selection_group.setManaged(False)
        if not selection_group.isValid():
            field_module.beginChange()
            selection_group = field_module.createFieldGroup()
            selection_group.setName(SELECTION_GROUP_NAME)
            field_module.endChange()
        scene.setSelectionField(selection_group)
        return selection_group

    def _update_selection_box_description(self, x, y):
        x_diff = float(x - self._start_position[0])
        y_diff = float(y - self._start_position[1])
        if abs(x_diff) < 0.0001:
            x_diff = 1
        if abs(y_diff) < 0.0001:
            y_diff = 1
        x_off = float(self._start_position[0]) / x_diff + 0.5
        y_off = float(self._start_position[1]) / y_diff + 0.5
        self._selection_box_description = [x_diff, y_diff, x_off, y_off]

    def _update_and_or_create_selection_box(self):
        # Using a non-ideal workaround for creating a rubber band for selection.
        # This will create strange visual artifacts when using two scene viewers looking at
        # the same scene.  Waiting on a proper solution in the API.
        # Note if the standard glyphs haven't been defined then the
        # selection box will not be visible
        x_diff = self._selection_box_description[0]
        y_diff = self._selection_box_description[1]
        x_off = self._selection_box_description[2]
        y_off = self._selection_box_description[3]

        scene = self._zinc_sceneviewer.getScene()
        scene.beginChange()
        if self._selection_box is None:
            self._selection_box = scene.createGraphicsPoints()
            self._selection_box.setScenecoordinatesystem(SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT)
        attributes = self._selection_box.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_CUBE_WIREFRAME)
        attributes.setBaseSize([x_diff, y_diff, 0.999])
        attributes.setGlyphOffset([x_off, -y_off, 0])
        scene.endChange()

    def _remove_selection_box(self):
        if self._selection_box is not None:
            scene = self._selection_box.getScene()
            scene.removeGraphics(self._selection_box)
            self._selection_box = None

    def _selecting_any(self):
        return self._graphics_selection_mode == GraphicsSelectionMode.ANY

    def _selecting_elements(self):
        return self._graphics_selection_mode == GraphicsSelectionMode.ELEMENTS or\
               self._selecting_any()

    def _selecting_points(self):
        return self._graphics_selection_mode == GraphicsSelectionMode.DATA or\
               self._graphics_selection_mode == GraphicsSelectionMode.NODE or\
               self._selecting_any()