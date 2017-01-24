# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './gui/qt\Settings().ui'
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
        self.groupBox = QtWidgets.QGroupBox(SettingsDialog)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.sendKeyLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.sendKeyLineEdit.setObjectName("sendKeyLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.sendKeyLineEdit)
        self.newLineKeyLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.newLineKeyLineEdit.setObjectName("newLineKeyLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.newLineKeyLineEdit)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.holdAutoscrollCheckBox = QtWidgets.QCheckBox(self.groupBox)
        self.holdAutoscrollCheckBox.setText("")
        self.holdAutoscrollCheckBox.setObjectName("holdAutoscrollCheckBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.holdAutoscrollCheckBox)
        self.verticalLayout_2.addLayout(self.formLayout)
        self.verticalLayout.addWidget(self.groupBox)
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
        self.groupBox.setTitle(_translate("SettingsDialog", "Terminal"))
        self.label.setText(_translate("SettingsDialog", "New line key"))
        self.label_2.setText(_translate("SettingsDialog", "Send key"))
        self.label_3.setText(_translate("SettingsDialog", "Hold autoscroll"))

