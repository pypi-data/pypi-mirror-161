# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'snapshotdialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from opencmiss.zincwidgets.sceneviewerwidget import SceneviewerWidget


class Ui_SnapshotDialog(object):
    def setupUi(self, SnapshotDialog):
        if not SnapshotDialog.objectName():
            SnapshotDialog.setObjectName(u"SnapshotDialog")
        SnapshotDialog.resize(400, 300)
        self.verticalLayout = QVBoxLayout(SnapshotDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(SnapshotDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.spinBoxHeight = QSpinBox(self.groupBox)
        self.spinBoxHeight.setObjectName(u"spinBoxHeight")
        self.spinBoxHeight.setEnabled(False)
        self.spinBoxHeight.setMaximum(999999)

        self.gridLayout.addWidget(self.spinBoxHeight, 2, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.lineEditFilename = QLineEdit(self.groupBox)
        self.lineEditFilename.setObjectName(u"lineEditFilename")

        self.horizontalLayout.addWidget(self.lineEditFilename)

        self.pushButtonFilename = QPushButton(self.groupBox)
        self.pushButtonFilename.setObjectName(u"pushButtonFilename")

        self.horizontalLayout.addWidget(self.pushButtonFilename)


        self.gridLayout.addLayout(self.horizontalLayout, 4, 0, 1, 3)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.spinBoxWidth = QSpinBox(self.groupBox)
        self.spinBoxWidth.setObjectName(u"spinBoxWidth")
        self.spinBoxWidth.setEnabled(False)
        self.spinBoxWidth.setMaximum(999999)

        self.gridLayout.addWidget(self.spinBoxWidth, 1, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 3, 0, 1, 1)

        self.checkBoxWYSIWYG = QCheckBox(self.groupBox)
        self.checkBoxWYSIWYG.setObjectName(u"checkBoxWYSIWYG")
        self.checkBoxWYSIWYG.setChecked(True)

        self.gridLayout.addWidget(self.checkBoxWYSIWYG, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(self.groupBox)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(1, 1, 1, 1)
        self.widgetPreview = SceneviewerWidget(self.groupBox_2)
        self.widgetPreview.setObjectName(u"widgetPreview")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.widgetPreview.sizePolicy().hasHeightForWidth())
        self.widgetPreview.setSizePolicy(sizePolicy)
        self.widgetPreview.setMinimumSize(QSize(50, 50))

        self.horizontalLayout_2.addWidget(self.widgetPreview)


        self.gridLayout.addWidget(self.groupBox_2, 0, 2, 4, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.buttonBox = QDialogButtonBox(SnapshotDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(SnapshotDialog)
        self.buttonBox.accepted.connect(SnapshotDialog.accept)
        self.buttonBox.rejected.connect(SnapshotDialog.reject)

        QMetaObject.connectSlotsByName(SnapshotDialog)
    # setupUi

    def retranslateUi(self, SnapshotDialog):
        SnapshotDialog.setWindowTitle(QCoreApplication.translate("SnapshotDialog", u"Snapshot", None))
        self.groupBox.setTitle(QCoreApplication.translate("SnapshotDialog", u"Options", None))
        self.label_3.setText(QCoreApplication.translate("SnapshotDialog", u"Height (px):", None))
        self.label.setText(QCoreApplication.translate("SnapshotDialog", u"Filename:", None))
        self.pushButtonFilename.setText(QCoreApplication.translate("SnapshotDialog", u"...", None))
        self.label_2.setText(QCoreApplication.translate("SnapshotDialog", u"Width (px):", None))
#if QT_CONFIG(tooltip)
        self.checkBoxWYSIWYG.setToolTip(QCoreApplication.translate("SnapshotDialog", u"What you see is what you get!", None))
#endif // QT_CONFIG(tooltip)
        self.checkBoxWYSIWYG.setText(QCoreApplication.translate("SnapshotDialog", u"WYSIWYG", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("SnapshotDialog", u"Preview", None))
    # retranslateUi

