import env
import threading

class Dispatcher:

    def __init__(self, socketio):
        self.socketio = socketio
        self.listeners = dict()
        self.lock = threading.RLock()

    def subscribe(self, topic, sid):
        print("subscribing", sid, "to", topic)
        with self.lock:
            if topic not in self.listeners:
                self.listeners[topic] = set()
            listeners = self.listeners[topic]
            listeners.add(sid)

    def unsubscribe(self, topic, sid):
        print("unsubscribing", sid, "from", topic)
        with self.lock:
            if topic not in self.listeners:
                return
            listeners = self.listeners[topic]
            listeners.discard(sid)

    def unsubscribe_from_all(self, sid):
        print("unsubscribing", sid, "from all")
        with self.lock:
            for topic in self.listeners:
                self.listeners[topic].discard(sid)

    def has_listeners(self, topic):
        with self.lock:
            return topic in self.listeners and \
                   len(self.listeners[topic]) > 0

    def dispatch(self, topic, *args):
        with self.lock:
            if topic not in self.listeners:
                return
            print("dispatching to", topic)
            # for sid in self.listeners[topic]:
            #     self.socketio.emit(topic, *args, room=sid)
            self.socketio.emit(topic, *args)

    def dispatch_service(self, service, segments):
        print('dispatching service', service)
        self.socketio.emit('segments', segments)
