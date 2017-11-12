from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QStandardItemModel

from src.connection.connection import Connection
from src.gui.icons import Icons


class RemoteFileSystemModel(QStandardItemModel):
    class _Data:
        def __init__(self, path):
            self.path = path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels(["Name"])

    def isDir(self, index):
        return self.filePath(index).endswith("/")

    def filePath(self, index):
        return self.data(index, Qt.UserRole).path

    # Communication model
    # x/\n <- dir (ends with /)
    #   0\n
    #   1\n
    #   A/\n <- empty dir
    #   /\n <- empty line means ../
    # \n
    # y/\n
    #   0\n
    # /\n
    # /\n <- end of FS
    def refresh(self, connection):
        self.removeRows(0, self.rowCount())
        assert isinstance(connection, Connection)
        output = connection.list_tree()
        # Stack of items on path, with their absolute textual paths
        path_items = [(self, "")]
        for x in output:
            if x == "/":
                path_items.remove(path_items[-1])
                continue

            abs_path = "{}/{}".format(path_items[-1][1], x)
            icon = Icons().tree_file
            is_dir = x.endswith("/")
            if is_dir:
                x = x[:-1]
                icon = Icons().tree_folder
            elif x.endswith(".py"):
                icon = Icons().tree_python

            item = QStandardItem(x)
            item.setIcon(icon)
            item.setData(self._Data(abs_path), Qt.UserRole)
            path_items[-1][0].appendRow(item)

            if is_dir:
                # noinspection PyTypeChecker
                path_items.append((item, abs_path))

        #TODO: Parse output
        # r = QStandardItem("root")
        # r.setData(self._Data("path/path/path"), Qt.UserRole)
        # self.appendRow(r)
        # r.appendRow(QStandardItem("child"))
