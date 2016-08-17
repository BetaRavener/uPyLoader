import sys

from PyQt5.QtCore import QStringListModel, QModelIndex, Qt
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileSystemModel, \
    QFileDialog, QDialog, QInputDialog, QLineEdit, QMessageBox

from gui.mainwindow import Ui_MainWindow
from src.baud_options import BaudOptions
from src.code_edit_dialog import CodeEditDialog
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
        self._code_editor = None

        self.actionNavigate.triggered.connect(self.navigate_directory)
        self.actionTerminal.triggered.connect(self.open_terminal)
        self.actionCode_Editor.triggered.connect(self.open_code_editor)
        self.actionUpload.triggered.connect(self.upload_transfer_scripts)

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
        self.listView.clicked.connect(self.mcu_file_selection_changed)
        self.listView.doubleClicked.connect(self.read_mcu_file)
        self.executeButton.clicked.connect(self.execute_mcu_code)
        self.removeButton.clicked.connect(self.remove_file)
        self.localPathEdit.setText(self._root_dir)

        self.treeView.clicked.connect(self.local_file_selection_changed)
        self.treeView.doubleClicked.connect(self.open_local_file)

        self.transferToMcuButton.clicked.connect(self.transfer_to_mcu)
        self.transferToPcButton.clicked.connect(self.transfer_to_pc)

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
        self.connectionComboBox.setEnabled(True)
        self.baudComboBox.setEnabled(True)
        self.refreshButton.setEnabled(True)
        self.listView.setEnabled(False)
        self.executeButton.setEnabled(False)
        self.removeButton.setEnabled(False)
        self.actionTerminal.setEnabled(False)
        self.actionUpload.setEnabled(False)
        self.transferToMcuButton.setEnabled(False)
        self.transferToPcButton.setEnabled(False)
        if self._terminal_dialog:
            self._terminal_dialog.close()
        if self._code_editor:
            self._code_editor.disconnected()
        self.refresh_ports()

    def connected(self):
        self.connectButton.setText("Disconnect")
        self.set_status("Connected")
        self.listButton.setEnabled(True)
        self.connectionComboBox.setEnabled(False)
        self.baudComboBox.setEnabled(False)
        self.refreshButton.setEnabled(False)
        self.listView.setEnabled(True)
        self.actionTerminal.setEnabled(True)
        if isinstance(self._connection, SerialConnection):
            self.actionUpload.setEnabled(True)
        self.transferToMcuButton.setEnabled(True)
        if self._code_editor:
            self._code_editor.connected(self._connection)
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
            self.localPathEdit.setText(self._root_dir)
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
        self.mcu_file_selection_changed()

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

    def run_file(self):
        content = self.codeEdit.toPlainText()
        self._connection.send_block(content)

    def open_local_file(self, idx):
        assert isinstance(idx, QModelIndex)
        model = self.treeView.model()
        assert isinstance(model, QFileSystemModel)

        if model.isDir(idx):
            return

        local_path = model.filePath(idx)
        remote_path = local_path.rsplit("/", 1)[1]
        if local_path.endswith(".py"):
            with open(local_path) as f:
                text = "".join(f.readlines())
                self.open_code_editor()
                self._code_editor.set_code(local_path, remote_path, text)
        else:
            QMessageBox.information(self, "Unknown file", "Files without .py ending won't open"
                                                          " in editor, but can still be transferred.")

    def mcu_file_selection_changed(self):
        idx = self.listView.currentIndex()
        assert isinstance(idx, QModelIndex)
        if idx.row() >= 0:
            self.executeButton.setEnabled(True)
            self.removeButton.setEnabled(True)
            self.transferToPcButton.setEnabled(True)
        else:
            self.executeButton.setEnabled(False)
            self.removeButton.setEnabled(False)
            self.transferToPcButton.setEnabled(False)

    def local_file_selection_changed(self):
        idx = self.treeView.currentIndex()
        assert isinstance(idx, QModelIndex)
        model = self.treeView.model()
        assert isinstance(model, QFileSystemModel)

        if model.isDir(idx):
            return

        local_path = model.filePath(idx)
        self.remoteNameEdit.setText(local_path.rsplit("/", 1)[1])

    def finished_read_mcu_file(self, file_name, transfer):
        assert isinstance(transfer, FileTransfer)
        result = transfer.read_result
        text = result.binary_data.decode("utf-8", errors="replace") if result.binary_data is not None else "!Failed to read file!"
        self.open_code_editor()
        self._code_editor.set_code(None, file_name, text)

    def read_mcu_file(self, idx):
        assert isinstance(idx, QModelIndex)
        model = self.listView.model()
        assert isinstance(model, QStringListModel)
        file_name = model.data(idx, Qt.EditRole)
        if not file_name.endswith(".py"):
            QMessageBox.information(self, "Unknown file", "Files without .py ending won't open"
                                                          " in editor, but can still be transferred.")
            return

        progress_dlg = FileTransferDialog(FileTransferDialog.DOWNLOAD)
        progress_dlg.finished.connect(lambda: self.finished_read_mcu_file(file_name, progress_dlg.transfer))
        progress_dlg.show()
        self._connection.read_file(file_name, progress_dlg.transfer)

    def upload_transfer_scripts(self):
        progress_dlg = FileTransferDialog(FileTransferDialog.UPLOAD)
        progress_dlg.finished.connect(self.list_mcu_files)
        progress_dlg.show()
        self._connection.upload_transfer_files(progress_dlg.transfer)

    def transfer_to_mcu(self):
        idx = self.treeView.currentIndex()
        assert isinstance(idx, QModelIndex)
        model = self.treeView.model()
        assert isinstance(model, QFileSystemModel)

        if model.isDir(idx):
            return

        local_path = model.filePath(idx)
        remote_path = self.remoteNameEdit.text()
        with open(local_path, "rb") as f:
            content = f.read()

        progress_dlg = FileTransferDialog(FileTransferDialog.UPLOAD)
        progress_dlg.finished.connect(self.list_mcu_files)
        progress_dlg.show()
        self._connection.write_file(remote_path, content, progress_dlg.transfer)

    def finished_transfer_to_pc(self, file_path, transfer):
        if not transfer.read_result.binary_data:
            return

        try:
            with open(file_path, "wb") as file:
                file.write(transfer.read_result.binary_data)
        except IOError:
            QMessageBox.critical(self, "Save operation failed", "Couldn't save the file. Check path and permissions.")

    def transfer_to_pc(self):
        idx = self.listView.currentIndex()
        assert isinstance(idx, QModelIndex)
        model = self.listView.model()
        assert isinstance(model, QStringListModel)
        remote_path = model.data(idx, Qt.EditRole)
        local_path = self.localPathEdit.text()+"/"+remote_path

        progress_dlg = FileTransferDialog(FileTransferDialog.DOWNLOAD)
        progress_dlg.finished.connect(lambda: self.finished_transfer_to_pc(local_path, progress_dlg.transfer))
        progress_dlg.show()
        self._connection.read_file(remote_path, progress_dlg.transfer)

    def open_terminal(self):
        if self._terminal_dialog is not None:
            return
        self._terminal_dialog = TerminalDialog(self._connection, self._terminal)
        self._terminal_dialog.finished.connect(self.close_terminal)
        self._terminal_dialog.show()

    def close_terminal(self):
        self._terminal_dialog = None

    def open_code_editor(self):
        if self._code_editor is not None:
            return
        self._code_editor = CodeEditDialog(self._connection)
        self._code_editor.mcu_file_saved.connect(self.list_mcu_files)
        self._code_editor.finished.connect(self.close_code_editor)
        self._code_editor.show()

    def close_code_editor(self):
        self._code_editor = None


# Main Function
if __name__ == '__main__':
    # Create main app
    myApp = QApplication(sys.argv)
    myApp.setQuitOnLastWindowClosed(True)

    ex2 = MainWindow()
    ex2.show()

    # Execute the Application and Exit
    sys.exit(myApp.exec_())
