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
from PySide2 import QtWidgets, QtGui, QtCore

from opencmiss.zincwidgets.fieldconditions import *
from opencmiss.zinc.material import Material
from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.status import OK as ZINC_OK
from opencmiss.zincwidgets.ui.ui_materialeditorwidget import Ui_MaterialEditor
from opencmiss.utils.zinc.general import ChangeManager


class MaterialModel(QtCore.QAbstractListModel):

    def __init__(self, parent=None):
        super(MaterialModel, self).__init__(parent)
        self._material_names = []
        self._material_module = None

    def setMaterialModule(self, material_module):
        self._material_module = material_module
        self._build_material_names_list()

    def getMaterialForIndex(self, index):
        return self._material_module.findMaterialByName(self._material_names[index.row()])

    def _try_to_remove_material(self, name):
        can_remove = True
        mm = self._material_module
        with ChangeManager(mm):
            material = mm.findMaterialByName(name)
            material.setManaged(False)
            del material

        recovered_material = self._material_module.findMaterialByName(name)
        if recovered_material.isValid():
            # I'm still in use.
            recovered_material.setManaged(True)
            can_remove = False

        return can_remove

    def _build_material_names_list(self):
        material_iterator = self._material_module.createMaterialiterator()
        material = material_iterator.next()

        while material.isValid():
            self._material_names.append(material.getName())
            material = material_iterator.next()

    def rowCount(self, parent_index):
        return len(self._material_names)

    def headerData(self, section, orientation, role):
        return ['Materials']

    def flags(self, index):
        if index.isValid():
            if index.column() == 0:
                return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        return QtCore.Qt.NoItemFlags

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == QtCore.Qt.DisplayRole:
            return self._material_names[index.row()]

        return None

    def setData(self, index, value, role):
        if index.isValid():
            value = value.rstrip()
            if role == QtCore.Qt.EditRole and value:
                current_name = self._material_names[index.row()]
                material = self._material_module.findMaterialByName(current_name)
                result = material.setName(value)
                if result == ZINC_OK:
                    self._material_names[index.row()] = value
                    return True

        return False

    def addData(self):
        index = self.index(-1, 0)
        row_count = len(self._material_names)
        self.beginInsertRows(index, row_count, row_count)
        mm = self._material_module
        with ChangeManager(mm):
            material = mm.createMaterial()
            name = material.getName()
            material.setManaged(True)
        self._material_names.append(name)
        self.endInsertRows()

    def removeData(self, index_list):
        """
        Only handling single selection, changes would be needed if
        multiple selection was enabled for any views.
        """
        parent = self.createIndex(-1, 0)
        success = False
        for index in index_list:
            self.beginRemoveRows(parent, index.row(), index.row())
            name = self._material_names[index.row()]
            success = self._try_to_remove_material(name)
            if success:
                self._material_names.pop(index.row())
            self.endRemoveRows()

        return success

    def reset(self):
        self.beginResetModel()
        self._material_names = []
        self._build_material_names_list()
        self.endResetModel()


class MaterialEditorWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        """
        Call the super class init functions
        """
        QtWidgets.QWidget.__init__(self, parent)
        self._ui = Ui_MaterialEditor()
        self._ui.setupUi(self)

        self._zincContext = None
        self._previewZincRegion = None
        self._nullObjectName = None
        self._materials = None
        self._materialmodulenotifier = None
        self._currentMaterial = None
        self._currentMaterialIndex = None
        self._previewZincScene = None

        self._material_model = MaterialModel()
        self._ui.materials_listView.setModel(self._material_model)
        self._ui.materials_listView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self._makeConnections()

    def _makeConnections(self):
        self._ui.create_button.clicked.connect(self._materialCreateClicked)
        self._ui.delete_button.clicked.connect(self._materialDeleteClicked)
        self._ui.materials_listView.clicked.connect(self._materialListItemClicked)
        self._ui.ambientSelectColour_button.clicked.connect(self._selectColourClicked)
        self._ui.diffuseSelectColour_button.clicked.connect(self._selectColourClicked)
        self._ui.emittedSelectColour_button.clicked.connect(self._selectColourClicked)
        self._ui.specularSelectColour_button.clicked.connect(self._selectColourClicked)
        self._ui.alpha_lineEdit.editingFinished.connect(self._alphaEntered)
        self._ui.alpha_slider.valueChanged.connect(self._alphaSliderValueChanged)
        self._ui.shininess_lineEdit.editingFinished.connect(self._shininessEntered)
        self._ui.shininess_slider.valueChanged.connect(self._shininessSliderValueChanged)
        self._ui.sceneviewerWidgetPreview.graphicsInitialized.connect(self._previewGraphicsInitialised)
        self._ui.texture_comboBox.currentIndexChanged.connect(self._textureChanged)
        self._ui.region_comboBox.currentIndexChanged.connect(self._regionChanged)
        self._ui.imageField_comboBox.currentIndexChanged.connect(self._imageFieldChanged)

    def setMaterials(self, materials):
        """
        Sets the Argon materials object which supplies the zinc context and has utilities for
        managing materials.
        
        :param materials: ArgonMaterials object
        """
        self._materials = materials
        self._zincContext = materials.getZincContext()
        self._ui.sceneviewerWidgetPreview.setContext(self._zincContext)
        self._previewZincRegion = self._zincContext.createRegion()
        self._previewZincRegion.setName("Material editor preview region")
        self._previewZincScene = self._previewZincRegion.getScene()
        sceneviewer = self._ui.sceneviewerWidgetPreview.getSceneviewer()
        if sceneviewer:
            self._setupPreviewScene(sceneviewer)

        material_module = self._zincContext.getMaterialmodule()
        self._material_model.setMaterialModule(material_module)
        # Sadly not possible.
        # self._materialmodulenotifier = material_module.createMaterialmodulenotifier()
        # self._materialmodulenotifier.setCallback(self._materialmoduleCallback)

    def _materialmoduleCallback(self, materialModuleEvent):
        """
        Material module does not have a notifier.
        """
        changeSummary = materialModuleEvent.getSummarySpectrumChangeFlags()
        if 0 != (changeSummary & (Material.CHANGE_FLAG_IDENTIFIER | Material.CHANGE_FLAG_ADD | Material.CHANGE_FLAG_REMOVE)):
            self._material_model.reset()

    def _materialCreateClicked(self):
        """
        Create a new material.
        """
        index = self._material_model.createIndex(self._material_model.rowCount(None), 0)
        self._material_model.addData()
        self._ui.materials_listView.clearSelection()
        self._ui.materials_listView.selectionModel().setCurrentIndex(index, QtCore.QItemSelectionModel.SelectCurrent)
        self._updateCurrentMaterial(self._material_model.getMaterialForIndex(index))

    def _materialDeleteClicked(self):
        """
        Delete the currently selected material.
        """
        selection = self._ui.materials_listView.selectedIndexes()
        self._clearCurrentMaterial()
        if self._material_model.removeData(selection):
            self._ui.materials_listView.clearSelection()
        else:
            if len(selection):
                # Re-instate current material after failed deletion.
                self._materialListItemClicked(selection[0])
            QtWidgets.QMessageBox.information(self, "Info", "This material is still in use and can't be deleted.")

    def _materialListItemClicked(self, modelIndex):
        if modelIndex.row() != self._currentMaterialIndex:
            self._currentMaterialIndex = modelIndex.row()
            self._updateCurrentMaterial(self._material_model.getMaterialForIndex(modelIndex))

    def _updateCurrentMaterial(self, material):
        self._currentMaterial = material
        self._displayMaterial()

    def _displayMaterial(self):
        """
        Display the currently chosen material
        """
        self._updateButtonColour()
        self._updateAlpha()
        self._updateShininess()
        self._buildTextureComboBox()
        self._buildRegionComboBox()
        self._previewMaterial()

    def _updateButtonColour(self):
        ambientColour, diffuseColour, emissionColour, specularColour = self._getCurrentMaterialColour()
        self._ui.ambientSelectColour_button.setStyleSheet("background-color: {}".format(ambientColour.name()))
        self._ui.diffuseSelectColour_button.setStyleSheet("background-color: {}".format(diffuseColour.name()))
        self._ui.emittedSelectColour_button.setStyleSheet("background-color: {}".format(emissionColour.name()))
        self._ui.specularSelectColour_button.setStyleSheet("background-color: {}".format(specularColour.name()))

    def _getCurrentMaterialColour(self):
        result, ambientColour = self._currentMaterial.getAttributeReal3(Material.ATTRIBUTE_AMBIENT)
        result, diffuseColour = self._currentMaterial.getAttributeReal3(Material.ATTRIBUTE_DIFFUSE)
        result, emissionColour = self._currentMaterial.getAttributeReal3(Material.ATTRIBUTE_EMISSION)
        result, specularColour = self._currentMaterial.getAttributeReal3(Material.ATTRIBUTE_SPECULAR)
        intAmbientColour = QtGui.QColor(int(ambientColour[0]*255), int(ambientColour[1]*255), int(ambientColour[2]*255))
        intDiffuseColour = QtGui.QColor(int(diffuseColour[0]*255), int(diffuseColour[1]*255), int(diffuseColour[2]*255))
        intEmissionColour = QtGui.QColor(int(emissionColour[0]*255), int(emissionColour[1]*255), int(emissionColour[2]*255))
        intSpecularColour = QtGui.QColor(int(specularColour[0]*255), int(specularColour[1]*255), int(specularColour[2]*255))
        return intAmbientColour, intDiffuseColour, intEmissionColour, intSpecularColour

    def _selectColourClicked(self, event):
        sender = self.sender()
        colorDialog = QtWidgets.QColorDialog(sender)
        colorDialog.setCurrentColor(sender.palette().button().color())
        color = colorDialog.getColor(initial = sender.palette().button().color())
        if color.isValid():
            self.sender().setStyleSheet("background-color: {}".format(color.name()))
            self._setMaterialColour(sender)
    
    def _setMaterialColour(self, attributeButton):
        if attributeButton == self._ui.ambientSelectColour_button:
            materialAttribute = Material.ATTRIBUTE_AMBIENT
        elif attributeButton == self._ui.diffuseSelectColour_button:
            materialAttribute = Material.ATTRIBUTE_DIFFUSE
        elif attributeButton == self._ui.emittedSelectColour_button:
            materialAttribute = Material.ATTRIBUTE_EMISSION
        elif attributeButton == self._ui.specularSelectColour_button:
            materialAttribute = Material.ATTRIBUTE_SPECULAR
        buttonColour = attributeButton.palette().button().color()
        colourF = [buttonColour.redF(), buttonColour.greenF(), buttonColour.blueF()]
        self._currentMaterial.setAttributeReal3(materialAttribute, colourF)

    def _alphaEntered(self):
        value = self._ui.alpha_lineEdit.text()
        self._currentMaterial.setAttributeReal(Material.ATTRIBUTE_ALPHA, float(value))
        self._updateAlpha()

    def _alphaSliderValueChanged(self):
        value = self._ui.alpha_slider.value()/100
        self._currentMaterial.setAttributeReal(Material.ATTRIBUTE_ALPHA, value)
        self._updateAlpha()

    def _updateAlpha(self):
        alpha = self._currentMaterial.getAttributeReal(Material.ATTRIBUTE_ALPHA)
        self._ui.alpha_slider.setValue(alpha*100)
        self._ui.alpha_lineEdit.setText(str(alpha))

    def _shininessEntered(self):
        value = self._ui.shininess_lineEdit.text()
        self._currentMaterial.setAttributeReal(Material.ATTRIBUTE_SHININESS, float(value))
        self._updateShininess()

    def _shininessSliderValueChanged(self):
        value = self._ui.shininess_slider.value()/100
        self._currentMaterial.setAttributeReal(Material.ATTRIBUTE_SHININESS, value)
        self._updateShininess()

    def _updateShininess(self):
        shininess = self._currentMaterial.getAttributeReal(Material.ATTRIBUTE_SHININESS)
        self._ui.shininess_slider.setValue(shininess*100)
        self._ui.shininess_lineEdit.setText(str(shininess))

    def _buildTextureComboBox(self):
        self._ui.texture_comboBox.clear()
        for i in range(4):
            self._ui.texture_comboBox.addItem("%d"%(i + 1))

    def _buildRegionComboBox(self):
        self._ui.region_comboBox.setRootRegion(self._zincContext.getDefaultRegion())
    
    def _buildImageFieldComboBox(self, region):
        self._ui.imageField_comboBox.clear()
        self._ui.imageField_comboBox.setConditional(is_field_image)
        self._ui.imageField_comboBox.setRegion(region)

    def _textureChanged(self, index):
        texture = self._currentMaterial.getTextureField(index)

    def _regionChanged(self, index):
        self._buildImageFieldComboBox(self._ui.region_comboBox.getRegion())
    
    def _imageFieldChanged(self, index):
        texture = self._ui.texture_comboBox.currentIndex() + 1
        imageField = self._ui.region_comboBox.getRegion().getFieldmodule().findFieldByName(self._ui.imageField_comboBox.currentText())
        self._currentMaterial.setTextureField(texture, imageField)

    def _clearCurrentMaterial(self):
        self._currentMaterial = None
        self._currentMaterialIndex = None
        self._previewZincScene.removeAllGraphics()
    
    def _previewMaterial(self):
        if self._previewZincScene is None:
            return
        if (self._currentMaterial is None) or (not self._currentMaterial.isValid()):
            self._previewZincScene.removeAllGraphics()
            return
        points = self._previewZincScene.getFirstGraphics()
        self._previewZincScene.beginChange()
        if not points.isValid():
            points = self._previewZincScene.createGraphicsPoints()
            pointsattr = points.getGraphicspointattributes()
            pointsattr.setBaseSize(1.0)
            tessellationModule = self._previewZincScene.getTessellationmodule()
            tessellation = tessellationModule.findTessellationByName("material_preview")
            if not tessellation.isValid():
                tessellation = tessellationModule.createTessellation()
                tessellation.setName("material_preview")
                tessellation.setManaged(False)
                tessellation.setCircleDivisions(48)
            points.setTessellation(tessellation)
        else:
            pointsattr = points.getGraphicspointattributes()
        pointsattr.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        points.setMaterial(self._currentMaterial)
        self._previewZincScene.endChange()

    def _setupPreviewScene(self, sceneviewer):
        with ChangeManager(sceneviewer):
            sceneviewer.setScene(self._previewZincScene)
            sceneviewer.setZoomRate(0)
            sceneviewer.setTumbleRate(0)
            sceneviewer.setTranslationRate(0)
            sceneviewer.setLookatParametersNonSkew([3.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.0])
            sceneviewer.setViewAngle(0.679673818908244)
            sceneviewer.setNearClippingPlane(2.4)
            sceneviewer.setFarClippingPlane(3.0)

    def _previewGraphicsInitialised(self):
        sceneviewer = self._ui.sceneviewerWidgetPreview.getSceneviewer()
        if sceneviewer:
            self._setupPreviewScene(sceneviewer)
