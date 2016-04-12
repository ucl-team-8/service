from datetime import datetime

class SocketManager:

    def __init__(self, socketio):
        socketio.on('connection', self.connect)

    def connect(self, socket):
        print("New socket")
        self.__attach_socket(socket)
        socket.on('disconnect', self.disconnect_callback(socket))

    def disconnect_callback(self, socket):
        def callback():
            self.disconnect(socket)
        return callback

    def disconnect(self, socket):
        self.__detach_socket(socket)

    def remove_socket(self, socket):
        print("Remove socket")
        pass

    def serialize_topic(self, topic):
        pass

    def deserialize_topic(self, topic):
        pass

    def __attach_socket(self, socket):
        pass

    def __detach_socket(self, socket):
        pass
