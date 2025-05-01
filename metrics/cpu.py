import psutil
import requests

class Cpu:
    '''Clase para obtener las métricas de la CPU.'''

    def __init__(self):
       pass

    def obtener_nucleos_fisicos(self):
        '''Devuelve el número de núcleos físicos de la CPU.'''
        return psutil.cpu_count(logical = False)

    def obtener_nucleos_logicos(self):
        '''Devuelve el número de núcleos lógicos de la CPU.'''
        return psutil.cpu_count(logical = True)
    
    def obtener_uso_cpu(self):
        '''
        Devuelve el uso de la CPU en un tuple, donde el primer elemento es un
        tuple conteniendo el uso de cada núcleo y el segundo elemento es el
        uso total de la CPU.
        '''
        uso_cpu_nucleos = tuple(psutil.cpu_percent(interval=5.0, percpu=True))
        uso_cpu_total = round(sum(uso_cpu_nucleos) / len(uso_cpu_nucleos), 2)
        uso_cpu = (uso_cpu_nucleos, uso_cpu_total)

        return uso_cpu

    def obtener_temperatura_cpu_windows(self):
        '''
        Devuelve la temperatura de la CPU en un tuple, donde el primer elemento
        es un tuple conteniendo la temperatura de cada núcleo, el segundo
        elemento es la temperatura promedio de los núcleos y el tercer elemento
        es la temperatura del paquete de la CPU.
        '''
        try:
            url = 'http://localhost:8085/data.json'
            respuesta = requests.get(url, timeout = 3)
            respuesta.raise_for_status()
            datos = respuesta.json()

            paquete_cpu = None
            temperatura_nucleos = []

            for hardware in datos['Children'][0]['Children']:
                # Se accede al objeto de la CPU por medio de la imagen por defecto que brinda LibreHardware Monitor.
                if hardware.get('ImageURL', '') == 'images_icon/cpu.png':
                    for sensor in hardware['Children']:
                        # Se accede al objeto que contiene los sensores de temperatura.
                        if sensor['Text'] == 'Temperatures':
                            core = 1

                            for sensor_temperatura in sensor['Children']:
                                # Se accede al objeto que contiene la temperatura de cada núcleo.
                                if sensor_temperatura['Text'] == f'CPU Core #{core}':
                                    # El valor tiene formato string con el símbolo de grados Celsius. Se curó a float.
                                    temperatura_nucleo = float(sensor_temperatura['Value'].replace('°C', '').strip())
                                    temperatura_nucleos.append(temperatura_nucleo)

                                    # A la primera ejecución de este if, se va a incrementar el valor para que acceda
                                    # a todos los núcleos, ya que están presentados en orden en el JSON.
                                    core += 1

                                # Se accede al objeto que contiene la temperatura del paquete de la CPU.
                                if sensor_temperatura['Text'] == 'CPU Package':
                                    # El valor tiene formato string con el símbolo de grados Celsius. Se curó a float.
                                    paquete_cpu = float(sensor_temperatura['Value'].replace('°C', '').strip())

            temperatura_nucleos = tuple(temperatura_nucleos)
            temperatura_promedio = round(sum(temperatura_nucleos) / len(temperatura_nucleos), 2)
            temperatura_cpu = (temperatura_nucleos, temperatura_promedio, paquete_cpu)
            
            return temperatura_cpu                                
        except requests.RequestException as error:
            print('Error al conectar con el servidor de LibreHardware Monitor:', error)
            return []
