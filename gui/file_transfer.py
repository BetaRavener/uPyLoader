# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './gui/qt\file_transfer.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


# Added by buildgui.py script to support pyinstaller
from src.helpers.pyinstaller_helper import PyInstallerHelper

class Ui_FileTransferDialog(object):
    def setupUi(self, FileTransferDialog):
        FileTransferDialog.setObjectName("FileTransferDialog")
        FileTransferDialog.resize(400, 120)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(FileTransferDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(FileTransferDialog)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.progressBar = QtWidgets.QProgressBar(FileTransferDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancelButton = QtWidgets.QPushButton(FileTransferDialog)
        self.cancelButton.setEnabled(False)
        self.cancelButton.setCheckable(False)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(FileTransferDialog)
        QtCore.QMetaObject.connectSlotsByName(FileTransferDialog)

    def retranslateUi(self, FileTransferDialog):
        _translate = QtCore.QCoreApplication.translate
        FileTransferDialog.setWindowTitle(_translate("FileTransferDialog", "File Transfer"))
        self.label.setText(_translate("FileTransferDialog", "TextLabel"))
        self.cancelButton.setText(_translate("FileTransferDialog", "Cancel"))

