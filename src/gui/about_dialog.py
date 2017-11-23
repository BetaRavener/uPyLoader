from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QMessageBox, QDialog

from gui.about_dialog import Ui_AboutDialog
from gui.code_edit import Ui_CodeEditDialog
from src.gui.file_transfer_dialog import FileTransferDialog
from src.utility.settings import Settings


class AboutDialog(QDialog, Ui_AboutDialog):
    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent, Qt.WindowCloseButtonHint)
        self.setupUi(self)
        self.setModal(True)
        self.setSizeGripEnabled(False)
        self.versionLabel.setText("0.1.3 (dev)")
