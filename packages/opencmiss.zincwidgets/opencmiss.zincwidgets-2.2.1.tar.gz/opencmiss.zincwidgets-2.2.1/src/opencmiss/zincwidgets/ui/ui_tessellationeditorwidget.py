# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tessellationeditorwidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from opencmiss.zincwidgets.ui import icons_rc

class Ui_TessellationEditorWidget(object):
    def setupUi(self, TessellationEditorWidget):
        if not TessellationEditorWidget.objectName():
            TessellationEditorWidget.setObjectName(u"TessellationEditorWidget")
        TessellationEditorWidget.resize(613, 476)
        self.verticalLayout = QVBoxLayout(TessellationEditorWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(TessellationEditorWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tableWidgetTessellations = QTableWidget(self.groupBox)
        self.tableWidgetTessellations.setObjectName(u"tableWidgetTessellations")
        self.tableWidgetTessellations.setAlternatingRowColors(True)
        self.tableWidgetTessellations.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidgetTessellations.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidgetTessellations.setShowGrid(False)
        self.tableWidgetTessellations.setColumnCount(0)
        self.tableWidgetTessellations.horizontalHeader().setVisible(True)
        self.tableWidgetTessellations.horizontalHeader().setStretchLastSection(True)
        self.tableWidgetTessellations.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.tableWidgetTessellations, 0, 0, 1, 3)

        self.pushButtonAddTessellation = QPushButton(self.groupBox)
        self.pushButtonAddTessellation.setObjectName(u"pushButtonAddTessellation")
        icon = QIcon()
        icon.addFile(u":/zincwidgets/images/icons/list-add-icon.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButtonAddTessellation.setIcon(icon)

        self.gridLayout.addWidget(self.pushButtonAddTessellation, 1, 0, 1, 1)

        self.pushButtonDeleteTessellation = QPushButton(self.groupBox)
        self.pushButtonDeleteTessellation.setObjectName(u"pushButtonDeleteTessellation")
        icon1 = QIcon()
        icon1.addFile(u":/zincwidgets/images/icons/list-remove-icon.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButtonDeleteTessellation.setIcon(icon1)

        self.gridLayout.addWidget(self.pushButtonDeleteTessellation, 1, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(510, 19, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 2, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBoxProperties = QGroupBox(TessellationEditorWidget)
        self.groupBoxProperties.setObjectName(u"groupBoxProperties")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxProperties)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.checkBoxDefaultTessellation = QCheckBox(self.groupBoxProperties)
        self.checkBoxDefaultTessellation.setObjectName(u"checkBoxDefaultTessellation")

        self.verticalLayout_2.addWidget(self.checkBoxDefaultTessellation)

        self.checkBoxDefaultPointsTessellation = QCheckBox(self.groupBoxProperties)
        self.checkBoxDefaultPointsTessellation.setObjectName(u"checkBoxDefaultPointsTessellation")

        self.verticalLayout_2.addWidget(self.checkBoxDefaultPointsTessellation)


        self.verticalLayout.addWidget(self.groupBoxProperties)


        self.retranslateUi(TessellationEditorWidget)

        QMetaObject.connectSlotsByName(TessellationEditorWidget)
    # setupUi

    def retranslateUi(self, TessellationEditorWidget):
        TessellationEditorWidget.setWindowTitle(QCoreApplication.translate("TessellationEditorWidget", u"Tessellation Editor", None))
        self.groupBox.setTitle(QCoreApplication.translate("TessellationEditorWidget", u"Tessellations", None))
#if QT_CONFIG(tooltip)
        self.pushButtonAddTessellation.setToolTip(QCoreApplication.translate("TessellationEditorWidget", u"Add spectrum", None))
#endif // QT_CONFIG(tooltip)
        self.pushButtonAddTessellation.setText("")
#if QT_CONFIG(tooltip)
        self.pushButtonDeleteTessellation.setToolTip(QCoreApplication.translate("TessellationEditorWidget", u"Remove spectrum", None))
#endif // QT_CONFIG(tooltip)
        self.pushButtonDeleteTessellation.setText("")
        self.groupBoxProperties.setTitle(QCoreApplication.translate("TessellationEditorWidget", u"Properties", None))
        self.checkBoxDefaultTessellation.setText(QCoreApplication.translate("TessellationEditorWidget", u"Default Tessellation", None))
        self.checkBoxDefaultPointsTessellation.setText(QCoreApplication.translate("TessellationEditorWidget", u"Default Points Tessellation", None))
    # retranslateUi

