import sys

from PyQt5.QtCore import QStringListModel, QModelIndex, Qt
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileSystemModel, QFileDialog, QDialog, QInputDialog, QLineEdit

from gui.mainwindow import Ui_MainWindow
from src.baud_options import BaudOptions
from src.connection_scanner import ConnectionScanner
from src.serial_connection import SerialConnection
from src.setting import Settings
from src.terminal import Terminal
from src.terminal_dialog import TerminalDialog
from src.wifi_connection import WifiConnection

__author__ = "Ivan Sevcik"


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setAttribute(Qt.WA_QuitOnClose)

        self._connection_scanner = ConnectionScanner()
        self._connection = None
        self._root_dir = Settings.root_dir
        self._mcu_files_model = None
        self._terminal = Terminal()
        self._terminal_dialog = None

        self.disconnected()

        self.actionNavigate.triggered.connect(self.navigate_directory)
        self.actionTerminal.triggered.connect(self.open_terminal)
        self.actionUpload.triggered.connect(lambda: self._connection.upload_transfer_files())

        self.refreshButton.clicked.connect(self.refresh_ports)

        # Populate baud speed combo box and select default
        self.baudComboBox.clear()
        for speed in BaudOptions.speeds:
            self.baudComboBox.addItem(str(speed))
        self.baudComboBox.setCurrentIndex(BaudOptions.speeds.index(115200))

        self.connectButton.clicked.connect(self.connect_pressed)

        self.update_file_tree()

        self.listButton.clicked.connect(self.list_mcu_files)
        self.listView.doubleClicked.connect(self.read_mcu_file)
        self.executeButton.clicked.connect(self.execute_mcu_code)
        self.removeButton.clicked.connect(self.remove_file)

        self.treeView.doubleClicked.connect(self.open_local_file)

        self.saveLocalButton.clicked.connect(self.save_file_local)
        self.saveMcuButton.clicked.connect(self.save_file_to_mcu)

        fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.codeEdit.setFont(fixed_font)

    def closeEvent(self, event):
        Settings.root_dir = self._root_dir
        Settings.save()
        if self._connection is not None and self._connection.is_connected():
            self.end_connection()
        if self._terminal_dialog:
            assert isinstance(self._terminal_dialog, QDialog)
            self._terminal_dialog.close()
        event.accept()

    def refresh_ports(self):
        self._connection_scanner.scan_connections()
        # Populate port combo box and select default
        self.portComboBox.clear()

        if self._connection_scanner.port_list:
            for port in self._connection_scanner.port_list:
                self.portComboBox.addItem(port)
            self.portComboBox.setCurrentIndex(0)
            self.connectButton.setEnabled(True)
        else:
            self.connectButton.setEnabled(False)

    def set_status(self, status):
        if status == "Connected":
            self.statusLabel.setStyleSheet("QLabel { background-color : none; color : green; font : bold;}")
        elif status == "Disconnected":
            self.statusLabel.setStyleSheet("QLabel { background-color : none; color : red; }")
        elif status == "Error":
            self.statusLabel.setStyleSheet("QLabel { background-color : red; color : white; }")
        self.statusLabel.setText(status)

    def disconnected(self):
        self.connectButton.setText("Connect")
        self.set_status("Disconnected")
        self.listButton.setEnabled(False)
        self.saveMcuButton.setEnabled(False)
        self.portComboBox.setEnabled(True)
        self.baudComboBox.setEnabled(True)
        self.refreshButton.setEnabled(True)
        self.listView.setEnabled(False)
        self.filenameEdit.setEnabled(False)
        self.actionTerminal.setEnabled(False)
        if self._terminal_dialog:
            self._terminal_dialog.close()
        self.refresh_ports()

    def connected(self):
        self.connectButton.setText("Disconnect")
        self.set_status("Connected")
        self.listButton.setEnabled(True)
        self.saveMcuButton.setEnabled(True)
        self.portComboBox.setEnabled(False)
        self.baudComboBox.setEnabled(False)
        self.refreshButton.setEnabled(False)
        self.listView.setEnabled(True)
        self.filenameEdit.setEnabled(True)
        self.actionTerminal.setEnabled(True)
        self.list_mcu_files()

    def navigate_directory(self):
        dialog = QFileDialog()
        dialog.setDirectory(self._root_dir)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly)
        dialog.exec()
        path = dialog.selectedFiles()
        if path and path[0]:
            self._root_dir = path[0]
            self.update_file_tree()

    def update_file_tree(self):
        model = QFileSystemModel()
        model.setRootPath(self._root_dir)
        self.treeView.setModel(model)
        self.treeView.setRootIndex(model.index(self._root_dir))

    def list_mcu_files(self):
        file_list = self._connection.list_files()
        self._mcu_files_model = QStringListModel()

        for file in file_list:
            idx = self._mcu_files_model.rowCount()
            self._mcu_files_model.insertRow(idx)
            self._mcu_files_model.setData(self._mcu_files_model.index(idx), file)

        self.listView.setModel(self._mcu_files_model)

    def execute_mcu_code(self):
        idx = self.listView.currentIndex()
        assert isinstance(idx, QModelIndex)
        model = self.listView.model()
        assert isinstance(model, QStringListModel)
        file_name = model.data(idx, Qt.EditRole)
        self._connection.run_file(file_name)

    def remove_file(self):
        idx = self.listView.currentIndex()
        assert isinstance(idx, QModelIndex)
        model = self.listView.model()
        assert isinstance(model, QStringListModel)
        file_name = model.data(idx, Qt.EditRole)
        self._connection.remove_file(file_name)
        self.list_mcu_files()

    def start_connection(self):
        port = self._connection_scanner.port_list[self.portComboBox.currentIndex()]
        baud_rate = BaudOptions.speeds[self.baudComboBox.currentIndex()]

        if port == "wifi":
            input_dlg = QInputDialog(parent=self)
            input_dlg.setTextEchoMode(QLineEdit.Password)
            input_dlg.setWindowTitle("Enter WebREPL password")
            input_dlg.setLabelText("Password")
            input_dlg.resize(500, 100)
            input_dlg.exec()
            password = input_dlg.textValue()
            self._connection = WifiConnection("192.168.4.1", 8266, self._terminal, password)
        else:
            self._connection = SerialConnection(port, baud_rate, self._terminal)

        if self._connection is not None and self._connection.is_connected():
            self.connected()
        else:
            self._connection = None
            self.set_status("Error")

    def end_connection(self):
        self._connection.disconnect()
        self._connection = None
        self.disconnected()

    def connect_pressed(self):
        if self._connection is not None and self._connection.is_connected():
            self.end_connection()
        else:
            self.start_connection()

    def save_file_local(self):
        idx = self.treeView.currentIndex()
        assert isinstance(idx, QModelIndex)
        with open(self.localPathEdit.text(), "w") as file:
            file.write(self.codeEdit.toPlainText())

    def save_file_to_mcu(self):
        self._connection.write_file(self.filenameEdit.text(), self.codeEdit.toPlainText())

    def open_local_file(self, idx):
        assert isinstance(idx, QModelIndex)
        model = self.treeView.model()
        assert isinstance(model, QFileSystemModel)

        if model.isDir(idx):
            return

        file_path = model.filePath(idx)
        with open(file_path) as f:
            text = "".join(f.readlines())
            self.codeEdit.clear()
            self.codeEdit.setText(text)
            self.localPathEdit.setText(file_path)
            self.filenameEdit.setText(file_path.rsplit("/", 1)[1])

    def read_mcu_file(self, idx):
        assert isinstance(idx, QModelIndex)
        model = self.listView.model()
        assert isinstance(model, QStringListModel)
        file_name = model.data(idx, Qt.EditRole)

        text = self._connection.read_file(file_name)

        self.codeEdit.clear()
        self.codeEdit.setText(text)
        self.filenameEdit.setText(file_name)

    def open_terminal(self):
        if self._terminal_dialog is not None:
            return
        self._terminal_dialog = TerminalDialog(self._connection, self._terminal)
        self._terminal_dialog.finished.connect(self.close_terminal)
        self._terminal_dialog.show()

    def close_terminal(self):
        self._terminal_dialog = None


# Main Function
if __name__ == '__main__':
    # Create main app
    myApp = QApplication(sys.argv)
    myApp.setQuitOnLastWindowClosed(True)

    ex2 = MainWindow()
    ex2.show()

    # Execute the Application and Exit
    sys.exit(myApp.exec_())
