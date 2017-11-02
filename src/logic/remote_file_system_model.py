from PyQt5.QtCore import QAbstractItemModel
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QVariant

# Implemented accoring to http://doc.qt.io/qt-5/qtwidgets-itemviews-simpletreemodel-example.html
from PyQt5.QtCore import Qt


class RemoteNode:
    def __init__(self, data, parent):
        assert parent is None or isinstance(parent, RemoteNode)
        self._parent = parent
        self._data = data
        self._children = []
        ## If the item has no parent, an invalid QModelIndex is returned.

    def data(self, column):
        return self._data[column]

    def append_child(self, node):
        self._children.append(node)
        return node

    def parent(self):
        return self._parent

    def column_count(self):
        return len(self._data)

    def child_count(self):
        return len(self._children)

    def child(self, row):
        return self._children[row]

    def row(self):
        if self._parent is None:
            return 0
        return self._parent._children.index(self)


class RemoteFileSystemModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Root node contains vertical header data and is used to represent
        # an imaginary parent of top-level items in the model
        self._root_node = RemoteNode(["Name"], None)
        self._setup_model_data()

    def _setup_model_data(self):
        r = self._root_node.append_child(RemoteNode(["root"], self._root_node))
        r.append_child(RemoteNode(["child"], r))

    def _find_node(self, index):
        return RemoteFileSystemModel._walk_structure(self._root_node, lambda x: x.owns_index(index))

    @staticmethod
    def _walk_structure(start_node, stop_condition):
        assert isinstance(start_node, RemoteNode)
        if stop_condition(start_node):
            return start_node
        else:
            for child in start_node.children():
                if RemoteFileSystemModel._walk_structure(child, stop_condition):
                    return child
        return None

    def isDir(self, index):
        assert isinstance(index, QModelIndex)
        return False

    # def refresh(self):
    #     # file_list = self._connection.list_files()
    #
    #     for file in file_list:
    #         idx = self._mcu_files_model.rowCount()
    #         self._mcu_files_model.insertRow(idx)
    #         self._mcu_files_model.setData(self._mcu_files_model.index(idx), file)
    #
    #     self.mcuFilesListView.setModel(self._mcu_files_model)
    #     self.mcu_file_selection_changed()

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().column_count()
        else:
            return self._root_node.column_count()

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_node = self._root_node
        else:
            parent_node = parent.internalPointer()

        return parent_node.child_count()

    # TODO:
    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child_node = index.internalPointer()
        parent_node = child_node.parent()

        if parent_node is None or parent_node is self._root_node:
            return QModelIndex()

        return self.createIndex(parent_node.row(), 0, parent_node)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal or role == Qt.DisplayRole:
            return self._root_node.data(section)

        return None

    def flags(self, index):
        if not index.isValid():
            return 0

        return super().flags(index)

    def data(self, index, role):
        if not index.isValid():
            return None
        if role != Qt.DisplayRole:
            return None

        node = index.internalPointer()

        return node.data(index.column())

    def index(self, row, column, parent=None):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_node = self._root_node
        else:
            parent_node = parent.internalPointer()

        child_node = parent_node.child(row)
        if child_node:
            return self.createIndex(row, column, child_node)
        else:
            return QModelIndex()

