from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import serial
import time

ser = serial.Serial('COM14', 9600)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5173"])

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('message', {'message': 'Connected to the server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    print('Received message:', data)

@socketio.on('on')
def handle_message():
    ser.write(str.encode("l"))
    
@socketio.on('off')
def handle_message():
    ser.write(str.encode("o"))
    
if __name__ == '__main__':
    app.run()