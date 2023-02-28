import sys

from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from src.gui.main_window import MainWindow
from src.helpers.pyinstaller_helper import PyInstallerHelper
from src.utility.settings import Settings

__author__ = "Ivan Sevcik"

# Main Function
if __name__ == '__main__':
    # Create main app
    myApp = QApplication(sys.argv)
    myApp.setQuitOnLastWindowClosed(True)

    myApp.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53,53,53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(15,15,15))
    palette.setColor(QPalette.AlternateBase, QColor(53,53,53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53,53,53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)

    palette.setColor(QPalette.Highlight, QColor(142,45,197).lighter())
    palette.setColor(QPalette.HighlightedText, Qt.black)
    myApp.setPalette(palette)

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
