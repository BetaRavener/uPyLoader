from time import sleep

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QMessageBox, QDialog

from gui.file_transfer import Ui_FileTransferDialog
from src.logic.file_transfer import FileTransfer


class FileTransferDialog(QDialog, Ui_FileTransferDialog):
    _update_signal = pyqtSignal()

    UPLOAD = 0
    DOWNLOAD = 1

    def __init__(self, type):
        super(FileTransferDialog, self).__init__(None, Qt.WindowTitleHint)
        self.setupUi(self)
        self.setModal(True)

        self._transfer = FileTransfer(lambda: self._update_signal.emit())

        if type == FileTransferDialog.UPLOAD:
            self.label.setText("Saving file.")
        elif type == FileTransferDialog.DOWNLOAD:
            self.label.setText("Reading file.")

        self.progressBar.setRange(0, 100)

        self.progressBar.setValue(0)
        self._update_signal.connect(self._update_progress)
        self.cancelButton.clicked.connect(self._transfer.cancel)

    def enable_cancel(self):
        self.cancelButton.setEnabled(True)

    def _update_progress(self):
        if self._transfer.error:
            additional_info = ""
            if self._transfer.error_msg:
                additional_info = "\n\nReason:\n{}".format(self._transfer.error_msg)
            QMessageBox().critical(self, "Error", "File transfer failed.{}".format(additional_info), QMessageBox.Ok)
            self.reject()
        elif self._transfer.cancelled:
            self.reject()
        elif self._transfer.finished:
            sleep(0.5)
            self.accept()
        else:
            self.progressBar.setValue(self._transfer.progress * 100)

    @property
    def transfer(self):
        return self._transfer
