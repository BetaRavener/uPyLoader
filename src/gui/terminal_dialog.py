from PyQt5.QtCore import QEvent
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QHideEvent, QFontDatabase, QTextCursor
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QDialog, QScrollBar

from gui.terminal import Ui_TerminalDialog
from src.helpers.qt_helper import QtHelper
from src.utility.settings import Settings
from src.utility.signal_interface import Listener

__author__ = "Ivan Sevcik"


class TerminalDialog(QDialog, Ui_TerminalDialog):
    _update_content_signal = pyqtSignal()

    def __init__(self, parent, connection, terminal):
        super(TerminalDialog, self).__init__(None, Qt.WindowCloseButtonHint)
        self.setupUi(self)

        self.setWindowFlags(Qt.Window)
        geometry = Settings().retrieve_geometry("terminal")
        if geometry:
            self.restoreGeometry(geometry)

        self.connection = connection
        self.terminal = terminal
        self._auto_scroll = True  # TODO: Settings?
        self.terminal_listener = Listener(self.emit_update_content)
        self._update_content_signal.connect(self.update_content)
        self.terminal.add_event.connect(self.terminal_listener)

        self.outputTextEdit.installEventFilter(self)
        self.outputTextEdit.verticalScrollBar().sliderPressed.connect(self._stop_scrolling)
        self.outputTextEdit.verticalScrollBar().sliderReleased.connect(self._scroll_released)
        self.outputTextEdit.verticalScrollBar().installEventFilter(self)
        self.inputTextBox.installEventFilter(self)
        self.clearButton.clicked.connect(self.clear_content)
        self.sendButton.clicked.connect(self.send_input)

        self.ctrlaButton.clicked.connect(lambda: self.send_control("a"))
        self.ctrlbButton.clicked.connect(lambda: self.send_control("b"))
        self.ctrlcButton.clicked.connect(lambda: self.send_control("c"))
        self.ctrldButton.clicked.connect(lambda: self.send_control("d"))
        self.ctrleButton.clicked.connect(lambda: self.send_control("e"))

        fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.outputTextEdit.setFont(fixed_font)
        self.inputTextBox.setFont(fixed_font)
        self.autoscrollCheckBox.setChecked(self._auto_scroll)
        self.autoscrollCheckBox.stateChanged.connect(self._auto_scroll_changed)

        self.terminal.read()
        self.outputTextEdit.setText(TerminalDialog.process_backspaces(self.terminal.history))
        self._input_history_index = 0

    def _stop_scrolling(self):
        self._auto_scroll = False

    def _scroll_released(self):
        if not self.autoscrollCheckBox.isChecked():
            self._auto_scroll = False
            return

        scrollbar = self.outputTextEdit.verticalScrollBar()
        assert isinstance(scrollbar, QScrollBar)
        current_scroll = scrollbar.value()
        self._auto_scroll = current_scroll >= scrollbar.maximum()

    def _auto_scroll_changed(self, state):
        self._auto_scroll = self.autoscrollCheckBox.isChecked()

    @staticmethod
    def process_backspaces(text):
        processed = ""
        for x in text:
            # Delete character there are any characters that are not backspaces
            if x == "\b" and processed and processed[-1:] != "\b":
                processed = processed[:-1]
            else:
                processed += x
        return processed

    def closeEvent(self, event):
        Settings().update_geometry("terminal", self.saveGeometry())
        if self.terminal_listener:
            self.terminal.add_event.disconnect(self.terminal_listener)
            self.terminal_listener = None
        super(TerminalDialog, self).closeEvent(event)

    def emit_update_content(self):
        """Update content indirection so that this can be called in multi-threaded environment"""
        self._update_content_signal.emit()

    def clear_content(self):
        self.outputTextEdit.clear()
        self.terminal.clear()

    def update_content(self):
        new_content = self.terminal.read()
        new_content = self.process_backspaces(new_content)
        if not new_content:
            return

        scrollbar = self.outputTextEdit.verticalScrollBar()
        assert isinstance(scrollbar, QScrollBar)
        # Preserve scroll while updating content
        current_scroll = scrollbar.value()

        prev_cursor = self.outputTextEdit.textCursor()
        self.outputTextEdit.moveCursor(QTextCursor.End)
        # Use any backspaces that were left in input to delete text
        cut = 0
        for x in new_content:
            if x != "\b":
                break
            self.outputTextEdit.textCursor().deletePreviousChar()
            cut += 1
        self.outputTextEdit.insertPlainText(new_content[cut:])
        self.outputTextEdit.setTextCursor(prev_cursor)

        if self._auto_scroll:
            scrollbar.setValue(scrollbar.maximum())
        else:
            scrollbar.setValue(current_scroll)

    def eventFilter(self, target, event):
        def match(s1, s2):
            for x in s2:
                if s1.matches(x) == QKeySequence.ExactMatch:
                    return True
            return False

        if target == self.inputTextBox:
            if isinstance(event, QKeyEvent):
                if event.type() == QKeyEvent.KeyPress:
                    event_sequence = QtHelper.key_event_sequence(event)
                    if match(event_sequence, Settings().new_line_key):
                        return False
                    if match(event_sequence, Settings().send_key):
                        self.send_input()
                        return True
                    if event.key() == Qt.Key_Tab:
                        self.inputTextBox.insertPlainText(" "*Settings().terminal_tab_spaces)
                        return True
                    if event.key() == Qt.Key_Up and (event.modifiers() & Qt.ControlModifier):
                        if self._input_history_index > 0:
                            self._input_history_index -= 1
                            self.inputTextBox.clear()
                            self.inputTextBox.setPlainText(self.terminal.input(self._input_history_index))
                    if event.key() == Qt.Key_Down and (event.modifiers() & Qt.ControlModifier):
                        if self._input_history_index < self.terminal.last_input_idx():
                            self._input_history_index += 1
                            self.inputTextBox.clear()
                            self.inputTextBox.setPlainText(self.terminal.input(self._input_history_index))
        elif target == self.outputTextEdit:
            if isinstance(event, QKeyEvent):
                if event.type() == QEvent.KeyPress:
                    if event.key() == Qt.Key_Up:
                        self.connection.send_bytes(b"\x1b[A")
                    if event.key() == Qt.Key_Down:
                        self.connection.send_bytes(b"\x1b[B")
                    else:
                        t = event.text()
                        if t:
                            self.connection.send_character(t)
                    return True
        elif target == self.outputTextEdit.verticalScrollBar():
            if isinstance(event, QHideEvent):
                return True
        return False

    def send_control(self, which):
        code = chr(ord(which) - ord("a") + 1)
        self.connection.send_character(code)

    def send_input(self):
        text = self.inputTextBox.toPlainText()
        if not text:
            return

        self.terminal.add_input(text)
        self._input_history_index = self.terminal.last_input_idx()
        self.connection.send_block(text)
        self.inputTextBox.selectAll()
