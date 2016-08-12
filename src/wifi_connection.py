import re
import socket
import struct
from threading import Thread

import math

from src import websocket_helper
from src.connection import Connection
from src.file_transfer import FileTransfer
from src.websocket import WebSocket


class WifiConnection(Connection):
    WEBREPL_REQ_S = "<2sBBQLH64s"
    WEBREPL_PUT_FILE = 1
    WEBREPL_GET_FILE = 2
    WEBREPL_GET_VER = 3

    def __init__(self, host, port, terminal, ask_for_password):
        Connection.__init__(self, terminal)

        self.s = socket.socket()
        self.s.settimeout(3)
        errno = self.s.connect_ex((host, port))
        if errno != 0:
            self._clear()
            return
        self.s.settimeout(None)

        websocket_helper.client_handshake(self.s)

        self.ws = WebSocket(self.s)
        self.login(ask_for_password())
        try:
            self.read_all()
        except:
            self._clear()
            return

        self._reader_thread = Thread(target=self._reader_thread_routine)
        self._reader_thread.start()

    def _clear(self):
        self.ws = None
        self.s.close()
        self.s = None

    def login(self, password):
        while True:
            c = self.ws.read(1)
            if c == b":":
                assert self.ws.read(1) == b" "
                break

        self.ws.write(password.encode("utf-8") + b"\r")

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

    def read_line(self):
        x = self.ws.read_all(0.2).decode("utf-8", errors="replace")

        if x and self._terminal is not None:
            self._terminal.add(x)

        return x

    def read_junk(self):
        self.ws.read_all(0)

    def send_character(self, char):
        self.ws.write(char)

    # TODO: Unite ending and text encoding across all communications
    def send_line(self, line_text, ending="\r\n"):
        if isinstance(ending, bytes):
            ending = ending.decode("utf-8", errors="replace")

        self.ws.write(line_text + ending)

    def list_files(self):
        self._auto_reader_lock.acquire()
        self._auto_read_enabled = False
        self.read_junk()
        self.ws.write("import os;os.listdir()\r\n")
        ret = self.read_all()
        self._auto_read_enabled = True
        self._auto_reader_lock.release()
        if not ret:
            return []  # TODO: Error
        return re.findall("'([^']+)'", ret)

    def read_resp(self, ws):
        data = ws.read(4)
        sig, code = struct.unpack("<2sH", data)
        assert sig == b"WB"
        return code

    # TODO: Edit protocol to send total length so progress can be set correctly
    def _read_file_job(self, file_name, transfer):
        assert isinstance(transfer, FileTransfer)

        ret = b""
        rec = struct.pack(WifiConnection.WEBREPL_REQ_S, b"WA", WifiConnection.WEBREPL_GET_FILE, 0, 0, 0, len(file_name),
                          file_name)

        self._auto_reader_lock.acquire()
        self._auto_read_enabled = False
        self.read_junk()

        self.ws.write(rec)
        assert self.read_resp(self.ws) == 0

        while True:
            # Confirm message
            self.ws.write(b"\1")
            (sz,) = struct.unpack("<H", self.ws.read(2))
            if sz == 0:
                break
            while sz:
                buf = self.ws.read(sz)
                if not buf:
                    raise OSError()
                ret += buf
                sz -= len(buf)

        if self.read_resp(self.ws) == 0:
            transfer.mark_finished()
            transfer.read_result.binary_data = ret
        else:
            transfer.mark_error()
            transfer.read_result.binary_data = None
        self._auto_read_enabled = True
        self._auto_reader_lock.release()

    def read_file(self, file_name, transfer):
        if isinstance(file_name, str):
            file_name = file_name.encode("utf-8")

        job_thread = Thread(target=self._read_file_job, args=(file_name, transfer))
        job_thread.setDaemon(True)
        job_thread.start()

    def _write_file_job(self, file_name, text, transfer):
        assert isinstance(transfer, FileTransfer)

        sz = len(text)
        rec = struct.pack(WifiConnection.WEBREPL_REQ_S, b"WA", WifiConnection.WEBREPL_PUT_FILE, 0, 0, sz,
                          len(file_name), file_name)

        self._auto_reader_lock.acquire()
        self._auto_read_enabled = False
        self.read_junk()

        self.ws.write(rec[:10])
        self.ws.write(rec[10:])
        if self.read_resp(self.ws) != 0:
            transfer.mark_error()
            self._auto_read_enabled = True
            self._auto_reader_lock.release()
            return

        cnt = 0
        while True:
            buf = text[cnt:cnt + 256]
            if not buf:
                break
            self.ws.write(buf)
            cnt += len(buf)
            transfer.progress = cnt / sz

        if self.read_resp(self.ws) == 0:
            transfer.mark_finished()
        else:
            transfer.mark_error()
        self._auto_read_enabled = True
        self._auto_reader_lock.release()

    def write_file(self, file_name, text, transfer):
        if isinstance(file_name, str):
            file_name = file_name.encode("utf-8")
        if isinstance(text, str):
            text = text.encode("utf-8")

        job_thread = Thread(target=self._write_file_job,
                            args=(file_name, text, transfer))
        job_thread.setDaemon(True)
        job_thread.start()