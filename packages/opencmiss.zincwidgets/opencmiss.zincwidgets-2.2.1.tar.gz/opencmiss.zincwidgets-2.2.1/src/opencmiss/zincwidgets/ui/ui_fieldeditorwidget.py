# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fieldeditorwidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from opencmiss.zincwidgets.fieldpropertieswidget import FieldPropertiesWidget


class Ui_FieldEditorWidget(object):
    def setupUi(self, FieldEditorWidget):
        if not FieldEditorWidget.objectName():
            FieldEditorWidget.setObjectName(u"FieldEditorWidget")
        FieldEditorWidget.setEnabled(True)
        FieldEditorWidget.resize(310, 1030)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(FieldEditorWidget.sizePolicy().hasHeightForWidth())
        FieldEditorWidget.setSizePolicy(sizePolicy)
        FieldEditorWidget.setMinimumSize(QSize(180, 0))
        self.verticalLayout = QVBoxLayout(FieldEditorWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.field_properties_widget = FieldPropertiesWidget(FieldEditorWidget)
        self.field_properties_widget.setObjectName(u"field_properties_widget")

        self.verticalLayout.addWidget(self.field_properties_widget)

        self.create_groupbox = QGroupBox(FieldEditorWidget)
        self.create_groupbox.setObjectName(u"create_groupbox")
        self.create_groupbox.setMinimumSize(QSize(180, 0))
        self.formLayout = QFormLayout(self.create_groupbox)
        self.formLayout.setObjectName(u"formLayout")
        self.name_label = QLabel(self.create_groupbox)
        self.name_label.setObjectName(u"name_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.name_label)

        self.name_lineedit = QLineEdit(self.create_groupbox)
        self.name_lineedit.setObjectName(u"name_lineedit")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.name_lineedit)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(118, 17, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.create_button = QPushButton(self.create_groupbox)
        self.create_button.setObjectName(u"create_button")

        self.horizontalLayout_2.addWidget(self.create_button)

        self.horizontalSpacer_2 = QSpacerItem(122, 17, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.formLayout.setLayout(1, QFormLayout.SpanningRole, self.horizontalLayout_2)


        self.verticalLayout.addWidget(self.create_groupbox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(FieldEditorWidget)

        QMetaObject.connectSlotsByName(FieldEditorWidget)
    # setupUi

    def retranslateUi(self, FieldEditorWidget):
        FieldEditorWidget.setWindowTitle(QCoreApplication.translate("FieldEditorWidget", u"Field Editor", None))
        self.create_groupbox.setTitle(QCoreApplication.translate("FieldEditorWidget", u"Create:", None))
        self.name_label.setText(QCoreApplication.translate("FieldEditorWidget", u"Name:", None))
        self.create_button.setText(QCoreApplication.translate("FieldEditorWidget", u"Create", None))
    # retranslateUi

