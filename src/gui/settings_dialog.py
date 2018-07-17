from PyQt5.QtCore import QDir
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QKeySequenceEdit

from gui.settings import Ui_SettingsDialog
from src.utility.settings import Settings


class SettingsDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, parent):
        super(SettingsDialog, self).__init__(parent, Qt.WindowCloseButtonHint)
        self.setupUi(self)
        self.setModal(True)

        # Workaround because UI compiler doesn't recognize QKeySequenceEdit
        # Create new items
        new_line_key_edit = SettingsDialog.one_key_sequence_edit(self.terminalGroupBox, "newLineKeyEdit")
        send_key_edit = SettingsDialog.one_key_sequence_edit(self.terminalGroupBox, "sendKeyEdit")
        # Replace old items in layout
        self.terminalFormLayout.replaceWidget(self.newLineKeyEdit, new_line_key_edit)
        self.terminalFormLayout.replaceWidget(self.sendKeyEdit, send_key_edit)
        # Set parent to None effectively removing old items
        self.newLineKeyEdit.setParent(None)
        self.sendKeyEdit.setParent(None)
        # Replace references
        self.newLineKeyEdit = new_line_key_edit
        self.sendKeyEdit = send_key_edit

        if Settings().external_editor_path:
            self.externalPathLineEdit.setText(Settings().external_editor_path)
        if Settings().external_editor_args:
            self.externalCommandLineEdit.setText(Settings().external_editor_args)
        self.externalPathBrowseButton.clicked.connect(self.browse_external_editor)

        self.newLineKeyEdit.setKeySequence(Settings().new_line_key)
        self.sendKeyEdit.setKeySequence(Settings().send_key)
        self.tabSpacesSpinBox.setValue(Settings().terminal_tab_spaces)

        if Settings().mpy_cross_path:
            self.mpyCrossPathLineEdit.setText(Settings().mpy_cross_path)
        self.mpyPathBrowseButton.clicked.connect(self.browse_mpy_cross)

        if Settings().preferred_port:
            self.preferredPortLineEdit.setText(Settings().preferred_port)

        self.useTransferFilesCheckBox.stateChanged.connect(self.update_external_scripts_controls)
        self.useCustomTransferFilesCheckBox.stateChanged.connect(self.update_external_scripts_controls)
        if Settings().external_transfer_scripts_folder:
            self.transferFilesPathLineEdit.setText(Settings().external_transfer_scripts_folder)

        self.useTransferFilesCheckBox.setChecked(Settings().use_transfer_scripts)
        self.useCustomTransferFilesCheckBox.setChecked(Settings().use_custom_transfer_scripts)

        self.transferFilesPathBrowseButton.clicked.connect(self.browse_external_transfer_files)

    def accept(self):
        self.save_settings()
        super(SettingsDialog, self).accept()

    def browse_external_editor(self):
        path = QFileDialog().getOpenFileName(
            caption="Select external editor",
            directory=QDir().homePath(),
            options=QFileDialog.ReadOnly)

        if path[0]:
            self.externalPathLineEdit.setText(path[0])

    def browse_mpy_cross(self):
        path = QFileDialog().getOpenFileName(
            caption="Select mpy-cross compiler",
            directory=QDir().homePath(),
            options=QFileDialog.ReadOnly)

        if path[0]:
            self.mpyCrossPathLineEdit.setText(path[0])

    def update_external_scripts_controls(self):
        self.useCustomTransferFilesCheckBox.setEnabled(self.useTransferFilesCheckBox.isChecked())
        edit_enabled = self.useCustomTransferFilesCheckBox.isEnabled() and \
                       self.useCustomTransferFilesCheckBox.isChecked()
        self.transferFilesPathLineEdit.setEnabled(edit_enabled)

    def browse_external_transfer_files(self):
        path = QFileDialog().getExistingDirectory(
            caption="Select transfer files folder",
            directory=QDir().homePath(),
            options=QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)

        if path:
            self.transferFilesPathLineEdit.setText(path)

    def save_settings(self):
        Settings().external_editor_path = self.externalPathLineEdit.text()
        Settings().external_editor_args = self.externalCommandLineEdit.text()
        Settings().new_line_key = self.newLineKeyEdit.keySequence()
        Settings().send_key = self.sendKeyEdit.keySequence()
        Settings().terminal_tab_spaces = self.tabSpacesSpinBox.value()
        Settings().mpy_cross_path = self.mpyCrossPathLineEdit.text()
        Settings().preferred_port = self.preferredPortLineEdit.text()
        Settings().use_transfer_scripts = self.useTransferFilesCheckBox.isChecked()
        Settings().use_custom_transfer_scripts = self.useCustomTransferFilesCheckBox.isChecked()
        Settings().external_transfer_scripts_folder = self.transferFilesPathLineEdit.text()
        Settings().save()

    @staticmethod
    def one_key_sequence_edit(parent, name):
        edit = QKeySequenceEdit(parent)
        edit.setObjectName(name)

        return edit
