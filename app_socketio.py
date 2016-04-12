from app_db import socketio, dispatcher
from flask import request
from flask_socketio import send, emit

@socketio.on('connect')
def onconnect():
    print("Client connected")

@socketio.on('subscribe')
def subscribe(topic):
    dispatcher.subscribe(topic, request.sid)

@socketio.on('unsubscribe')
def unsubscribe(topic):
    dispatcher.unsubscribe(topic, request.sid)

@socketio.on('disconnect')
def ondisconnect():
    print("Client disconnected")
    dispatcher.unsubscribe_from_all(request.sid)
