from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QTreeView


class TransferTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._current_dir_path = ""

        self._context_menu = QMenu(self)
        self._add_menu_action("Transfer", self._transfer_handler)
        # TODO: Implement
        # self._add_menu_action("Transfer changed", self._transfer_changed_handler)
        self._context_menu.addSeparator()
        self._destination_menu_action = self._add_menu_action(
            "Set as destination", self._set_transfer_directory_handler)

    def _add_menu_action(self, title, handler):
        action = QAction(title, self._context_menu)
        action.triggered.connect(handler)
        self._context_menu.addAction(action)
        return action

    def _transfer_handler(self):
        pass

    def _transfer_changed_handler(self):
        pass

    def _set_transfer_directory_handler(self):
        dir_row = self.selectionModel().selectedRows()[0]
        self._set_transfer_directory(self.model().filePath(dir_row))

    def _find_item_idx_for_path(self, path):
        model = self.model()
        items_path = [QModelIndex()]
        while items_path:
            for r in range(model.rowCount(items_path[0])):
                idx = model.index(r, 0, items_path[0])
                if model.filePath(idx) == path:
                    return idx
                if model.hasChildren(idx):
                    # noinspection PyTypeChecker
                    items_path.append(idx)
            items_path.pop(0)
        return None

    def _set_transfer_directory(self, path):
        self._current_dir_path = path
        idx = self._find_item_idx_for_path(path)
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


