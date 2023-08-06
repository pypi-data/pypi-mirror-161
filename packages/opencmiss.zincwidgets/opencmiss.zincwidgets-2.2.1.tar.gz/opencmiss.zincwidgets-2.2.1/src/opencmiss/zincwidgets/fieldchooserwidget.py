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

from opencmiss.zinc.field import Field


class FieldChooserWidget(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        """
        Call the super class init functions
        """
        QtWidgets.QComboBox.__init__(self, parent)
        self._nullObjectName = None
        self._region = None
        self._conditional = None
        self._field = None
        self._allowUnmanagedField = False
        self._fieldmodulenotifier = None
        self._listen_for_field_notifications = True

    def __del__(self):
        if self._fieldmodulenotifier is not None:
            self._fieldmodulenotifier.clearCallback()

    def _fieldmodule_callback(self, fieldmoduleevent):
        """
        Callback for change in fields; may need to rebuild field list
        """
        changeSummary = fieldmoduleevent.getSummaryFieldChangeFlags()
        # print "_fieldmodule_callback changeSummary =", changeSummary
        if ((0 != (changeSummary & (Field.CHANGE_FLAG_IDENTIFIER | Field.CHANGE_FLAG_ADD | Field.CHANGE_FLAG_REMOVE))) or
                ((self._conditional != None) and (0 != (changeSummary & Field.CHANGE_FLAG_DEFINITION)))):
            self._build_field_list()

    def _build_field_list(self):
        """
        Rebuilds the list of items in the ComboBox from the field module
        """
        self.blockSignals(True)
        self.clear()
        if self._region and self._region.isValid():
            if self._nullObjectName:
                self.addItem(self._nullObjectName)
            fielditer = self._region.getFieldmodule().createFielditerator()
            field = fielditer.next()
            while field.isValid():
                name = field.getName()
                if (self._allowUnmanagedField or field.isManaged()) and ((self._conditional is None) or self._conditional(field)):
                    self.addItem(name)
                field = fielditer.next()
        self.blockSignals(False)
        self._displayField()

    def _displayField(self):
        """
        Display the currently chosen field in the ComboBox
        """
        self.blockSignals(True)
        if self._field:
            fieldName = self._field.getName()
            # following doesn't handle field name matching _nullObjectName
            index = self.findText(fieldName)
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

    def getRegion(self):
        return self._region

    def set_listen_for_field_notifications(self, state):
        self._listen_for_field_notifications = state
        if not state:
            self.clear_callback()

    def listen_for_field_notifications(self):
        return self._listen_for_field_notifications

    def clear_callback(self):
        if self._fieldmodulenotifier is not None:
            self._fieldmodulenotifier.clearCallback()
            self._fieldmodulenotifier = None

    def setRegion(self, region):
        """
        Sets the region that this widget chooses fields from
        """
        if region and region.isValid():
            self._region = region
        else:
            self._region = None
        self._field = None
        self._build_field_list()
        if region and self._listen_for_field_notifications:
            self._fieldmodulenotifier = region.getFieldmodule().createFieldmodulenotifier()
            self._fieldmodulenotifier.setCallback(self._fieldmodule_callback)
        else:
            self._fieldmodulenotifier = None

    def setConditional(self, conditional):
        """
        Set a callable which takes a field and returns true if field should be included
        Call before setting the current field
        """
        self._conditional = conditional
        self._build_field_list()

    def getField(self):
        """
        Must call this from currentIndexChanged() slot to get/update current field
        """
        fieldName = self.currentText()
        if self._nullObjectName and (fieldName == self._nullObjectName):
            self._field = None
        else:
            self._field = self._region.getFieldmodule().findFieldByName(fieldName)
        return self._field

    def allowUnmanagedField(self, flag):
        self._allowUnmanagedField = flag

    def setField(self, field):
        """
        Set the currently selected field; call after setConditional
        """
        if not field or not field.isValid():
            self._field = None
        elif not self._allowUnmanagedField and not field.isManaged():
            print("Field chooser cannot set unmanaged field")
            self._field = None
        elif self._conditional and not self._conditional(field):
            print("Field chooser cannot set field not satisfying conditional function")
            self._field = None
        else:
            self._field = field
        self._displayField()
