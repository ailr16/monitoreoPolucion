#Script de prueba para interfaz ADC-UART basada en ATTiny85
#ailr16     Febrero 2022

import serial
import time
import RPi.GPIO as GPIO

mod = serial.Serial(port='/dev/ttyS0', baudrate = 9600, timeout = 1)      #UART1
sonido = serial.Serial(port='/dev/ttyAMA1', baudrate = 9600, timeout = 1)    #UART4
gps = serial.Serial(port='/dev/ttyAMA2', baudrate = 9600, timeout = 1)    #UART5

GPIO.setmode(GPIO.BOARD)
in_signal = 16

lee1 = 0
lee2 = 0

def i_event(channel):
    lista = []                          #Inicializa lista vacia
    b1 = 'x'                            #Inicializa bytes para verificar paquete
    b2 = 'x'
    while ord(b1)!=60 and ord(b2)!=2:   #Busca inicio del paquete
        b1 = mod.read()
        b2 = mod.read()

    j = 0
    while j<15:                         #Guarda el paquete recibido
        lista.append(ord(mod.read()))
        j = j + 1

    co2 = lista[0]*256 + lista[1]       #Decodifica el paquete
    pm25 = lista[6]*256 + lista[7]
    pm10 = lista[8]*256 + lista[9]
    temp = lista[10] + lista[11]/10

    lee1 = ord(sonido.read())
    lee2 = ord(sonido.read())
    
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

    print("CO2= " + str(co2) + ", PM25= " + str(pm25) + ", PM10= " + str(pm10) + ", TEMP= " + str(temp))
    print("SPL= " + str(lee1*256+lee2))
    print("GPS= " + str(lat) + "," + str(lon) + "\n")
            
GPIO.setup(in_signal, GPIO.IN)
GPIO.add_event_detect(in_signal, GPIO.FALLING, callback=i_event)

time.sleep(60)
