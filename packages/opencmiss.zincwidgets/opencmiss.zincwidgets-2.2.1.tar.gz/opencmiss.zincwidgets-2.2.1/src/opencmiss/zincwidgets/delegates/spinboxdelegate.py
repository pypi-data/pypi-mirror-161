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
from PySide2 import QtCore, QtWidgets


class SpinBoxDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None):
        super(SpinBoxDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QSpinBox(parent)
        editor.setFrame(False)
        editor.setMinimum(3)
        editor.setMaximum(9999)
        editor.setValue(9)

        return editor

    def setEditorData(self, editor, index):
        data = index.model().data(index, QtCore.Qt.EditRole)
        if data is not None:
            value = int(index.model().data(index, QtCore.Qt.EditRole))
            editor.setValue(value)

    def setModelData(self, editor, model, index):
        value = editor.value()
        model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
