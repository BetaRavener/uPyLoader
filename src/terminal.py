from src.signal_interface import Event


class Terminal:
    def __init__(self):
        self.add_event = Event(Terminal.add_event_handler)
        self.buffer = ""
        self.history = ""

    def add(self, string):
        self.buffer += string
        self.add_event.signal()

    def read(self):
        self.history += self.buffer
        ret = self.buffer
        self.buffer = ""
        return ret

    @staticmethod
    def add_event_handler(listener_handler):
        listener_handler()
