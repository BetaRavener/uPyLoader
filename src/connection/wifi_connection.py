import re
import socket
import struct
from threading import Thread
import traceback

import time

from src.connection.connection import Connection
from src.connection.websocket import WebSocket
from src.helpers import websocket_helper
from src.logic.file_transfer import FileTransfer
from src.utility.exceptions import PasswordException, NewPasswordException, OperationError, HostnameResolutionError


class WifiConnection(Connection):
    WEBREPL_REQ_S = "<2sBBQLH64s"
    WEBREPL_PUT_FILE = 1
    WEBREPL_GET_FILE = 2
    WEBREPL_GET_VER = 3

    def __init__(self, host, port, terminal, password_prompt):
        Connection.__init__(self, terminal)
        self._host = host
        self._port = port
        self.s = None
        self.ws = None

        try:
            self._start_connection()
        except Exception as e:
            self._clear()
            raise e

        if not self.handle_password(password_prompt):
            self._clear()
            raise PasswordException()

        self._reader_thread = Thread(target=self._reader_thread_routine)
        self._reader_thread.start()

    def _start_connection(self):
        self.s = socket.socket()
        self.s.settimeout(3)
        try:
            errno = self.s.connect_ex((self._host, self._port))
        except socket.gaierror:  # Failed to resolve hostname
            raise HostnameResolutionError()
        if errno != 0:
            raise ConnectionError("Failed to connect to the device.")
        self.s.settimeout(None)

        # Test if connection is working
        try:
            websocket_helper.client_handshake(self.s)
        except (ConnectionResetError, ConnectionAbortedError):
            raise ConnectionError("Device refused connection.")

        self.s.setblocking(0)
        self.ws = WebSocket(self.s)
        return True

    def _clear(self):
        self.ws = None
        if self.s:
            self.s.close()
        self.s = None

    def set_password(self):
        password = "passw".encode("utf-8") + b"\r"
        self.ws.write(password)
        response = self.ws.read_all().decode("utf-8")
        if response.find("Confirm password:") < 0:
            return False
        self.ws.write(password)
        try:
            response = self.ws.read_all().decode("utf-8")
            return response.find("Password successfully set") >= 0
        except ConnectionAbortedError:
            # If connection was aborted, password was set
            return True

    def login(self, password):
        self.ws.write(password.encode("utf-8") + b"\r")
        try:
            response = self.ws.read_all().decode("utf-8")
            return response.find("WebREPL connected") >= 0
        except ConnectionAbortedError:
            return False

    def handle_password(self, password_prompt):
        content = self.ws.read_all().decode("utf-8")

        if content.find("New password:") >= 0:
            self.set_password()
            raise NewPasswordException()
        elif content.find("Password:") >= 0:
            return self.login(password_prompt("Enter WebREPL password"))
        else:
            return False

    def is_connected(self):
        return self.ws is not None

    def disconnect(self):
        if self.is_connected():
            if self._reader_thread.is_alive():
                self._reader_running = False
                self._reader_thread.join()
            self.s.close()
            self.s = None

    def read_all(self):
        x = self.ws.read_all().decode("utf-8", errors="replace")

        if x and self._terminal is not None:
            self._terminal.add(x)

        return x

    # TODO: Join with serial implementation? At least the special character handling
    def read_line(self):
        x = self.ws.read_all(0.2)

        if x and self._terminal is not None:
            if x == b'\x08\x1b[K':
                x = b'\x08'
            if x[:3] == b'\x1b[':  # Control sequence
                # TODO: regex firt match 14D on x[3:]
                pass

            self._terminal.add(x.decode("utf-8", errors="replace"))

        return x

    def read_junk(self):
        self.ws.read_all(0)

    def read_one_byte(self):
        return self.ws.read(1)

    def send_character(self, char):
        assert isinstance(char, str)
        self.ws.write(char)

    def send_bytes(self, binary):
        self.ws.write(binary)

    def send_line(self, line_text, ending="\r\n"):
        assert isinstance(line_text, str)
        assert isinstance(ending, str)
        self.ws.write(line_text + ending)

    @staticmethod
    def read_resp(ws):
        data = ws.read(4)
        sig, code = struct.unpack("<2sH", data)
        assert sig == b"WB"
        return code

    def _read_file_job(self, file_name, transfer):
        assert isinstance(transfer, FileTransfer)

        try:
            file_size = self.get_file_size(file_name)
        except OperationError:
            transfer.mark_error("Failed to determine file size.")
            return

        if isinstance(file_name, str):
            file_name = file_name.encode("utf-8")

        ret = b""
        rec = struct.pack(WifiConnection.WEBREPL_REQ_S, b"WA", WifiConnection.WEBREPL_GET_FILE,
                          0, 0, 0, len(file_name), file_name)

        self._auto_reader_lock.acquire()
        self._auto_read_enabled = False
        self.read_junk()

        self.ws.write(rec, True)
        assert self.read_resp(self.ws) == 0

        while True:
            # Confirm message
            self.ws.write(b"\1", True)
            (sz,) = struct.unpack("<H", self.ws.read(2))
            if sz == 0:
                break
            while sz:
                buf = self.ws.read(sz)
                if not buf:
                    raise OSError()
                ret += buf
                sz -= len(buf)
            transfer.progress = len(ret) / file_size

        if self.read_resp(self.ws) == 0:
            transfer.mark_finished()
            transfer.read_result.binary_data = ret
        else:
            transfer.mark_error()
            transfer.read_result.binary_data = None
        self._auto_read_enabled = True
        self._auto_reader_lock.release()

    def _write_file_job(self, file_name, text, transfer):
        def mark_error_and_release():
            transfer.mark_error()
            self._auto_read_enabled = True
            self._auto_reader_lock.release()

        assert isinstance(transfer, FileTransfer)
        if isinstance(file_name, str):
            file_name = file_name.encode("utf-8")
        if isinstance(text, str):
            text = text.encode("utf-8")

        sz = len(text)
        rec = struct.pack(WifiConnection.WEBREPL_REQ_S, b"WA", WifiConnection.WEBREPL_PUT_FILE, 0, 0, sz,
                          len(file_name), file_name)

        self._auto_reader_lock.acquire()
        self._auto_read_enabled = False
        self.read_junk()

        self.ws.write(rec[:10], file_transfer=True)
        self.ws.write(rec[10:], file_transfer=True)
        try:
            if self.read_resp(self.ws) != 0:
                mark_error_and_release()
                return
        except TimeoutError:
            mark_error_and_release()
            return

        cnt = 0
        # Increase timeout from default value which gives
        # more time to MCU to process large files.
        original_timeout = self.ws.recv_timeout
        self.ws.recv_timeout = 30
        try:
            while True:
                buf = text[cnt:cnt + 256]
                if not buf:
                    break
                self.ws.write(buf, file_transfer=True)
                cnt += len(buf)
                transfer.progress = cnt / sz

            if self.read_resp(self.ws) == 0:
                transfer.mark_finished()
            else:
                transfer.mark_error()
        except ConnectionResetError:
            transfer.mark_error("Connection was reset.")
        except ConnectionError:
            transfer.mark_error()
        except Exception as generalException:
            info = "Unexpected error, report this on project's github issues page\n{}: {}\n{}".format(
                type(generalException).__name__,
                str(generalException),
                "".join(traceback.format_tb(generalException.__traceback__))
            )
            transfer.mark_error(info)
        finally:
            self.ws.recv_timeout = original_timeout

        self._auto_read_enabled = True
        self._auto_reader_lock.release()
