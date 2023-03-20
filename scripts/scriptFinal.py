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

##########################Variables globales###########################
GPIO.setmode(GPIO.BOARD)            #Numeracion de la tarjeta
i = 12                               #Variable para contador
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

#############################Thingspeak#################################
ps = subprocess.Popen(['iwgetid'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
try:
    output = subprocess.check_output(('grep', 'ESSID'), stdin=ps.stdout)    #Verifica Conexion Wifi
    wifi_status = True
except subprocess.CalledProcessError:
    wifi_status = False                                                     #No hay conexion wifi
    print("not wifi, testing eth")
    ping_ethernet= os.system("ping -c4 10.10.10.20")
    if ping_ethernet == 0:
        wifi_status = True
        print("eth detected")
    else:
        wifi_status = False
        print("starting offline mode")

archivo = open('key')
ts_apikey = str(archivo.readline())      #API KEY para Thingspeak
ts_apikey = ts_apikey[:-1]
print("KEY loaded:", ts_apikey, "\n")
archivo.close()

if wifi_status == True:
    ts_server = urllib3.PoolManager()   #Iniciar comunicacion con servidor
else:
    pass

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

    #Guarda el paquete recibido
    j = 0
    while j<15:                         
        lista.append(ord(mod.read()))
        j = j + 1

    #Decodifica el paquete
    co2 = lista[0]*256 + lista[1]
    pm25 = lista[6]*256 + lista[7]
    pm10 = lista[8]*256 + lista[9]
    temp = lista[10] + lista[11]/10

    return [co2, pm25, pm10, temp]      #Regresa una lista con valores recibidos


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

def i_event(channel):                   #Atencion a la interrupcion
        global i                        #Accede a la variable para contador
        print('sm300d2 sync signal detected')

        i = i + 1                       #Incrementa el contador
        if i == 15:                     #Al recibir 20 pulsos
            i = 0                       #Resetea el contador
            lee_modulos(lee_SM300(), ['Alto', 4], [0,0,0]) #Lee modulos
        else:
            act_hora()                  #Actualiza hora en pantalla
            
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

    label_res_spl["text"] = spl[0]                 #spl

    label_res_lat["text"] = round(pos[1], 5)       #latitud
    label_res_lon["text"] = round(pos[2], 5)       #longitud

    print(f'{ts_apikey},{aire[0]},{aire[1]},{aire[2]},{spl},{aire[3]},{pos[1]},{pos[2]}')

    if wifi_status == True:                     #Si hay conexion wifi
        #Crea string para la solicitud
        http_request = f'https://api.thingspeak.com/update?api_key={ts_apikey}&field1={aire[0]}&field2={aire[1]}&field3={aire[2]}&field4={spl[1]}&field5={aire[3]}&field7={pos[1]}&field8={pos[2]}'
        r = ts_server.request('GET', http_request)  #Envia a thingspeak
        print("sended to server")
    else:
        lecturas = f'{ts_apikey},{aire[0]},{aire[1]},{aire[2]},{spl},{aire[3]},{pos[1]},{pos[2]}'
        archivo_offline = open("offline", 'a')
        archivo_offline.write(lecturas + "\n")
        archivo_offline.close
        print("saved offline")

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