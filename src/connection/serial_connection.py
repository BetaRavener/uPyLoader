import base64
import os
import re
import time
from threading import Thread

import serial
from src.utility.settings import Settings

from src.connection.connection import Connection
from src.helpers.pyinstaller_helper import PyInstallerHelper
from src.logic.file_transfer import FileTransfer, FileTransferError
from src.utility.exceptions import OperationError


class SerialConnection(Connection):
    def __init__(self, port, baud_rate, terminal=None, reset=False):
        Connection.__init__(self, terminal)

        self._port = port
        self._baud_rate = baud_rate

        try:
            self._serial = serial.Serial(None, self._baud_rate, timeout=0, write_timeout=0.2)
            self._serial.dtr = False
            self._serial.rts = False
            self._serial.port = port
            self._serial.open()
            if reset:
                self._serial.rts = True
                time.sleep(0.1)
                self._serial.rts = False
                x = ""
                while not x.endswith(">>>"):
                    x += self._serial.read().decode('utf-8', errors="ignore")
            self.send_kill()
        except (OSError, serial.SerialException) as e:
            self._serial = None
            return
        except Exception as e:
            return

        self._reader_thread = Thread(target=self._reader_thread_routine)
        self._reader_thread.start()

    def is_connected(self):
        return self._serial is not None

    def disconnect(self):
        if self.is_connected():
            if self._reader_thread.is_alive():
                self._reader_running = False
                self._reader_thread.join()
            self._serial.close()
            self._serial = None

    def send_line(self, line_text, ending="\r\n"):
        assert isinstance(line_text, str)
        assert isinstance(ending, str)

        self._serial.write((line_text + ending).encode('utf-8'))
        time.sleep(Settings().send_sleep)

    def send_character(self, char):
        assert isinstance(char, str)

        self._serial.write(char.encode('utf-8'))
        time.sleep(Settings().send_sleep)

    def send_bytes(self, binary):
        self._serial.write(binary)
        time.sleep(Settings().send_sleep)

    def read_line(self):
        x = self._serial.readline()

        if x and self._terminal is not None:
            if x == b'\x08\x1b[K':
                x = b'\x08'

            self._terminal.add(x.decode("utf-8", errors="replace"))

        return x

    def _break_device_read(self):
        time.sleep(1)
        self.send_kill()

    def read_with_timeout(self, count, timeout_s=2.0):
        period = 0.005
        data = bytearray()
        for i in range(0, int(timeout_s / period)):
            rec = self._serial.read(count - len(data))
            if rec:
                data.extend(rec)
                if len(data) == count:
                    return bytes(data)
            time.sleep(period)

        return None

    def read_all(self):
        buffer = ""
        while True:
            x = self._serial.read(100)
            if x is None or not x:
                break
            buffer += x.decode('utf-8', errors="replace")

        if self._terminal is not None:
            self._terminal.add(buffer)

        return buffer

    def read_junk(self):
        self.read_all()

    def read_one_byte(self):
        return self._serial.read(1)

    def list_files(self):
        success = True
        self._auto_reader_lock.acquire()
        self._auto_read_enabled = False
        self.send_kill()
        self.read_junk()
        self.send_line("import os; os.listdir()")
        self._serial.flush()
        ret = ""
        try:
            ret = self.read_to_next_prompt()
        except TimeoutError:
            success = False
        self._auto_read_enabled = True
        self._auto_reader_lock.release()

        if success and ret:
            return re.findall("'([^']+)'", ret)
        else:
            raise OperationError()

    @staticmethod
    def escape_characters(text):
        ret = ""
        for c in text:
            if c == "\n":
                ret += "\\n"
            elif c == "\"":
                ret += "\\\""
            else:
                ret += c
        return ret

    def check_transfer_scripts_version(self):
        self._auto_reader_lock.acquire()
        self._auto_read_enabled = False
        self.send_kill()
        self.read_junk()
        self.send_block("with open(\"__upload.py\") as f:\n  f.readline()\n")
        self._serial.flush()
        success = True
        try:
            resp = self.read_to_next_prompt()
            idx = resp.find("#V")
            if idx < 0 or resp[idx:idx+3] != "#V2":
                raise ValueError
            self.read_junk()
            self.send_block("with open(\"__download.py\") as f:\n  f.readline()\n")
            self._serial.flush()
            resp = self.read_to_next_prompt()
            idx = resp.find("#V")
            if idx < 0 or resp[idx:idx+3] != "#V2":
                raise ValueError
        except (TimeoutError, ValueError):
            success = False
        self._auto_read_enabled = True
        self._auto_reader_lock.release()
        return success

    @staticmethod
    def _transfer_file_path(transfer_file_name):
        # External transfer scripts folder should be used (use case: files need to be edited)
        if Settings().external_transfer_scripts_folder:
            path = "".join([Settings().external_transfer_scripts_folder, "/", transfer_file_name])
            # Check if file exists. If not, ignore external folder path.
            if os.path.isfile(path):
                return path
            else:
                raise FileNotFoundError

        return PyInstallerHelper.resource_path("mcu/" + transfer_file_name)

    def send_upload_file(self, file_name):
        with open(SerialConnection._transfer_file_path("upload.py")) as f:
            data = f.read()
            data = data.replace("file_name.py", file_name)
            self.send_start_paste()
            lines = data.split("\n")
            for line in lines:
                self.send_line(line, "\r")
            self.send_end_paste()

    def send_download_file(self, file_name):
        with open(SerialConnection._transfer_file_path("download.py")) as f:
            data = f.read()
            data = data.replace("file_name.py", file_name)
            self.send_start_paste()
            lines = data.split("\n")
            for line in lines:
                self.send_line(line, "\r")
            self.send_end_paste()

    def _upload_transfer_files_job(self, transfer):
        assert isinstance(transfer, FileTransfer)
        transfer.set_file_count(2)
        self._auto_reader_lock.acquire()
        self._auto_read_enabled = False
        try:
            self.send_upload_file("__upload.py")
            self.read_all()
            with open(SerialConnection._transfer_file_path("upload.py")) as f:
                data = f.read()
                data = data.replace("\"file_name.py\"", "file_name")
                self.send_file(data.encode('utf-8'), transfer)
            transfer.mark_finished()

            self.run_file("__upload.py", "file_name=\"{}\"".format("__download.py"))
            self.read_all()
            with open(SerialConnection._transfer_file_path("download.py")) as f:
                data = f.read()
                data = data.replace("\"file_name.py\"", "file_name")
                self.send_file(data.encode('utf-8'), transfer)
            transfer.mark_finished()
        except FileNotFoundError:
            transfer.mark_error("Couldn't locate transfer scripts.")
        except FileTransferError as e:
            transfer.mark_error(e.details)
        self._auto_read_enabled = True
        self._auto_reader_lock.release()

    def upload_transfer_files(self, transfer):
        job_thread = Thread(target=self._upload_transfer_files_job, args=[transfer])
        # Set thread as daemon so in case main window is closed, this
        # tasks gets aborted and program will close immediately
        job_thread.setDaemon(True)
        job_thread.start()

    def handle_transfer_error(self, message):
        # Make sure that the device isn't stuck in read
        self._break_device_read()
        raise FileTransferError(message)

    def send_file(self, data, transfer):
        assert isinstance(transfer, FileTransfer)
        # Split data into smaller chunks
        idx = 0
        # Using chunks of 48 bytes, encoded chunk should be at most 64 bytes
        n = 48
        total_len = len(data)
        while idx < total_len:
            chunk = data[idx:idx + n]
            # Encode data to prevent special REPL sequences
            en_chunk = base64.b64encode(chunk)
            self._serial.write(b"".join([b"#", str(len(en_chunk)).zfill(2).encode("ascii"), en_chunk]))
            ack = self.read_with_timeout(2)

            error = None
            if not ack:
                error = "Device failed to respond in specified timeout."
            elif ack == b"#2":
                error = "Device didn't receive next message in time or message header got corrupted."
            elif ack == b"#3":
                error = "Device didn't receive as much data as was indicated in the message header."
            elif ack != b"#1":
                error = "Error in protocol. Expected #1 but device replied with:\n{}.".format(
                    ack.decode(errors='ignore'))

            if error:
                error += "\n\nLast message was:\n{}.".format(chunk.decode(errors='ignore'))
                self.handle_send_file_error(error)

            idx += len(chunk)
            transfer.progress = idx / total_len

        # Mark end and check for success
        self._serial.write(b"#00")
        check = self.read_with_timeout(2)

        error = None
        if not check:
            error = "Device failed to respond in specified timeout."
        if check != b"#0":
            error = "Error in protocol. Expected #0 but device replied with: {}.".format(
                check.decode(errors='ignore'))

        if error:
            self.handle_send_file_error(error)

    def recv_file(self, transfer):
        assert isinstance(transfer, FileTransfer)
        result = b""

        # Initiate transfer
        self._serial.write(b"###")
        while True:
            data = self.read_with_timeout(3)
            if not data or data[0] != ord("#"):
                self._serial.write(b"#2")
                break
            count = int(data[1:3])
            if count == 0:
                transfer.read_result.binary_data = result
                return
            data = self.read_with_timeout(count)
            if data:
                result += base64.b64decode(data)
                # Send ACK
                self._serial.write(b"#1")
            else:
                self._serial.write(b"#3")
                break

        transfer.read_result.binary_data = None
        self.handle_transfer_error("")

    def _write_file_job(self, file_name, text, transfer):
        if isinstance(text, str):
            text = text.encode('utf-8')

        self._auto_reader_lock.acquire()
        self._auto_read_enabled = False
        if Settings().use_transfer_scripts:
            self.run_file("__upload.py", "file_name=\"{}\"".format(file_name))
        else:
            try:
                self.send_upload_file(file_name)
            except FileNotFoundError:
                transfer.mark_error("Couldn't locate upload transfer script.")
        if not transfer.error:
            self.read_junk()
            try:
                self.send_file(text, transfer)
                transfer.mark_finished()
            except FileTransferError as e:
                transfer.mark_error(e.details)
        self._auto_read_enabled = True
        self._auto_reader_lock.release()

    def _read_file_job(self, file_name, transfer):
        self._auto_reader_lock.acquire()
        self._auto_read_enabled = False
        if Settings().use_transfer_scripts:
            self.run_file("__download.py", "file_name=\"{}\"".format(file_name))
        else:
            try:
                self.send_download_file(file_name)
            except FileNotFoundError:
                transfer.mark_error("Couldn't locate download transfer script.")
        if not transfer.error:
            self.read_junk()
            try:
                self.recv_file(transfer)
                transfer.mark_finished()
            except FileTransferError as e:
                transfer.mark_error(e.details)
        self._auto_read_enabled = True
        self._auto_reader_lock.release()
