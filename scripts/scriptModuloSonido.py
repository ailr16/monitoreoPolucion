#Script de prueba para interfaz ADC-UART basada en ATTiny85
#ailr16     Febrero 2022

import serial
import time
import RPi.GPIO as GPIO

uart = serial.Serial(port='/dev/ttyS0', baudrate=9600, timeout=1)
gps = serial.Serial(port='/dev/ttyAMA1', baudrate=9600, timeout = 1)

GPIO.setmode(GPIO.BOARD)
in_signal = 22

lee1 = 0
lee2 = 0

def i_event(channel):
    lee1 = ord(uart.read())
    lee2 = ord(uart.read())
    
    proto = ['p','r','o','t','o','c']

    while proto != ['$','G','P','R','M','C']:
        linea = gps.readline()
        linea = linea.decode("utf-8")
        proto = [linea[0], linea[1], linea[2], linea[3], linea[4], linea[5]]

    if linea[17] == 'A':
        status = 1
        lat = int(linea[19] + linea[20]) + int(linea[21] + linea[22])/60 + int(linea[24]+ linea[25] + linea[26] + linea[27] + linea[28])/6000000
        ns = linea[30]
        if ns == 'S':
            lat = lat*(-1)
        lon = int(linea[32] + linea[33] + linea[34]) + int(linea[35] + linea[36])/60 + int(linea[38] + linea[39] + linea[40] + linea[41] + linea[42])/6000000
        ew = linea[44]
        if ew == 'W':
            lon = lon*(-1)
        
    else:
        status = 0
        lat = 0
        lon = 0
    
    print("SPL= " + str(lee1*256+lee2))
    print("GPS= " + str(lat) + "," + str(lon))
            
GPIO.setup(in_signal, GPIO.IN)
GPIO.add_event_detect(in_signal, GPIO.FALLING, callback=i_event)

time.sleep(60)
