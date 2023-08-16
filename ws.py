from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import serial
import serial.tools.list_ports
import time
import threading
import asyncio

def getSerialPort():
    for port in serial.tools.list_ports.comports():
        if (" ".join(port.description.split(" ")[:-1]) == "Arduino Leonardo"):
            global COMPort
            COMPort = port.name
            print(port.name)
            return True
    return False

def readSerial():
    global ser
    global deviceConnected
    try:
        ser.read_all()
        data = (ser.read_until(b';'))
        global output
        output = str(data, 'UTF-8')
        keys = output[:-1].split(',')
        # print("a")
        socketio.emit("keys", {"q": keys[1], "w": keys[0]})
    except Exception as e:
        if (getSerialPort()):
            time.sleep(0.5)
            ser = serial.Serial(COMPort, 9600)
            print("Device connected")
            socketio.emit("connected")
            deviceConnected = True
        else:
            if (deviceConnected):
                deviceConnected = False
                socketio.emit("disconnected")
                print("Device disconnected")
    threading.Timer(0.016,readSerial).start()

COMPort = ''
ser = None
deviceConnected = False

try:
    ser = serial.Serial(COMPort, 9600)
except:
    print("Device not connected")

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5173"])

output = 0
readSerial()

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('message', {'message': 'Connected to the server', 'data': output})
    if (deviceConnected):
        emit("connected")
        
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
    
@socketio.on('ct')
def handle_message():
    ser.write(str.encode("ct"))
    
@socketio.on('cb')
def handle_message():
    ser.write(str.encode("cb"))
    
@socketio.on('d')
def handle_message():
    ser.write(str.encode("d"))
    
if __name__ == '__main__':
    app.run()