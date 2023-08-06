# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'timeeditorwidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from opencmiss.zincwidgets.ui import icons_rc

class Ui_TimeEditorWidget(object):
    def setupUi(self, TimeEditorWidget):
        if not TimeEditorWidget.objectName():
            TimeEditorWidget.setObjectName(u"TimeEditorWidget")
        TimeEditorWidget.resize(853, 106)
        self.gridLayout = QGridLayout(TimeEditorWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(TimeEditorWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.lineEditTime = QLineEdit(self.groupBox)
        self.lineEditTime.setObjectName(u"lineEditTime")

        self.gridLayout_2.addWidget(self.lineEditTime, 0, 0, 1, 1)

        self.horizontalSliderTime = QSlider(self.groupBox)
        self.horizontalSliderTime.setObjectName(u"horizontalSliderTime")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalSliderTime.sizePolicy().hasHeightForWidth())
        self.horizontalSliderTime.setSizePolicy(sizePolicy)
        self.horizontalSliderTime.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.horizontalSliderTime, 0, 1, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.spinBoxNumberofSteps = QSpinBox(self.groupBox)
        self.spinBoxNumberofSteps.setObjectName(u"spinBoxNumberofSteps")
        self.spinBoxNumberofSteps.setMinimum(2)
        self.spinBoxNumberofSteps.setMaximum(999999)

        self.horizontalLayout_2.addWidget(self.spinBoxNumberofSteps)


        self.gridLayout_2.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.doubleSpinBoxMinimumTime = QDoubleSpinBox(self.groupBox)
        self.doubleSpinBoxMinimumTime.setObjectName(u"doubleSpinBoxMinimumTime")
        self.doubleSpinBoxMinimumTime.setMinimum(-99999999.989999994635582)

        self.horizontalLayout.addWidget(self.doubleSpinBoxMinimumTime)

        self.horizontalSpacer = QSpacerItem(71, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButtonPlayReverse = QPushButton(self.groupBox)
        self.pushButtonPlayReverse.setObjectName(u"pushButtonPlayReverse")
        icon = QIcon()
        icon.addFile(u":/zincwidgets/images/icons/playback-start-reverse-icon.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButtonPlayReverse.setIcon(icon)

        self.horizontalLayout.addWidget(self.pushButtonPlayReverse)

        self.pushButtonStop = QPushButton(self.groupBox)
        self.pushButtonStop.setObjectName(u"pushButtonStop")
        icon1 = QIcon()
        icon1.addFile(u":/zincwidgets/images/icons/playback-stop-icon.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButtonStop.setIcon(icon1)

        self.horizontalLayout.addWidget(self.pushButtonStop)

        self.pushButtonPlay = QPushButton(self.groupBox)
        self.pushButtonPlay.setObjectName(u"pushButtonPlay")
        icon2 = QIcon()
        icon2.addFile(u":/zincwidgets/images/icons/playback-start-icon.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButtonPlay.setIcon(icon2)

        self.horizontalLayout.addWidget(self.pushButtonPlay)

        self.horizontalSpacer_2 = QSpacerItem(71, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.doubleSpinBoxMaximumTime = QDoubleSpinBox(self.groupBox)
        self.doubleSpinBoxMaximumTime.setObjectName(u"doubleSpinBoxMaximumTime")
        self.doubleSpinBoxMaximumTime.setMinimum(-99999999.989999994635582)
        self.doubleSpinBoxMaximumTime.setMaximum(99999999.989999994635582)
        self.doubleSpinBoxMaximumTime.setValue(10.000000000000000)

        self.horizontalLayout.addWidget(self.doubleSpinBoxMaximumTime)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 1, 1, 1)


        self.gridLayout.addWidget(self.groupBox, 0, 1, 1, 1)


        self.retranslateUi(TimeEditorWidget)

        QMetaObject.connectSlotsByName(TimeEditorWidget)
    # setupUi

    def retranslateUi(self, TimeEditorWidget):
        TimeEditorWidget.setWindowTitle(QCoreApplication.translate("TimeEditorWidget", u"Time Editor", None))
        self.groupBox.setTitle(QCoreApplication.translate("TimeEditorWidget", u"Timer", None))
        self.label_3.setText(QCoreApplication.translate("TimeEditorWidget", u"# of steps:", None))
        self.label.setText(QCoreApplication.translate("TimeEditorWidget", u"Min.:", None))
        self.pushButtonPlayReverse.setText("")
        self.pushButtonStop.setText("")
        self.pushButtonPlay.setText("")
        self.label_2.setText(QCoreApplication.translate("TimeEditorWidget", u"Max.:", None))
    # retranslateUi

