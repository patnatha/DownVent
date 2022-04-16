import serial
import serial.tools.list_ports as stlp

the_port = None
for port in stlp.comports():
    if("USB-Serial" in port.description):
        the_port = port.device

ser = serial.Serial(port=the_port, baudrate=19200, bytesize=serial.SEVENBITS,
                    parity=serial.PARITY_ODD, stopbits=serial.STOPBITS_ONE)

def read_resp():
    global ser
    theMsg = ''
    while(True):
        theByte = ser.read(1)
        decodeByte = theByte.decode('utf-8')
        if(decodeByte == '\r'):
            break
        else:
            theMsg += decodeByte

    return(theMsg)

#Disable checksum
print("DISABLE CHECKSUM")
ser.write(b'\x1B')
ser.write(bytes("VTDw\r", "utf-8"))
print("VENT RESPONSE:",read_resp())

#Set auto mode
print("SET IN AUTO MODE")
ser.write(b'\x1B')
ser.write(bytes("VTX \r", "utf-8"))
print("VENT RESPONSE:", read_resp())

while(True):
    theRes = read_resp()
    print(theRes)
    
    if(theRes.startswith(":VTD")):
        tv = theRes[4:8]
        print("Measured Tidal Volume:", tv)

        mv = theRes[8:12]
        print("Measured Minute Volume:", mv)

        rr = theRes[12:15]
        print("Measured RR:", rr)

        o2 = theRes[15:18]
        print("Mesured O2:", o2)

        maxPres = theRes[18:21]
        print("Measured Max Pressure:", maxPres)

        inspPlat = theRes[21:24]
        print("Measured Inspiratory Plateau:", inspPlat)

        meanPres = theRes[24:27]
        print("Measured Mean Pressure:", meanPres)
    elif(theRes.startswith(":VTQ")):
        tv = theRes[4:8]
        print("Set Tidal Volume:", tv)

        rr = theRes[8:11]
        print("Set RR:", rr)

        itoe = theRes[11:15]
        print("Set I to E: 1:" + itoe[0:3] + "." + itoe[3]) 

        peep = theRes[17:19]
        print("Set PEEP:", peep)

        inspPres = theRes[22:24]
        print("Set Insp Pres:", inspPres)

        ventMode = theRes[44:45]
        if(ventMode == "v"):
            ventMode = "Volume"
        elif(ventMode == "p"):
            ventMode = "Pressure"
        elif(ventMode == "b"):
            ventMode = "Backup Volume"
        elif(vnetMode == "-"):
            ventMode == "Bag"
        print("Set Vent Mode:", ventMode)

ser.close()

