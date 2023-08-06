from PySide2 import QtCore

from opencmiss.zinc.sceneviewerinput import Sceneviewerinput

SELECTION_GROUP_NAME = 'cmiss_selection'
SELECTION_RUBBERBAND_NAME = 'selection_rubberband'

# mapping from qt to zinc start
# Create a button map of Qt mouse buttons to Zinc input buttons
BUTTON_MAP = {
    QtCore.Qt.LeftButton: Sceneviewerinput.BUTTON_TYPE_LEFT,
    QtCore.Qt.MidButton: Sceneviewerinput.BUTTON_TYPE_MIDDLE,
    QtCore.Qt.RightButton: Sceneviewerinput.BUTTON_TYPE_RIGHT,
    QtCore.Qt.NoButton: None}


# Create a modifier map of Qt modifier keys to Zinc modifier keys
def modifier_map(qt_modifiers):
    """
    Return a Zinc Sceneviewerinput modifiers object that is created from
    the Qt modifier flags passed in.
    """
    modifiers = Sceneviewerinput.MODIFIER_FLAG_NONE

    if qt_modifiers & QtCore.Qt.SHIFT:
        modifiers = modifiers | Sceneviewerinput.MODIFIER_FLAG_SHIFT

    return modifiers


class ProjectionMode(object):
    PARALLEL = 0
    PERSPECTIVE = 1


class SelectionMode(object):
    NONE = -1
    EXCLUSIVE = 0
    ADDITIVE = 1


class GraphicsSelectionMode(object):
    ANY = -1
    DATA = 0
    ELEMENTS = 1
    NODE = 2
