import os

from PyQt5.QtCore import QModelIndex, Qt, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QTreeView


class TransferTreeView(QTreeView):
    transfer_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setItemsExpandable(False)
        self.setRootIsDecorated(False)
        self.setExpandsOnDoubleClick(False)
        self.doubleClicked.connect(self._double_clicked_handler)

        self._current_dir_path = ""

        self._context_menu = QMenu(self)
        self._add_menu_action("Transfer", self._transfer_handler)
        # TODO: Implement
        # self._add_menu_action("Transfer changed", self._transfer_changed_handler)
        self._context_menu.addSeparator()
        self._destination_menu_action = self._add_menu_action(
            "Set as destination", self._set_transfer_directory_handler)

    def _double_clicked_handler(self, idx):
        model = self.model()
        if model.isDir(idx):
            self.set_current_dir(self.model().filePath(idx))

    def root_dir(self):
        return "/"

    def go_up_dir(self):
        if not os.path.samefile(self._current_dir_path, self.root_dir()):
            idx = self._current_dir_path[:-1].rfind("/")
            self.set_current_dir(self._current_dir_path[:idx+1])

    def go_root_dir(self):
        self.set_current_dir(self.root_dir())

    def set_current_dir(self, path):
        self._current_dir_path = path
        idx = self.model().index(path)
        self.setRootIndex(idx)

    def current_dir(self):
        return self._current_dir_path

    def _add_menu_action(self, title, handler):
        action = QAction(title, self._context_menu)
        action.triggered.connect(handler)
        self._context_menu.addAction(action)
        return action

    def _transfer_handler(self):
        self.transfer_signal.emit()

    def _transfer_changed_handler(self):
        pass

    def _set_transfer_directory_handler(self):
        dir_row = self.selectionModel().selectedRows()[0]
        self._set_transfer_directory(self.model().filePath(dir_row))

    def _set_transfer_directory(self, path):
        self._current_dir_path = path
        idx = self.model().index(path)
        self.model().setData(idx, Qt.UserRole)

    def contextMenuEvent(self, *args, **kwargs):
        ev = args[0]
        assert isinstance(ev, QContextMenuEvent)

        point = ev.pos()
        rows = self.selectionModel().selectedRows()
        self._destination_menu_action.setEnabled(False)

        if rows:
            if len(rows) == 1 and self.model().isDir(rows[0]):
                self._destination_menu_action.setEnabled(True)

            self._context_menu.exec(self.mapToGlobal(point))


