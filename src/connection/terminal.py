from src.utility.signal_interface import Event


class Terminal:
    def __init__(self):
        self.add_event = Event()
        self.buffer = ""
        self.history = ""
        self.input_history = []

    def add(self, string):
        self.buffer += string
        self.add_event.signal()

    def read(self):
        self.history += self.buffer
        ret, self.buffer = self.buffer, ""
        return ret

    def clear(self):
        self.history = self.buffer = ""

    def add_input(self, input_string):
        self.input_history.append(input_string)

    def last_input_idx(self):
        return len(self.input_history) - 1

    def input(self, idx):
        return self.input_history[idx]
