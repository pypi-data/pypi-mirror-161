
from PySide2 import QtCore, QtWidgets

from opencmiss.zincwidgets.sceneviewerwidget import SceneviewerWidget


def create_view(zinc_context, scenes, specification=None):
    widget = QtWidgets.QWidget()
    layout = QtWidgets.QGridLayout()
    widget.setLayout(layout)

    for scene in scenes:
        s = SceneviewerWidget(widget)
        s.setContext(zinc_context)
        s.setFocusPolicy(QtCore.Qt.StrongFocus)
        row = scene.get("Row", 0)
        col = scene.get("Col", 0)
        layout.addWidget(s, row, col)

    return widget
