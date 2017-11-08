from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QTreeView


class TransferTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.context_menu = QMenu(self)

        self._add_menu_action("Transfer", self._transfer_handler)
        # TODO: Implement
        # self._add_menu_action("Transfer changed", self._transfer_changed_handler)
        self.context_menu.addSeparator()
        self._destination_menu_action = self._add_menu_action(
            "Set as destination", self._set_transfer_directory_handler)

    def _add_menu_action(self, title, handler):
        action = QAction(title, self.context_menu)
        action.triggered.connect(handler)
        self.context_menu.addAction(action)
        return action

    def _transfer_handler(self):
        pass

    def _transfer_changed_handler(self):
        pass

    def _set_transfer_directory_handler(self):
        pass

    def contextMenuEvent(self, *args, **kwargs):
        ev = args[0]
        assert isinstance(ev, QContextMenuEvent)

        point = ev.pos()
        rows = self.selectionModel().selectedRows()
        self._destination_menu_action.setEnabled(False)

        if rows:
            if len(rows) == 1 and self.model().isDir(rows[0]):
                self._destination_menu_action.setEnabled(True)

            self.context_menu.exec(self.mapToGlobal(point))


