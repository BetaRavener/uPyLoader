from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QHideEvent, QFontDatabase, QTextCursor
from PyQt5.QtWidgets import QDialog, QScrollBar

from gui.terminal import Ui_TerminalDialog
from src.signal_interface import Listener

__author__ = "Ivan Sevcik"


class TerminalDialog(QDialog, Ui_TerminalDialog):
    _update_content_signal = pyqtSignal()

    def __init__(self, connection, terminal):
        super(TerminalDialog, self).__init__(None, Qt.WindowCloseButtonHint)
        self.setupUi(self)

        self.connection = connection
        self.terminal = terminal
        self.terminal_listener = Listener(self.emit_update_content)
        self._update_content_signal.connect(self.update_content)
        self.terminal.add_event.connect(self.terminal_listener)

        self.outputTextEdit.verticalScrollBar().sliderPressed.connect(lambda: self.autoscrollCheckBox.setChecked(False))
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
        self.autoscrollCheckBox.setChecked(True)

        self.terminal.read()
        self.outputTextEdit.setText(self.terminal.history)
        self._input_history_index = 0

    def closeEvent(self, event):
        if self.terminal_listener:
            self.terminal.add_event.disconnect(self.terminal_listener)
            self.terminal_listener = None
        self.reject()
        event.accept()

    def emit_update_content(self):
        """Update content indirection so that this can be called in multi-threaded environment"""
        self._update_content_signal.emit()

    def clear_content(self):
        self.outputTextEdit.clear()
        self.terminal.clear()

    def update_content(self):
        new_content = self.terminal.read()
        if not new_content:
            return

        scrollbar = self.outputTextEdit.verticalScrollBar()
        assert isinstance(scrollbar, QScrollBar)
        # Preserve scroll while updating content
        current_scroll = scrollbar.value()
        scrolling = scrollbar.isSliderDown()

        prev_cursor = self.outputTextEdit.textCursor()
        self.outputTextEdit.moveCursor(QTextCursor.End)
        #self.outputTextEdit.insertPlainText(bytes(new_content, "utf-8").decode("unicode_escape"))
        self.outputTextEdit.insertPlainText(new_content)
        self.outputTextEdit.setTextCursor(prev_cursor)

        if self.autoscrollCheckBox.isChecked() and not scrolling:
            scrollbar.setValue(scrollbar.maximum())
        else:
            scrollbar.setValue(current_scroll)



    def eventFilter(self, target, event):
        if target == self.inputTextBox:
            if isinstance(event, QKeyEvent):
                if event.type() == QKeyEvent.KeyPress:
                    if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                        if not (event.modifiers() & Qt.ShiftModifier):
                            self.send_input()
                            return True
                    if event.key() == Qt.Key_Tab:
                        self.inputTextBox.insertPlainText(" "*4)
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
