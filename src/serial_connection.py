from threading import Thread

import re
import serial
import time

from src.connection import Connection
from src.file_transfer import FileTransfer, ReadResult
from src.setting import Settings


class SerialConnection(Connection):
    def __init__(self, port, baud_rate, terminal=None):
        Connection.__init__(self, terminal)

        self._port = port
        self._baud_rate = baud_rate

        try:
            # These timeouts should be large enough so that any continuous transmission is fully received
            self._serial = serial.Serial(self._port, self._baud_rate, timeout=0.2, write_timeout=0.2)
            self.send_kill()
        except (OSError, serial.SerialException):
            self._serial = None
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
        time.sleep(Settings.send_sleep)

    def send_character(self, char):
        assert isinstance(char, str)

        self._serial.write(char.encode('utf-8'))
        time.sleep(Settings.send_sleep)

    def read_line(self):
        x = self._serial.readline()

        if x and self._terminal is not None:
            self._terminal.add(x.decode("utf-8", errors="replace"))

        return x

    def read_timeout(self, count, retries=100):
        data = b""
        for i in range(0, retries):
            rec = self._serial.read(count - len(data))
            if rec:
                data += rec
                if len(data) == count:
                    return data
            time.sleep(0.01)
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

    def list_files(self):
        self._auto_reader_lock.acquire()
        self._auto_read_enabled = False
        self.send_kill()
        self.read_junk()
        self.send_line("import os; os.listdir()")
        self._serial.flush()

        ret = self.read_all()
        self._auto_read_enabled = True
        self._auto_reader_lock.release()
        return re.findall("'([^']+)'", ret)

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

    def send_upload_file(self, file_name):
        with open("mcu/upload.py") as f:
            data = f.read()
            data = data.replace("file_name.py", file_name)
            self.send_start_paste()
            lines = data.split("\n")
            for line in lines:
                self.send_line(line, "\r")
            self.send_end_paste()

    def send_download_file(self, file_name):
        with open("mcu/download.py") as f:
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
        self.send_upload_file("__upload.py")
        self.read_all()
        with open("mcu/upload.py") as f:
            data = f.read()
            data = data.replace("\"file_name.py\"", "file_name")
            res = self.send_file(data.encode('utf-8'), transfer)

        self.send_upload_file("__download.py")
        self.read_all()
        with open("mcu/download.py") as f:
            data = f.read()
            data = data.replace("\"file_name.py\"", "file_name")
            res = self.send_file(data.encode('utf-8'), transfer)
        self._auto_read_enabled = True
        self._auto_reader_lock.release()

    def upload_transfer_files(self, transfer):
        job_thread = Thread(target=self._upload_transfer_files_job, args=[transfer])
        job_thread.setDaemon(True)
        job_thread.start()

    def send_file(self, data, transfer):
        assert isinstance(transfer, FileTransfer)
        # Encode data to prevent special REPL sequences
        encoded = bytearray()
        for x in data:
            if x < 10:
                encoded.append(0x00)
                encoded.append(x | 0xF0)
            else:
                encoded.append(x)
        # Split encoded data into smaller chunks
        idx = 0
        n = 64
        total_len = len(encoded)
        while idx < total_len:
            chunk = encoded[idx:idx+n]
            # Shorten chunk to prevent brake at special sequence
            if chunk[len(chunk)-1] == 0x0:
                chunk = chunk[0:-1]
            self._serial.write(b"".join([b"#", bytes([len(chunk)]), chunk]))
            ack = self.read_timeout(2)
            if not ack or ack != b"#1":
                transfer.mark_error()
                return False
            idx += len(chunk)
            transfer.progress = idx / total_len
        # Mark end
        self._serial.write(b"#\0")
        check = self.read_timeout(3)

        if check == b"#1#":
            transfer.mark_finished()
            return True
        else:
            transfer.mark_error()
            return False

    # TODO: Edit protocol to send total length so progress can be set correctly
    def recv_file(self, transfer):
        assert isinstance(transfer, FileTransfer)
        result = b""
        suc = False
        # Initiate transfer
        self._serial.write(b"###")
        while True:
            data = self.read_timeout(2)
            if not data or data[0] != ord("#"):
                self._serial.write(b"#2")
                break
            count = data[1]
            if count == 0:
                suc = True
                break
            data = self.read_timeout(count)
            if data:
                result += data
                # Send ACK
                self._serial.write(b"#1")
            else:
                self._serial.write(b"#3")
                break

        self._serial.write(b"#1#" if suc else b"#0#")
        if suc:
            transfer.mark_finished()
            transfer.read_result.binary_data = result
        else:
            transfer.mark_error()
            transfer.read_result.binary_data = None

    def _write_file_job(self, file_name, text, transfer, use_script):
        self._auto_reader_lock.acquire()
        self._auto_read_enabled = False
        if use_script:
            self.run_file("__upload.py", "file_name=\"{}\"".format(file_name))
        else:
            self.send_upload_file(file_name)
        self.read_junk()
        self.send_file(text, transfer)
        self._auto_read_enabled = True
        self._auto_reader_lock.release()

    def write_file(self, file_name, content, transfer):
        if isinstance(content, str):
            content = content.encode('utf-8')

        job_thread = Thread(target=self._write_file_job,
                            args=(file_name, content, transfer, Settings.use_transfer_scripts))
        job_thread.setDaemon(True)
        job_thread.start()

    def _read_file_job(self, file_name, transfer, use_script):
        self._auto_reader_lock.acquire()
        self._auto_read_enabled = False
        if use_script:
            self.run_file("__download.py", "file_name=\"{}\"".format(file_name))
        else:
            self.send_download_file(file_name)
        self.read_junk()
        self.recv_file(transfer)
        self._auto_read_enabled = True
        self._auto_reader_lock.release()

    def read_file(self, file_name, transfer):
        job_thread = Thread(target=self._read_file_job, args=(file_name, transfer, Settings.use_transfer_scripts))
        job_thread.setDaemon(True)
        job_thread.start()
