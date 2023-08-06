"""
   Copyright 2016 University of Auckland

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

from opencmiss.argon.argonlogger import ArgonLogger
from opencmiss.zinc.field import Field

from opencmiss.zincwidgets.fields import FieldInterface
from opencmiss.zincwidgets.ui.ui_fieldeditorwidget import Ui_FieldEditorWidget


class FieldEditorWidget(QtWidgets.QWidget):
    fieldCreated = QtCore.Signal(Field, str)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self._field = None
        self._field_module = None
        self._ui = Ui_FieldEditorWidget()
        self._ui.setupUi(self)
        self._field_interface = FieldInterface(None, None)
        self._timekeeper = None
        self._update_field_properties()
        self._update_ui()
        self._make_connections()

    def _make_connections(self):
        self._ui.create_button.clicked.connect(self._create_field_clicked)
        self._ui.field_properties_widget.requirementChanged.connect(self._update_ui)
        self._ui.name_lineedit.textChanged.connect(self._update_ui)

    def _create_field_clicked(self):
        defined_field = self._field_interface.define_new_field(self._field_module, self._ui.name_lineedit.text())
        if defined_field and defined_field.isValid():
            self.fieldCreated.emit(defined_field, self._field_interface.get_field_type())
        else:
            ArgonLogger.getLogger().error("Failed to create field due to invalid field definition.")

    def _update_ui(self):
        if self._field_interface.defining_field():
            self._ui.create_groupbox.show()
            enable_create_button = len(self._ui.name_lineedit.text()) > 0 and self._field_interface.can_define_field()
            self._ui.create_button.setEnabled(enable_create_button)
        else:
            self._ui.create_groupbox.hide()

    def _update_field_properties(self):
        self._ui.field_properties_widget.set_field(self._field_interface)

    def set_timekeeper(self, timekeeper):
        """
        Set when timekeeper changes.
        :param timekeeper: The timekeeper to set.
        """
        self._timekeeper = timekeeper

    def set_field_module(self, field_module):
        """
        Set the current field module. Resets all field widgets.
        :param field_module: The field module to set.
        """
        self._field_module = field_module
        self._set_field_interface(None, None)
        self._update_field_properties()

    def set_field_and_type(self, field, field_type):
        """
        Set the field and field type of the field to be edited.
        :param field: The field to be edited.
        :param field_type: The type of field to be edited.
        """
        self._set_field_interface(field, field_type)
        self._update_field_properties()
        self._update_ui()

    def define_new_field(self, field_type):
        """
        Set up the editor to define a new field of type field_type.
        :param field_type: The type of field to define.
        """
        self._set_field_interface(None, field_type, set_managed=True)
        self._ui.name_lineedit.setText(self._get_temp_field_name())
        self._update_field_properties()
        self._update_ui()

    def _set_field_interface(self, field, field_type, set_managed=False):
        field_interface = FieldInterface(field, field_type)
        field_interface.set_region(self._field_module.getRegion())
        field_interface.set_timekeeper(self._timekeeper)
        if set_managed:
            field_interface.set_managed(True)

        self._field_interface = field_interface

    def _get_temp_field_name(self):
        index = 1
        prospective_name = f"field{index}"
        if self._field_module and self._field_module.isValid():
            field = self._field_module.findFieldByName(prospective_name)
            while field and field.isValid():
                index += 1
                prospective_name = f"field{index}"
                field = self._field_module.findFieldByName(prospective_name)

        return prospective_name
