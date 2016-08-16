import time
from threading import Lock


class Connection:
    def __init__(self, terminal=None):
        self._terminal = terminal
        self._reader_running = False
        self._auto_read_enabled = True
        self._auto_reader_lock = Lock()

    def is_connected(self):
        raise NotImplementedError()

    def disconnect(self):
        raise NotImplementedError()

    def read_line(self):
        raise NotImplementedError()

    def read_all(self):
        raise NotImplementedError()

    def read_junk(self):
        self.read_all()

    def send_line(self, line_text, ending):
        raise NotImplementedError()

    def send_character(self, char):
        raise NotImplementedError()

    def send_block(self, text):
        lines = text.split("\n")
        if len(lines) == 1:
            self.send_line(lines[0], "\r")
        elif len(lines) > 1:
            self.send_start_paste()
            for line in lines:
                self.send_line(line, "\r")
            self.send_end_paste()

    def run_file(self, file_name, globals_init=""):
        self.send_start_paste()
        if globals_init:
            self.send_line(globals_init, "\r")
        self.send_line("with open(\"{}\") as f:".format(file_name), "\r")
        self.send_line("    exec(f.read(), globals())", "\r")
        self.send_end_paste()

    def remove_file(self, file_name):
        self.send_line("import os; os.remove(\"{}\")".format(file_name))

    def send_start_paste(self):
        self.send_character("\5")

    def send_end_paste(self):
        self.send_character("\4")

    def send_kill(self):
        self.send_character("\3")

    def _reader_thread_routine(self):
        self._reader_running = True
        while self._reader_running:
            self._auto_reader_lock.acquire()
            x = ""
            if self._auto_read_enabled:
                x = self.read_line()
            self._auto_reader_lock.release()
            time.sleep(0.1 if x == "" else 0)

    def list_files(self):
        raise NotImplementedError()

    def write_file(self, file_name, text, progress):
        raise NotImplementedError()

    def read_file(self, file_name, progress):
        raise NotImplementedError()
