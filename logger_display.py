import serial
from lcdbackpack import LcdBackpack
from serial.tools import list_ports
import time
from datetime import datetime
import os
import requests

def find_port():
    for port in list_ports.comports():
        if(port.description == "Adafruit Industries"):
            return(port.device)
    return(None)

anes_token = None
vent_token = None
rc_url = None
which_or = None
def load_tokens():
    global  anes_token, vent_token, rc_url, which_or
    theFile = os.path.join(os.path.dirname(__file__), "display.auth")
    f = open(theFile)
    for line in f:
        split_it = line.strip("\n").split(":")
        if(line[0] == "rc_url"):
            rc_url = line[1] + ":" + line[2]
        elif(line[0] == "or"):
            which_or = line[1]
        elif(line[0] == "anes"):
            anes_token = line[1]
        elif(line[0] == "vent"):
            vent_token = line[1]
load_tokens()

def query_count(token):
    
 
while True:
    device_port = find_port()
    if(device_port != None):
        try:
            lcd = LcdBackpack(device_port, 9600)
            lcd.connect()
            lcd.clear()
            lcd.display_on()
            lcd.set_lcd_size(16,2)
            lcd.set_brightness(255)
            lcd.set_contrast(225)
            lcd.set_autoscroll(False)
            lcd.set_backlight_red()

            lcd.set_cursor_home()
            theMsg = (" " + datetime.now().strftime("%H:%M %m/%d/%y") + " ")
            theMsg += ("V:0000 - A:0000") 
            lcd.write(theMsg)
            lcd.disconnect()
        except Exception as err:
            print(err)

    time.sleep(5)
