from PyQt5.QtCore import QStringListModel, QModelIndex, Qt
from PyQt5.QtWidgets import QDialog, QMessageBox

from gui.wifi_preset import Ui_WiFiPresetDialog
from src.helpers.ip_helper import IpHelper
from src.utility.settings import Settings

__author__ = "Ivan Sevcik"


class WiFiPresetDialog(QDialog, Ui_WiFiPresetDialog):
    def __init__(self):
        super(WiFiPresetDialog, self).__init__(None, Qt.WindowCloseButtonHint)
        self.setupUi(self)

        self.selected_ip = None
        self.selected_port = None
        self.selected_password = None

        self.presetsListView.doubleClicked.connect(self.select_preset)
        self.addButton.clicked.connect(self.add_preset)
        self.removeButton.clicked.connect(self.remove_preset)

        self.model = QStringListModel()
        self.presetsListView.setModel(self.model)
        self.update_preset_list()

    def update_preset_list(self):
        self.model.removeRows(0, self.model.rowCount())
        for preset in Settings().wifi_presets:
            idx = self.model.rowCount()
            self.model.insertRow(idx)
            name, ip, port, _ = preset
            text = "{}\nIP: {}    Port: {}".format(name, ip, port)
            self.model.setData(self.model.index(idx), text)

    def closeEvent(self, event):
        self.reject()
        event.accept()

    def add_preset(self):
        name = self.nameLineEdit.text()
        ip = self.ipLineEdit.text()
        port = self.portSpinBox.value()
        password = self.passwordLineEdit.text()
        # Make sure password is non if empty
        if not password:
            password = None

        if not name:
            QMessageBox().warning(self, "Missing name", "Fill the name of preset", QMessageBox.Ok)
            return

        if not IpHelper.is_valid_ipv4(ip):
            QMessageBox().warning(self, "Invalid IP", "The IP address has invalid format", QMessageBox.Ok)
            return

        Settings().wifi_presets.append((name, ip, port, password))
        self.update_preset_list()

    def remove_preset(self):
        idx = self.presetsListView.currentIndex()
        assert isinstance(idx, QModelIndex)
        if idx.row() < 0:
            return

        Settings().wifi_presets.remove(Settings().wifi_presets[idx.row()])
        self.update_preset_list()

    def select_preset(self):
        idx = self.presetsListView.currentIndex()
        assert isinstance(idx, QModelIndex)
        if idx.row() < 0:
            return

        _, self.selected_ip, self.selected_port, self.selected_password = Settings().wifi_presets[idx.row()]
        self.accept()
