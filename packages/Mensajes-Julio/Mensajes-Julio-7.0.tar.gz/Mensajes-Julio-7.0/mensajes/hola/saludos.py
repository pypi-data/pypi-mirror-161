import numpy as np

def saludar():
    print("Hola, te estoy saludando desde saludos.saludar")

def prueba():
    print("Esto es una prueba de la nueva version Mensajes-Julio 7.0")

def generar_array(numeros):
    return np.arange(numeros)

class Saludo():
    def __init__(self):
        print("Hola, te saludo desde el init de la clase Saludo")

if __name__ =='__main__':
    print(generar_array(5))
