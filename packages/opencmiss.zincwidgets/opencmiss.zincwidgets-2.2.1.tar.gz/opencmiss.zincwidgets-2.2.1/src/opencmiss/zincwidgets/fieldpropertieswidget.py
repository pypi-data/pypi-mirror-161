from PySide2 import QtWidgets, QtCore

from opencmiss.zincwidgets.fields.lists import FIELDS_REQUIRING_X_REAL_SOURCE_FIELDS
from opencmiss.zincwidgets.fieldtypechooserwidget import convert_field_type_to_display_name


class FieldPropertiesWidget(QtWidgets.QWidget):

    requirementChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super(FieldPropertiesWidget, self).__init__(parent)
        self._field = None
        self._vertical_layout = QtWidgets.QVBoxLayout(self)
        self._vertical_layout.setContentsMargins(0, 0, 0, 0)

    def set_field(self, field):
        self._clear_ui()
        self._field = field
        if self._field.field_is_known():
            self._setup_ui()

    def _clear_ui(self):
        for i in reversed(range(self._vertical_layout.count())):
            widget_to_remove = self._vertical_layout.itemAt(i).widget()
            # remove it from the layout list
            self._vertical_layout.removeWidget(widget_to_remove)
            # remove it from the GUI
            widget_to_remove.setParent(None)

    def clear_field(self):
        self._field = None
        self._clear_ui()

    def _setup_ui(self):
        # Every field has a title and global properties.
        self._setup_title()
        self._setup_general_properties()
        # Setup field specific widgets.
        requirement_offset = 0
        for prop in self._field.properties():
            requirement_offset += self._setup_property(prop, requirement_offset)

    def _setup_title(self):
        self._title_groupbox = QtWidgets.QGroupBox(self)
        self._title_groupbox.setTitle(u"Field type")
        self._title_layout = QtWidgets.QVBoxLayout(self._title_groupbox)
        self._title_label = QtWidgets.QLabel(convert_field_type_to_display_name(self._field.field_display_label()))
        self._title_layout.addWidget(self._title_label)
        self._vertical_layout.addWidget(self._title_groupbox)

    def _setup_general_properties(self):
        is_managed = self._field.is_managed()
        is_type_coordinate = self._field.is_type_coordinate()

        self._properties_groupbox = QtWidgets.QGroupBox(self)
        self._properties_groupbox.setTitle(u"Properties")
        self._properties_layout = QtWidgets.QVBoxLayout(self._properties_groupbox)
        self._type_coordinate_checkbox = QtWidgets.QCheckBox(self._properties_groupbox)
        self._type_coordinate_checkbox.setCheckState(QtCore.Qt.Checked if is_type_coordinate else QtCore.Qt.Unchecked)
        self._type_coordinate_checkbox.stateChanged.connect(self._type_coordinate_clicked)
        self._type_coordinate_checkbox.setText(u"Is Coordinate")
        self._managed_checkbox = QtWidgets.QCheckBox(self._properties_groupbox)
        self._managed_checkbox.setEnabled(not self._field.defining_field())
        self._managed_checkbox.setCheckState(QtCore.Qt.Checked if is_managed else QtCore.Qt.Unchecked)
        self._managed_checkbox.stateChanged.connect(self._managed_clicked)
        self._managed_checkbox.setText(u"Managed")

        self._properties_layout.addWidget(self._managed_checkbox)
        self._properties_layout.addWidget(self._type_coordinate_checkbox)

        self._vertical_layout.addWidget(self._properties_groupbox)

    def _managed_clicked(self, state):
        self._field.set_managed(state == QtCore.Qt.Checked)

    def _type_coordinate_clicked(self, state):
        self._field.set_type_coordinate(state == QtCore.Qt.Checked)

    def _setup_property(self, prop, offset):
        if len(prop["requirements"]) > 0:
            groupbox = QtWidgets.QGroupBox(self)
            groupbox.setTitle(prop["group"])
            groupbox.setObjectName(f'{prop["group"].lower()}_group_box')
            layout = QtWidgets.QVBoxLayout(groupbox)
            for index, req in enumerate(prop["requirements"]):
                self._setup_requirement(layout, req)
                self._field.populate_requirement(index + offset, req)

            self._vertical_layout.addWidget(groupbox)

        return len(prop["requirements"])

    def _setup_requirement(self, layout, req):
        req.set_callback(self._requirement_changed)
        widget = req.widget()
        if widget is not None:
            layout.addWidget(widget)

    def _reload(self):
        self._field.set_required_source_fields()

        widget_index = -1
        for i in range(self._vertical_layout.count()):
            item = self._vertical_layout.itemAt(i)
            if item.widget().objectName() == "parameters_group_box":
                widget_index = i

        for prop in self._field.properties():
            if prop["group"] == "Parameters":
                groupbox = QtWidgets.QGroupBox(self)
                groupbox.setObjectName("parameters_group_box")
                groupbox.setTitle(prop["group"])
                layout = QtWidgets.QVBoxLayout(groupbox)
                for index, req in enumerate(prop["requirements"]):
                    self._setup_requirement(layout, req)

                if widget_index == -1:
                    last = self._vertical_layout.count()
                    self._vertical_layout.insertWidget(last - 1, groupbox)
                else:
                    widget_to_remove = self._vertical_layout.takeAt(widget_index).widget()
                    widget_to_remove.setParent(None)
                    self._vertical_layout.insertWidget(widget_index, groupbox)

    def _requirement_changed(self, event=None):
        if self._field.get_field_type() in FIELDS_REQUIRING_X_REAL_SOURCE_FIELDS:
            if self._field.has_additional_requirements_met():
                if event == "textChanged":
                    self._reload()

        self.requirementChanged.emit()
