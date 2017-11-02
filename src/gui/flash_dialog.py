import subprocess
import time
from threading import Thread, Lock

import serial
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QDialog, QScrollBar, QMessageBox, QFileDialog

from gui.flash_dialog import Ui_FlashDialog
from src.connection.connection_scanner import ConnectionScanner
from src.utility.logger import Logger
from src.utility.settings import Settings


class FlashDialog(QDialog, Ui_FlashDialog):
    _flash_output_signal = pyqtSignal()
    _flash_finished_signal = pyqtSignal(int)

    def __init__(self, parent):
        super(FlashDialog, self).__init__(parent, Qt.WindowCloseButtonHint)
        self.setupUi(self)
        self.setModal(True)

        self._connection_scanner = ConnectionScanner()
        self._port = None
        self._flash_output = None
        self._flash_output_mutex = Lock()
        self._flashing = False

        if Settings().python_flash_executable:
            self.pythonPathEdit.setText(Settings().python_flash_executable)

        self.pickPythonButton.clicked.connect(self._pick_python)
        self.pickFirmwareButton.clicked.connect(self._pick_firmware)
        self.refreshButton.clicked.connect(self._refresh_ports)
        self.wiringButton.clicked.connect(self._show_wiring)
        self.eraseButton.clicked.connect(lambda: self._start(False, True))
        self.flashButton.clicked.connect(lambda: self._start(True, False))

        self._flash_output_signal.connect(self._update_output)
        self._flash_finished_signal.connect(self._flash_finished)

        self._refresh_ports()

    def closeEvent(self, event):
        if self._flashing:
            event.ignore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self._flashing:
            event.ignore()

    def _refresh_ports(self):
        self._connection_scanner.scan_connections(with_wifi=False)
        # Populate port combo box and select default
        self.portComboBox.clear()

        if self._connection_scanner.port_list:
            for port in self._connection_scanner.port_list:
                self.portComboBox.addItem(port)
            self.portComboBox.setCurrentIndex(0)
            self.eraseButton.setEnabled(True)
            self.flashButton.setEnabled(True)
        else:
            self.eraseButton.setEnabled(False)
            self.flashButton.setEnabled(False)

    def _pick_python(self):
        p = QFileDialog.getOpenFileName(parent=self, caption="Select python executable")
        path = p[0]
        if path:
            self.pythonPathEdit.setText(path)
            Settings().python_flash_executable = path

    def _pick_firmware(self):
        firmware_dir = None
        if Settings().last_firmware_directory:
            firmware_dir = Settings().last_firmware_directory

        p = QFileDialog.getOpenFileName(parent=self, caption="Select python executable",
                                        directory=firmware_dir, filter="*.bin")
        path = p[0]
        if path:
            self.firmwarePathEdit.setText(path)
            Settings().last_firmware_directory = "/".join(path.split("/")[0:-1])

    def _show_wiring(self):
        wiring = "RST\t-> RTS\n" \
                 "GPIO0\t-> DTR\n" \
                 "TXD\t-> RXD\n" \
                 "RXD\t-> TXD\n" \
                 "VCC\t-> 3V3\n" \
                 "GND\t-> GND"
        QMessageBox.information(self, "Wiring", wiring)

    def _update_output(self):
        scrollbar = self.outputEdit.verticalScrollBar()
        assert isinstance(scrollbar, QScrollBar)
        # Preserve scroll while updating content
        current_scroll = scrollbar.value()
        scrolling = scrollbar.isSliderDown()

        with self._flash_output_mutex:
            self.outputEdit.setPlainText(self._flash_output.decode('utf-8', errors="ignore"))

        if not scrolling:
            scrollbar.setValue(scrollbar.maximum())
        else:
            scrollbar.setValue(current_scroll)

    def _flash_job(self, python_path, firmware_file, erase_flash):
        try:
            params = [python_path, "flash.py", self._port]
            if firmware_file:
                params.append("--fw={}".format(firmware_file))
            if erase_flash:
                params.append("--erase")
            if Settings().debug_mode:
                params.append("--debug")
            with subprocess.Popen(params, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                  stderr=subprocess.PIPE, bufsize=1) as sub:
                buf = bytearray()
                delete = 0
                Logger.log("Pipe receiving:\r\n")
                while True:
                    x = sub.stdout.read(1)
                    Logger.log(x)

                    # Flushing content only in large blocks helps with flickering
                    # Flush output if:
                    # - didn't receive any character (timeout?)
                    # - received first backspace (content is going to be deleted)
                    # - received whitespace or dot (used to signal progress)
                    if not x \
                            or (x[0] == 8 and delete == 0) \
                            or (x[0] in b"\r\n\t ."):
                        with self._flash_output_mutex:
                            if delete > 0:
                                self._flash_output = self._flash_output[:-delete]
                            self._flash_output.extend(buf)
                        self._flash_output_signal.emit()
                        buf = bytearray()
                        delete = 0

                    if not x:
                        break

                    if x[0] == 8:
                        delete += 1
                    else:
                        buf.append(x[0])

                Logger.log("\r\nPipe end.\r\n")
                sub.stdout.close()
                code = sub.wait()

                self._flash_finished_signal.emit(code)
        except (FileNotFoundError, OSError):
            self._flash_finished_signal.emit(-1)
            return

    def _start(self, flash, erase):
        self._flash_output = bytearray()
        self.outputEdit.setPlainText("")
        python_path = self.pythonPathEdit.text()
        if not python_path:
            QMessageBox.critical(self, "Error", "Python2 path was not set.")
            return
        firmware_file = None
        if flash:
            firmware_file = self.firmwarePathEdit.text()
            if not firmware_file:
                QMessageBox.critical(self, "Error", "Firmware file was not set.")
                return
        self._port = self._connection_scanner.port_list[self.portComboBox.currentIndex()]
        job_thread = Thread(target=self._flash_job, args=[python_path, firmware_file, erase])
        job_thread.setDaemon(True)
        job_thread.start()
        self.eraseButton.setEnabled(False)
        self.flashButton.setEnabled(False)
        self._flashing = True

    def _flash_finished(self, code):
        Logger.log("Flash output contents:\r\n")
        Logger.log(self._flash_output)

        if code == 0:
            self._flash_output.extend(b"Rebooting from flash mode...\n")
            self._update_output()
            try:
                s = serial.Serial(self._port, 115200)
                s.dtr = False
                s.rts = True
                time.sleep(0.1)
                s.rts = False
                time.sleep(0.1)
                self._flash_output.extend(b"Done, you may now use the device.\n")
                self._update_output()
            except (OSError, serial.SerialException):
                QMessageBox.critical(self, "Flashing Error", "Failed to reboot into working mode.")

        elif code == -1:
            QMessageBox.critical(self, "Flashing Error", "Failed to run script.\nCheck that path to python is correct.")
        else:
            QMessageBox.critical(self, "Flashing Error", "Failed to flash new firmware")
        self.eraseButton.setEnabled(True)
        self.flashButton.setEnabled(True)
        self._flashing = False
