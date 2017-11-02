from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QStandardItemModel

from src.connection.connection import Connection


class RemoteFileSystemModel(QStandardItemModel):
    class _Data:
        def __init__(self, path):
            self.path = path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels(["Name"])

    def isDir(self, index):
        return self.data(index, Qt.UserRole).path.endswith("/")

    # Communication model
    # x/\n <- dir (ends with /)
    #   0\n
    #   1\n
    #   A/\n <- empty dir
    #   \n <- empty line means ../
    # \n
    # y/\n
    #   0\n
    # \n
    # \n <- end of FS
    def refresh(self, connection):
        assert isinstance(connection, Connection)
        output = connection.list_files()
        #TODO: Parse output
        r = QStandardItem("root")
        r.setData(self._Data("path/path/path", self._Data.FILE), Qt.UserRole)
        self.appendRow(r)
        r.appendRow(QStandardItem("child"))
