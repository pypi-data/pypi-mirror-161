'''
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
'''
from PySide2 import QtWidgets

from opencmiss.zincwidgets.ui.ui_scenelayoutchooserdialog import Ui_SceneLayoutChooserDialog


class SceneLayoutChooserDialog(QtWidgets.QDialog):

    def __init__(self, parent):
        super(SceneLayoutChooserDialog, self).__init__(parent)

        self._ui = Ui_SceneLayoutChooserDialog()
        self._ui.setupUi(self)

    def selected_layout(self):
        layout = None

        if self._ui.radioButtonLayout1.isChecked():
            layout = self._ui.radioButtonLayout1.objectName()
        elif self._ui.radioButtonLayout2x2Grid.isChecked():
            layout = self._ui.radioButtonLayout2x2Grid.objectName()

        return layout.replace("radioButton", "")
