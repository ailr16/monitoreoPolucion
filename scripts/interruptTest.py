#Prueba para enviar un mensaje a Azure IoT
#ailr16 2022

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

in_signal = 16
i = 0

def i_event(channel):
	global i
	i = i + 1
	print("Flanco detectado" + str(i))

GPIO.setup(in_signal, GPIO.IN)
GPIO.add_event_detect(in_signal, GPIO.FALLING, callback=i_event)

try:
	print("Espera")
	time.sleep(10)
	print("Adios")

finally:
	GPIO.cleanup()
	
	
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

