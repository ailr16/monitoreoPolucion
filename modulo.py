import serial
import random  
import time
from azure.iot.device import IoTHubDeviceClient, Message

uart = serial.Serial(port='/dev/ttyS0', baudrate=9600, timeout = 1)
CONNECTION_STRING = "HostName=monitoreoPolucion.azure-devices.net;DeviceId=m1;SharedAccessKey=oH7JV1wKJ8QDnxJQFLJU5c8tlEDuY/Sln2bVXH8YqAU=" 
MSG_SND = '{{"co2", {co2},"pm25", {pm25},"pm10", {pm10},"temp", {temp}}}'

co2 = 0
pm25 = 0
pm10 = 0
temp = 0

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

while True:
    def iothub_client_init():  
        client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)  
        return client  
    def iothub_client_telemetry_sample_run():  
        try:  
            client = iothub_client_init()  
            print ( "Sending data to IoT Hub, press Ctrl-C to exit" )  
            while True:
                sensores = leeModulo()
                msg_txt_formatted = MSG_SND.format(co2=sensores[0], pm25=sensores[1], pm10=sensores[2], temp=sensores[3])  
                message = Message(msg_txt_formatted)  
                print( "Sending message: {}".format(message) )  
                client.send_message(message)  
                print ( "Message successfully sent" )  
                time.sleep(20)  
        except KeyboardInterrupt:
            print ( "IoTHubClient stopped" )  
    if __name__ == '__main__':  
        print ( "Press Ctrl-C to exit" )  
        iothub_client_telemetry_sample_run()

