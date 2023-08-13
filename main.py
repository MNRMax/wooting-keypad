import serial
import time

ser = serial.Serial('COM14', 9600)

time.sleep(1)


# while True:
#     data = (ser.read(10))
#     temperature = str(data, 'UTF-8')
#     print(temperature)
    
import tkinter as tk

def send_button_click():
    ser.write(str.encode("test"))
    
app = tk.Tk()
app.title("Keypad Controller")

send_button = tk.Button(app, text="Send", command=send_button_click)
send_button.pack(padx=20, pady=10)

app.mainloop()