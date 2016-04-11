
class Dispatcher:

    def __init__(self):
        self.listeners = dict()

    def subscribe(self, topic, socket):
        if topic not in self.listeners:
            self.listeners[topic] = set()
        listeners = self.listeners[topic]
        listeners.add(socket)

    def unsubscribe(self, topic, socket):
        if topic not in self.listeners:
            return
        listeners = self.listeners[topic]
        listeners.discard(socket)

    def has_listeners(self, topic):
        return topic in self.listeners and \
               len(self.listeners[topic]) > 0

    def dispatch(self, topic, *args):
        if topic not in self.listeners:
            return
        for socket in self.listeners[topic]:
            socket.emit(topic, *args)
