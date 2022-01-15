import tkinter
import serial
import urllib3
import time
import RPi.GPIO as GPIO
import os

def apagar():
	os.system("sudo shutdown -h now")

time.sleep(2)

gps = serial.Serial(port='/dev/ttyS0', baudrate=9600, timeout = 1)
mod = serial.Serial(port='/dev/ttyAMA1', baudrate=9600, timeout = 1)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.IN)

http = urllib3.PoolManager()

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

def leePosicion():
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

	return [co2, pm25, pm10, temp]

def leeSonido():
	nivel = 0
	array = [0,0,0,0,0]
	i = 0
	a = 0
	b = 0
	while i < 5:
		if GPIO.input(16):
			array[i] = 1
			a = a + 1
		else:
			array[i] = 0
			b = b + 1
		i = i + 1
		time.sleep(1)
	if a > b:
		nivel = 1
	else:
		nivel = 0
	return nivel

def leeImprime():
	compruebaHora()
	pos = leePosicion()
	aire = leeModulo()
	sonido = leeSonido()
	if pos[0]==1:
		labelLATres["text"] = str(round(pos[1],4))
		labelLONres["text"] = str(round(pos[2],4))
	else:
		labelLATres["text"] = "ERROR"
		labelLONres["text"] = "ERROR"

	labelCO2res["text"] = aire[0]
	labelPM25res["text"] = aire[1]
	labelPM10res["text"] = aire[2]
	labelTEMPres["text"] = aire[3]
	if sonido == 1:
		labelSPLres["text"] = "Alto"
	else:
		labelSPLres["text"] = "Moderado"
	r = http.request('GET', 'https://api.thingspeak.com/update?api_key=CCGVDI087OPEW7OT&field1=' + str(aire[0]) + '&field2=' + str(aire[1]) + '&field3=' + str(aire[2]) + '&field4=' + str(sonido) + '&field5=' + str(aire[3]) + '&field7=' + str(pos[1]) + '&field8=' + str(pos[2]))
	ventana.after(10100, leeImprime)

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

leeImprime()
ventana.mainloop()
