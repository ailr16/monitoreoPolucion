import time

archivo = open('key')
print("Se ha abierto el archivo")
print(archivo.readline())
archivo.close()
print("Se ha cerrado el archivo")
time.sleep(1)