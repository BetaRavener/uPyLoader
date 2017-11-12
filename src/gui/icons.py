from PyQt5.QtGui import QIcon

from src.utility.singleton import Singleton


class Icons(metaclass=Singleton):
    def __init__(self):
        self.tree_file = QIcon("icons/tree_file.png")
        self.tree_folder = QIcon("icons/tree_folder.png")
        self.tree_python = QIcon("icons/tree_python.png")
