# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './gui/qt\code_edit.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


# Added by buildgui.py script to support pyinstaller
from src.helpers.pyinstaller_helper import PyInstallerHelper

class Ui_CodeEditDialog(object):
    def setupUi(self, CodeEditDialog):
        CodeEditDialog.setObjectName("CodeEditDialog")
        CodeEditDialog.resize(954, 537)
        self.verticalLayout = QtWidgets.QVBoxLayout(CodeEditDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(CodeEditDialog)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, -1, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_7 = QtWidgets.QLabel(CodeEditDialog)
        self.label_7.setMinimumSize(QtCore.QSize(40, 0))
        self.label_7.setObjectName("label_7")
        self.horizontalLayout.addWidget(self.label_7)
        self.localPathEdit = QtWidgets.QLineEdit(CodeEditDialog)
        self.localPathEdit.setObjectName("localPathEdit")
        self.horizontalLayout.addWidget(self.localPathEdit)
        self.saveLocalButton = QtWidgets.QPushButton(CodeEditDialog)
        self.saveLocalButton.setMaximumSize(QtCore.QSize(70, 16777215))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(PyInstallerHelper.resource_path("icons/floppy.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.saveLocalButton.setIcon(icon)
        self.saveLocalButton.setIconSize(QtCore.QSize(20, 20))
        self.saveLocalButton.setFlat(False)
        self.saveLocalButton.setObjectName("saveLocalButton")
        self.horizontalLayout.addWidget(self.saveLocalButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_8 = QtWidgets.QLabel(CodeEditDialog)
        self.label_8.setMinimumSize(QtCore.QSize(40, 0))
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_2.addWidget(self.label_8)
        self.remotePathEdit = QtWidgets.QLineEdit(CodeEditDialog)
        self.remotePathEdit.setObjectName("remotePathEdit")
        self.horizontalLayout_2.addWidget(self.remotePathEdit)
        self.runButton = QtWidgets.QPushButton(CodeEditDialog)
        self.runButton.setMinimumSize(QtCore.QSize(0, 0))
        self.runButton.setMaximumSize(QtCore.QSize(60, 16777215))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(PyInstallerHelper.resource_path("icons/run.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.runButton.setIcon(icon1)
        self.runButton.setIconSize(QtCore.QSize(20, 20))
        self.runButton.setFlat(False)
        self.runButton.setObjectName("runButton")
        self.horizontalLayout_2.addWidget(self.runButton)
        self.saveMcuButton = QtWidgets.QPushButton(CodeEditDialog)
        self.saveMcuButton.setMaximumSize(QtCore.QSize(70, 16777215))
        self.saveMcuButton.setIcon(icon)
        self.saveMcuButton.setFlat(False)
        self.saveMcuButton.setObjectName("saveMcuButton")
        self.horizontalLayout_2.addWidget(self.saveMcuButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4.addLayout(self.verticalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.codeEdit = QtWidgets.QTextEdit(CodeEditDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.codeEdit.sizePolicy().hasHeightForWidth())
        self.codeEdit.setSizePolicy(sizePolicy)
        self.codeEdit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.codeEdit.setObjectName("codeEdit")
        self.verticalLayout.addWidget(self.codeEdit)

        self.retranslateUi(CodeEditDialog)
        QtCore.QMetaObject.connectSlotsByName(CodeEditDialog)

    def retranslateUi(self, CodeEditDialog):
        _translate = QtCore.QCoreApplication.translate
        CodeEditDialog.setWindowTitle(_translate("CodeEditDialog", "Code Editor"))
        self.label_4.setText(_translate("CodeEditDialog", "Filename:"))
        self.label_7.setText(_translate("CodeEditDialog", "Local"))
        self.saveLocalButton.setText(_translate("CodeEditDialog", "Save"))
        self.label_8.setText(_translate("CodeEditDialog", "MCU"))
        self.runButton.setText(_translate("CodeEditDialog", "Run"))
        self.saveMcuButton.setText(_translate("CodeEditDialog", "Save"))

