from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QStandardItemModel


class RemoteFileSystemModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels(["Name"])
        self._setup_model_data()

    def _setup_model_data(self):
        r = QStandardItem("root")
        r.setData("path/path/path", Qt.UserRole)
        self.appendRow(r)
        r.appendRow(QStandardItem("child"))
