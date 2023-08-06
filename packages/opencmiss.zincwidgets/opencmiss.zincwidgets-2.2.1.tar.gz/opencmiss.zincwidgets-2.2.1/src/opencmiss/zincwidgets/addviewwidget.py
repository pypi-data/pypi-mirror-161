
from PySide2 import QtCore, QtWidgets

from opencmiss.zincwidgets.ui.ui_addviewwidget import Ui_AddView


class AddView(QtWidgets.QWidget):

    clicked = QtCore.Signal()

    def __init__(self, parent=None):
        super(AddView, self).__init__(parent)
        self._ui = Ui_AddView()
        self._ui.setupUi(self)
        self._ui.pushButton.clicked.connect(self.clicked)
