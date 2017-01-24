# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './gui/qt\settings.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        SettingsDialog.setObjectName("SettingsDialog")
        SettingsDialog.resize(706, 479)
        self.verticalLayout = QtWidgets.QVBoxLayout(SettingsDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.terminalGroupBox = QtWidgets.QGroupBox(SettingsDialog)
        self.terminalGroupBox.setObjectName("terminalGroupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.terminalGroupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.terminalFormLayout = QtWidgets.QFormLayout()
        self.terminalFormLayout.setObjectName("terminalFormLayout")
        self.label = QtWidgets.QLabel(self.terminalGroupBox)
        self.label.setObjectName("label")
        self.terminalFormLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(self.terminalGroupBox)
        self.label_2.setObjectName("label_2")
        self.terminalFormLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtWidgets.QLabel(self.terminalGroupBox)
        self.label_3.setObjectName("label_3")
        self.terminalFormLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.holdAutoscrollCheckBox = QtWidgets.QCheckBox(self.terminalGroupBox)
        self.holdAutoscrollCheckBox.setText("")
        self.holdAutoscrollCheckBox.setObjectName("holdAutoscrollCheckBox")
        self.terminalFormLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.holdAutoscrollCheckBox)
        self.newLineKeyEdit = QtWidgets.QLineEdit(self.terminalGroupBox)
        self.newLineKeyEdit.setObjectName("newLineKeyEdit")
        self.terminalFormLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.newLineKeyEdit)
        self.sendKeyEdit = QtWidgets.QLineEdit(self.terminalGroupBox)
        self.sendKeyEdit.setObjectName("sendKeyEdit")
        self.terminalFormLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.sendKeyEdit)
        self.verticalLayout_2.addLayout(self.terminalFormLayout)
        self.verticalLayout.addWidget(self.terminalGroupBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(SettingsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SettingsDialog)
        self.buttonBox.accepted.connect(SettingsDialog.accept)
        self.buttonBox.rejected.connect(SettingsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SettingsDialog)

    def retranslateUi(self, SettingsDialog):
        _translate = QtCore.QCoreApplication.translate
        SettingsDialog.setWindowTitle(_translate("SettingsDialog", "Settings"))
        self.terminalGroupBox.setTitle(_translate("SettingsDialog", "Terminal"))
        self.label.setText(_translate("SettingsDialog", "New line key"))
        self.label_2.setText(_translate("SettingsDialog", "Send key"))
        self.label_3.setText(_translate("SettingsDialog", "Hold autoscroll"))

