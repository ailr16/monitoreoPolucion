#Script Py para enviar un mensaje a Azure IoT (basado en post de un blog)
#ailr16     2022

import random  
import time
from azure.iot.device import IoTHubDeviceClient, Message

CONNECTION_STRING = "HostName=monitoreoPolucion.azure-devices.net;DeviceId=m1;SharedAccessKey=oH7JV1wKJ8QDnxJQFLJU5c8tlEDuY/Sln2bVXH8YqAU=" 
MSG_SND = '{{"temperature", {temperature},"humidity", {humidity}}}'

while True:
    humidity = 16
    temperature = 32
    def iothub_client_init():  
        client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)  
        return client  
    def iothub_client_telemetry_sample_run():  
        try:  
            client = iothub_client_init()  
            print ( "Sending data to IoT Hub, press Ctrl-C to exit" )  
            while True:  
                msg_txt_formatted = MSG_SND.format(temperature=temperature, humidity=humidity)  
                message = Message(msg_txt_formatted)  
                print( "Sending message: {}".format(message) )  
                client.send_message(message)  
                print ( "Message successfully sent" )  
                time.sleep(3)  
        except KeyboardInterrupt:  
            print ( "IoTHubClient stopped" )  
    if __name__ == '__main__':  
        print ( "Press Ctrl-C to exit" )  
        iothub_client_telemetry_sample_run()
