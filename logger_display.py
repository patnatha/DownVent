import serial
from lcdbackpack import LcdBackpack
from serial.tools import list_ports
import time
from datetime import datetime
import os
import requests
import json

last_check_datetime = None
last_anes_cnt = None
last_vent_cnt = None

def find_port():
    try:
        for port in list_ports.comports():
            if(port.description == "Adafruit Industries"):
                return(port.device)
    except Exception as err:
        print("find_port ERROR:", err)

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
        line = line.strip("\n").split(":")
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
    try:
        data = {
        'token': token,
        'content': 'record',
        'action': 'export',
        'format': 'json',
        'type': 'flat',
        'csvDelimiter': '',
        'fields[0]': 'record_id',
        'rawOrLabel': 'raw',
        'rawOrLabelHeaders': 'raw',
        'exportCheckboxLabel': 'false',
        'exportSurveyFields': 'false',
        'exportDataAccessGroups': 'false',
        'returnFormat': 'json',
        'filterLogic': '[or] = "' + which_or + '"',
        'dateRangeBegin': datetime.now().strftime("%Y-%m-%d") + " 00:00:00",
        'dateRangeEnd': datetime.now().strftime("%Y-%m-%d") + " 23:59:59"
        }
        r = requests.post(rc_url,data=data)
        if(r.status_code == 200):
            return(len(r.json()))
        else:
            return(-1)
    except Exception as err:
        print("query_count ERROR:", err)
        return(-2)

last_anes_cnt = query_count(anes_token)
last_vent_cnt = query_count(vent_token)
last_check_datetime = datetime.now()

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
            lcd.set_contrast(200)
            lcd.set_autoscroll(False)
            lcd.set_backlight_red()

            while True:
                cur_time = datetime.now()
                if((cur_time - last_check_datetime).seconds > 60):
                    last_vent_cnt = query_count(vent_token)
                    last_anes_cnt = query_count(anes_token)
                    if(last_vent_cnt == 0 or last_anes_cnt == 0):
                        lcd.set_backlight_red()
                    else:
                        lcd.set_backlight_green()
                    last_check_datetime = cur_time

                lcd.set_cursor_home()
                theMsg = (" " + cur_time.strftime("%H:%M %m/%d/%y") + " ")
                theMsg += "V:"
                theMsg += str(last_vent_cnt).zfill(4)
                theMsg += " - " 
                theMsg += "A:" 
                theMsg += str(last_anes_cnt).zfill(4)
                lcd.write(theMsg)
                time.sleep(5)

            lcd.disconnect()
        except Exception as err:
            print(err)

    time.sleep(60)
