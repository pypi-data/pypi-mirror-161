# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'graphicseditorwidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from opencmiss.zincwidgets.fieldchooserwidget import FieldChooserWidget
from opencmiss.zincwidgets.materialchooserwidget import MaterialChooserWidget
from opencmiss.zincwidgets.enumerationchooserwidget import EnumerationChooserWidget
from opencmiss.zincwidgets.glyphchooserwidget import GlyphChooserWidget
from opencmiss.zincwidgets.spectrumchooserwidget import SpectrumChooserWidget
from opencmiss.zincwidgets.tessellationchooserwidget import TessellationChooserWidget


class Ui_GraphicsEditorWidget(object):
    def setupUi(self, GraphicsEditorWidget):
        if not GraphicsEditorWidget.objectName():
            GraphicsEditorWidget.setObjectName(u"GraphicsEditorWidget")
        GraphicsEditorWidget.setEnabled(True)
        GraphicsEditorWidget.resize(298, 1218)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(GraphicsEditorWidget.sizePolicy().hasHeightForWidth())
        GraphicsEditorWidget.setSizePolicy(sizePolicy)
        GraphicsEditorWidget.setMinimumSize(QSize(180, 0))
        self.verticalLayout = QVBoxLayout(GraphicsEditorWidget)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(2, 0, 0, 0)
        self.general_groupbox = QGroupBox(GraphicsEditorWidget)
        self.general_groupbox.setObjectName(u"general_groupbox")
        self.general_groupbox.setMaximumSize(QSize(16777215, 16777215))
        self.general_groupbox.setCheckable(False)
        self.formLayout_3 = QFormLayout(self.general_groupbox)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.subgroup_field_label = QLabel(self.general_groupbox)
        self.subgroup_field_label.setObjectName(u"subgroup_field_label")

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.subgroup_field_label)

        self.subgroup_field_chooser = FieldChooserWidget(self.general_groupbox)
        self.subgroup_field_chooser.setObjectName(u"subgroup_field_chooser")

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.subgroup_field_chooser)

        self.coordinate_field_label = QLabel(self.general_groupbox)
        self.coordinate_field_label.setObjectName(u"coordinate_field_label")

        self.formLayout_3.setWidget(2, QFormLayout.LabelRole, self.coordinate_field_label)

        self.coordinate_field_chooser = FieldChooserWidget(self.general_groupbox)
        self.coordinate_field_chooser.setObjectName(u"coordinate_field_chooser")
        self.coordinate_field_chooser.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.formLayout_3.setWidget(2, QFormLayout.FieldRole, self.coordinate_field_chooser)

        self.scenecoordinatesystem_label = QLabel(self.general_groupbox)
        self.scenecoordinatesystem_label.setObjectName(u"scenecoordinatesystem_label")

        self.formLayout_3.setWidget(4, QFormLayout.LabelRole, self.scenecoordinatesystem_label)

        self.scenecoordinatesystem_chooser = EnumerationChooserWidget(self.general_groupbox)
        self.scenecoordinatesystem_chooser.setObjectName(u"scenecoordinatesystem_chooser")

        self.formLayout_3.setWidget(4, QFormLayout.FieldRole, self.scenecoordinatesystem_chooser)

        self.domain_label = QLabel(self.general_groupbox)
        self.domain_label.setObjectName(u"domain_label")

        self.formLayout_3.setWidget(6, QFormLayout.LabelRole, self.domain_label)

        self.boundarymode_label = QLabel(self.general_groupbox)
        self.boundarymode_label.setObjectName(u"boundarymode_label")

        self.formLayout_3.setWidget(8, QFormLayout.LabelRole, self.boundarymode_label)

        self.boundarymode_chooser = EnumerationChooserWidget(self.general_groupbox)
        self.boundarymode_chooser.setObjectName(u"boundarymode_chooser")

        self.formLayout_3.setWidget(8, QFormLayout.FieldRole, self.boundarymode_chooser)

        self.face_label = QLabel(self.general_groupbox)
        self.face_label.setObjectName(u"face_label")

        self.formLayout_3.setWidget(10, QFormLayout.LabelRole, self.face_label)

        self.face_enumeration_chooser = EnumerationChooserWidget(self.general_groupbox)
        self.face_enumeration_chooser.setObjectName(u"face_enumeration_chooser")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.face_enumeration_chooser.sizePolicy().hasHeightForWidth())
        self.face_enumeration_chooser.setSizePolicy(sizePolicy1)

        self.formLayout_3.setWidget(10, QFormLayout.FieldRole, self.face_enumeration_chooser)

        self.wireframe_checkbox = QCheckBox(self.general_groupbox)
        self.wireframe_checkbox.setObjectName(u"wireframe_checkbox")

        self.formLayout_3.setWidget(12, QFormLayout.SpanningRole, self.wireframe_checkbox)

        self.material_label = QLabel(self.general_groupbox)
        self.material_label.setObjectName(u"material_label")

        self.formLayout_3.setWidget(13, QFormLayout.LabelRole, self.material_label)

        self.material_chooser = MaterialChooserWidget(self.general_groupbox)
        self.material_chooser.setObjectName(u"material_chooser")
        self.material_chooser.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.formLayout_3.setWidget(13, QFormLayout.FieldRole, self.material_chooser)

        self.data_field_label = QLabel(self.general_groupbox)
        self.data_field_label.setObjectName(u"data_field_label")

        self.formLayout_3.setWidget(15, QFormLayout.LabelRole, self.data_field_label)

        self.data_field_chooser = FieldChooserWidget(self.general_groupbox)
        self.data_field_chooser.setObjectName(u"data_field_chooser")
        self.data_field_chooser.setEditable(False)
        self.data_field_chooser.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.formLayout_3.setWidget(15, QFormLayout.FieldRole, self.data_field_chooser)

        self.spectrum_label = QLabel(self.general_groupbox)
        self.spectrum_label.setObjectName(u"spectrum_label")

        self.formLayout_3.setWidget(17, QFormLayout.LabelRole, self.spectrum_label)

        self.spectrum_chooser = SpectrumChooserWidget(self.general_groupbox)
        self.spectrum_chooser.setObjectName(u"spectrum_chooser")

        self.formLayout_3.setWidget(17, QFormLayout.FieldRole, self.spectrum_chooser)

        self.tessellation_label = QLabel(self.general_groupbox)
        self.tessellation_label.setObjectName(u"tessellation_label")

        self.formLayout_3.setWidget(19, QFormLayout.LabelRole, self.tessellation_label)

        self.tessellation_chooser = TessellationChooserWidget(self.general_groupbox)
        self.tessellation_chooser.setObjectName(u"tessellation_chooser")

        self.formLayout_3.setWidget(19, QFormLayout.FieldRole, self.tessellation_chooser)

        self.domain_chooser = EnumerationChooserWidget(self.general_groupbox)
        self.domain_chooser.setObjectName(u"domain_chooser")

        self.formLayout_3.setWidget(6, QFormLayout.FieldRole, self.domain_chooser)


        self.verticalLayout.addWidget(self.general_groupbox)

        self.contours_groupbox = QGroupBox(GraphicsEditorWidget)
        self.contours_groupbox.setObjectName(u"contours_groupbox")
        self.contours_groupbox.setMaximumSize(QSize(16777215, 16777215))
        self.contours_groupbox.setFlat(False)
        self.formLayout_2 = QFormLayout(self.contours_groupbox)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setHorizontalSpacing(7)
        self.formLayout_2.setVerticalSpacing(7)
        self.formLayout_2.setContentsMargins(7, 7, 7, 7)
        self.isovalues_lineedit = QLineEdit(self.contours_groupbox)
        self.isovalues_lineedit.setObjectName(u"isovalues_lineedit")

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.isovalues_lineedit)

        self.isoscalar_field_label = QLabel(self.contours_groupbox)
        self.isoscalar_field_label.setObjectName(u"isoscalar_field_label")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.isoscalar_field_label)

        self.isoscalar_field_chooser = FieldChooserWidget(self.contours_groupbox)
        self.isoscalar_field_chooser.setObjectName(u"isoscalar_field_chooser")
        self.isoscalar_field_chooser.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.isoscalar_field_chooser)

        self.isovalues_label = QLabel(self.contours_groupbox)
        self.isovalues_label.setObjectName(u"isovalues_label")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.isovalues_label)


        self.verticalLayout.addWidget(self.contours_groupbox)

        self.streamlines_groupbox = QGroupBox(GraphicsEditorWidget)
        self.streamlines_groupbox.setObjectName(u"streamlines_groupbox")
        self.formLayout_5 = QFormLayout(self.streamlines_groupbox)
        self.formLayout_5.setObjectName(u"formLayout_5")
        self.formLayout_5.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_5.setContentsMargins(7, 7, 7, 7)
        self.stream_vector_field_label = QLabel(self.streamlines_groupbox)
        self.stream_vector_field_label.setObjectName(u"stream_vector_field_label")

        self.formLayout_5.setWidget(0, QFormLayout.LabelRole, self.stream_vector_field_label)

        self.stream_vector_field_chooser = FieldChooserWidget(self.streamlines_groupbox)
        self.stream_vector_field_chooser.setObjectName(u"stream_vector_field_chooser")
        self.stream_vector_field_chooser.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.formLayout_5.setWidget(0, QFormLayout.FieldRole, self.stream_vector_field_chooser)

        self.streamlines_track_length_label = QLabel(self.streamlines_groupbox)
        self.streamlines_track_length_label.setObjectName(u"streamlines_track_length_label")

        self.formLayout_5.setWidget(1, QFormLayout.LabelRole, self.streamlines_track_length_label)

        self.streamlines_track_length_lineedit = QLineEdit(self.streamlines_groupbox)
        self.streamlines_track_length_lineedit.setObjectName(u"streamlines_track_length_lineedit")

        self.formLayout_5.setWidget(1, QFormLayout.FieldRole, self.streamlines_track_length_lineedit)

        self.streamline_track_direction_label = QLabel(self.streamlines_groupbox)
        self.streamline_track_direction_label.setObjectName(u"streamline_track_direction_label")

        self.formLayout_5.setWidget(2, QFormLayout.LabelRole, self.streamline_track_direction_label)

        self.streamlines_track_direction_chooser = EnumerationChooserWidget(self.streamlines_groupbox)
        self.streamlines_track_direction_chooser.setObjectName(u"streamlines_track_direction_chooser")

        self.formLayout_5.setWidget(2, QFormLayout.FieldRole, self.streamlines_track_direction_chooser)

        self.streamlines_colour_data_type_label = QLabel(self.streamlines_groupbox)
        self.streamlines_colour_data_type_label.setObjectName(u"streamlines_colour_data_type_label")

        self.formLayout_5.setWidget(3, QFormLayout.LabelRole, self.streamlines_colour_data_type_label)

        self.streamlines_colour_data_type_chooser = EnumerationChooserWidget(self.streamlines_groupbox)
        self.streamlines_colour_data_type_chooser.setObjectName(u"streamlines_colour_data_type_chooser")

        self.formLayout_5.setWidget(3, QFormLayout.FieldRole, self.streamlines_colour_data_type_chooser)


        self.verticalLayout.addWidget(self.streamlines_groupbox)

        self.lines_groupbox = QGroupBox(GraphicsEditorWidget)
        self.lines_groupbox.setObjectName(u"lines_groupbox")
        self.formLayout_4 = QFormLayout(self.lines_groupbox)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.formLayout_4.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_4.setContentsMargins(7, 7, 7, 7)
        self.line_shape_label = QLabel(self.lines_groupbox)
        self.line_shape_label.setObjectName(u"line_shape_label")

        self.formLayout_4.setWidget(0, QFormLayout.LabelRole, self.line_shape_label)

        self.line_shape_chooser = EnumerationChooserWidget(self.lines_groupbox)
        self.line_shape_chooser.setObjectName(u"line_shape_chooser")

        self.formLayout_4.setWidget(0, QFormLayout.FieldRole, self.line_shape_chooser)

        self.line_base_size_label = QLabel(self.lines_groupbox)
        self.line_base_size_label.setObjectName(u"line_base_size_label")

        self.formLayout_4.setWidget(1, QFormLayout.LabelRole, self.line_base_size_label)

        self.line_base_size_lineedit = QLineEdit(self.lines_groupbox)
        self.line_base_size_lineedit.setObjectName(u"line_base_size_lineedit")

        self.formLayout_4.setWidget(1, QFormLayout.FieldRole, self.line_base_size_lineedit)

        self.line_orientation_scale_field_label = QLabel(self.lines_groupbox)
        self.line_orientation_scale_field_label.setObjectName(u"line_orientation_scale_field_label")

        self.formLayout_4.setWidget(2, QFormLayout.LabelRole, self.line_orientation_scale_field_label)

        self.line_orientation_scale_field_chooser = FieldChooserWidget(self.lines_groupbox)
        self.line_orientation_scale_field_chooser.setObjectName(u"line_orientation_scale_field_chooser")
        sizePolicy1.setHeightForWidth(self.line_orientation_scale_field_chooser.sizePolicy().hasHeightForWidth())
        self.line_orientation_scale_field_chooser.setSizePolicy(sizePolicy1)
        self.line_orientation_scale_field_chooser.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.formLayout_4.setWidget(2, QFormLayout.FieldRole, self.line_orientation_scale_field_chooser)

        self.line_scale_factors_label = QLabel(self.lines_groupbox)
        self.line_scale_factors_label.setObjectName(u"line_scale_factors_label")

        self.formLayout_4.setWidget(3, QFormLayout.LabelRole, self.line_scale_factors_label)

        self.line_scale_factors_lineedit = QLineEdit(self.lines_groupbox)
        self.line_scale_factors_lineedit.setObjectName(u"line_scale_factors_lineedit")

        self.formLayout_4.setWidget(3, QFormLayout.FieldRole, self.line_scale_factors_lineedit)


        self.verticalLayout.addWidget(self.lines_groupbox)

        self.points_groupbox = QGroupBox(GraphicsEditorWidget)
        self.points_groupbox.setObjectName(u"points_groupbox")
        self.points_groupbox.setMaximumSize(QSize(16777215, 16777215))
        self.formLayout = QFormLayout(self.points_groupbox)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setContentsMargins(7, 7, 7, 7)
        self.glyph_label = QLabel(self.points_groupbox)
        self.glyph_label.setObjectName(u"glyph_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.glyph_label)

        self.glyph_chooser = GlyphChooserWidget(self.points_groupbox)
        self.glyph_chooser.setObjectName(u"glyph_chooser")
        self.glyph_chooser.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.glyph_chooser)

        self.point_base_size_label = QLabel(self.points_groupbox)
        self.point_base_size_label.setObjectName(u"point_base_size_label")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.point_base_size_label)

        self.point_base_size_lineedit = QLineEdit(self.points_groupbox)
        self.point_base_size_lineedit.setObjectName(u"point_base_size_lineedit")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.point_base_size_lineedit)

        self.point_orientation_scale_field_label = QLabel(self.points_groupbox)
        self.point_orientation_scale_field_label.setObjectName(u"point_orientation_scale_field_label")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.point_orientation_scale_field_label)

        self.point_orientation_scale_field_chooser = FieldChooserWidget(self.points_groupbox)
        self.point_orientation_scale_field_chooser.setObjectName(u"point_orientation_scale_field_chooser")
        self.point_orientation_scale_field_chooser.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.point_orientation_scale_field_chooser)

        self.point_scale_factors_label = QLabel(self.points_groupbox)
        self.point_scale_factors_label.setObjectName(u"point_scale_factors_label")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.point_scale_factors_label)

        self.label_field_label = QLabel(self.points_groupbox)
        self.label_field_label.setObjectName(u"label_field_label")

        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.label_field_label)

        self.label_field_chooser = FieldChooserWidget(self.points_groupbox)
        self.label_field_chooser.setObjectName(u"label_field_chooser")
        self.label_field_chooser.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.label_field_chooser)

        self.point_scale_factors_lineedit = QLineEdit(self.points_groupbox)
        self.point_scale_factors_lineedit.setObjectName(u"point_scale_factors_lineedit")

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.point_scale_factors_lineedit)


        self.verticalLayout.addWidget(self.points_groupbox)

        self.sampling_groupbox = QGroupBox(GraphicsEditorWidget)
        self.sampling_groupbox.setObjectName(u"sampling_groupbox")
        self.formLayout_6 = QFormLayout(self.sampling_groupbox)
        self.formLayout_6.setObjectName(u"formLayout_6")
        self.formLayout_6.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.sampling_mode_label = QLabel(self.sampling_groupbox)
        self.sampling_mode_label.setObjectName(u"sampling_mode_label")

        self.formLayout_6.setWidget(0, QFormLayout.LabelRole, self.sampling_mode_label)

        self.sampling_mode_chooser = EnumerationChooserWidget(self.sampling_groupbox)
        self.sampling_mode_chooser.setObjectName(u"sampling_mode_chooser")

        self.formLayout_6.setWidget(0, QFormLayout.FieldRole, self.sampling_mode_chooser)


        self.verticalLayout.addWidget(self.sampling_groupbox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(GraphicsEditorWidget)
        self.data_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.dataFieldChanged)
        self.material_chooser.currentIndexChanged.connect(GraphicsEditorWidget.materialChanged)
        self.glyph_chooser.currentIndexChanged.connect(GraphicsEditorWidget.glyphChanged)
        self.point_base_size_lineedit.editingFinished.connect(GraphicsEditorWidget.pointBaseSizeEntered)
        self.point_scale_factors_lineedit.editingFinished.connect(GraphicsEditorWidget.pointScaleFactorsEntered)
        self.point_orientation_scale_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.pointOrientationScaleFieldChanged)
        self.label_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.labelFieldChanged)
        self.isoscalar_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.isoscalarFieldChanged)
        self.wireframe_checkbox.clicked.connect(GraphicsEditorWidget.wireframeClicked)
        self.isovalues_lineedit.editingFinished.connect(GraphicsEditorWidget.isovaluesEntered)
        self.line_base_size_lineedit.editingFinished.connect(GraphicsEditorWidget.lineBaseSizeEntered)
        self.line_orientation_scale_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.lineOrientationScaleFieldChanged)
        self.line_scale_factors_lineedit.editingFinished.connect(GraphicsEditorWidget.lineScaleFactorsEntered)
        self.line_shape_chooser.currentIndexChanged.connect(GraphicsEditorWidget.lineShapeChanged)
        self.stream_vector_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.streamVectorFieldChanged)
        self.sampling_mode_chooser.currentIndexChanged.connect(GraphicsEditorWidget.samplingModeChanged)
        self.streamlines_track_length_lineedit.editingFinished.connect(GraphicsEditorWidget.streamlinesTrackLengthEntered)
        self.coordinate_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.coordinateFieldChanged)
        self.streamlines_track_direction_chooser.currentIndexChanged.connect(GraphicsEditorWidget.streamlinesTrackDirectionChanged)
        self.streamlines_colour_data_type_chooser.currentIndexChanged.connect(GraphicsEditorWidget.streamlinesColourDataTypeChanged)
        self.spectrum_chooser.currentIndexChanged.connect(GraphicsEditorWidget.spectrumChanged)
        self.tessellation_chooser.currentIndexChanged.connect(GraphicsEditorWidget.tessellationChanged)
        self.subgroup_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.subgroupFieldChanged)
        self.face_enumeration_chooser.currentIndexChanged.connect(GraphicsEditorWidget.faceChanged)
        self.scenecoordinatesystem_chooser.currentIndexChanged.connect(GraphicsEditorWidget.scenecoordinatesystemChanged)
        self.boundarymode_chooser.currentIndexChanged.connect(GraphicsEditorWidget.boundarymodeChanged)
        self.domain_chooser.currentIndexChanged.connect(GraphicsEditorWidget.dataFieldChanged)

        QMetaObject.connectSlotsByName(GraphicsEditorWidget)
    # setupUi

    def retranslateUi(self, GraphicsEditorWidget):
        GraphicsEditorWidget.setWindowTitle(QCoreApplication.translate("GraphicsEditorWidget", u"Graphics Editor", None))
        self.general_groupbox.setTitle("")
        self.subgroup_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Subgroup:", None))
        self.coordinate_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Coordinates:", None))
        self.scenecoordinatesystem_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Coord System:", None))
        self.domain_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Domain:", None))
        self.boundarymode_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Boundary Mode:", None))
        self.face_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Face:", None))
        self.wireframe_checkbox.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Wireframe", None))
        self.material_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Material:", None))
        self.data_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Data field:", None))
        self.spectrum_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Spectrum:", None))
        self.tessellation_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Tessellation:", None))
        self.contours_groupbox.setTitle(QCoreApplication.translate("GraphicsEditorWidget", u"Contours:", None))
        self.isoscalar_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Scalar field:", None))
        self.isovalues_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Isovalues:", None))
        self.streamlines_groupbox.setTitle(QCoreApplication.translate("GraphicsEditorWidget", u"Streamlines:", None))
        self.stream_vector_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Vector field:", None))
        self.streamlines_track_length_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Time length:", None))
        self.streamline_track_direction_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Direction:", None))
        self.streamlines_colour_data_type_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Colour data:", None))
        self.lines_groupbox.setTitle(QCoreApplication.translate("GraphicsEditorWidget", u"Lines:", None))
        self.line_shape_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Shape:", None))
        self.line_base_size_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Base size:", None))
        self.line_orientation_scale_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Scale field:", None))
        self.line_scale_factors_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Scaling:", None))
        self.points_groupbox.setTitle(QCoreApplication.translate("GraphicsEditorWidget", u"Points:", None))
        self.glyph_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Glyph:", None))
        self.point_base_size_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Base size:", None))
        self.point_orientation_scale_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Scale field:", None))
        self.point_scale_factors_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Scaling:", None))
        self.label_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Label field:", None))
        self.sampling_groupbox.setTitle(QCoreApplication.translate("GraphicsEditorWidget", u"Sampling:", None))
        self.sampling_mode_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Mode:", None))
    # retranslateUi

