class Event:
    def __init__(self):
        self.listeners = []

    def connect(self, listener):
        self.listeners.append(listener)

    def disconnect(self, listener):
        self.listeners.remove(listener)

    def signal(self):
        for listener in self.listeners:
            listener.handler()


class Listener:
    def __init__(self, handler):
        self.handler = handler
