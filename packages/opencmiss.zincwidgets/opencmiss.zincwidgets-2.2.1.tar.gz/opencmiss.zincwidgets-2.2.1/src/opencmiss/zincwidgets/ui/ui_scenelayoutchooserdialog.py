# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'scenelayoutchooserdialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from  . import icons_rc

class Ui_SceneLayoutChooserDialog(object):
    def setupUi(self, SceneLayoutChooserDialog):
        if not SceneLayoutChooserDialog.objectName():
            SceneLayoutChooserDialog.setObjectName(u"SceneLayoutChooserDialog")
        SceneLayoutChooserDialog.resize(752, 483)
        self.verticalLayout = QVBoxLayout(SceneLayoutChooserDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(SceneLayoutChooserDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.radioButtonLayout1 = QRadioButton(self.groupBox)
        self.radioButtonLayout1.setObjectName(u"radioButtonLayout1")
        icon = QIcon()
        icon.addFile(u":/zincwidgets/images/icons/layout-single-scene.png", QSize(), QIcon.Normal, QIcon.Off)
        self.radioButtonLayout1.setIcon(icon)
        self.radioButtonLayout1.setIconSize(QSize(256, 256))
        self.radioButtonLayout1.setChecked(True)

        self.gridLayout.addWidget(self.radioButtonLayout1, 0, 0, 1, 1)

        self.radioButtonLayout2x2Grid = QRadioButton(self.groupBox)
        self.radioButtonLayout2x2Grid.setObjectName(u"radioButtonLayout2x2Grid")
        icon1 = QIcon()
        icon1.addFile(u":/zincwidgets/images/icons/layout-four-scenes.png", QSize(), QIcon.Normal, QIcon.Off)
        self.radioButtonLayout2x2Grid.setIcon(icon1)
        self.radioButtonLayout2x2Grid.setIconSize(QSize(256, 256))

        self.gridLayout.addWidget(self.radioButtonLayout2x2Grid, 0, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.buttonBox = QDialogButtonBox(SceneLayoutChooserDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(SceneLayoutChooserDialog)
        self.buttonBox.accepted.connect(SceneLayoutChooserDialog.accept)
        self.buttonBox.rejected.connect(SceneLayoutChooserDialog.reject)

        QMetaObject.connectSlotsByName(SceneLayoutChooserDialog)
    # setupUi

    def retranslateUi(self, SceneLayoutChooserDialog):
        SceneLayoutChooserDialog.setWindowTitle(QCoreApplication.translate("SceneLayoutChooserDialog", u"Scene Layout Chooser", None))
        self.groupBox.setTitle(QCoreApplication.translate("SceneLayoutChooserDialog", u"Select layout:", None))
        self.radioButtonLayout1.setText("")
        self.radioButtonLayout2x2Grid.setText("")
    # retranslateUi

