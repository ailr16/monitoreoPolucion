import serial                       #Comunicacion serie
import tkinter                      #GUI
import RPi.GPIO as GPIO             #GPIO de la RPi
import time                         #Libreria de tiempo
import os                           #Utilidades del SO
import urllib3                      #Para protocolo HTTP
import subprocess                   #Procesos del SO

gps = serial.Serial(port='/dev/ttyAMA2', baudrate = 9600, timeout = 1)    #UART5

def lee_gps():
    proto = ['p','r','o','t','o','c']               #Inicializa lista vacia

    while proto != ['$','G','P','R','M','C']:       #Cuando no detecte $GPRMC
        linea = gps.readline()                      #Lee una linea
        linea = linea.decode("utf-8")               #Decodifica UTF-8
        proto = [linea[0], linea[1], linea[2], linea[3], linea[4], linea[5]]        #Guarda los primeros 6 carracteres

    if linea[17] == 'A':                            #Si el caracter 18 es A la lectura esta completa
        status = 1                                  #Activa la bandera de status
        lat = int(linea[19] + linea[20]) + int(linea[21] + linea[22])/60 + int(linea[24]+ linea[25] + linea[26] + linea[27] + linea[28])/6000000    #Decodifica latitud
        ns = linea[30]                              #Obtiene la direccion N o S
        if ns == 'S':                               #Si es sur es negativo
            lat = lat*(-1)
        lon = int(linea[32] + linea[33] + linea[34]) + int(linea[35] + linea[36])/60 + int(linea[38] + linea[39] + linea[40] + linea[41] + linea[42])/6000000   #Decodifica longitud
        ew = linea[44]                              #Obtiene direccion E o W
        if ew == 'W':                               #Si es oeste es negativo
            lon = lon*(-1)
        archivo_gps = open("gps", 'w')              #Abre el archivo gps para guardar la ultima ubicacion
        archivo_gps.write(str(lat) + "," + str(lon))    #Escribe la ubicacion
        archivo_gps.close                           #Cierra el archivo
    else:                                           #El caracter no fue A -> la lectura es erronea
        status = 0                                  #Todos los valores seran cero para evitar errores
        lat = 0
        lon = 0
        
    return [status, lat, lon]                       #Regresa status latitud y longitud

for i in range(1,10,1):
    print(lee_gps())
    time.sleep(2)