from copy import copy

from PySide2 import QtWidgets
from opencmiss.zinc.element import Element
from opencmiss.zinc.field import FieldFindMeshLocation, FieldEdgeDiscontinuity
from opencmiss.zinc.node import Node

from opencmiss.zincwidgets.fieldchooserwidget import FieldChooserWidget
from opencmiss.zincwidgets.fields.lists import MESH_NAMES, SEARCH_MODES, MEASURE_TYPES, FACE_TYPES, VALUE_TYPES, QUADRATURE_RULES
from opencmiss.zincwidgets.fields.parsers import display_as_vector, parse_to_vector, display_as_integer_vector, parse_to_integer_vector
from opencmiss.zincwidgets.regionchooserwidget import RegionChooserWidget


class FieldRequirementBase(object):

    def __init__(self):
        super().__init__()
        self._widget = QtWidgets.QFrame()
        self._callback = None
        self._finalised = False

    @staticmethod
    def fulfilled():
        return False

    def set_callback(self, callback):
        self._callback = callback

    def widget(self):
        return self._widget

    def set_finalised(self):
        self._finalised = True


class FieldRequirementNeverMet(FieldRequirementBase):
    pass


class FieldRequirementAlwaysMet(FieldRequirementBase):

    @staticmethod
    def fulfilled():
        return True


class FieldRequirementTimekeeper(FieldRequirementBase):

    def __init__(self, timekeeper):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self._widget)
        layout.setContentsMargins(0, 0, 0, 0)
        label_timekeeper = QtWidgets.QLabel("Timekeeper:")
        label_available = QtWidgets.QLabel("Available" if timekeeper and timekeeper.isValid() else "Not available")
        layout.addWidget(label_timekeeper)
        layout.addWidget(label_available)
        self._timekeeper = timekeeper

    def value(self):
        return self._timekeeper

    def set_value(self, value):
        self._timekeeper = value

    def fulfilled(self):
        return self._timekeeper and self._timekeeper.isValid()


class FieldRequirementComboBoxBase(FieldRequirementBase):

    def __init__(self, label, items):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self._widget)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QtWidgets.QLabel(label)
        self._combobox = QtWidgets.QComboBox(self._widget)
        self._combobox.addItems(items)
        layout.addWidget(label)
        layout.addWidget(self._combobox)

    def value(self):
        return self._combobox.currentIndex()

    def set_value(self, value):
        self._combobox.blockSignals(True)
        self._combobox.setCurrentIndex(value)
        self._combobox.blockSignals(False)

    def fulfilled(self):
        return True

    def set_finalised(self):
        self._combobox.setEnabled(False)


class FieldRequirementMeasure(FieldRequirementComboBoxBase):

    def __init__(self):
        super().__init__("Measure:", MEASURE_TYPES)

    def value(self):
        return self._combobox.currentIndex() + FieldEdgeDiscontinuity.MEASURE_C1

    def set_value(self, value):
        self._combobox.blockSignals(True)
        self._combobox.setCurrentIndex(value - FieldEdgeDiscontinuity.MEASURE_C1)
        self._combobox.blockSignals(False)


class FieldRequirementMesh(FieldRequirementComboBoxBase):

    def __init__(self, region, label=None, names=None):
        super().__init__("Mesh:" if label is None else label, MESH_NAMES if names is None else names)
        self._region = region

    def value(self):
        mesh_name = self._combobox.currentText()
        field_module = self._region.getFieldmodule()
        return field_module.findMeshByName(mesh_name)

    def set_value(self, value):
        mesh_name = value.getName()
        self._combobox.blockSignals(True)
        self._combobox.setCurrentText(mesh_name)
        self._combobox.blockSignals(False)


class FieldRequirementSearchMode(FieldRequirementComboBoxBase):

    def __init__(self):
        super().__init__("Search mode:", SEARCH_MODES)

    def value(self):
        return self._combobox.currentIndex() + FieldFindMeshLocation.SEARCH_MODE_EXACT

    def set_value(self, value):
        self._combobox.blockSignals(True)
        self._combobox.setCurrentIndex(value - FieldFindMeshLocation.SEARCH_MODE_EXACT)
        self._combobox.blockSignals(False)


class FieldRequirementFaceType(FieldRequirementComboBoxBase):

    def __init__(self):
        super().__init__("Face type:", FACE_TYPES)

    def value(self):
        return self._combobox.currentIndex() + Element.FACE_TYPE_ALL

    def set_value(self, value):
        self._combobox.blockSignals(True)
        self._combobox.setCurrentIndex(value - Element.FACE_TYPE_ALL)
        self._combobox.blockSignals(False)


class FieldRequirementQuadratureRule(FieldRequirementComboBoxBase):

    def __init__(self):
        super().__init__("Quadrature rule:", QUADRATURE_RULES)

    def value(self):
        return self._combobox.currentIndex() + Element.QUADRATURE_RULE_GAUSSIAN

    def set_value(self, value):
        self._combobox.blockSignals(True)
        self._combobox.setCurrentIndex(value - Element.QUADRATURE_RULE_GAUSSIAN)
        self._combobox.blockSignals(False)


class FieldRequirementValueType(FieldRequirementComboBoxBase):

    def __init__(self):
        super().__init__("Value type:", VALUE_TYPES)

    def value(self):
        return self._combobox.currentIndex() + Node.VALUE_LABEL_VALUE

    def set_value(self, value):
        self._combobox.blockSignals(True)
        self._combobox.setCurrentIndex(value - Node.VALUE_LABEL_VALUE)
        self._combobox.blockSignals(False)


class FieldRequirementMeshLike(FieldRequirementMesh):

    def __init__(self, region):
        search_mesh_names = copy(MESH_NAMES)
        field_module = region.getFieldmodule()
        field_iterator = field_module.createFielditerator()
        field = field_iterator.next()
        while field.isValid():
            if field.castElementGroup().isValid():
                search_mesh_names.append(field.getName())
            field = field_iterator.next()
        super().__init__(region, "Search mesh:", search_mesh_names)


class FieldRequirementRegion(FieldRequirementBase):

    def __init__(self, region, label):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self._widget)
        layout.setContentsMargins(0, 0, 0, 0)
        label_widget = QtWidgets.QLabel(label)
        self._region_chooser = RegionChooserWidget(self._widget)
        self._region_chooser.setRootRegion(region)
        layout.addWidget(label_widget)
        layout.addWidget(self._region_chooser)
        self._region_chooser.currentTextChanged.connect(self._region_changed)

    def _region_changed(self):
        self._callback(self._region_chooser.getRegion())

    def value(self):
        return self._region_chooser.getField()

    def set_value(self, value):
        self._region_chooser.blockSignals(True)
        self._region_chooser.setRegion(value)
        self._region_chooser.blockSignals(False)

    def fulfilled(self):
        return True

    def set_finalised(self):
        self._region_chooser.setEnabled(False)

    def region_chooser(self):
        return self._region_chooser


class FieldRequirementSourceFieldBase(FieldRequirementBase):

    def __init__(self, region, label, conditional_constraint):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self._widget)
        layout.setContentsMargins(0, 0, 0, 0)
        label_widget = QtWidgets.QLabel(label)
        self._source_field_chooser = FieldChooserWidget(self._widget)
        self._source_field_chooser.setObjectName("field_requirements_source_field_base_chooser")
        self._source_field_chooser.set_listen_for_field_notifications(False)
        self._source_field_chooser.allowUnmanagedField(True)
        self._source_field_chooser.setNullObjectName("-")
        self._source_field_chooser.setRegion(region)
        if conditional_constraint is not None:
            self._source_field_chooser.setConditional(conditional_constraint)
        layout.addWidget(label_widget)
        layout.addWidget(self._source_field_chooser)
        self._source_field_chooser.currentTextChanged.connect(self._field_changed)

    def _field_changed(self):
        self._callback("fieldChanged")

    def value(self):
        return self._source_field_chooser.getField()

    def set_value(self, value):
        self._source_field_chooser.blockSignals(True)
        self._source_field_chooser.setField(value)
        self._source_field_chooser.blockSignals(False)

    def fulfilled(self):
        region = self._source_field_chooser.getRegion()
        if region is None:
            return False

        field = self._source_field_chooser.getField()
        return True if field and field.isValid() else False

    def set_finalised(self):
        self._source_field_chooser.setEnabled(False)


class FieldRequirementSourceField(FieldRequirementSourceFieldBase):

    def __init__(self, region, label, conditional_constraint=None):
        super().__init__(region, label, conditional_constraint)


class FieldRequirementSourceFieldRegionDependent(FieldRequirementSourceFieldBase):

    def __init__(self, region, label, conditional_constraint):
        super().__init__(region, label, conditional_constraint)

    def set_region(self, region):
        self._source_field_chooser.setRegion(region)


class FieldRequirementSourceFieldRegionDependentFieldDependent(FieldRequirementSourceFieldRegionDependent):

    def __init__(self, region, dependent_requirement, label, conditional_constraint):
        super().__init__(region, label, conditional_constraint)
        self._dependent_requirement = dependent_requirement

    def fulfilled(self):
        field_valid = super().fulfilled()
        return field_valid and self._dependent_requirement.value().dependsOnField(self.value())


class FieldRequirementOptionalSourceField(FieldRequirementSourceFieldBase):

    def __init__(self, region, label, conditional_constraint=None):
        super().__init__(region, label, conditional_constraint)

    def fulfilled(self):
        return True


class FieldRequirementLineEditBase(FieldRequirementBase):

    def __init__(self, label):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self._widget)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QtWidgets.QLabel(label)
        self._line_edit = QtWidgets.QLineEdit(self._widget)
        layout.addWidget(label)
        layout.addWidget(self._line_edit)
        self._line_edit.textEdited.connect(self._text_changed)

    def _text_changed(self):
        self._callback('textChanged')

    def set_finalised(self):
        self._line_edit.setEnabled(False)


class FieldRequirementStringValue(FieldRequirementLineEditBase):

    def __init__(self):
        super().__init__("String:")

    def value(self):
        return self._line_edit.text()

    def set_value(self, value):
        self._line_edit.blockSignals(True)
        self._line_edit.setText(value)
        self._line_edit.blockSignals(False)

    def fulfilled(self):
        return len(self.value()) > 0


class FieldRequirementSpinBoxBase(FieldRequirementBase):

    def __init__(self, label, minimum):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self._widget)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QtWidgets.QLabel(label)
        self._spin_box = QtWidgets.QSpinBox()
        self._spin_box.setMinimum(minimum)
        layout.addWidget(label)
        layout.addWidget(self._spin_box)
        self._spin_box.textChanged.connect(self._text_changed)

    def _text_changed(self):
        self._callback('textChanged')

    def set_finalised(self):
        self._spin_box.setEnabled(False)


class FieldRequirementNaturalNumberValue(FieldRequirementSpinBoxBase):

    def __init__(self, label):
        super().__init__(label, 1)

    def value(self):
        return self._spin_box.value()

    def set_value(self, value):
        self._spin_box.blockSignals(True)
        self._spin_box.setValue(value)
        self._spin_box.blockSignals(False)

    def fulfilled(self):
        value = self.value()
        return False if value is None else value > 0


class FieldRequirementNumberOfComponents(FieldRequirementNaturalNumberValue):

    def __init__(self):
        super(FieldRequirementNumberOfComponents, self).__init__("# of Components:")


class FieldRequirementNumberOfRows(FieldRequirementNaturalNumberValue):

    def __init__(self):
        super(FieldRequirementNumberOfRows, self).__init__("# of Rows:")


class FieldRequirementNaturalNumberVector(FieldRequirementLineEditBase):

    def __init__(self, label):
        super().__init__(label)

    def value(self):
        return parse_to_integer_vector(self._line_edit.text())

    def set_value(self, value):
        self._line_edit.blockSignals(True)
        self._line_edit.setText(display_as_integer_vector(value))
        self._line_edit.blockSignals(False)

    def fulfilled(self):
        values = self.value()
        return False if len(values) == 0 else all([v > 0 for v in values])


class FieldRequirementRealListValues(FieldRequirementLineEditBase):

    def __init__(self):
        super().__init__("Values:")

    def value(self):
        return parse_to_vector(self._line_edit.text())

    def set_value(self, value):
        self._line_edit.blockSignals(True)
        self._line_edit.setText(display_as_vector(value))
        self._line_edit.blockSignals(False)

    def fulfilled(self):
        return len(self.value()) > 0
