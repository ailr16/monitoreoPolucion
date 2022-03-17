import urllib3                      #Para protocolo HTTP
import time

archivo = open('key')
ts_apikey = str(archivo.readline())      #API KEY para Thingspeak
archivo.close()
ts_server = urllib3.PoolManager()   #Iniciar comunicacion con servidor

http_request = f'https://api.thingspeak.com/update?api_key={ts_apikey}&field1={1024}&field2={512}&field3={256}&field4={128}&field5={64}&field7={32}&field8={16}'
r = ts_server.request('GET', http_request)  #Envia a thingspeak

time.sleep(2)