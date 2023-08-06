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
import json
import os.path

from PySide2 import QtCore, QtWidgets

from opencmiss.zincwidgets.ui.ui_snapshotdialog import Ui_SnapshotDialog


class SnapshotDialog(QtWidgets.QDialog):

    sceneviewerInitialized = QtCore.Signal()

    def __init__(self, parent, shared_gl_context):
        super(SnapshotDialog, self).__init__(parent)

        self._ui = Ui_SnapshotDialog()
        self._ui.setupUi(self, shared_gl_context)

        self._location = None
        self._filename = None

        self._makeConnections()

    def _makeConnections(self):
        self._ui.pushButtonFilename.clicked.connect(self._filenamePushButtonClicked)
        self._ui.checkBoxWYSIWYG.stateChanged.connect(self._wysiwygStateChanged)
        self._ui.widgetPreview.graphicsInitialized.connect(self.sceneviewerInitialized)

    def _filenamePushButtonClicked(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, caption='Choose file ...', dir=self._location, filter="Image Format (*.png, *.jpeg);;All (*.*)")
        if filename:
            self._location = os.path.dirname(filename)
            self._ui.lineEditFilename.setText(filename)

    def _wysiwygStateChanged(self, state):
        self._ui.spinBoxHeight.setEnabled(not state)
        self._ui.spinBoxWidth.setEnabled(not state)

    def setLocation(self, location):
        self._location = location

    def getLocation(self):
        return self._location

    def setFilename(self, filename):
        self._ui.lineEditFilename.setText(filename)

    def getFilename(self):
        return self._ui.lineEditFilename.text()

    def getWYSIWYG(self):
        return self._ui.checkBoxWYSIWYG.isChecked()

    def getHeight(self):
        return self._ui.spinBoxHeight.value()

    def getWidth(self):
        return self._ui.spinBoxWidth.value()

    def setZincContext(self, zincContext):
        self._ui.widgetPreview.setContext(zincContext)

    def setScene(self, scene):
        self._ui.widgetPreview.getSceneviewer().setScene(scene)

    def serialize(self):
        state = {}
        state['filename'] = self.getFilename()
        state['wysiwyg'] = self.getWYSIWYG()
        state['location'] = self.getLocation()
        state['width'] = self.getWidth()
        state['height'] = self.getHeight()
        return json.dumps(state)

    def deserialize(self, state):
        try:
            d = json.loads(state)
            self.setFilename(d['filename'])
            self._ui.checkBoxWYSIWYG.setChecked(d['wysiwyg'])
            self.setLocation(d['location'])
            self._ui.spinBoxHeight.setValue(d['height'])
            self._ui.spinBoxWidth.setValue(d['width'])
        except Exception:
            pass
