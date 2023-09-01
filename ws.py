from flask import Flask, render_template, send_file
from flask_socketio import SocketIO, emit
import serial
import serial.tools.list_ports
import time
import threading
import asyncio
import json

color = "#00ffff"
activationWooting = 0.4
reactivationWooting = 0.2
activationNormal = 2.3
mode = "n"

with open('settings.json', 'r') as f:
    data = json.load(f)
    for item in data:
        if item == "activationNormal":
            activationNormal = data.get(item)
        elif item == "activationWooting":
            activationWooting = data.get(item)
        elif item == "reactivationWooting":
            reactivationWooting = data.get(item)
        elif item == "mode":
            mode = data.get(item)
        elif item == "color":
            color = data.get(item)

def sendToBoard():
    ser.write(str.encode(mode))
    ser.write(str.encode(color))
    ser.write(str.encode(f'an{activationNormal*25:04}'))
    ser.write(str.encode(f'aw{activationWooting*25:04}'))
    ser.write(str.encode(f'rw{reactivationWooting*25:04}'))

def getSerialPort():
    for port in serial.tools.list_ports.comports():
        if (" ".join(port.description.split(" ")[:-1]) == "Arduino Leonardo"):
            global COMPort
            COMPort = port.name
            print(port.name)
            return True
    return False

def saveToJSON():
    settingsDict = {
        "activationNormal": activationNormal,
        "activationWooting": activationWooting,
        "reactivationWooting": reactivationWooting,
        "mode": mode,
        "color": color
    }
    with open("settings.json", "w") as outfile:
        outfile.write(json.dumps(settingsDict))

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
            sendToBoard()
            deviceConnected = True
        else:
            if (deviceConnected):
                deviceConnected = False
                socketio.emit("disconnected")
                print("Device disconnected")
    threading.Timer(0.016, readSerial).start()


COMPort = ''
ser = None
deviceConnected = False

try:
    ser = serial.Serial(COMPort, 9600)
except:
    print("Device not connected")

app = Flask(__name__, static_url_path='/')
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5173", "http://127.0.0.1:5000", "https://mnrmaxwooting.netlify.app"])

output = 0
readSerial()

@app.route('/')
def home():
    return send_file('./static/index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('data', {'data': {
        "color": color,
        "activationWooting": activationWooting,
        "reactivationWooting": reactivationWooting,
        "activationNormal": activationNormal,
        "mode": mode
    }})
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
    global color
    color = data.get("color")
    ser.write(str.encode(data.get("color")))
    saveToJSON()


@socketio.on('serial')
def handle_message(data):
    ser.write(str.encode(data.get("message")))


@socketio.on('settings')
def handle_message(data):
    global activationWooting
    global reactivationWooting
    global activationNormal
    global mode
    settings = data.get("data")
    for item in settings:
        if item == "activationNormal":
            activationNormal = settings.get(item)
        elif item == "activationWooting":
            activationWooting = settings.get(item)
        elif item == "reactivationWooting":
            reactivationWooting = settings.get(item)
        elif item == "mode":
            mode = settings.get(item)

    saveToJSON()
    sendToBoard()

if __name__ == '__main__':
    app.run()
