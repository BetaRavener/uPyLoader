from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QStandardItemModel

from src.gui.controls.transfer_tree_view import TransferTreeView
from src.logic.remote_file_system_model import RemoteFileSystemModel


class RemoteTreeView(TransferTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModel(RemoteFileSystemModel())
