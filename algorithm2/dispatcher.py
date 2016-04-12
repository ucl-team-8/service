
class Dispatcher:

    def __init__(self, socketio):
        self.socketio = socketio
        self.listeners = dict()

    def subscribe(self, topic, socket):
        print("subscribing", socket, "to", topic)
        if topic not in self.listeners:
            self.listeners[topic] = set()
        listeners = self.listeners[topic]
        listeners.add(socket)

    def unsubscribe(self, topic, socket):
        print("unsubscribing", socket, "from", topic)
        if topic not in self.listeners:
            return
        listeners = self.listeners[topic]
        listeners.discard(socket)

    def unsubscribe_from_all(self, socket):
        print("unsubscribing", socket, "from all")
        for topic in self.listeners:
            self.listeners[topic].remove(socket)

    def has_listeners(self, topic):
        return topic in self.listeners and \
               len(self.listeners[topic]) > 0

    def dispatch(self, topic, *args):
        print("dispatching to", topic)
        if topic not in self.listeners:
            return
        for sid in self.listeners[topic]:
            self.socketio.emit(topic, *args, room=sid)
