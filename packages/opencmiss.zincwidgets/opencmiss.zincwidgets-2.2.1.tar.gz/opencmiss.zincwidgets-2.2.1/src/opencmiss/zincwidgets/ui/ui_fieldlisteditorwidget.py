# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fieldlisteditorwidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from opencmiss.zincwidgets.fieldeditorwidget import FieldEditorWidget
from opencmiss.zincwidgets.regionchooserwidget import RegionChooserWidget
from opencmiss.zincwidgets.fieldtypechooserwidget import FieldTypeChooserWidget


class Ui_FieldListEditorWidget(object):
    def setupUi(self, FieldListEditorWidget):
        if not FieldListEditorWidget.objectName():
            FieldListEditorWidget.setObjectName(u"FieldListEditorWidget")
        FieldListEditorWidget.resize(304, 729)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(FieldListEditorWidget.sizePolicy().hasHeightForWidth())
        FieldListEditorWidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(FieldListEditorWidget)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.scrollArea = QScrollArea(FieldListEditorWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy1)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 298, 723))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.region_frame = QFrame(self.scrollAreaWidgetContents)
        self.region_frame.setObjectName(u"region_frame")
        self.region_frame.setFrameShape(QFrame.StyledPanel)
        self.region_frame.setFrameShadow(QFrame.Raised)
        self.formLayout = QFormLayout(self.region_frame)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 2, 0, 2)
        self.region_label = QLabel(self.region_frame)
        self.region_label.setObjectName(u"region_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.region_label)

        self.region_chooser = RegionChooserWidget(self.region_frame)
        self.region_chooser.setObjectName(u"region_chooser")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.region_chooser)


        self.verticalLayout_2.addWidget(self.region_frame)

        self.field_listview = QListView(self.scrollAreaWidgetContents)
        self.field_listview.setObjectName(u"field_listview")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.field_listview.sizePolicy().hasHeightForWidth())
        self.field_listview.setSizePolicy(sizePolicy2)

        self.verticalLayout_2.addWidget(self.field_listview)

        self.frame = QFrame(self.scrollAreaWidgetContents)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.add_field_type_chooser = FieldTypeChooserWidget(self.frame)
        self.add_field_type_chooser.setObjectName(u"add_field_type_chooser")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.add_field_type_chooser.sizePolicy().hasHeightForWidth())
        self.add_field_type_chooser.setSizePolicy(sizePolicy3)
        self.add_field_type_chooser.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.horizontalLayout.addWidget(self.add_field_type_chooser)

        self.delete_field_button = QPushButton(self.frame)
        self.delete_field_button.setObjectName(u"delete_field_button")

        self.horizontalLayout.addWidget(self.delete_field_button)


        self.verticalLayout_2.addWidget(self.frame)

        self.field_editor = FieldEditorWidget(self.scrollAreaWidgetContents)
        self.field_editor.setObjectName(u"field_editor")
        sizePolicy1.setHeightForWidth(self.field_editor.sizePolicy().hasHeightForWidth())
        self.field_editor.setSizePolicy(sizePolicy1)

        self.verticalLayout_2.addWidget(self.field_editor)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(FieldListEditorWidget)

        QMetaObject.connectSlotsByName(FieldListEditorWidget)
    # setupUi

    def retranslateUi(self, FieldListEditorWidget):
        FieldListEditorWidget.setWindowTitle(QCoreApplication.translate("FieldListEditorWidget", u"Field List Editor", None))
        self.region_label.setText(QCoreApplication.translate("FieldListEditorWidget", u"Region:", None))
        self.delete_field_button.setText(QCoreApplication.translate("FieldListEditorWidget", u"Delete", None))
    # retranslateUi

