# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './gui/qt\about_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


# Added by buildgui.py script to support pyinstaller
from src.helpers.pyinstaller_helper import PyInstallerHelper

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(300, 120)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutDialog.sizePolicy().hasHeightForWidth())
        AboutDialog.setSizePolicy(sizePolicy)
        AboutDialog.setMinimumSize(QtCore.QSize(300, 120))
        AboutDialog.setMaximumSize(QtCore.QSize(300, 120))
        AboutDialog.setSizeGripEnabled(False)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(AboutDialog)
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout_2.setSpacing(7)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.iconLabel = QtWidgets.QLabel(AboutDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.iconLabel.sizePolicy().hasHeightForWidth())
        self.iconLabel.setSizePolicy(sizePolicy)
        self.iconLabel.setMinimumSize(QtCore.QSize(64, 64))
        self.iconLabel.setMaximumSize(QtCore.QSize(64, 64))
        self.iconLabel.setText("")
        self.iconLabel.setPixmap(QtGui.QPixmap(PyInstallerHelper.resource_path("icons/main-512.png")))
        self.iconLabel.setScaledContents(True)
        self.iconLabel.setObjectName("iconLabel")
        self.verticalLayout_2.addWidget(self.iconLabel)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        spacerItem1 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(AboutDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem2 = QtWidgets.QSpacerItem(100, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.versionLabel = QtWidgets.QLabel(AboutDialog)
        self.versionLabel.setObjectName("versionLabel")
        self.horizontalLayout.addWidget(self.versionLabel)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(AboutDialog)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        _translate = QtCore.QCoreApplication.translate
        AboutDialog.setWindowTitle(_translate("AboutDialog", "About uPyLoader"))
        self.label.setText(_translate("AboutDialog", "Version:"))
        self.versionLabel.setText(_translate("AboutDialog", "XXX"))

