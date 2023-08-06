"""
Zinc Enumeration Chooser Widget

Widget for choosing an enumeration item, derived from QComboBox

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from PySide2 import QtCore, QtWidgets

import re
import copy
from opencmiss.zinc.element import Element
from opencmiss.zinc.status import OK as ZINC_OK

class EnumerationChooserWidget(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        '''
        Call the super class init functions
        '''
        QtWidgets.QComboBox.__init__(self, parent)
        self._currentEnum = None

    def setEnumsList(self, enumToString, stringToEnum, validEnums: list = None):
        self._enumToString = enumToString
        self._stringToEnum = stringToEnum
        self._validEnums = copy.copy(validEnums) if validEnums else None
        self._buildItemList()

    def _buildItemList(self):
        '''
        Rebuilds the list of items in the ComboBox from the item module
        '''
        self.blockSignals(True)
        self.clear()
        i = 1
        while True:
            name = self._getStringFromEnum(i)
            if name:
                self.addItem(name)
                i += 1
            else:
                break
        self.blockSignals(False)
        self._displayItem()

    def _getStringFromEnum(self, enumIndex):
        """
        :param enumIndex: a valid enum or an index + 1 into self._validEnums if set.
        :return: Enumeration string or None if invalid enumIndex.
        """
        if self._validEnums:
            if enumIndex <= len(self._validEnums):
                enumString = self._enumToString(self._validEnums[enumIndex - 1])
            else:
                enumString = None
        else:
            enumString = self._enumToString(enumIndex)

        if not enumString:
            return None
        enumString = enumString.lower()
        if bool(re.search(r'_\d', enumString)):
            enumString = enumString.replace('_', ' = ')
        else:
            enumString = enumString.replace('_', ' ')
        return enumString

    def _getEnumFromString(self, enumString):
        enumString = enumString.upper()
        if bool(re.search(r' = ', enumString)):
            enumString = enumString.replace(' = ', '_')
        else:
            enumString = enumString.replace(' ', '_')
        return self._stringToEnum(enumString)

    def _displayItem(self):
        '''
        Display the currently chosen item in the ComboBox
        '''
        self.blockSignals(True)
        if self._currentEnum:
            itemName = self._getStringFromEnum(self._currentEnum)
            index = self.findText(itemName)
        else:
            index = 0
        self.setCurrentIndex(index)
        self.blockSignals(False)

    def getEnum(self):
        '''
        Must call this from currentIndexChanged() slot to get/update current item
        '''
        itemName = str(self.currentText())
        self._currentEnum = self._getEnumFromString(itemName)
        return self._currentEnum

    def setEnum(self, enum):
        '''
        Set the currently selected enum
        '''
        if not enum:
            self._currentEnum = None
        else:
            enumIndex = enum
            if self._validEnums:
                enumIndex = self._validEnums.index(enum) + 1  # throws exception if not found; can change if too severe
            if self._getStringFromEnum(enumIndex):
                self._currentEnum = enum
            else:
                self._currentEnum = None
        self._displayItem()
