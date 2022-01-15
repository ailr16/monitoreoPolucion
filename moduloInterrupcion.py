#############################Librerias############################
import serial
import tkinter
import RPi.GPIO as GPIO
import random  
import time
import os
from azure.iot.device import IoTHubDeviceClient, Message

#######################Variables generales########################
GPIO.setmode(GPIO.BOARD)
in_signal = 16
i = 0
stat = 0
sensores = [0, 0, 0, 0]

##########################Puertos serie###########################
mod = serial.Serial(port='/dev/ttyS0', baudrate=9600, timeout = 1)

#######################Servidor remoto############################
CONNECTION_STRING = "HostName=monitoreoPolucion.azure-devices.net;DeviceId=m1;SharedAccessKey=oH7JV1wKJ8QDnxJQFLJU5c8tlEDuY/Sln2bVXH8YqAU=" 
MSG_SND = '{{"co2", {co2},"pm25", {pm25},"pm10", {pm10},"temp", {temp}}}'
client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

###################Funciones fuera de loop########################
def apagar():
    os.system("sudo shutdown -h now")

def leeModulo():
    lista = []
    b1 = 'x'
    b2 = 'x'
    while ord(b1)!=60 and ord(b2)!=2:
        b1 = mod.read()
        b2 = mod.read()

    i = 0
    while i<15:
        lista.append(ord(mod.read()))
        i = i + 1

    co2 = lista[0]*256 + lista[1]
    #h20 = lista[2]*256 + lista[3]
    #tvoc = lista[4]*256 + lista[5]
    pm25 = lista[6]*256 + lista[7]
    pm10 = lista[8]*256 + lista[9]
    temp = lista[10] + lista[11]/10
    #hum = lista[12] + lista[13]/10
    
    #print("co2="+str(co2))
    #print("pm25="+str(pm25))
    #print("pm10="+str(pm10))
    #print("temp="+str(temp))
    
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
        global sensores
        if i == 20:
            iothub_client_telemetry_sample_run(client)
            i = 0
            leeImprime(leeModulo())
        else:
            compruebaHora()

GPIO.setup(in_signal, GPIO.IN)
GPIO.add_event_detect(in_signal, GPIO.FALLING, callback=i_event)

###################Loop ventana########################
ventana = tkinter.Tk()
ventana.title("App")

ventana.attributes('-fullscreen', True)
ventana.configure(bg = '#B3FFCC', cursor = "dot")
fondoLabel = '#B3FFCC'

bg1 = tkinter.PhotoImage(file = "img1.png")
bg2 = tkinter.PhotoImage(file = "img2.png")

labelBG = tkinter.Label(ventana, image = bg1, text = "hola")
labelBG.place(x = 0, y = 0)

tiempo = time.ctime()
hora = tiempo[11]+tiempo[12]
minutos = tiempo[14]+tiempo[15]

labelHora = tkinter.Label(ventana, text = hora+':'+minutos, bg = "#FFFFFF", font=("Arial", 40))
labelHora.place(relx = 0.102, rely = 0.264)

labelCO2 = tkinter.Label(ventana, text = "CO2", bg = "#66E1FF", font=("Arial", 18))
labelCO2.place(relx = 0.465, rely = 0.14)

labelCO2res = tkinter.Label(ventana, text = "CO2", bg = "#66E1FF", font=("Arial", 28))
labelCO2res.place(relx = 0.456, rely = 0.194)

labelPM25 = tkinter.Label(ventana, text = "PM2.5", bg = "#66E1FF", font=("Arial", 18))
labelPM25.place(relx = 0.79, rely = 0.15)

labelPM25res = tkinter.Label(ventana, text = "PM2.5", bg = "#66E1FF", font=("Arial", 28))
labelPM25res.place(relx = 0.81, rely = 0.21)

labelPM10 = tkinter.Label(ventana, text = "PM10", bg = "#66E1FF", font=("Arial", 18))
labelPM10.place(relx = 0.797, rely = 0.31)

labelPM10res = tkinter.Label(ventana, text = "PM10", bg = "#66E1FF", font=("Arial", 28))
labelPM10res.place(relx = 0.81, rely = 0.37)

labelSPL = tkinter.Label(ventana, text = "SPL", bg = "#FFFFFF", font=("Arial", 18))
labelSPL.place(relx = 0.202, rely = 0.745)

labelSPLres = tkinter.Label(ventana, text = "SPL", bg = "#FFFFFF", font=("Arial", 23))
labelSPLres.place(relx = 0.156, rely = 0.805)

labelTEMP = tkinter.Label(ventana, text = "TEMP", bg = "#66E1FF", font=("Arial", 18))
labelTEMP.place(relx = 0.414, rely = 0.51)

labelTEMPres = tkinter.Label(ventana, text = "TEMP", bg = "#66E1FF", font=("Arial", 28))
labelTEMPres.place(relx = 0.41, rely = 0.562)

labelLAT = tkinter.Label(ventana, text = "LATITUD", bg = "#66E1FF", font=("Arial", 15))
labelLAT.place(relx = 0.671, rely = 0.71)

labelLATres = tkinter.Label(ventana, text = "lat", bg = "#66E1FF", font=("Arial", 22))
labelLATres.place(relx = 0.654, rely = 0.76)

labelLON = tkinter.Label(ventana, text = "LONGITUD", bg = "#66E1FF", font=("Arial", 15))
labelLON.place(relx = 0.658, rely = 0.83)

labelLONres = tkinter.Label(ventana, text = "lon", bg = "#66E1FF", font=("Arial", 22))
labelLONres.place(relx = 0.65, rely = 0.88)

boton = tkinter.Button(ventana, text = "Salir", command = exit)
boton.place(relx = 0.9, rely = 0.72)  
  
boton = tkinter.Button(ventana, text = "Apagar", command = lambda: apagar())
boton.place(relx = 0.9, rely = 0.85)

def leeImprime(aire):
    compruebaHora()
    
    labelCO2res["text"] = aire[0]
    labelPM25res["text"] = aire[1]
    labelPM10res["text"] = aire[2]
    labelTEMPres["text"] = aire[3]

def compruebaHora():
    tiempo = time.ctime()
    hora = tiempo[11]+tiempo[12]
    minutos = tiempo[14]+tiempo[15]
    labelHora["text"] = hora+':'+minutos
    if int(hora) >= 19:
        labelBG["image"] = bg2
        labelHora["bg"] = "#062544"
        labelHora["fg"] = "#FFFFFF"
        labelSPL["bg"] = "#66E1FF"
        labelSPLres["bg"] = "#66E1FF"
    else:
        labelBG["image"] = bg1
        labelHora["bg"] = "#FFFFFF"
        labelHora["fg"] = "#000000"
        labelSPL["bg"] = "#FFFFFF"
        labelSPLres["bg"] = "#FFFFFF"
        
ventana.mainloop()

    