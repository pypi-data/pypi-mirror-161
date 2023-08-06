
from PySide2 import QtCore, QtWidgets

from opencmiss.zincwidgets.sceneviewerwidget import SceneviewerWidget


class ViewWidget(QtWidgets.QWidget):
    """
    A widget that holds sceneviewers in a specific layout.
    """

    graphicsReady = QtCore.Signal()
    currentChanged = QtCore.Signal()

    def __init__(self, scenes, grid_description=None, parent=None):
        """
        Create a view widget with a list of scenes and associated grid description.

        :param scenes: A list of scenes.
        :param grid_description: A dictionary describing the grid layout of the widgets. (Not currently used.)
        :param parent: Parent widget
        """
        super(ViewWidget, self).__init__(parent)
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        self._sceneviewers = []
        self._ready_state = []
        self._initial_state = []
        self._active_sceneviewer = None

        for index, scene in enumerate(scenes):
            s = SceneviewerWidget(self)
            s.graphicsInitialized.connect(self._graphics_initialised)
            s.becameActive.connect(self._active_view_changed)
            self._sceneviewers.append(s)
            self._ready_state.append(False)
            s.setFocusPolicy(QtCore.Qt.StrongFocus)
            row = scene.get("Row", 0)
            col = scene.get("Col", 0)
            self._initial_state.append(scene.get("Sceneviewer", {}))
            layout.addWidget(s, row, col)

    def _active_view_changed(self):
        self._active_sceneviewer = self.sender()
        layout = self.layout()
        rows = layout.rowCount()
        columns = layout.columnCount()
        for r in range(rows):
            for c in range(columns):
                sceneviewer_widget = layout.itemAtPosition(r, c).widget()
                sceneviewer_widget.setActiveState(sceneviewer_widget == self.sender())

        self.currentChanged.emit()

    def _graphics_initialised(self):
        index = self._sceneviewers.index(self.sender())
        self._initial_state[index].applyParameters(self.sender().getSceneviewer())
        if self._active_sceneviewer is None:
            self._active_view_changed()
        self._ready_state[index] = True
        if all(self._ready_state):
            self.graphicsReady.emit()

    def getSceneviewer(self, row, col):
        """
        Get the sceneviewer from the view widget layout at position defined by the row and column.

        :param row: The row index of the sceneviewer.
        :param col: The column index of the sceneviewer.
        :return: opencmiss.zinc.sceneviewer.Sceneviewer
        """
        layout = self.layout()
        sceneviewer_widget = layout.itemAtPosition(row, col).widget()
        return sceneviewer_widget.getSceneviewer()

    def getActiveSceneviewer(self):
        """
        Get the currently active sceneviewer.  Returns None if there is no currently
        active sceneviewer.

        :return: opencmiss.zinc.sceneviewer.Sceneviewer
        """
        if self._active_sceneviewer is not None:
            return self._active_sceneviewer.getSceneviewer()

        return None

    def setContext(self, context):
        """
        Set the context for all sceneviewers in the view widget.

        :param context: opencmiss.zinc.context.Context.
        """
        for sceneviewer in self._sceneviewers:
            sceneviewer.setContext(context)
