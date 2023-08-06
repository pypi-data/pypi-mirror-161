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
from PySide2 import QtCore, QtWidgets

from opencmiss.zinc.sceneviewer import Sceneviewer
from opencmiss.zinc.spectrum import Spectrum, Spectrumcomponent
from opencmiss.zinc.status import OK as ZINC_OK

from opencmiss.zincwidgets.ui.ui_spectrumeditorwidget import Ui_SpectrumEditorWidget
from opencmiss.argon.settings.mainsettings import FLOAT_STRING_FORMAT
from opencmiss.argon.argonlogger import ArgonLogger

COMPONENT_NAME_FORMAT = '{:d}. '
SPECTRUM_DATA_ROLE = QtCore.Qt.UserRole + 1


class SpectrumEditorWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(SpectrumEditorWidget, self).__init__(parent)
        self._ui = Ui_SpectrumEditorWidget()
        self._ui.setupUi(self)

        self._ui.comboBoxColourMap.addItems(extractColourMappingEnum())
        self._ui.comboBoxScale.addItems(extractScaleTypeEnum())

        self._spectrums = None
        self._zincContext = None
        self._selected_spectrum_row = -1
        self._selected_spectrum_components_row = -1
        self._previewZincRegion = None
        self._previewZincScene = None
        self._spectrummodulenotifier = None
        self._currentSpectrumName = None
        self._updateUi()

        self._makeConnections()

    def _makeConnections(self):
        self._ui.pushButtonAddSpectrum.clicked.connect(self._addSpectrumClicked)
        self._ui.pushButtonDeleteSpectrum.clicked.connect(self._deleteSpectrumClicked)
        self._ui.pushButtonAddSpectrumComponent.clicked.connect(self._addSpectrumComponentClicked)
        self._ui.pushButtonDeleteSpectrumComponent.clicked.connect(self._deleteSpectrumComponentClicked)

        self._ui.listWidgetSpectrums.itemClicked.connect(self._spectrumItemClicked)
        self._ui.listWidgetSpectrums.itemChanged.connect(self._spectrumChanged)
        self._ui.checkBoxOverwrite.clicked.connect(self._overwriteClicked)
        self._ui.checkBoxDefault.clicked.connect(self._defaultClicked)
        self._ui.pushButtonAutorange.clicked.connect(self._autorangeClicked)

        self._ui.listWidgetSpectrumComponents.itemClicked.connect(self._spectrumComponentItemClicked)

        self._ui.pushButtonMoveDownSpectrumComponent.clicked.connect(self._moveDownSpectrumComponentClicked)
        self._ui.pushButtonMoveUpSpectrumComponent.clicked.connect(self._moveUpSpectrumComponentClicked)
        self._ui.comboBoxColourMap.currentIndexChanged.connect(self._colourMapIndexChanged)
        self._ui.pushButtonReverseColours.clicked.connect(self._reverseColoursClicked)

        self._ui.spinBoxDataFieldComponent.valueChanged.connect(self._dataFieldComponentValueChanged)

        self._ui.lineEditDataRangeMin.editingFinished.connect(self._dataRangeMinEntered)
        self._ui.lineEditDataRangeMax.editingFinished.connect(self._dataRangeMaxEntered)
        self._ui.lineEditColourRangeMin.editingFinished.connect(self._colourRangeMinEntered)
        self._ui.lineEditColourRangeMax.editingFinished.connect(self._colourRangeMaxEntered)
        self._ui.checkBoxExtendBelow.clicked.connect(self._extendBelowClicked)
        self._ui.checkBoxExtendAbove.clicked.connect(self._extendAboveClicked)
        self._ui.checkBoxFixMinimum.clicked.connect(self._fixMinimumClicked)
        self._ui.checkBoxFixMaximum.clicked.connect(self._fixMaximumClicked)

        self._ui.comboBoxScale.currentIndexChanged.connect(self._scaleIndexChanged)
        self._ui.lineEditExaggeration.editingFinished.connect(self._exaggerationEntered)

        self._ui.sceneviewerWidgetPreview.graphicsInitialized.connect(self._graphicsInitialised)

    def _getCurrentSpectrum(self):
        currentItem = self._ui.listWidgetSpectrums.currentItem()
        if not currentItem:
            return None
        name = currentItem.text()
        sm = self._zincContext.getSpectrummodule()
        spectrum = sm.findSpectrumByName(name)
        if spectrum.isValid():
            return spectrum
        return None

    def _clearSpectrumUi(self):
        self._ui.listWidgetSpectrumComponents.clear()
        self._ui.checkBoxOverwrite.setChecked(False)
        self._clearSpectrumComponentUi()

    def _clearSpectrumComponentUi(self):
        self._ui.comboBoxColourMap.setCurrentIndex(0)
        self._ui.comboBoxScale.setCurrentIndex(0)

    def _spectrummoduleCallback(self, spectrummoduleevent):
        """
        Callback for change in spectrums; may need to rebuild spectrum list
        """
        changeSummary = spectrummoduleevent.getSummarySpectrumChangeFlags()
        # print("Spectrum Editor: _spectrummoduleCallback changeSummary " + str(changeSummary))
        if 0 != (changeSummary & (Spectrum.CHANGE_FLAG_IDENTIFIER | Spectrum.CHANGE_FLAG_ADD | Spectrum.CHANGE_FLAG_REMOVE)):
            self._buildSpectrumList()

    def _buildSpectrumList(self):
        sm = self._zincContext.getSpectrummodule()
        si = sm.createSpectrumiterator()
        lws = self._ui.listWidgetSpectrums
        lws.clear()
        s = si.next()
        selectedItem = None
        while s.isValid():
            name = s.getName()
            item = createSpectrumListItem(name)
            lws.addItem(item)
            if name == self._currentSpectrumName:
                selectedItem = item
            s = si.next()
        if not selectedItem:
            if lws.count() > 0:
                selectedItem = lws.item(0)
                self._currentSpectrumName = selectedItem.text()
            else:
                self._currentSpectrumName = None
        if selectedItem:
            lws.setCurrentItem(selectedItem)
            selectedItem.setSelected(True)
        self._updateUi()

    def _updateUi(self):
        self._clearSpectrumUi()
        spectrum = self._getCurrentSpectrum()
        spectrum_selected = spectrum is not None

        self._ui.pushButtonDeleteSpectrum.setEnabled(spectrum_selected)
        self._ui.sceneviewerWidgetPreview.setEnabled(spectrum_selected)
        self._ui.groupBoxSpectrumProperties.setEnabled(spectrum_selected)
        self._ui.groupBoxComponents.setEnabled(spectrum_selected)
        self._ui.groupBoxComponentProperties.setEnabled(spectrum_selected)

        if spectrum_selected:
            # Only one spectrum can be selected at a time.
            sm = self._zincContext.getSpectrummodule()
            is_default_spectrum = (spectrum == sm.getDefaultSpectrum())
            self._ui.pushButtonDeleteSpectrum.setEnabled(not is_default_spectrum)
            self._ui.checkBoxDefault.setChecked(is_default_spectrum)
            self._ui.checkBoxOverwrite.setChecked(spectrum.isMaterialOverwrite())
            sc = spectrum.getFirstSpectrumcomponent()
            while sc.isValid():
                count = self._ui.listWidgetSpectrumComponents.count() + 1
                self._ui.listWidgetSpectrumComponents.addItem(createItem(getComponentString(sc, count), sc))
                sc = spectrum.getNextSpectrumcomponent(sc)

            if self._ui.listWidgetSpectrumComponents.count():
                self._ui.listWidgetSpectrumComponents.setCurrentRow(0)

        self._previewSpectrum(spectrum)
        self._updateComponentUi()

    def _previewSpectrum(self, spectrum):
        if self._previewZincScene is None:
            return
        if (spectrum is None) or (not spectrum.isValid()):
            self._previewZincScene.removeAllGraphics()
            return
        points = self._previewZincScene.getFirstGraphics()
        self._previewZincScene.beginChange()
        if not points.isValid():
            points = self._previewZincScene.createGraphicsPoints()
            pointsattr = points.getGraphicspointattributes()
            pointsattr.setBaseSize(1.0)
        else:
            pointsattr = points.getGraphicspointattributes()
        colourBar = self._spectrums.findOrCreateSpectrumGlyphColourBar(spectrum)
        pointsattr.setGlyph(colourBar)
        self._previewZincScene.endChange()
        sceneviewer = self._ui.sceneviewerWidgetPreview.getSceneviewer()
        if sceneviewer:
            sceneviewer.beginChange()
            sceneviewer.setScene(self._previewZincScene)
            sceneviewer.setProjectionMode(Sceneviewer.PROJECTION_MODE_PARALLEL)
            _, centre = colourBar.getCentre(3)
            eye = [centre[0], centre[1], centre[2] + 5.0]
            up = [-1.0, 0.0, 0.0]
            sceneviewer.setLookatParametersNonSkew(eye, centre, up)
            sceneviewer.setNearClippingPlane(1.0)
            sceneviewer.setFarClippingPlane(10.0)
            sceneviewer.setViewAngle(0.25)
            sceneviewer.endChange()

    def _getCurrentSpectrumcomponent(self):
        spectrum_component_items = self._ui.listWidgetSpectrumComponents.selectedItems()
        if len(spectrum_component_items) > 0:
            active_item = spectrum_component_items[0]
            return active_item.data(SPECTRUM_DATA_ROLE)
        return None

    def _updateComponentUi(self):
        spectrum_component_items = self._ui.listWidgetSpectrumComponents.selectedItems()
        spectrum_component_selected = (len(spectrum_component_items) > 0)

        self._ui.pushButtonDeleteSpectrumComponent.setEnabled(spectrum_component_selected)
        self._ui.comboBoxColourMap.setEnabled(spectrum_component_selected)
        self._ui.pushButtonAutorange.setEnabled(spectrum_component_selected)
        self._ui.comboBoxScale.setEnabled(spectrum_component_selected)
        self._ui.spinBoxDataFieldComponent.setEnabled(spectrum_component_selected)
        self._ui.pushButtonReverseColours.setEnabled(spectrum_component_selected)
        self._ui.lineEditDataRangeMin.setEnabled(spectrum_component_selected)
        self._ui.lineEditDataRangeMax.setEnabled(spectrum_component_selected)
        self._ui.lineEditColourRangeMin.setEnabled(spectrum_component_selected)
        self._ui.lineEditColourRangeMax.setEnabled(spectrum_component_selected)
        self._ui.checkBoxExtendBelow.setEnabled(spectrum_component_selected)
        self._ui.checkBoxExtendAbove.setEnabled(spectrum_component_selected)
        self._ui.checkBoxFixMinimum.setEnabled(spectrum_component_selected)
        self._ui.checkBoxFixMaximum.setEnabled(spectrum_component_selected)
        self._ui.pushButtonMoveDownSpectrumComponent.setEnabled(spectrum_component_selected)
        self._ui.pushButtonMoveUpSpectrumComponent.setEnabled(spectrum_component_selected)

        if spectrum_component_selected:
            active_spectrum_component = spectrum_component_items[0]
            sc = active_spectrum_component.data(SPECTRUM_DATA_ROLE)
            self._ui.comboBoxColourMap.blockSignals(True)
            self._ui.comboBoxColourMap.setCurrentIndex(sc.getColourMappingType())
            self._ui.comboBoxColourMap.blockSignals(False)
            self._ui.spinBoxDataFieldComponent.setValue(sc.getFieldComponent())
            self._ui.lineEditDataRangeMin.setText(FLOAT_STRING_FORMAT.format(sc.getRangeMinimum()))
            self._ui.lineEditDataRangeMax.setText(FLOAT_STRING_FORMAT.format(sc.getRangeMaximum()))
            self._ui.lineEditColourRangeMin.setText(FLOAT_STRING_FORMAT.format(sc.getColourMinimum()))
            self._ui.lineEditColourRangeMax.setText(FLOAT_STRING_FORMAT.format(sc.getColourMaximum()))
            self._ui.checkBoxExtendBelow.setChecked(sc.isExtendBelow())
            self._ui.checkBoxExtendAbove.setChecked(sc.isExtendAbove())
            self._ui.checkBoxFixMinimum.setChecked(sc.isFixMinimum())
            self._ui.checkBoxFixMaximum.setChecked(sc.isFixMaximum())
            self._ui.comboBoxScale.setCurrentIndex(sc.getScaleType())
            self._ui.lineEditExaggeration.setText(FLOAT_STRING_FORMAT.format(sc.getExaggeration()))

            row = self._ui.listWidgetSpectrumComponents.row(active_spectrum_component)
            self._ui.pushButtonMoveUpSpectrumComponent.setEnabled(row > 0)
            self._ui.pushButtonMoveDownSpectrumComponent.setEnabled(row < (self._ui.listWidgetSpectrumComponents.count() - 1))

            active_spectrum_component.setText(getComponentString(sc, row + 1))

    def _spectrumChanged(self, item):
        newName = item.text()
        sm = self._zincContext.getSpectrummodule()
        spectrum = sm.findSpectrumByName(self._currentSpectrumName)
        # spectrum = item.data(SPECTRUM_DATA_ROLE)
        if self._spectrums.renameSpectrum(spectrum, newName):
            self._currentSpectrumName = newName
        else:
            item.setText(spectrum.getName())

    def _spectrumItemClicked(self, item):
        item.setSelected(True)
        self._currentSpectrumName = item.text()
        self._selected_spectrum_row = self._ui.listWidgetSpectrums.row(item)
        self._updateUi()

    def _spectrumComponentItemClicked(self, item):
        lwsc = self._ui.listWidgetSpectrumComponents
        item.setSelected(True)
        selected_items = lwsc.selectedItems()
        if len(selected_items):
            if self._selected_spectrum_components_row == lwsc.row(item):
                # self._ui.listWidgetSpectrumComponents.clearSelection()
                # self._selected_spectrum_components_row = -1
                # self._clearSpectrumComponentUi()
                pass
            else:
                self._selected_spectrum_components_row = lwsc.row(item)

        self._updateComponentUi()

    def _selectSpectrumByName(self, name):
        lws = self._ui.listWidgetSpectrums
        for row in range(lws.count()):
            item = lws.item(row)
            if item.text() == name:
                item.setSelected(True)
                self._currentSpectrumName = name
                self._updateUi()
                return
        self._currentSpectrumName = None

    def _selectSpectrum(self, spectrum):
        if (spectrum is None) or (not spectrum.isValid()):
            return
        self._selectSpectrumByName(spectrum.getName())

    def _addSpectrumClicked(self):
        sm = self._zincContext.getSpectrummodule()
        sm.beginChange()
        spectrum = sm.createSpectrum()
        spectrum.setManaged(True)
        self._currentSpectrumName = spectrum.getName()
        sm.endChange()
        self._selectSpectrum(spectrum)
        self._updateUi()

    def _deleteSpectrumClicked(self):
        self._previewSpectrum(None)  # preview graphics references spectrum
        if not self._spectrums.removeSpectrumByName(self._currentSpectrumName):
            ArgonLogger.getLogger().error("Can't delete spectrum " + self._currentSpectrumName + " as it is in use")
            self._updateUi()

    def _addSpectrumComponentClicked(self):
        s = self._getCurrentSpectrum()
        sc = s.createSpectrumcomponent()
        count = self._ui.listWidgetSpectrumComponents.count() + 1
        item = createItem(getComponentString(sc, count), sc)
        self._ui.listWidgetSpectrumComponents.addItem(item)
        item.setSelected(True)
        self._spectrumComponentItemClicked(item)

    def _deleteSpectrumComponentClicked(self):
        selected_items = self._ui.listWidgetSpectrumComponents.selectedItems()
        if len(selected_items):
            row = self._ui.listWidgetSpectrumComponents.row(selected_items[0])
            item = self._ui.listWidgetSpectrumComponents.takeItem(row)
            sc = item.data(SPECTRUM_DATA_ROLE)
            s = self._getCurrentSpectrum()
            if s:
                s.removeSpectrumcomponent(sc)
        self._updateComponentUi()

    def _defaultClicked(self):
        if self._ui.checkBoxDefault.isChecked():
            s = self._getCurrentSpectrum()
            sm = self._ui.sceneviewerWidgetPreview.getContext().getSpectrummodule()
            sm.setDefaultSpectrum(s)
        else:
            # Can't un-set default; need to make another one default
            self._ui.checkBoxDefault.setChecked(True)

    def _overwriteClicked(self):
        s = self._getCurrentSpectrum()
        s.setMaterialOverwrite(self._ui.checkBoxOverwrite.isChecked())

    def _autorangeClicked(self):
        """
        Autorange all components of spectrum.
        Maintains proportions of minimums and miximums for spectrum components, fixed minimums and maximums.
        """
        s = self._getCurrentSpectrum()
        region = self._zincContext.getDefaultRegion()
        scene = region.getScene()
        scenefiltermodule = self._zincContext.getScenefiltermodule()
        scenefilter = scenefiltermodule.getDefaultScenefilter()
        s.autorange(scene, scenefilter)
        self._updateComponentUi()

    def _reverseColoursClicked(self):
        sc = self._getCurrentSpectrumcomponent()
        if sc:
            sm = self._zincContext.getSpectrummodule()
            sm.beginChange()
            newColourMaximum = sc.getColourMinimum()
            newColourMinimum = sc.getColourMaximum()
            sc.setColourMaximum(newColourMaximum)
            sc.setColourMinimum(newColourMinimum)
            sm.endChange()
            self._updateComponentUi()

    def _dataFieldComponentValueChanged(self, value):
        selected_items = self._ui.listWidgetSpectrumComponents.selectedItems()
        if len(selected_items):
            active_item = selected_items[0]
            sc = active_item.data(SPECTRUM_DATA_ROLE)
            sc.setFieldComponent(value)

            self._updateComponentUi()

    def _colourMapIndexChanged(self, index):
        selected_items = self._ui.listWidgetSpectrumComponents.selectedItems()
        if len(selected_items):
            active_item = selected_items[0]
            sc = active_item.data(SPECTRUM_DATA_ROLE)
            sc.setColourMappingType(index)

            self._updateComponentUi()

    def _dataRangeMinEntered(self):
        sc = self._getCurrentSpectrumcomponent()
        try:
            valueText = self._ui.lineEditDataRangeMin.text()
            value = float(valueText)
            result = sc.setRangeMinimum(value)
            if result != ZINC_OK:
                raise ValueError("")
        except ValueError:
            ArgonLogger.getLogger().error("Error setting spectrum component data range minimum")
        self._ui.lineEditDataRangeMin.setText(FLOAT_STRING_FORMAT.format(sc.getRangeMinimum()))

    def _dataRangeMaxEntered(self):
        sc = self._getCurrentSpectrumcomponent()
        try:
            valueText = self._ui.lineEditDataRangeMax.text()
            value = float(valueText)
            result = sc.setRangeMaximum(value)
            if result != ZINC_OK:
                raise ValueError("")
        except ValueError:
            ArgonLogger.getLogger().error("Error setting spectrum component data range maximum")
        self._ui.lineEditDataRangeMax.setText(FLOAT_STRING_FORMAT.format(sc.getRangeMaximum()))

    def _colourRangeMinEntered(self):
        sc = self._getCurrentSpectrumcomponent()
        try:
            valueText = self._ui.lineEditColourRangeMin.text()
            value = float(valueText)
            result = sc.setColourMinimum(value)
            if result != ZINC_OK:
                raise ValueError("")
        except ValueError:
            ArgonLogger.getLogger().error("Error setting spectrum component colour range minimum")
        self._ui.lineEditColourRangeMin.setText(FLOAT_STRING_FORMAT.format(sc.getColourMinimum()))

    def _colourRangeMaxEntered(self):
        sc = self._getCurrentSpectrumcomponent()
        try:
            valueText = self._ui.lineEditColourRangeMax.text()
            value = float(valueText)
            result = sc.setColourMaximum(value)
            if result != ZINC_OK:
                raise ValueError("")
        except ValueError:
            ArgonLogger.getLogger().error("Error setting spectrum component colour range maximum")
        self._ui.lineEditColourRangeMax.setText(FLOAT_STRING_FORMAT.format(sc.getColourMaximum()))

    def _extendBelowClicked(self):
        sc = self._getCurrentSpectrumcomponent()
        sc.setExtendBelow(self._ui.checkBoxExtendBelow.isChecked())

    def _extendAboveClicked(self):
        sc = self._getCurrentSpectrumcomponent()
        sc.setExtendAbove(self._ui.checkBoxExtendAbove.isChecked())

    def _fixMinimumClicked(self):
        sc = self._getCurrentSpectrumcomponent()
        sc.setFixMinimum(self._ui.checkBoxFixMinimum.isChecked())

    def _fixMaximumClicked(self):
        sc = self._getCurrentSpectrumcomponent()
        sc.setFixMaximum(self._ui.checkBoxFixMaximum.isChecked())

    def _scaleIndexChanged(self, index):
        selected_items = self._ui.listWidgetSpectrumComponents.selectedItems()
        if len(selected_items):
            active_item = selected_items[0]
            sc = active_item.data(SPECTRUM_DATA_ROLE)
            sc.setScaleType(index)

            self._updateComponentUi()

    def _exaggerationEntered(self):
        sc = self._getCurrentSpectrumcomponent()
        try:
            valueText = self._ui.lineEditExaggeration.text()
            value = float(valueText)
            result = sc.setExaggeration(value)
            if result != ZINC_OK:
                raise ValueError("")
        except ValueError:
            ArgonLogger.getLogger().error("Error setting log scale exaggeration")
        self._ui.lineEditExaggeration.setText(FLOAT_STRING_FORMAT.format(sc.getExaggeration()))

    def _moveDownSpectrumComponentClicked(self):
        self._moveSpectrumComponent(1)

    def _moveSpectrumComponent(self, direction):
        selected_items = self._ui.listWidgetSpectrumComponents.selectedItems()
        if len(selected_items):
            active_item = selected_items[0]
            row = self._ui.listWidgetSpectrumComponents.row(active_item)
            next_row = row + direction
            self._ui.listWidgetSpectrumComponents.takeItem(row)
            self._ui.listWidgetSpectrumComponents.insertItem(next_row, active_item)
            item = self._ui.listWidgetSpectrumComponents.item(row)
            sc = item.data(SPECTRUM_DATA_ROLE)
            item.setText(getComponentString(sc, row + 1))
            self._ui.listWidgetSpectrumComponents.setCurrentRow(next_row)
            self._selected_spectrum_components_row = next_row

            self._updateComponentUi()

    def _moveUpSpectrumComponentClicked(self):
        self._moveSpectrumComponent(-1)

    def _graphicsInitialised(self):
        if self._ui.listWidgetSpectrums.count():
            self._ui.listWidgetSpectrums.setCurrentRow(0)
            first_item = self._ui.listWidgetSpectrums.item(0)
            self._spectrumItemClicked(first_item)

    def setSpectrums(self, spectrums):
        """
        Sets the Argon spectrums object which supplies the zinc context and has utilities for
        managing spectrums.
        :param spectrums: ArgonSpectrums object
        """
        self._spectrums = spectrums
        self._currentSpectrumName = None
        self._zincContext = spectrums.getZincContext()
        self._ui.sceneviewerWidgetPreview.setContext(self._zincContext)
        self._previewZincRegion = self._zincContext.createRegion()
        self._previewZincRegion.setName("Spectrum editor preview region")
        self._previewZincScene = self._previewZincRegion.getScene()
        sceneviewer = self._ui.sceneviewerWidgetPreview.getSceneviewer()
        if sceneviewer:
            sceneviewer.setScene(self._previewZincScene)
        spectrummodule = self._zincContext.getSpectrummodule()
        self._spectrummodulenotifier = spectrummodule.createSpectrummodulenotifier()
        self._spectrummodulenotifier.setCallback(self._spectrummoduleCallback)
        self._buildSpectrumList()


INVALID_POSTFIX = '_INVALID'
COLOUR_MAPPING_PREFIX = 'COLOUR_MAPPING_TYPE_'
SCALE_TYPE_PREFIX = 'SCALE_TYPE_'
PRIVATE_SPECTRUM_FORMAT = 'spectrum_{0}'


def createSpectrumListItem(name):
    i = QtWidgets.QListWidgetItem(name)
    i.setFlags(i.flags() | QtCore.Qt.ItemIsEditable)

    return i


def createItem(name, data, editable=False):
    i = QtWidgets.QListWidgetItem(name)
    i.setData(SPECTRUM_DATA_ROLE, data)
    if editable:
        i.setFlags(i.flags() | QtCore.Qt.ItemIsEditable)

    return i


def getComponentString(sc, row):
    name = COMPONENT_NAME_FORMAT.format(row)
    name += ' ' + stringFromColourMappingInt(sc.getColourMappingType())
    name += ' ' + stringFromScaleInt(sc.getScaleType())
    if sc.isColourReverse():
        name += ' reverse'
    return name


def stringFromColourMappingInt(value):
    attr_dict = Spectrumcomponent.__dict__
    for key in attr_dict:
        if key.startswith(COLOUR_MAPPING_PREFIX) and attr_dict[key] == value:
            return key.replace(COLOUR_MAPPING_PREFIX, '').lower()

    return 'invalid'


def stringFromScaleInt(value):
    attr_dict = Spectrumcomponent.__dict__
    for key in attr_dict:
        if key.startswith(SCALE_TYPE_PREFIX) and attr_dict[key] == value:
            return key.replace(SCALE_TYPE_PREFIX, '').lower()

    return 'invalid'


def extractColourMappingEnum():
    enum = []
    attr_dict = Spectrumcomponent.__dict__
    for key in attr_dict:
        if key.startswith(COLOUR_MAPPING_PREFIX):
            if key.endswith(INVALID_POSTFIX):
                enum.append((attr_dict[key], '---'))
            else:
                enum.append((attr_dict[key], key.replace(COLOUR_MAPPING_PREFIX, '')))

    sorted_enum = sorted(enum)
    return [a[1] for a in sorted_enum]


def extractScaleTypeEnum():
    enum = []
    attr_dict = Spectrumcomponent.__dict__
    for key in attr_dict:
        if key.startswith(SCALE_TYPE_PREFIX):
            if key.endswith(INVALID_POSTFIX):
                enum.append((attr_dict[key], '---'))
            else:
                enum.append((attr_dict[key], key.replace(SCALE_TYPE_PREFIX, '')))

    sorted_enum = sorted(enum)
    return [a[1] for a in sorted_enum]
