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
import re

from PySide2 import QtWidgets

from opencmiss.zincwidgets.fields.lists import FIELD_TYPES, INTERNAL_FIELD_NAMES, INTERNAL_FIELD_TYPE_NAME, NONE_FIELD_TYPE_NAME


def convert_field_type_to_display_name(name):
    if name == INTERNAL_FIELD_TYPE_NAME or name == NONE_FIELD_TYPE_NAME:
        return name

    return re.sub(r"([A-Z])", r" \1", name[5:])


def convert_display_name_to_field_name(name):
    return f"Field{name.replace(' ', '')}"


class FieldTypeChooserWidget(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        QtWidgets.QComboBox.__init__(self, parent)
        self._null_object_name = "-"
        self._currentFieldType = None
        self._build_field_type_list()

    def _build_field_type_list(self):
        """
        Rebuilds the list of items in the ComboBox from the field module
        """
        self.blockSignals(True)
        self.clear()
        if self._null_object_name:
            self.addItem(self._null_object_name)

        self.addItems([convert_field_type_to_display_name(f) for f in FIELD_TYPES])
        self.blockSignals(False)

    def _display_field_type(self):
        """
        Display the currently chosen field type in the ComboBox
        """
        self.blockSignals(True)
        if self._currentFieldType:
            index = self.findText(self._currentFieldType)
        else:
            index = 0
        self.setCurrentIndex(index)
        self.blockSignals(False)

    def setNullObjectName(self, null_object_name):
        """
        Enable a null object option with the supplied name e.g. '-' or '<select>'
        Default is None
        """
        self._null_object_name = null_object_name
        self._build_field_type_list()

    def getFieldType(self):
        """
        Must call this from currentIndexChanged() slot to get/update current material
        """
        field_type_name = self.currentText()
        if self._null_object_name and (field_type_name == self._null_object_name):
            field_type_name = None
        return convert_display_name_to_field_name(field_type_name)

    def setFieldType(self, field_type):
        """
        Set the currently selected field; call after setConditional
        """
        if not field_type:
            self._currentFieldType = None
        else:
            self._currentFieldType = convert_field_type_to_display_name(field_type)
        self._display_field_type()
