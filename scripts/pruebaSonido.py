import serial                       #Comunicacion serie
import tkinter                      #GUI
import RPi.GPIO as GPIO             #GPIO de la RPi
import time                         #Libreria de tiempo
import os                           #Utilidades del SO
import urllib3                      #Para protocolo HTTP
import subprocess                   #Procesos del SO

sonido = serial.Serial(port='/dev/ttyAMA1', baudrate = 9600, timeout = 1)    #UART4

def lee_sonido():
    res_num = 0
    res = ''
    lee1 = 0
    lee2 = 0

    lee1 = ord(sonido.read())
    lee2 = ord(sonido.read())
    
    res_num = lee1*256+lee2
    
    if  res_num > 0 and res_num < 316:
        res = 'Bajo'
        res_n = 1
    elif res_num >= 316  and res_num < 328:
        res = 'Moderado'
        res_n = 2
    elif res_num >= 328 and res_num <= 332:
        res = 'Alto'
        res_n = 3
    else:
        res = 'Muy alto'
        res_n = 4
        
    return [res, res_n]


for i in range(1,10,1):
    print(lee_sonido())
    time.sleep(2)