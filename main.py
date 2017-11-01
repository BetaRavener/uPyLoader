import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from src.gui.main_window import MainWindow
from src.helpers.pyinstaller_helper import PyInstallerHelper
from src.utility.settings import Settings

__author__ = "Ivan Sevcik"

# Main Function
if __name__ == '__main__':
    # Create main app
    myApp = QApplication(sys.argv)
    myApp.setQuitOnLastWindowClosed(True)

    path = PyInstallerHelper.resource_path("icons\\main.png")

    icon = QIcon(path)
    myApp.setWindowIcon(icon)

    try:
        sys.argv.index("--debug")
        Settings().debug_mode = True
    except ValueError:
        pass

    ex2 = MainWindow()
    ex2.show()

    # Execute the Application and Exit
    sys.exit(myApp.exec_())
