"""
   Copyright 2017 University of Auckland

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

from opencmiss.zinc.tessellation import Tessellation


class TessellationChooserWidget(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        """
        Call the super class init functions
        """
        QtWidgets.QComboBox.__init__(self, parent)
        self._nullObjectName = None
        self._tessellationmodule = None
        self._tessellationmodulenotifier = None
        self._tessellation = None

    def _tessellationmoduleCallback(self, tessellationmoduleevent):
        """
        Callback for change in tessellations; may need to rebuild tessellation list
        """
        changeSummary = tessellationmoduleevent.getSummaryTessellationChangeFlags()
        #print("_tessellationmoduleCallback changeSummary " + str(changeSummary))
        # Can't do this as may be received after new tessellation module is set!
        # if changeSummary == Tessellation.CHANGE_FLAG_FINAL:
        #    self.setTessellationmodule(None)
        if 0 != (changeSummary & (Tessellation.CHANGE_FLAG_IDENTIFIER | Tessellation.CHANGE_FLAG_ADD | Tessellation.CHANGE_FLAG_REMOVE)):
            self._buildTessellationList()

    def _buildTessellationList(self):
        """
        Rebuilds the list of items in the ComboBox from the tessellation module
        """
        self.blockSignals(True)
        self.clear()
        if self._tessellationmodule:
            if self._nullObjectName:
                self.addItem(self._nullObjectName)
            tessellationiter = self._tessellationmodule.createTessellationiterator()
            tessellation = tessellationiter.next()
            while tessellation.isValid():
                name = tessellation.getName()
                self.addItem(name)
                tessellation = tessellationiter.next()
        self.blockSignals(False)
        self._displayTessellation()

    def _displayTessellation(self):
        """
        Display the currently chosen tessellation in the ComboBox
        """
        self.blockSignals(True)
        if self._tessellation:
            tessellationName = self._tessellation.getName()
            # following doesn't handle tessellation name matching _nullObjectName
            index = self.findText(tessellationName)
        else:
            index = 0
        self.setCurrentIndex(index)
        self.blockSignals(False)

    def setNullObjectName(self, nullObjectName):
        """
        Enable a null object option with the supplied name e.g. '-' or '<select>'
        Default is None
        """
        self._nullObjectName = nullObjectName

    def setTessellationmodule(self, tessellationmodule):
        """
        Sets the tessellation module that this widget chooses tessellations from
        """
        if tessellationmodule and tessellationmodule.isValid():
            self._tessellationmodule = tessellationmodule
            self._tessellationmodulenotifier = tessellationmodule.createTessellationmodulenotifier()
            self._tessellationmodulenotifier.setCallback(self._tessellationmoduleCallback)
        else:
            self._tessellationmodule = None
            self._tessellationmodulenotifier = None
        self._buildTessellationList()

    def getTessellation(self):
        """
        Must call this from currentIndexChanged() slot to get/update current tessellation
        """
        tessellationName = self.currentText()
        if self._nullObjectName and (tessellationName == self._nullObjectName):
            self._tessellation = None
        else:
            self._tessellation = self._tessellationmodule.findTessellationByName(tessellationName)
        return self._tessellation

    def setTessellation(self, tessellation):
        """
        Set the currently selected tessellation
        """
        if not tessellation or not tessellation.isValid():
            self._tessellation = None
        else:
            self._tessellation = tessellation
        self._displayTessellation()
