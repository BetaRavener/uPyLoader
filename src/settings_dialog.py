
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from gui.settings import Ui_SettingsDialog


class SettingsDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, parent):
        super(SettingsDialog, self).__init__(parent, Qt.WindowCloseButtonHint)
        self.setupUi(self)
        self.setModal(True)
        self.saveGeometry()
