import serial
import time
import RPi.GPIO as GPIO

uart = serial.Serial(port='/dev/ttyS0', baudrate=9600, timeout=1)

GPIO.setmode(GPIO.BOARD)
in_signal = 16

lee1 = 0
lee2 = 0

def i_event(channel):
    lee1 = ord(uart.read())
    lee2 = ord(uart.read())
    print(lee1*256+lee2)
            
GPIO.setup(in_signal, GPIO.IN)
GPIO.add_event_detect(in_signal, GPIO.FALLING, callback=i_event)

time.sleep(60)
