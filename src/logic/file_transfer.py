class ReadResult:
    def __init__(self):
        self.binary_data = b""


class FileTransferError(Exception):
    def __init__(self, details=""):
        self.details = details


class FileTransfer:
    def __init__(self, signal):
        self._progress = 0
        self._file = 0
        self._file_count = 1
        self._cancel_scheduled = False
        self._cancelled = False
        self._finished = False
        self._error_msg = ""
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
        self._check_state_for_completion()
        self._file += 1
        if self._file == self._file_count:
            self._finished = True
        else:
            self._progress = 0
        self._signal()

    def cancel(self):
        self._cancel_scheduled = True

    @property
    def cancel_scheduled(self):
        return self._cancel_scheduled

    @property
    def cancelled(self):
        return self._cancelled

    def confirm_cancel(self):
        self._check_state_for_completion()
        self._cancelled = True
        self._signal()

    @property
    def error_msg(self):
        return self._error_msg

    @property
    def error(self):
        return self._error

    def mark_error(self, msg=""):
        self._check_state_for_completion()
        self._error_msg = msg
        self._error = True
        self._signal()

    def set_file_count(self, count):
        self._file_count = count

    def _check_state_for_completion(self):
        reason = None
        if self._finished:
            reason = "was completed successfully"
        elif self._cancelled:
            reason = "was cancelled"
        elif self._error:
            reason = "failed because error occurred"

        if reason:
            raise RuntimeError("Can't set new state. File transfer {}.".format(reason))
