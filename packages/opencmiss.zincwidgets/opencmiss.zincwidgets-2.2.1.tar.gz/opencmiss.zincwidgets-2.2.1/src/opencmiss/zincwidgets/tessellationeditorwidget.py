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

from PySide2 import QtCore, QtWidgets

from opencmiss.zinc.status import OK as ZINC_OK
from opencmiss.zincwidgets.ui.ui_tessellationeditorwidget import Ui_TessellationEditorWidget
from opencmiss.zincwidgets.delegates.spinboxdelegate import SpinBoxDelegate

TESSELLATION_NAME_FORMAT = 'tessellation{0}'
TESSELLATION_DATA_ROLE = QtCore.Qt.UserRole + 1


class TessellationEditorWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(TessellationEditorWidget, self).__init__(parent)
        self._ui = Ui_TessellationEditorWidget()
        self._ui.setupUi(self)
        self._ui.tableWidgetTessellations.setColumnCount(4)
        h1 = QtWidgets.QTableWidgetItem('Name')
        self._ui.tableWidgetTessellations.setHorizontalHeaderItem(0, h1)
        h2 = QtWidgets.QTableWidgetItem('Minimum\nDivisions')
        self._ui.tableWidgetTessellations.setHorizontalHeaderItem(1, h2)
        h3 = QtWidgets.QTableWidgetItem('Refinement\nFactors')
        self._ui.tableWidgetTessellations.setHorizontalHeaderItem(2, h3)
        h4 = QtWidgets.QTableWidgetItem('Circle\nDivisions')
        self._ui.tableWidgetTessellations.setHorizontalHeaderItem(3, h4)
        self._ui.tableWidgetTessellations.resizeColumnsToContents()
        spin_box_delegate = SpinBoxDelegate(self._ui.tableWidgetTessellations)
        self._ui.tableWidgetTessellations.setItemDelegateForColumn(3, spin_box_delegate)
        self._selected_tessellation_row = -1

        self._makeConnections()

    def _updateUi(self):
        self._ui.tableWidgetTessellations.resizeColumnsToContents()
        hh = self._ui.tableWidgetTessellations.horizontalHeader()
        hh.setStretchLastSection(True)
        selected_items = self._ui.tableWidgetTessellations.selectedItems()
        tessellation_selected = len(selected_items) > 0

        self._ui.pushButtonDeleteTessellation.setEnabled(tessellation_selected)
        self._ui.groupBoxProperties.setEnabled(tessellation_selected)

        if tessellation_selected:
            tm = self._context.getTessellationmodule()
            first_item = selected_items[0]
            t = first_item.data(TESSELLATION_DATA_ROLE)
            default_tessellation = t == tm.getDefaultTessellation()
            default_points_tessellation = t == tm.getDefaultPointsTessellation()
            self._ui.checkBoxDefaultTessellation.setChecked(default_tessellation)
            self._ui.checkBoxDefaultPointsTessellation.setChecked(default_points_tessellation)
            self._ui.pushButtonDeleteTessellation.setEnabled(not default_tessellation and not default_points_tessellation)
        else:
            self._ui.checkBoxDefaultTessellation.setChecked(False)
            self._ui.checkBoxDefaultPointsTessellation.setChecked(False)

    def _makeConnections(self):
        self._ui.pushButtonAddTessellation.clicked.connect(self._addTessellationClicked)
        self._ui.pushButtonDeleteTessellation.clicked.connect(self._deleteTessellationClicked)

        self._ui.tableWidgetTessellations.itemClicked.connect(self._tessellationItemClicked)
        self._ui.tableWidgetTessellations.itemChanged.connect(self._tessellationItemChanged)

        self._ui.checkBoxDefaultTessellation.clicked.connect(self._defaultTessellationClicked)
        self._ui.checkBoxDefaultPointsTessellation.clicked.connect(self._defaultPointsTessellationClicked)

    def _tessellationItemChanged(self, item):
        item_column = item.column()
        item_row = item.row()
        if item_column == 0:
            t = item.data(TESSELLATION_DATA_ROLE)
        else:
            first_item = self._ui.tableWidgetTessellations.item(item_row, 0)
            t = first_item.data(TESSELLATION_DATA_ROLE)

        if item_column == 0:
            if ZINC_OK != t.setName(item.data(QtCore.Qt.DisplayRole)):
                item.setData(QtCore.Qt.DisplayRole, t.getName())
        elif item_column == 1 or item_column == 2:
            item_data = item.data(QtCore.Qt.DisplayRole)
            value = processMultiFormatData(item_data)
            if item_column == 1:
                if value is None:
                    min_value_count, _ = t.getMinimumDivisions(0)
                    _, min_values = t.getMinimumDivisions(min_value_count)
                    item.setData(QtCore.Qt.DisplayRole, str(min_values))
                else:
                    t.setMinimumDivisions(value)
            elif item_column == 2:
                if value is None:
                    ref_value_count, _ = t.getRefinementFactors(0)
                    _, ref_values = t.getRefinementFactors(ref_value_count)
                    item.setData(QtCore.Qt.DisplayRole, str(ref_values))
                else:
                    t.setRefinementFactors(value)
        elif item_column == 3:
            t.setCircleDivisions(int(item.data(QtCore.Qt.DisplayRole)))

    def _defaultTessellationClicked(self):
        selected_items = self._ui.tableWidgetTessellations.selectedItems()
        if len(selected_items):
            tm = self._context.getTessellationmodule()
            first_item = selected_items[0]
            t = first_item.data(TESSELLATION_DATA_ROLE)
            tm.setDefaultTessellation(t)

            self._updateUi()

    def _defaultPointsTessellationClicked(self):
        selected_items = self._ui.tableWidgetTessellations.selectedItems()
        if len(selected_items):
            tm = self._context.getTessellationmodule()
            first_item = selected_items[0]
            t = first_item.data(TESSELLATION_DATA_ROLE)
            tm.setDefaultPointsTessellation(t)

            self._updateUi()

    def _addTessellationClicked(self):
        tm = self._context.getTessellationmodule()
        count = 1
        tessellation_name = TESSELLATION_NAME_FORMAT.format(count)
        t = tm.findTessellationByName(tessellation_name)
        while t.isValid():
            count += 1
            tessellation_name = TESSELLATION_NAME_FORMAT.format(count)
            t = tm.findTessellationByName(tessellation_name)

        t = tm.createTessellation()
        t.setName(tessellation_name)

        addRow(self._ui.tableWidgetTessellations, t, 1, 1, 12)
        self._updateUi()

    def _deleteTessellationClicked(self):
        selected_items = self._ui.tableWidgetTessellations.selectedItems()
        if len(selected_items):
            first_item = selected_items[0]
            self._ui.tableWidgetTessellations.removeRow(first_item.row())

            self._updateUi()

    def _tessellationItemClicked(self, item):
        twt = self._ui.tableWidgetTessellations
        selected_items = twt.selectedItems()
        if len(selected_items):
            if self._selected_tessellation_row == twt.row(item):
                self._ui.tableWidgetTessellations.clearSelection()
                self._selected_tessellation_row = -1
            else:
                self._selected_tessellation_row = twt.row(item)

        self._updateUi()

    def setTessellations(self, tessellations):
        self._context = tessellations.getZincContext()
        tm = self._context.getTessellationmodule()
        ti = tm.createTessellationiterator()
        t = ti.next()
        self._ui.tableWidgetTessellations.blockSignals(True)
        self._ui.tableWidgetTessellations.setRowCount(0)
        while t.isValid():
            min_value_count, _ = t.getMinimumDivisions(0)
            ref_value_count, _ = t.getRefinementFactors(0)
            _, min_values = t.getMinimumDivisions(min_value_count)
            _, ref_values = t.getRefinementFactors(ref_value_count)

            addRow(self._ui.tableWidgetTessellations, t, min_values, ref_values, t.getCircleDivisions())
            t = ti.next()

        self._ui.tableWidgetTessellations.blockSignals(False)
        self._updateUi()


def processMultiFormatData(data):
    value = None
    try:
        value = int(data)
    except ValueError:
        pass

    if value is None:
        # Not a straight int
        values = data.split(',')
        try:
            value = [int(v) for v in values]
        except ValueError:
            pass

    if value is None:
        values = data.split('*')
        try:
            value = [int(v) for v in values]
        except ValueError:
            pass

    if value is None:
        try:
            value = json.loads(data)
        except json.decoder.JSONDecodeError:  # @UndefinedVariable
            pass

    return value


def addRow(table, tessellation, div, ref, circ):
    rows = table.rowCount()
    table.insertRow(rows)

    name_item = QtWidgets.QTableWidgetItem(tessellation.getName())
    name_item.setData(TESSELLATION_DATA_ROLE, tessellation)
    table.setItem(rows, 0, name_item)

    div_item = QtWidgets.QTableWidgetItem(str(div))
    table.setItem(rows, 1, div_item)

    ref_item = QtWidgets.QTableWidgetItem(str(ref))
    table.setItem(rows, 2, ref_item)

    circ_div_item = QtWidgets.QTableWidgetItem()
    circ_div_item.setData(0, circ)
    table.setItem(rows, 3, circ_div_item)
