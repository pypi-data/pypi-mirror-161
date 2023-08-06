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
from PySide2 import QtWidgets


class BaseView(QtWidgets.QWidget):

    def __init__(self, parent):
        super(BaseView, self).__init__(parent)
        self._name = 'Base View'
        self._dock_widgets = []

    def getName(self):
        return self._name

    def setZincContext(self, zincContext):
        raise NotImplementedError()

    def getDependentEditors(self):
        return self._dock_widgets

    def registerDependentEditor(self, editor):
        """
        Add the given editor to the list of dependent editors for
        this view.
        """
        self._dock_widgets.append(editor)

    def serialize(self):
        return ''

    def deserialize(self, string):
        pass
