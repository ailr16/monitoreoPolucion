#Script final para el dispositivo
#ailr16     Marzo 2022

################################Librerias###############################
import serial                       #Comunicacion serie
import tkinter                      #GUI
import RPi.GPIO as GPIO             #GPIO de la RPi
import time                         #Libreria de tiempo
import os                           #Utilidades del SO
import urllib3                      #Para protocolo HTTP
import subprocess                   #Procesos del SO

##########################Variables generales###########################
GPIO.setmode(GPIO.BOARD)            #Numeracion de la tarjeta
i = 0                               #Variable para contador
wifi_status = False
med_sonido = [0,0,0,0]

######################Pines para interrupciones#########################
int_sm300 = 16                      #Pin para interrupcion SM300D2
int_sonido = 18                     #Pin para interrupcion modulo sonido
int_gps = 22                        #Pin para interrupcion gps

#############################Puertos serie##############################
mod = serial.Serial(port='/dev/ttyS0', baudrate = 9600, timeout = 1)      #UART1
sonido = serial.Serial(port='/dev/ttyAMA1', baudrate = 9600, timeout = 1)    #UART4
gps = serial.Serial(port='/dev/ttyAMA2', baudrate = 9600, timeout = 1)    #UART5

#######################Funciones fuera de loop##########################
def apagar():                           #Apagar el sistema
    os.system("sudo shutdown -h now")

def lee_SM300():                        #Leer modulo SM300D2
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

    return [co2, pm25, pm10, temp]      #Regresa una lista con valores recibidos


def lee_gps():
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
        
    return [status, lat, lon]

def lee_sonido():
    res_num = 0
    res = ''
    lee1 = 0
    lee2 = 0

    lee1 = ord(sonido.read())
    lee2 = ord(sonido.read())
    
    res_num = lee1*256+lee2
    
    if  res_num > 0 and res_num < 400:
        res = 'Bajo'
    elif res_num > 400 and res_num < 700:
        res = 'Moderado'
    elif res_num > 700 and res_num < 850:
        res = 'Alto'
    else:
        res = 'Muy alto'
        
    return res

def i_event(channel):                   #Atencion a la interrupcion
        global i                        #Accede a la variable para contador

        i = i + 1                       #Incrementa el contador
        if i == 20:                     #Al recibir 20 pulsos
            i = 0                       #Resetea el contador
            lee_modulos(lee_SM300(), lee_sonido(), lee_gps()) #Lee modulos
        else:
            #act_hora()                  #Actualiza hora en pantalla
            pass
            
GPIO.setup(int_sm300, GPIO.IN)          #Pin 16 como entrada
GPIO.add_event_detect(int_sm300, GPIO.FALLING, callback=i_event)    #Interrupcion pin 16

###################Loop ventana########################
ventana = tkinter.Tk()
ventana.title("Monitoreo")

ventana.attributes('-fullscreen', True)             #Pantalla completa
ventana.configure(bg = '#B3FFCC', cursor = "dot")   #Cursor punto
fondoLabel = '#B3FFCC'

bg1 = tkinter.PhotoImage(file = "img1.png")         #Carga fondo claro
bg2 = tkinter.PhotoImage(file = "img2.png")         #Carga fondo obscuro

label_bg = tkinter.Label(ventana, image = bg1, text = "hola")   #Etiqueta contenedor de fondo
label_bg.place(x = 0, y = 0)

tiempo = time.ctime()                               #Obtener hora del sistema
hora = tiempo[11]+tiempo[12]
minutos = tiempo[14]+tiempo[15]

#Creacion de etiquetas
label_hora = tkinter.Label(ventana, text = hora+':'+minutos, bg = "#FFFFFF", font=("Arial", 40))
label_co2 = tkinter.Label(ventana, text = "CO2", bg = "#66E1FF", font=("Arial", 18))
label_pm25 = tkinter.Label(ventana, text = "PM2.5", bg = "#66E1FF", font=("Arial", 18))
label_pm10 = tkinter.Label(ventana, text = "PM10", bg = "#66E1FF", font=("Arial", 18))
label_spl = tkinter.Label(ventana, text = "SPL", bg = "#FFFFFF", font=("Arial", 18))
label_temp = tkinter.Label(ventana, text = "TEMP", bg = "#66E1FF", font=("Arial", 18))
label_lat = tkinter.Label(ventana, text = "LATITUD", bg = "#66E1FF", font=("Arial", 15))
label_lon = tkinter.Label(ventana, text = "LONGITUD", bg = "#66E1FF", font=("Arial", 15))

#Colocar etiquetas
label_hora.place(relx = 0.102, rely = 0.264)
label_co2.place(relx = 0.465, rely = 0.14)
label_pm25.place(relx = 0.79, rely = 0.15)
label_pm10.place(relx = 0.797, rely = 0.31)
label_spl.place(relx = 0.202, rely = 0.745)
label_temp.place(relx = 0.414, rely = 0.51)
label_lat.place(relx = 0.671, rely = 0.71)
label_lon.place(relx = 0.658, rely = 0.83)

#Crear etiquetas para mostrar resultados
label_res_co2 = tkinter.Label(ventana, text = "CO2", bg = "#66E1FF", font=("Arial", 28))
label_res_pm25 = tkinter.Label(ventana, text = "PM2.5", bg = "#66E1FF", font=("Arial", 28))
label_res_pm10 = tkinter.Label(ventana, text = "PM10", bg = "#66E1FF", font=("Arial", 28))
label_res_spl = tkinter.Label(ventana, text = "SPL", bg = "#FFFFFF", font=("Arial", 23))
label_res_temp = tkinter.Label(ventana, text = "TEMP", bg = "#66E1FF", font=("Arial", 28))
label_res_lat = tkinter.Label(ventana, text = "lat", bg = "#66E1FF", font=("Arial", 22))
label_res_lon = tkinter.Label(ventana, text = "lon", bg = "#66E1FF", font=("Arial", 22))

#Colocar etiquetas de resultado
label_res_co2.place(relx = 0.456, rely = 0.194)
label_res_pm25.place(relx = 0.81, rely = 0.21)
label_res_pm10.place(relx = 0.81, rely = 0.37)
label_res_spl.place(relx = 0.156, rely = 0.805)
label_res_temp.place(relx = 0.41, rely = 0.562)
label_res_lat.place(relx = 0.654, rely = 0.76)
label_res_lon.place(relx = 0.65, rely = 0.88)

#Boton para salir
boton = tkinter.Button(ventana, text = "Salir", command = exit)
boton.place(relx = 0.9, rely = 0.72)  

#Boton para apagar
boton = tkinter.Button(ventana, text = "Apagar", command = lambda: apagar())
boton.place(relx = 0.9, rely = 0.85)

def lee_modulos(aire, spl, pos):
    act_hora()                                  #Actualiza hora
    
    #imprime datos en pantalla
    label_res_co2["text"] = aire[0]             #co2
    label_res_pm25["text"] = aire[1]            #pm25
    label_res_pm10["text"] = aire[2]            #pm10
    label_res_temp["text"] = aire[3]            #temp

    label_res_spl["text"] = spl                 #spl

    label_res_lat["text"] = pos[0]              #latitud
    label_res_lon["text"] = pos[1]              #longitud

def act_hora():
    tiempo = time.ctime()                       #Obtiene hora del sistema
    hora = tiempo[11]+tiempo[12]
    minutos = tiempo[14]+tiempo[15]
    label_hora["text"] = hora+':'+minutos       #Imprime hora
    if int(hora) >= 19 and int(hora) < 7:       #Fondo obscuro de 19:00 a 7:00
        label_bg["image"] = bg2
        label_hora["bg"] = "#062544"
        label_hora["fg"] = "#FFFFFF"
        label_spl["bg"] = "#66E1FF"
        label_res_spl["bg"] = "#66E1FF"
    else:                                       #Fondo claro para el resto del dia
        label_bg["image"] = bg1
        label_hora["bg"] = "#FFFFFF"
        label_hora["fg"] = "#000000"
        label_spl["bg"] = "#FFFFFF"
        label_res_spl["bg"] = "#FFFFFF"
        
ventana.mainloop()                              #Loop para mantener la ventana