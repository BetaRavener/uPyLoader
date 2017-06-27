class ReadResult:
    def __init__(self):
        self.binary_data = b""


class FileTransfer:
    def __init__(self, signal):
        self._progress = 0
        self._file = 0
        self._file_count = 1
        self._cancel_sheduled = False
        self._cancelled = False
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

    def cancel(self):
        self._cancel_sheduled = True

    @property
    def cancel_sheduled(self):
        return self._cancel_sheduled

    @property
    def cancelled(self):
        return self._cancelled

    def confirm_cancel(self):
        self._cancelled = True
        self._signal()

    @property
    def error(self):
        return self._error

    def mark_error(self):
        self._error = True
        self._signal()

    def set_file_count(self, count):
        self._file_count = count
