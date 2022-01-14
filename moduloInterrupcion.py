import serial
import RPi.GPIO as GPIO
import random  
import time
from azure.iot.device import IoTHubDeviceClient, Message

GPIO.setmode(GPIO.BOARD)
in_signal = 16
i = 0
stat = 0
sensores = [0, 0, 0, 0]

uart = serial.Serial(port='/dev/ttyS0', baudrate=9600, timeout = 1)

CONNECTION_STRING = "HostName=monitoreoPolucion.azure-devices.net;DeviceId=m1;SharedAccessKey=oH7JV1wKJ8QDnxJQFLJU5c8tlEDuY/Sln2bVXH8YqAU=" 
MSG_SND = '{{"co2", {co2},"pm25", {pm25},"pm10", {pm10},"temp", {temp}}}'
client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

def leeModulo():
    lista = []
    b1 = 'x'
    b2 = 'x'
    while ord(b1)!=60 and ord(b2)!=2:
        b1 = uart.read()
        b2 = uart.read()

    i = 0
    while i<15:
        lista.append(ord(uart.read()))
        i = i + 1

    co2 = lista[0]*256 + lista[1]
    #h20 = lista[2]*256 + lista[3]
    #tvoc = lista[4]*256 + lista[5]
    pm25 = lista[6]*256 + lista[7]
    pm10 = lista[8]*256 + lista[9]
    temp = lista[10] + lista[11]/10
    #hum = lista[12] + lista[13]/10
    
    print("co2="+str(co2))
    print("pm25="+str(pm25))
    print("pm10="+str(pm10))
    print("temp="+str(temp))
    
    return [co2, pm25, pm10, temp]

def iothub_client_telemetry_sample_run(client):
    print ( "Sending data to IoT Hub, press Ctrl-C to exit" )
    sensores = leeModulo()
    msg_txt_formatted = MSG_SND.format(co2=sensores[0], pm25=sensores[1], pm10=sensores[2], temp=sensores[3])
    message = Message(msg_txt_formatted)
    print( "Sending message: {}".format(message) )
    client.send_message(message)
    print ( "Message successfully sent" )

def i_event(channel):
        global i
        global client
        i = i + 1
        print("Flanco detectado" + str(i))
        global sensores
        if i == 20:
            #sensores = leeModulo()
            iothub_client_telemetry_sample_run(client)
            i = 0
        else:
            sensores = sensores

GPIO.setup(in_signal, GPIO.IN)
GPIO.add_event_detect(in_signal, GPIO.FALLING, callback=i_event)

while True:
    pass
    