# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'spectrumeditorwidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from opencmiss.zincwidgets.sceneviewerwidget import SceneviewerWidget

from opencmiss.zincwidgets.ui import icons_rc

class Ui_SpectrumEditorWidget(object):
    def setupUi(self, SpectrumEditorWidget):
        if not SpectrumEditorWidget.objectName():
            SpectrumEditorWidget.setObjectName(u"SpectrumEditorWidget")
        SpectrumEditorWidget.resize(300, 875)
        self.verticalLayout = QVBoxLayout(SpectrumEditorWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(SpectrumEditorWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 298, 873))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setContentsMargins(7, 7, 7, 7)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.widget_2 = QWidget(self.groupBox)
        self.widget_2.setObjectName(u"widget_2")
        self.verticalLayout_3 = QVBoxLayout(self.widget_2)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.pushButtonAddSpectrum = QPushButton(self.widget_2)
        self.pushButtonAddSpectrum.setObjectName(u"pushButtonAddSpectrum")
        icon = QIcon()
        icon.addFile(u":/zincwidgets/images/icons/list-add-icon.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButtonAddSpectrum.setIcon(icon)

        self.verticalLayout_3.addWidget(self.pushButtonAddSpectrum)

        self.pushButtonDeleteSpectrum = QPushButton(self.widget_2)
        self.pushButtonDeleteSpectrum.setObjectName(u"pushButtonDeleteSpectrum")
        icon1 = QIcon()
        icon1.addFile(u":/zincwidgets/images/icons/list-remove-icon.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButtonDeleteSpectrum.setIcon(icon1)

        self.verticalLayout_3.addWidget(self.pushButtonDeleteSpectrum)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)


        self.horizontalLayout_2.addWidget(self.widget_2)

        self.listWidgetSpectrums = QListWidget(self.groupBox)
        self.listWidgetSpectrums.setObjectName(u"listWidgetSpectrums")

        self.horizontalLayout_2.addWidget(self.listWidgetSpectrums)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.sceneviewerWidgetPreview = SceneviewerWidget(self.scrollAreaWidgetContents)
        self.sceneviewerWidgetPreview.setObjectName(u"sceneviewerWidgetPreview")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.sceneviewerWidgetPreview.sizePolicy().hasHeightForWidth())
        self.sceneviewerWidgetPreview.setSizePolicy(sizePolicy1)
        self.sceneviewerWidgetPreview.setMinimumSize(QSize(0, 40))

        self.verticalLayout_2.addWidget(self.sceneviewerWidgetPreview)

        self.groupBoxSpectrumProperties = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxSpectrumProperties.setObjectName(u"groupBoxSpectrumProperties")
        self.horizontalLayout_4 = QHBoxLayout(self.groupBoxSpectrumProperties)
        self.horizontalLayout_4.setContentsMargins(7, 7, 7, 7)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.checkBoxDefault = QCheckBox(self.groupBoxSpectrumProperties)
        self.checkBoxDefault.setObjectName(u"checkBoxDefault")

        self.horizontalLayout_4.addWidget(self.checkBoxDefault)

        self.checkBoxOverwrite = QCheckBox(self.groupBoxSpectrumProperties)
        self.checkBoxOverwrite.setObjectName(u"checkBoxOverwrite")

        self.horizontalLayout_4.addWidget(self.checkBoxOverwrite)

        self.pushButtonAutorange = QPushButton(self.groupBoxSpectrumProperties)
        self.pushButtonAutorange.setObjectName(u"pushButtonAutorange")

        self.horizontalLayout_4.addWidget(self.pushButtonAutorange)


        self.verticalLayout_2.addWidget(self.groupBoxSpectrumProperties)

        self.groupBoxComponents = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxComponents.setObjectName(u"groupBoxComponents")
        sizePolicy.setHeightForWidth(self.groupBoxComponents.sizePolicy().hasHeightForWidth())
        self.groupBoxComponents.setSizePolicy(sizePolicy)
        self.horizontalLayout_3 = QHBoxLayout(self.groupBoxComponents)
        self.horizontalLayout_3.setContentsMargins(7, 7, 7, 7)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.widget_4 = QWidget(self.groupBoxComponents)
        self.widget_4.setObjectName(u"widget_4")
        self.verticalLayout_5 = QVBoxLayout(self.widget_4)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.pushButtonAddSpectrumComponent = QPushButton(self.widget_4)
        self.pushButtonAddSpectrumComponent.setObjectName(u"pushButtonAddSpectrumComponent")
        self.pushButtonAddSpectrumComponent.setIcon(icon)

        self.verticalLayout_5.addWidget(self.pushButtonAddSpectrumComponent)

        self.pushButtonDeleteSpectrumComponent = QPushButton(self.widget_4)
        self.pushButtonDeleteSpectrumComponent.setObjectName(u"pushButtonDeleteSpectrumComponent")
        self.pushButtonDeleteSpectrumComponent.setIcon(icon1)

        self.verticalLayout_5.addWidget(self.pushButtonDeleteSpectrumComponent)

        self.pushButtonMoveUpSpectrumComponent = QPushButton(self.widget_4)
        self.pushButtonMoveUpSpectrumComponent.setObjectName(u"pushButtonMoveUpSpectrumComponent")
        icon2 = QIcon()
        icon2.addFile(u":/zincwidgets/images/icons/go-up-icon.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButtonMoveUpSpectrumComponent.setIcon(icon2)

        self.verticalLayout_5.addWidget(self.pushButtonMoveUpSpectrumComponent)

        self.pushButtonMoveDownSpectrumComponent = QPushButton(self.widget_4)
        self.pushButtonMoveDownSpectrumComponent.setObjectName(u"pushButtonMoveDownSpectrumComponent")
        icon3 = QIcon()
        icon3.addFile(u":/zincwidgets/images/icons/go-down-icon.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButtonMoveDownSpectrumComponent.setIcon(icon3)

        self.verticalLayout_5.addWidget(self.pushButtonMoveDownSpectrumComponent)


        self.horizontalLayout_3.addWidget(self.widget_4)

        self.listWidgetSpectrumComponents = QListWidget(self.groupBoxComponents)
        self.listWidgetSpectrumComponents.setObjectName(u"listWidgetSpectrumComponents")
        self.listWidgetSpectrumComponents.setDragDropMode(QAbstractItemView.InternalMove)
        self.listWidgetSpectrumComponents.setMovement(QListView.Free)

        self.horizontalLayout_3.addWidget(self.listWidgetSpectrumComponents)


        self.verticalLayout_2.addWidget(self.groupBoxComponents)

        self.groupBoxComponentProperties = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxComponentProperties.setObjectName(u"groupBoxComponentProperties")
        self.formLayout_2 = QFormLayout(self.groupBoxComponentProperties)
        self.formLayout_2.setContentsMargins(7, 7, 7, 7)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.labelFieldComponent = QLabel(self.groupBoxComponentProperties)
        self.labelFieldComponent.setObjectName(u"labelFieldComponent")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.labelFieldComponent)

        self.spinBoxDataFieldComponent = QSpinBox(self.groupBoxComponentProperties)
        self.spinBoxDataFieldComponent.setObjectName(u"spinBoxDataFieldComponent")
        self.spinBoxDataFieldComponent.setValue(1)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.spinBoxDataFieldComponent)

        self.labelColourMap = QLabel(self.groupBoxComponentProperties)
        self.labelColourMap.setObjectName(u"labelColourMap")

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.labelColourMap)

        self.comboBoxColourMap = QComboBox(self.groupBoxComponentProperties)
        self.comboBoxColourMap.setObjectName(u"comboBoxColourMap")

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.comboBoxColourMap)

        self.groupBox_3 = QGroupBox(self.groupBoxComponentProperties)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout = QGridLayout(self.groupBox_3)
        self.gridLayout.setContentsMargins(7, 7, 7, 7)
        self.gridLayout.setObjectName(u"gridLayout")
        self.checkBoxFixMinimum = QCheckBox(self.groupBox_3)
        self.checkBoxFixMinimum.setObjectName(u"checkBoxFixMinimum")

        self.gridLayout.addWidget(self.checkBoxFixMinimum, 1, 1, 1, 1)

        self.checkBoxExtendBelow = QCheckBox(self.groupBox_3)
        self.checkBoxExtendBelow.setObjectName(u"checkBoxExtendBelow")

        self.gridLayout.addWidget(self.checkBoxExtendBelow, 1, 4, 1, 1)

        self.lineEditDataRangeMax = QLineEdit(self.groupBox_3)
        self.lineEditDataRangeMax.setObjectName(u"lineEditDataRangeMax")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(2)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lineEditDataRangeMax.sizePolicy().hasHeightForWidth())
        self.lineEditDataRangeMax.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.lineEditDataRangeMax, 2, 2, 1, 1)

        self.labelRangeMaximum = QLabel(self.groupBox_3)
        self.labelRangeMaximum.setObjectName(u"labelRangeMaximum")

        self.gridLayout.addWidget(self.labelRangeMaximum, 2, 0, 1, 1)

        self.labelRangeColour = QLabel(self.groupBox_3)
        self.labelRangeColour.setObjectName(u"labelRangeColour")

        self.gridLayout.addWidget(self.labelRangeColour, 0, 3, 1, 1)

        self.labelRangeMinimum = QLabel(self.groupBox_3)
        self.labelRangeMinimum.setObjectName(u"labelRangeMinimum")

        self.gridLayout.addWidget(self.labelRangeMinimum, 1, 0, 1, 1)

        self.lineEditDataRangeMin = QLineEdit(self.groupBox_3)
        self.lineEditDataRangeMin.setObjectName(u"lineEditDataRangeMin")
        sizePolicy2.setHeightForWidth(self.lineEditDataRangeMin.sizePolicy().hasHeightForWidth())
        self.lineEditDataRangeMin.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.lineEditDataRangeMin, 1, 2, 1, 1)

        self.checkBoxFixMaximum = QCheckBox(self.groupBox_3)
        self.checkBoxFixMaximum.setObjectName(u"checkBoxFixMaximum")

        self.gridLayout.addWidget(self.checkBoxFixMaximum, 2, 1, 1, 1)

        self.lineEditColourRangeMax = QLineEdit(self.groupBox_3)
        self.lineEditColourRangeMax.setObjectName(u"lineEditColourRangeMax")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.lineEditColourRangeMax.sizePolicy().hasHeightForWidth())
        self.lineEditColourRangeMax.setSizePolicy(sizePolicy3)

        self.gridLayout.addWidget(self.lineEditColourRangeMax, 2, 3, 1, 1)

        self.checkBoxExtendAbove = QCheckBox(self.groupBox_3)
        self.checkBoxExtendAbove.setObjectName(u"checkBoxExtendAbove")

        self.gridLayout.addWidget(self.checkBoxExtendAbove, 2, 4, 1, 1)

        self.labelRangeExtend = QLabel(self.groupBox_3)
        self.labelRangeExtend.setObjectName(u"labelRangeExtend")

        self.gridLayout.addWidget(self.labelRangeExtend, 0, 4, 1, 1)

        self.lineEditColourRangeMin = QLineEdit(self.groupBox_3)
        self.lineEditColourRangeMin.setObjectName(u"lineEditColourRangeMin")
        sizePolicy3.setHeightForWidth(self.lineEditColourRangeMin.sizePolicy().hasHeightForWidth())
        self.lineEditColourRangeMin.setSizePolicy(sizePolicy3)

        self.gridLayout.addWidget(self.lineEditColourRangeMin, 1, 3, 1, 1)

        self.labelRangeData = QLabel(self.groupBox_3)
        self.labelRangeData.setObjectName(u"labelRangeData")

        self.gridLayout.addWidget(self.labelRangeData, 0, 2, 1, 1)

        self.labelRangeFix = QLabel(self.groupBox_3)
        self.labelRangeFix.setObjectName(u"labelRangeFix")

        self.gridLayout.addWidget(self.labelRangeFix, 0, 1, 1, 1)


        self.formLayout_2.setWidget(6, QFormLayout.SpanningRole, self.groupBox_3)

        self.labelScaleType = QLabel(self.groupBoxComponentProperties)
        self.labelScaleType.setObjectName(u"labelScaleType")

        self.formLayout_2.setWidget(8, QFormLayout.LabelRole, self.labelScaleType)

        self.comboBoxScale = QComboBox(self.groupBoxComponentProperties)
        self.comboBoxScale.setObjectName(u"comboBoxScale")

        self.formLayout_2.setWidget(8, QFormLayout.FieldRole, self.comboBoxScale)

        self.labelExaggeration = QLabel(self.groupBoxComponentProperties)
        self.labelExaggeration.setObjectName(u"labelExaggeration")

        self.formLayout_2.setWidget(9, QFormLayout.LabelRole, self.labelExaggeration)

        self.lineEditExaggeration = QLineEdit(self.groupBoxComponentProperties)
        self.lineEditExaggeration.setObjectName(u"lineEditExaggeration")

        self.formLayout_2.setWidget(9, QFormLayout.FieldRole, self.lineEditExaggeration)

        self.pushButtonReverseColours = QPushButton(self.groupBoxComponentProperties)
        self.pushButtonReverseColours.setObjectName(u"pushButtonReverseColours")

        self.formLayout_2.setWidget(7, QFormLayout.FieldRole, self.pushButtonReverseColours)


        self.verticalLayout_2.addWidget(self.groupBoxComponentProperties)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(SpectrumEditorWidget)

        QMetaObject.connectSlotsByName(SpectrumEditorWidget)
    # setupUi

    def retranslateUi(self, SpectrumEditorWidget):
        SpectrumEditorWidget.setWindowTitle(QCoreApplication.translate("SpectrumEditorWidget", u"Spectrum Editor", None))
        self.groupBox.setTitle(QCoreApplication.translate("SpectrumEditorWidget", u"Spectrums", None))
#if QT_CONFIG(tooltip)
        self.pushButtonAddSpectrum.setToolTip(QCoreApplication.translate("SpectrumEditorWidget", u"Add spectrum", None))
#endif // QT_CONFIG(tooltip)
        self.pushButtonAddSpectrum.setText("")
#if QT_CONFIG(tooltip)
        self.pushButtonDeleteSpectrum.setToolTip(QCoreApplication.translate("SpectrumEditorWidget", u"Remove spectrum", None))
#endif // QT_CONFIG(tooltip)
        self.pushButtonDeleteSpectrum.setText("")
        self.groupBoxSpectrumProperties.setTitle("")
        self.checkBoxDefault.setText(QCoreApplication.translate("SpectrumEditorWidget", u"Default", None))
#if QT_CONFIG(tooltip)
        self.checkBoxOverwrite.setToolTip(QCoreApplication.translate("SpectrumEditorWidget", u"Overwrite graphics material colour with spectrum colour", None))
#endif // QT_CONFIG(tooltip)
        self.checkBoxOverwrite.setText(QCoreApplication.translate("SpectrumEditorWidget", u"Overwrite", None))
        self.pushButtonAutorange.setText(QCoreApplication.translate("SpectrumEditorWidget", u"Autorange", None))
        self.groupBoxComponents.setTitle(QCoreApplication.translate("SpectrumEditorWidget", u"Components", None))
#if QT_CONFIG(tooltip)
        self.pushButtonAddSpectrumComponent.setToolTip(QCoreApplication.translate("SpectrumEditorWidget", u"Add component", None))
#endif // QT_CONFIG(tooltip)
        self.pushButtonAddSpectrumComponent.setText("")
#if QT_CONFIG(tooltip)
        self.pushButtonDeleteSpectrumComponent.setToolTip(QCoreApplication.translate("SpectrumEditorWidget", u"Remove component", None))
#endif // QT_CONFIG(tooltip)
        self.pushButtonDeleteSpectrumComponent.setText("")
#if QT_CONFIG(tooltip)
        self.pushButtonMoveUpSpectrumComponent.setToolTip(QCoreApplication.translate("SpectrumEditorWidget", u"Move component up", None))
#endif // QT_CONFIG(tooltip)
        self.pushButtonMoveUpSpectrumComponent.setText("")
#if QT_CONFIG(tooltip)
        self.pushButtonMoveDownSpectrumComponent.setToolTip(QCoreApplication.translate("SpectrumEditorWidget", u"Move component down", None))
#endif // QT_CONFIG(tooltip)
        self.pushButtonMoveDownSpectrumComponent.setText("")
        self.groupBoxComponentProperties.setTitle(QCoreApplication.translate("SpectrumEditorWidget", u"Component Properties", None))
#if QT_CONFIG(tooltip)
        self.labelFieldComponent.setToolTip(QCoreApplication.translate("SpectrumEditorWidget", u"Index of component to use from data field", None))
#endif // QT_CONFIG(tooltip)
        self.labelFieldComponent.setText(QCoreApplication.translate("SpectrumEditorWidget", u"Field component:", None))
#if QT_CONFIG(tooltip)
        self.spinBoxDataFieldComponent.setToolTip(QCoreApplication.translate("SpectrumEditorWidget", u"Index of component to use from data field", None))
#endif // QT_CONFIG(tooltip)
        self.labelColourMap.setText(QCoreApplication.translate("SpectrumEditorWidget", u"Colour map:", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("SpectrumEditorWidget", u"Range", None))
        self.checkBoxFixMinimum.setText("")
        self.checkBoxExtendBelow.setText("")
        self.lineEditDataRangeMax.setText(QCoreApplication.translate("SpectrumEditorWidget", u"1", None))
#if QT_CONFIG(tooltip)
        self.labelRangeMaximum.setToolTip(QCoreApplication.translate("SpectrumEditorWidget", u"Component to use from data field", None))
#endif // QT_CONFIG(tooltip)
        self.labelRangeMaximum.setText(QCoreApplication.translate("SpectrumEditorWidget", u"Max:", None))
        self.labelRangeColour.setText(QCoreApplication.translate("SpectrumEditorWidget", u"Colour:", None))
#if QT_CONFIG(tooltip)
        self.labelRangeMinimum.setToolTip(QCoreApplication.translate("SpectrumEditorWidget", u"Component to use from data field", None))
#endif // QT_CONFIG(tooltip)
        self.labelRangeMinimum.setText(QCoreApplication.translate("SpectrumEditorWidget", u"Min:", None))
        self.lineEditDataRangeMin.setText(QCoreApplication.translate("SpectrumEditorWidget", u"0", None))
        self.checkBoxFixMaximum.setText("")
        self.lineEditColourRangeMax.setText(QCoreApplication.translate("SpectrumEditorWidget", u"1", None))
        self.checkBoxExtendAbove.setText("")
        self.labelRangeExtend.setText(QCoreApplication.translate("SpectrumEditorWidget", u"Ext", None))
        self.lineEditColourRangeMin.setText(QCoreApplication.translate("SpectrumEditorWidget", u"0", None))
#if QT_CONFIG(tooltip)
        self.labelRangeData.setToolTip(QCoreApplication.translate("SpectrumEditorWidget", u"Component to use from data field", None))
#endif // QT_CONFIG(tooltip)
        self.labelRangeData.setText(QCoreApplication.translate("SpectrumEditorWidget", u"Data:", None))
        self.labelRangeFix.setText(QCoreApplication.translate("SpectrumEditorWidget", u"Fix", None))
        self.labelScaleType.setText(QCoreApplication.translate("SpectrumEditorWidget", u"Scale type:", None))
        self.labelExaggeration.setText(QCoreApplication.translate("SpectrumEditorWidget", u"Exaggeration:", None))
        self.pushButtonReverseColours.setText(QCoreApplication.translate("SpectrumEditorWidget", u"Reverse colours", None))
    # retranslateUi

