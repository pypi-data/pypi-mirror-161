"""
Zinc Region Chooser Widget

Widget for choosing a region from a region tree, derived from QComboBox

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from PySide2 import QtWidgets


class RegionChooserWidget(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        """
        Call the super class init functions
        """
        QtWidgets.QComboBox.__init__(self, parent)
        self._root_region = None
        self._region = None
        self._notifier = None

    def _get_region_index(self, find_region, region, count):
        """
        Recursive function to determine the index of findRegion in the tree under region, starting
        at count. The index matches the position in the combobox.
        :return index, count. Index of findRegion under region tree or None if not found,
        and count of regions searched.
        """
        if region == find_region:
            return count, None
        child = region.getFirstChild()
        while child.isValid():
            count = count + 1
            found, count = self._get_region_index(find_region, child, count)
            if found is not None:
                return found, None
            child = child.getNextSibling()

        return None, count

    def _add_region_to_list_recursive(self, region, parent_path):
        name = region.getName()
        if name is None:
            self.addItem('/')
            path = ''
        else:
            path = parent_path + region.getName()
            self.addItem(path)
        child = region.getFirstChild()
        while child.isValid():
            self._add_region_to_list_recursive(child, path + '/')
            child = child.getNextSibling()

    def _build_region_list(self):
        """
        Rebuilds the list of items in the ComboBox from the region tree
        """
        self.blockSignals(True)
        self.clear()
        self._add_region_to_list_recursive(self._root_region, '/')
        self.blockSignals(False)
        if self._has_region(self._region):
            self._display_region()
        else:
            self._region = self.getRegion()

    def _display_region(self):
        """
        Display the currently chosen region in the ComboBox
        """
        count, _ = self._get_region_index(self._region, self._root_region, 0)
        self.blockSignals(True)
        self.setCurrentIndex(count)
        self.blockSignals(False)

    def _has_region(self, region):
        index, _ = self._get_region_index(region, self._root_region, 0)
        return index is not None

    def _region_tree_changed(self, event):
        if event.isValid():
            self._build_region_list()

    def getRootRegion(self):
        return self._root_region

    def setRootRegion(self, root_region):
        """
        Sets the root region that this widget chooses regions from.
        Also sets current region to rootRegion.
        """
        self._root_region = root_region
        self._region = root_region
        self._build_region_list()
        self._notifier = root_region.createRegionnotifier()
        self._notifier.setCallback(self._region_tree_changed)

    def getRegion(self):
        """
        Must call this from client's currentIndexChanged() slot to get/update current region.
        Returns a valid Zinc region or None if the a valid region is not found.

        :return: Zinc region.
        """
        regionPath = str(self.currentText())
        self._region = self._root_region.findSubregionAtPath(regionPath)
        if not self._region.isValid():
            self._region = None
        return self._region

    def setRegion(self, region):
        """
        Set the currently selected region.
        """
        if not self._has_region(region):
            return

        self._region = region
        self._display_region()
