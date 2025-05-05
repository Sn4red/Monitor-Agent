import shutil
import datetime
import time
import os

# Constantes
DISCO_PATH = "c:\\" #Ruta del disco a monitoriar en Linux "/" o "c:\\" en Windows
UMBRAL_PORCENTAJE = 90 #Disco supera 90%
INTERVALO_SEGUNDOS = 120 # Intervalos de segundos para la verificacion
LOG_PATH = "logs/registro_disco.txt" #Ruta que se crea para registrar los evento o sucesos

class MonitorDisco:
    #Indica que es un metodo constructor "def _init_" cuando se crea un objeto
    def __init__(self, path=DISCO_PATH, umbral=UMBRAL_PORCENTAJE, intervalo=INTERVALO_SEGUNDOS, log_path=LOG_PATH):
        self.path = path
        self.umbral = umbral
        self.intervalo = intervalo
        self.log_path = log_path

    #Definimos un metodo, sef se encarga para acceder los atributos
    #"Self.path -->la ruta del disco a monitorear"
    # Linea 24 se crea la funcion  
    def obtener_porcentaje_disco(self):
        uso = shutil.disk_usage(self.path)
        porcentaje = (uso.used / uso.total) * 100
        return uso.total, uso.used, uso.free, porcentaje
    
    #Definimos el metodo, va recibir un mensaje.
    #En la linea 32 permite acceder el archivo log
    #En la linea 31 se muestra la fecha y hora  
    #El STRFTIME convierte una cadena de texto
    def registrar_log(self, mensaje):
        hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_path, "a") as archivo:
            archivo.write(f"[{hora}] {mensaje}\n")
    

    #Realiza un monitoreo continuo del uso del disco duro
    #El estado actual del espacio libre en GB
    #Linea 45 -> El 2f muestra el porcentaje en 2 decimales
    def monitorear(self):
        print(" Iniciando monitoreo del disco...\n")
        while True:
            total, usado, libre, porcentaje = self.obtener_porcentaje_disco()
            print(f"Uso actual del disco: {porcentaje:.2f}% | Libre: {libre / (1024**3):.2f} GB | Usado: {usado /(1024**3):.2f} GB")
            

            if porcentaje >= self.umbral:
                alerta = f" Alerta!! : Disco duro casi lleno ({porcentaje:.2f}%)."
                print(alerta)
                self.registrar_log(alerta) #Guarda el mensaje al archivo log
            else:
                estado = f" Disco optimo: {porcentaje:.2f}% en uso."
                self.registrar_log(estado) 

            time.sleep(self.intervalo) #Evita que el monitoreo se ejecute constatemente sin descanso

#Esta linea muestra que el bloque se ejecute
#si el archivo se corre directamente
if __name__ == "__main__":
    try:
        monitor = MonitorDisco()
        monitor.monitorear()
    except KeyboardInterrupt:
        print("\n⏹ Monitoreo detenido por el usuario.")
