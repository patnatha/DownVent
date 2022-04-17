import serial
import serial.tools.list_ports as stlp
import time
import datetime
import redcap as rc

ser = None
def open_serial():
    global ser
    ser = serial.Serial(port=the_port, baudrate=19200, bytesize=serial.SEVENBITS,
                        parity=serial.PARITY_ODD, stopbits=serial.STOPBITS_ONE)

def close_serial():
    global ser
    if(ser != None):
        ser.close()
        ser = None

def search_coms():
    try:
        the_port = None
        for port in stlp.comports():
            if("USB-Serial" in port.description):
                the_port = port.device
        return(the_port)
    except Exception as err:
        print("search_coms, ERROR:", err)
        return(None)

def read_resp():
    global ser
    theMsg = ''
    while(True):
        try:
            theByte = ser.read(1)
            decodeByte = theByte.decode('utf-8')
            if(decodeByte == '\r'):
                break
            else:
                theMsg += decodeByte
        except Exception as err:
            print("read_resp, ERROR:", err)

    return(theMsg)

def send_msg(the_bytes):
    ser.write(b'\x1B')
    sendy = ser.write(bytes(the_bytes, "utf-8"))
    ser.write(bytes('\r', "utf-8"))

    if(sendy > 0):
        confirm = read_resp()
        return(confirm)
    else:    
        return(None)

def convert_int(the_string, sind, eind):
    try:
        theStr = the_string[sind:eind]
        return(int(theStr))
    except Exception as err:
        print("convert_int", sind, eind)
        return(None)

sendDict = {}
def default_send_dict():
    global sendDict
    sendDict = {"datetime": None, "measured": None, "set": None}

def cur_time_string():
    return(datetime.datetime.now().strftime("%Y-%m-%d %H:%M%:S"))

while(True):
    if(ser == None):
        found_port = search_coms()
        if(found_port != None):
            print("FOUND COM:", found_port)
            open_serial()

            resp = send_msg("VTDw")
            print("DISABLE CHECKSUM:", resp)

            resp = send_msg("VTX ")
            print("SET AUTO MODE:", resp)

            default_send_dict()
        else:
            print("NO AVAILABLE PORTS")
            time.sleep(60)
    else:
        theRes = read_resp()
        print(cur_time_string, "-", theRes)
        
        if(theRes.startswith(":VTD")):
            tv = convert_int(theRes, 4, 8)
            print("Measured Tidal Volume:", tv)

            mv = convert_int(theRes, 8, 12)
            print("Measured Minute Volume:", mv)

            rr = convert_int(theRes,theRes, 12, 15)
            print("Measured RR:", rr)

            o2 = convert_int(theRes, theRes, 15, 18)
            print("Mesured O2:", o2)

            maxPres = convert_int(theRes, 18, 21)
            print("Measured Max Pressure:", maxPres)

            inspPlat = convert_int(theRes, 21, 24)
            print("Measured Inspiratory Plateau:", inspPlat)

            meanPres = convert_int(theRes, 24, 27)
            print("Measured Mean Pressure:", meanPres)

            minPres = convert_int(theRes, 27, 30)
            print("Measured Min Pressure:", minPres)

            #Check to see if this new message was a new breath
            indByte = theRes[30:31]
            if(indByte == '\x40'):
                indByte = True
            elif(indByte == '\x00'):
                indByte = False
            else:
                indByte = False
                
            if(sendDict["datetime"] == None):
                sendDict["datetime"] = cur_time_string()
            sendDict["measured"] = {}
            sendDict["measured"]["meas_tidal_vol"] = tv
            sendDict["measured"]["meas_minute_vol"] = mv
            sendDict["measured"]["meas_rr"] = rr
            sendDict["measured"]["meas_o2"] = o2
            sendDict["measured"]["meas_max_pres"] = maxPres
            sendDict["measured"]["meas_insp_plat"] = inspPlat
            sendDict["measured"]["meas_mean_pres"] = meanPres
            sendDict["measured"]["meas_min_pres"] = minPres
        elif(theRes.startswith(":VTQ")):
            tv = convert_int(theRes, 4, 8)
            print("Set Tidal Volume:", tv)

            rr = convert_int(theRes, 8, 11)
            print("Set RR:", rr)

            try:
                itoe = theRes[11, 15]
                strVal = itoe[0:3] + "." + itoe[3]
                itoe = float(strVal)
            except Exception as err:
                itoe = None
            print("Set I to E: 1:", itoe) 

            peep = convert_int(theRes, 17, 19)
            print("Set PEEP:", peep)

            inspPres = convert_int(theRes, 22, 24)
            print("Set Insp Pres:", inspPres)

            try:
                ventMode = theRes[44:45]
                if(ventMode == "v"):
                    ventMode = "Volume"
                elif(ventMode == "p"):
                    ventMode = "Pressure"
                elif(ventMode == "b"):
                    ventMode = "Backup Volume"
                elif(vnetMode == "-"):
                    ventMode = "Bag"
                else:
                    ventMode = None
            except Exception as err:
                ventMode = None
            print("Set Vent Mode:", ventMode)

            if(sendDict["datetime"] == None):
                sendDict["datetime"] = cur_time_string()
            sendDict["set"] = {}
            sendDict["set"]["set_tidal_volume"] = tv
            sendDict["set"]["set_rr"] = rr
            sendDict["set"]["set_itoe"] = itoe
            sendDict["set"]["set_peep"] = peep
            sendDict["set"]["set_insp_pres"] = inspPres
            sendDict["set"]["set_vent_mode"] = ventMode

        if(sendDict["measured"] != None and sendDict["set"] != None):
            #Send redcap
            print("Send Record")        
            default_send_dict()

