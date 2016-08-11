import re
import socket
import struct
from threading import Thread

from src import websocket_helper
from src.connection import Connection
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

    #########################################################
    # def put_file(ws, local_file, remote_file):
    #     sz = os.stat(local_file)[6]
    #     dest_fname = (SANDBOX + remote_file).encode("utf-8")
    #     rec = struct.pack(WEBREPL_REQ_S, b"WA", WEBREPL_PUT_FILE, 0, 0, sz, len(dest_fname), dest_fname)
    #     debugmsg("%r %d" % (rec, len(rec)))
    #     ws.write(rec[:10])
    #     ws.write(rec[10:])
    #     assert read_resp(ws) == 0
    #     cnt = 0
    #     with open(local_file, "rb") as f:
    #         while True:
    #             sys.stdout.write("Sent %d of %d bytes\r" % (cnt, sz))
    #             sys.stdout.flush()
    #             buf = f.read(1024)
    #             if not buf:
    #                 break
    #             ws.write(buf)
    #             cnt += len(buf)
    #     print()
    #     assert read_resp(ws) == 0
    #########################################################
    # def get_file(ws, local_file, remote_file):
    #     src_fname = (SANDBOX + remote_file).encode("utf-8")
    #     rec = struct.pack(WEBREPL_REQ_S, b"WA", WEBREPL_GET_FILE, 0, 0, 0, len(src_fname), src_fname)
    #     debugmsg("%r %d" % (rec, len(rec)))
    #     ws.write(rec)
    #     assert read_resp(ws) == 0
    #     with open(local_file, "wb") as f:
    #         cnt = 0
    #         while True:
    #             ws.write(b"\0")
    #             (sz,) = struct.unpack("<H", ws.read(2))
    #             if sz == 0:
    #                 break
    #             while sz:
    #                 buf = ws.read(sz)
    #                 if not buf:
    #                     raise OSError()
    #                 cnt += len(buf)
    #                 f.write(buf)
    #                 sz -= len(buf)
    #                 sys.stdout.write("Received %d bytes\r" % cnt)
    #                 sys.stdout.flush()
    #     print()
    #     assert read_resp(ws) == 0
    #########################################################

    def read_file(self, file_name):
        ret = ""

        file_name = file_name.encode("utf-8")
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
                ret += buf.decode("utf-8")
                sz -= len(buf)
        assert self.read_resp(self.ws) == 0
        self._auto_read_enabled = True
        self._auto_reader_lock.release()
        return ret

    def write_file(self, file_name, text):
        if type(text) is str:
            text = text.encode("utf-8")

        sz = len(text)
        file_name = file_name.encode("utf-8")
        rec = struct.pack(WifiConnection.WEBREPL_REQ_S, b"WA", WifiConnection.WEBREPL_PUT_FILE, 0, 0, sz,
                          len(file_name), file_name)

        self._auto_reader_lock.acquire()
        self._auto_read_enabled = False
        self.read_junk()
        self.ws.write(rec[:10])
        self.ws.write(rec[10:])
        assert self.read_resp(self.ws) == 0
        cnt = 0

        while True:
            buf = text[cnt:cnt + 1024]
            if not buf:
                break
            self.ws.write(buf)
            cnt += len(buf)

        print()
        assert self.read_resp(self.ws) == 0
        self._auto_read_enabled = True
        self._auto_reader_lock.release()
