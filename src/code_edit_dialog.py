from time import sleep

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QProgressDialog, QMessageBox, QDialog

from gui.code_edit import Ui_CodeEditDialog
from src.file_transfer import FileTransfer
from src.file_transfer_dialog import FileTransferDialog


class CodeEditDialog(QDialog, Ui_CodeEditDialog):
    mcu_file_saved = pyqtSignal()

    def __init__(self, connection):
        super(CodeEditDialog, self).__init__()
        self.setupUi(self)

        self._connection = connection

        self.saveLocalButton.clicked.connect(self._save_local)
        self.saveMcuButton.clicked.connect(self._save_to_mcu)
        #self.runButton.clicked.connect(self._run_file)
        self.runButton.hide()

        fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.codeEdit.setFont(fixed_font)

        if connection and connection.is_connected():
            self.connected(connection)
        else:
            self.disconnected()

    def disconnected(self):
        self._connection = None
        self.saveMcuButton.setEnabled(False)

    def connected(self, connection):
        self._connection = connection
        self.saveMcuButton.setEnabled(True)

    def _save_local(self):
        path = self.localPathEdit.text()
        if not path:
            QMessageBox.warning(self, "Invalid path", "Enter correct path for local file.")
            return

        try:
            with open(path, "w") as file:
                file.write(self.codeEdit.toPlainText())
        except IOError:
            QMessageBox.critical(self, "Save operation failed", "Couldn't save the file. Check path and permissions.")

    def _save_to_mcu(self):
        name = self.remotePathEdit.text()
        if not name:
            QMessageBox.warning(self, "Invalid name", "Enter correct name for remote file.")
            return

        content = self.codeEdit.toPlainText()
        if not content:
            QMessageBox.warning(self, "Empty file", "Can't write empty file.")
            return

        progress_dlg = FileTransferDialog(FileTransferDialog.UPLOAD)
        progress_dlg.finished.connect(self.mcu_file_saved.emit)
        progress_dlg.show()
        self._connection.write_file(name, content, progress_dlg.transfer)

    def set_code(self, local_path, remote_path, code):
        self.codeEdit.clear()
        self.codeEdit.setText(code)
        self.localPathEdit.setText(local_path if local_path else "")
        self.remotePathEdit.setText(remote_path if remote_path else "")