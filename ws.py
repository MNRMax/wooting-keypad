from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import serial
import time
import threading
import asyncio

ser = serial.Serial('COM4', 9600)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5173"])

output = 0
def task():
    ser.read_all()
    data = (ser.read_until(b';'))
    global output
    output = str(data, 'UTF-8')
    socketio.emit("keys", {"q": output[:-1]})
    print(output)
    threading.Timer(0.016,task).start()
task()
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('message', {'message': 'Connected to the server', 'data': output})
        
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    print('Received message:', data)

@socketio.on('on')
def handle_message(data):
    print(data.get("color"))
    ser.write(str.encode(data.get("color")))
    
@socketio.on('off')
def handle_message():
    ser.write(str.encode("o"))
    
if __name__ == '__main__':
    app.run()