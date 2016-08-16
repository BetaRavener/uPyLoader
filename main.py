import sys

from PyQt5.QtCore import QStringListModel, QModelIndex, Qt
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileSystemModel, \
    QFileDialog, QDialog, QInputDialog, QLineEdit, QMessageBox

from gui.mainwindow import Ui_MainWindow
from src.baud_options import BaudOptions
from src.connection_scanner import ConnectionScanner
from src.file_transfer import FileTransfer
from src.file_transfer_dialog import FileTransferDialog
from src.ip_helper import IpHelper
from src.serial_connection import SerialConnection
from src.setting import Settings
from src.terminal import Terminal
from src.terminal_dialog import TerminalDialog
from src.wifi_connection import WifiConnection
from src.wifi_preset_dialog import WiFiPresetDialog

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

        self.actionNavigate.triggered.connect(self.navigate_directory)
        self.actionTerminal.triggered.connect(self.open_terminal)
        self.actionUpload.triggered.connect(lambda: self._connection.upload_transfer_files())

        self.connectionComboBox.currentIndexChanged.connect(self.connection_changed)
        self.refreshButton.clicked.connect(self.refresh_ports)

        # Populate baud speed combo box and select default
        self.baudComboBox.clear()
        for speed in BaudOptions.speeds:
            self.baudComboBox.addItem(str(speed))
        self.baudComboBox.setCurrentIndex(BaudOptions.speeds.index(115200))

        self.presetButton.clicked.connect(self.show_presets)

        self.connectButton.clicked.connect(self.connect_pressed)

        self.update_file_tree()

        self.listButton.clicked.connect(self.list_mcu_files)
        self.listView.clicked.connect(self.select_mcu_file)
        self.listView.doubleClicked.connect(self.read_mcu_file)
        self.executeButton.clicked.connect(self.execute_mcu_code)
        self.removeButton.clicked.connect(self.remove_file)

        self.treeView.doubleClicked.connect(self.open_local_file)

        self.saveLocalButton.clicked.connect(self.save_file_local)
        self.saveMcuButton.clicked.connect(self.save_file_to_mcu)
        self.runButton.clicked.connect(self.run_file)
        self.runButton.hide()

        fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.codeEdit.setFont(fixed_font)

        self.disconnected()

    def closeEvent(self, event):
        Settings.root_dir = self._root_dir
        Settings.save()
        if self._connection is not None and self._connection.is_connected():
            self.end_connection()
        if self._terminal_dialog:
            assert isinstance(self._terminal_dialog, QDialog)
            self._terminal_dialog.close()
        event.accept()

    def connection_changed(self):
        connection = self._connection_scanner.port_list[self.connectionComboBox.currentIndex()]
        self.connectionStackedWidget.setCurrentIndex(1 if connection == "wifi" else 0)

    def refresh_ports(self):
        self._connection_scanner.scan_connections()
        # Populate port combo box and select default
        self.connectionComboBox.clear()

        if self._connection_scanner.port_list:
            for port in self._connection_scanner.port_list:
                self.connectionComboBox.addItem(port)
            self.connectionComboBox.setCurrentIndex(0)
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
        self.runButton.setEnabled(False)
        self.connectionComboBox.setEnabled(True)
        self.baudComboBox.setEnabled(True)
        self.refreshButton.setEnabled(True)
        self.listView.setEnabled(False)
        self.filenameEdit.setEnabled(False)
        self.executeButton.setEnabled(False)
        self.removeButton.setEnabled(False)
        self.actionTerminal.setEnabled(False)
        if self._terminal_dialog:
            self._terminal_dialog.close()
        self.refresh_ports()

    def connected(self):
        self.connectButton.setText("Disconnect")
        self.set_status("Connected")
        self.listButton.setEnabled(True)
        self.saveMcuButton.setEnabled(True)
        self.runButton.setEnabled(True)
        self.connectionComboBox.setEnabled(False)
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

    def ask_for_password(self):
        input_dlg = QInputDialog(parent=self)
        input_dlg.setTextEchoMode(QLineEdit.Password)
        input_dlg.setWindowTitle("Enter WebREPL password")
        input_dlg.setLabelText("Password")
        input_dlg.resize(500, 100)
        input_dlg.exec()
        return input_dlg.textValue()

    def start_connection(self):
        connection = self._connection_scanner.port_list[self.connectionComboBox.currentIndex()]

        if connection == "wifi":
            ip_address = self.ipLineEdit.text()
            port = self.portSpinBox.value()
            if not IpHelper.is_valid_ipv4(ip_address):
                QMessageBox.warning(self, "Invalid IP", "The IP address has invalid format")
                return

            self._connection = WifiConnection(ip_address, port, self._terminal, lambda: self.ask_for_password())
        else:
            baud_rate = BaudOptions.speeds[self.baudComboBox.currentIndex()]
            self._connection = SerialConnection(connection, baud_rate, self._terminal)

        if self._connection is not None and self._connection.is_connected():
            self.connected()
        else:
            self._connection = None
            self.set_status("Error")

    def end_connection(self):
        self._connection.disconnect()
        self._connection = None
        self.disconnected()

    def show_presets(self):
        dialog = WiFiPresetDialog()
        dialog.accepted.connect(lambda: self.use_preset(dialog.selected_ip, dialog.selected_port))
        dialog.exec()

    def use_preset(self, ip, port):
        self.ipLineEdit.setText(ip)
        self.portSpinBox.setValue(port)

    def connect_pressed(self):
        if self._connection is not None and self._connection.is_connected():
            self.end_connection()
        else:
            self.start_connection()

    def save_file_local(self):
        path = self.localPathEdit.text()
        if not path:
            QMessageBox.warning(self, "Invalid path", "Enter correct path for local file.")
            return

        try:
            with open(path, "w") as file:
                file.write(self.codeEdit.toPlainText())
        except IOError:
            QMessageBox.critical(self, "Save operation failed", "Couldn't save the file. Check path and permissions.")

    def save_file_to_mcu(self):
        name = self.filenameEdit.text()
        if not name:
            QMessageBox.warning(self, "Invalid name", "Enter correct name for remote file.")
            return
        content = self.codeEdit.toPlainText()
        if not content:
            QMessageBox.warning(self, "Empty file", "Can't write empty file.")
            return

        progress_dlg = FileTransferDialog(FileTransferDialog.UPLOAD)
        progress_dlg.finished.connect(self.list_mcu_files)
        progress_dlg.show()
        self._connection.write_file(name, content, progress_dlg.transfer)

    def run_file(self):
        content = self.codeEdit.toPlainText()
        self._connection.send_block(content)

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

    def select_mcu_file(self):
        self.executeButton.setEnabled(True)
        self.removeButton.setEnabled(True)

    def finished_read_mcu_file(self, file_name, transfer):
        assert isinstance(transfer, FileTransfer)
        result = transfer.read_result
        text = result.binary_data.decode("utf-8", errors="replace") if result.binary_data is not None else "!Failed to read file!"
        self.codeEdit.clear()
        self.codeEdit.setText(text)
        self.filenameEdit.setText(file_name)

    def read_mcu_file(self, idx):
        assert isinstance(idx, QModelIndex)
        model = self.listView.model()
        assert isinstance(model, QStringListModel)
        file_name = model.data(idx, Qt.EditRole)

        progress_dlg = FileTransferDialog(FileTransferDialog.DOWNLOAD)
        progress_dlg.finished.connect(lambda: self.finished_read_mcu_file(file_name, progress_dlg.transfer))
        progress_dlg.show()
        self._connection.read_file(file_name, progress_dlg.transfer)

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
