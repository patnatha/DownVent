import serial
import serial.tools.list_ports as stlp
import time
import datetime
import redcap as rc

ser = None
last_ser_read = None
def open_serial(the_port):
    try:
        global ser
        ser = serial.Serial(port=the_port, baudrate=19200, 
                            write_timeout=5, timeout=2,
                            bytesize=serial.SEVENBITS,
                            parity=serial.PARITY_ODD, 
                            stopbits=serial.STOPBITS_ONE)
    except Exception as err:
        ser = None
        print("OPEN PORT ERROR,", err)

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
    global last_ser_read
    theMsg = ''
    while(True):
        try:
            theByte = ser.read(1)
            if(theByte == b''): raise Exception("read_timeout")
            
            decodeByte = theByte.decode('utf-8')
            if(decodeByte == '\r'):
                #Bank the last time was read from serial
                last_ser_read = datetime.datetime.now()
                break
            else:
                theMsg += decodeByte
        except Exception as err:
            #If error is not a read timeout then print the error
            if("read_timeout" not in str(err)): 
                print("read_resp, ERROR:", err)
                close_serial()

            #If it has been greater than 30 seconds since last serial read
            if(last_ser_read != None and 
               ((datetime.datetime.now() - last_ser_read).total_seconds() > 20)):
                close_serial()

            #Return blank message
            theMsg = None
            break

    return(theMsg)

def send_msg(the_bytes):
    if(ser == None): return(None)

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
        #print("convert_int", sind, eind, err)
        return(None)

sendDict = {}
def default_send_dict():
    global sendDict
    sendDict = {"datetime": None, "measured": None, "set": None}

def cur_time_string():
    return(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

no_port_sleep = 30
while(True):
    if(ser == None):
        found_port = search_coms()
        if(found_port != None):
            print("FOUND PORT:", found_port)
            open_serial(found_port)

            resp = send_msg("VTDw")
            if(resp != None):
                print("DISABLE CHECKSUM:", resp)
            
                resp = send_msg("VTX ")
                if(resp != None):
                    print("SET AUTO MODE:", resp)
                else:
                    close_serial()
                    time.sleep(no_port_sleep)
            else:
                close_serial()
                time.sleep(no_port_sleep)

            default_send_dict()
        else:
            print("NO AVAILABLE PORTS")
            time.sleep(no_port_sleep)
    else:
        theRes = read_resp()
        if(theRes == None):
            continue

        print(cur_time_string(), "-", theRes)
        
        if(theRes.startswith(":VTD")):
            tv = convert_int(theRes, 4, 8)
            print("Measured Tidal Volume:", tv)

            mv = convert_int(theRes, 8, 12)
            print("Measured Minute Volume:", mv)

            rr = convert_int(theRes, 12, 15)
            print("Measured RR:", rr)

            o2 = convert_int(theRes, 15, 18)
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
            print("Measured Data Status:", indByte)    

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
            sendDict["measured_ind_byte"] = indByte
        elif(theRes.startswith(":VTQ")):
            tv = convert_int(theRes, 4, 8)
            print("Set Tidal Volume:", tv)

            rr = convert_int(theRes, 8, 11)
            print("Set RR:", rr)

            try:
                itoe = theRes[11:15]
                strVal = itoe[0:3] + "." + itoe[3:4]
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

            #print(len(theRes))
            #print(theRes[45:58])
            #print(theRes[45:58].encode("utf-8"))

            if(sendDict["datetime"] == None):
                sendDict["datetime"] = cur_time_string()
            sendDict["set"] = {}
            sendDict["set"]["set_tidal_volume"] = tv
            sendDict["set"]["set_rr"] = rr
            sendDict["set"]["set_itoe"] = itoe
            sendDict["set"]["set_peep"] = peep
            sendDict["set"]["set_insp_pres"] = inspPres
            sendDict["set"]["set_vent_mode"] = ventMode

        if(sendDict["datetime"] != None and
                sendDict["measured"] != None and 
                sendDict["set"] != None):

            if(sendDict["measured_ind_byte"]):
                toSend = {}
                for x in sendDict["set"]:
                    toSend[x] = sendDict["set"][x]
                for y in sendDict["measured"]:
                    toSend[y] = sendDict["measured"][y]
                rcres = rc.post_redcap(toSend)
                print("Send Record:", rcres)

            default_send_dict()

