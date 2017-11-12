from PyQt5.QtWidgets import QFileSystemModel

from src.gui.controls.transfer_tree_view import TransferTreeView


class LocalTreeView(TransferTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModel(QFileSystemModel())
        self._root_dir = ""

    def root_dir(self):
        return self._root_dir

    def set_root_dir(self, path):
        self._root_dir = path
        model = self.model()
        model.setRootPath(path)
        self.setRootIndex(model.index(path))
        self._set_transfer_directory(path)
