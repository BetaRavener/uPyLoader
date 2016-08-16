class ReadResult:
    def __init__(self):
        self.binary_data = b""


class FileTransfer:
    # TODO: Implement cancelled in wifi and serial connection
    def __init__(self, signal):
        self._progress = 0
        self._file = 0
        self._files = 1
        self.cancelled = False
        self._finished = False
        self._error = False
        self._signal = signal
        self.read_result = ReadResult()

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self._signal()

    @property
    def finished(self):
        return self._finished

    def mark_finished(self):
        self._file += 1
        if self._file == self._file_count:
            self._finished = True
        else:
            self._progress = 0
        self._signal()

    @property
    def error(self):
        return self._error

    def mark_error(self):
        self._error = True
        self._signal()

    def set_file_count(self, count):
        self._file_count = count