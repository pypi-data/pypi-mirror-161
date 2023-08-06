import sys
from PySide2 import QtCore, QtWidgets


class EditableTabBar(QtWidgets.QTabBar):

    tabTextEdited = QtCore.Signal(int, str)

    def __init__(self, parent):
        super().__init__(parent)
        self._editable = True
        self._editor = QtWidgets.QLineEdit(self)
        self._editor.setWindowFlags(QtCore.Qt.Popup)
        self._editor.setFocusProxy(self)
        self._editor.installEventFilter(self)
        self.setStyleSheet("alignment: left;")
        self._make_connections()

    def _make_connections(self):
        self._editor.editingFinished.connect(self._handleEditingFinished)

    def set_editable(self, state):
        self._editable = state

    def is_editable(self):
        return self._editable

    def eventFilter(self, widget, event):
        if ((event.type() == QtCore.QEvent.MouseButtonPress and
             not self._editor.geometry().contains(event.globalPos())) or
            (event.type() == QtCore.QEvent.KeyPress and
             event.key() == QtCore.Qt.Key_Escape)):
            self._editor.hide()
            return True
        return super().eventFilter(widget, event)

    def mouseDoubleClickEvent(self, event):
        if self._editable:
            index = self.tabAt(event.pos())
            if index >= 0:
                self.editTab(index)

    def editTab(self, index):
        rect = self.tabRect(index)
        self._editor.setFixedSize(rect.size())
        self._editor.move(self.mapToGlobal(rect.topLeft()))
        self._editor.setText(self.tabText(index))
        if not self._editor.isVisible():
            self._editor.show()

    def _handleEditingFinished(self):
        index = self.currentIndex()
        if index >= 0:
            self._editor.hide()
            text = self._editor.text()
            self.setTabText(index, text)
            self.tabTextEdited.emit(index, text)
