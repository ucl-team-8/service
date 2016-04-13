import env

class Dispatcher:

    def __init__(self, socketio):
        self.socketio = socketio
        self.listeners = dict()

    def subscribe(self, topic, sid):
        print("subscribing", sid, "to", topic)
        if topic not in self.listeners:
            self.listeners[topic] = set()
        listeners = self.listeners[topic]
        listeners.add(sid)

    def unsubscribe(self, topic, sid):
        print("unsubscribing", sid, "from", topic)
        if topic not in self.listeners:
            return
        listeners = self.listeners[topic]
        listeners.discard(sid)

    def unsubscribe_from_all(self, sid):
        print("unsubscribing", sid, "from all")
        for topic in self.listeners:
            self.listeners[topic].remove(sid)

    def has_listeners(self, topic):
        return topic in self.listeners and \
               len(self.listeners[topic]) > 0

    def dispatch(self, topic, *args):
        if topic not in self.listeners:
            return
        print("dispatching to", topic)
        for sid in self.listeners[topic]:
            self.socketio.emit(topic, *args, room=sid)
        # self.socketio.emit(topic, *args)

    def dispatch_service(self, service, segments):
        print('dispatching service', service)
        self.socketio.emit('segments', segments)
