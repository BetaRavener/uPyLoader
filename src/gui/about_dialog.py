from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from gui.about_dialog import Ui_AboutDialog
from src.utility.build_info import BuildInfo
from src.utility.versioning import Versioning


class AboutDialog(QDialog, Ui_AboutDialog):
    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent, Qt.WindowCloseButtonHint)
        self.setupUi(self)
        self.setModal(True)
        self.setSizeGripEnabled(False)
        self.versionLabel.setText(Versioning.get_version_string())
        self.buildDateLabel.setText(BuildInfo().build_date)
