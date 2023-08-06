# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'exportwebglwidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ExportWebGLWidget(object):
    def setupUi(self, ExportWebGLWidget):
        if not ExportWebGLWidget.objectName():
            ExportWebGLWidget.setObjectName(u"ExportWebGLWidget")
        ExportWebGLWidget.resize(507, 359)
        self.verticalLayout = QVBoxLayout(ExportWebGLWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_3 = QLabel(ExportWebGLWidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)

        self.prefix_lineEdit = QLineEdit(ExportWebGLWidget)
        self.prefix_lineEdit.setObjectName(u"prefix_lineEdit")

        self.gridLayout_2.addWidget(self.prefix_lineEdit, 0, 1, 1, 1)

        self.label_4 = QLabel(ExportWebGLWidget)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 0, 2, 1, 1)

        self.timeSteps_lineEdit = QLineEdit(ExportWebGLWidget)
        self.timeSteps_lineEdit.setObjectName(u"timeSteps_lineEdit")

        self.gridLayout_2.addWidget(self.timeSteps_lineEdit, 0, 3, 1, 1)

        self.label = QLabel(ExportWebGLWidget)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)

        self.initialTime_lineEdit = QLineEdit(ExportWebGLWidget)
        self.initialTime_lineEdit.setObjectName(u"initialTime_lineEdit")

        self.gridLayout_2.addWidget(self.initialTime_lineEdit, 1, 1, 1, 1)

        self.label_2 = QLabel(ExportWebGLWidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 1, 2, 1, 1)

        self.finishTime_lineEdit = QLineEdit(ExportWebGLWidget)
        self.finishTime_lineEdit.setObjectName(u"finishTime_lineEdit")

        self.gridLayout_2.addWidget(self.finishTime_lineEdit, 1, 3, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_2)

        self.export_button = QPushButton(ExportWebGLWidget)
        self.export_button.setObjectName(u"export_button")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.export_button.sizePolicy().hasHeightForWidth())
        self.export_button.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.export_button)


        self.retranslateUi(ExportWebGLWidget)

        QMetaObject.connectSlotsByName(ExportWebGLWidget)
    # setupUi

    def retranslateUi(self, ExportWebGLWidget):
        ExportWebGLWidget.setWindowTitle(QCoreApplication.translate("ExportWebGLWidget", u"Export WebGL", None))
        self.label_3.setText(QCoreApplication.translate("ExportWebGLWidget", u"Prefix : ", None))
        self.label_4.setText(QCoreApplication.translate("ExportWebGLWidget", u"Time Steps : ", None))
        self.label.setText(QCoreApplication.translate("ExportWebGLWidget", u"Initial Time : ", None))
        self.label_2.setText(QCoreApplication.translate("ExportWebGLWidget", u"Finish Time : ", None))
        self.export_button.setText(QCoreApplication.translate("ExportWebGLWidget", u"Export WebGL Json Files", None))
    # retranslateUi

