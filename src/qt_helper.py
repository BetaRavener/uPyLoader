from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence


class QtHelper:
    @staticmethod
    def key_event_sequence(event):
        val = event.key()
        mod = event.modifiers()
        if mod & Qt.ShiftModifier:
            val += Qt.SHIFT
        if mod & Qt.ControlModifier:
            val += Qt.CTRL
        if mod & Qt.AltModifier:
            val += Qt.ALT
        if mod & Qt.MetaModifier:
            val += Qt.META
        return QKeySequence(val)