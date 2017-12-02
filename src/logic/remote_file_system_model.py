from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QStandardItemModel

from src.connection.connection import Connection
from src.gui.icons import Icons
from src.utility.exceptions import OperationError


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

    @staticmethod
    def _assign_icon(item, is_dir):
        icon = Icons().tree_file
        if is_dir:
            icon = Icons().tree_folder
        elif item.endswith(".py"):
            icon = Icons().tree_python
        return icon

    def _add_entry(self, name, abs_path, is_dir, parent):
        item = QStandardItem(name)
        item.setIcon(self._assign_icon(name, is_dir))
        item.setData(self._Data(abs_path), Qt.UserRole)
        parent.appendRow(item)
        return item

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
    def _process_tree(self, tree):
        # Stack of items on path, with their absolute textual paths
        path_items = [(self, "")]
        for x in tree:
            if x == "/":
                path_items.remove(path_items[-1])
                continue

            abs_path = "{}/{}".format(path_items[-1][1], x)
            is_dir = x.endswith("/")

            # Remove slash
            if is_dir:
                x = x[:-1]

            item = self._add_entry(x, abs_path, is_dir, path_items[-1][0])

            if is_dir:
                # noinspection PyTypeChecker
                path_items.append((item, abs_path))

    def _process_list(self, file_list):
        for x in file_list:
            self._add_entry(x, x, False, self)

    def refresh(self, connection):
        self.removeRows(0, self.rowCount())
        assert isinstance(connection, Connection)
        try:
            output = connection.list_tree()
            self._process_tree(output)
            return
        # Ignore error now, we have fallback option
        except OperationError:
            pass

        # If this raises exception, something is wrong
        output = connection.list_files()
        self._process_list(output)
