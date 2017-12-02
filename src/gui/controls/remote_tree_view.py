from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QMessageBox

from src.gui.controls.transfer_tree_view import TransferTreeView
from src.logic.remote_file_system_model import RemoteFileSystemModel
from src.utility.exceptions import OperationError


class RemoteTreeView(TransferTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModel(RemoteFileSystemModel())

    def go_up_dir(self):
        if self._current_dir_path != self.root_dir():
            idx = self._current_dir_path[:-1].rfind("/")
            self.set_current_dir(self._current_dir_path[:idx+1])

    def refresh(self, connection):
        try:
            self.model().refresh(connection)
            self.set_current_dir(self._current_dir_path)
        except OperationError:
            QMessageBox().critical(self, "Operation failed", "Could not list files.", QMessageBox.Ok)
            return
