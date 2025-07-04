import psutil
import os
import subprocess
import json
import sys

from datetime import datetime

# * WMI sólo es importado si el sistema operativo es Windows.
if os.name == 'nt':
    import wmi

class Storage:
    '''Clase para obtener las métricas del storage.'''

    def obtener_almacenamiento_windows(self):
        '''
        Devuelve la información del almacenamiento en Windows en un tuple,
        donde cada elemento es un dictionary que contiene el modelo del disco
        y un tuple de particiones. Cada partición es un dictionary,
        conteniendo la unidad de la partición y el sistema de archivos.
        '''
        instancia_wmi = wmi.WMI()

        almacenamiento = []

        for disco in instancia_wmi.Win32_DiskDrive():
            modelo = disco.Model
            particiones = []

            for particion in disco.associators(
                'Win32_DiskDriveToDiskPartition'
            ):
                for disco_logico in particion.associators(
                    'Win32_LogicalDiskToPartition'
                ):
                    particiones.append({
                        'particion': disco_logico.DeviceID,
                        'sistema_archivos': disco_logico.FileSystem,
                    })

            particiones = tuple(particiones)

            almacenamiento.append({
                'modelo': modelo,
                'particiones': particiones
            })

        almacenamiento = tuple(almacenamiento)

        return almacenamiento

    def obtener_almacenamiento_linux(self):
        '''
        Devuelve la información del almacenamiento en Linux en un tuple,
        donde cada elemento es un dictionary que contiene el nombre del
        dispositivo, el modelo y un tuple de particiones. Cada partición es un
        dictionary, conteniendo la unidad de la partición y el sistema de
        archivos.
        '''
        almacenamiento = []

        try:
            comando = [
                'lsblk', '-J', '-o', 'NAME,MODEL,MOUNTPOINTS,TYPE,FSTYPE'
            ]

            resultado = subprocess.run(
                comando, capture_output=True, text=True, check=True
            )

            resultadoJSON = json.loads(resultado.stdout)['blockdevices']

            almacenamiento = []

            for disco in resultadoJSON:
                if disco.get('type') == 'disk':
                    nombre = disco.get('name')
                    modelo = disco.get('model')

                    if nombre.startswith('nvme'):
                        nombre = '/dev/' + nombre.rsplit('n', 1)[0]
                    elif nombre.startswith('sd'):
                        nombre = '/dev/' + nombre
                    elif nombre.startswith('mmcblk'):
                        nombre = '/dev/' + nombre

                    particiones = []

                    for particion in disco.get('children'):
                        particiones.append({
                            'particion': particion.get('mountpoints')[0],
                            'sistema_archivos': particion.get('fstype')
                        })

                    particiones = tuple(particiones)

                    almacenamiento.append({
                        'nombre': nombre,
                        'modelo': modelo,
                        'particiones': particiones
                    })

            almacenamiento = tuple(almacenamiento)

            return almacenamiento
        except Exception as error:
            print(f'{datetime.now()} >>> *** Error al ejecutar lsblk ***')
            print(error)

            # * Si no se puede ejecutar lsblk, se finaliza el agente.
            sys.exit(1)

    def obtener_horas_encendido(self, ejecucion_smartctl):
        '''
        Devuelve las horas de encendido del disco en base a la salida del
        comando smartctl.
        '''
        for linea in ejecucion_smartctl.splitlines():
            if 'Power On Hours' in linea:
                cadenas = linea.split()

                for cadena in cadenas:
                    horas_encendido = cadena.replace(',', '')

                    if horas_encendido.isdigit():
                        return int(horas_encendido)

        return -1

    def obtener_datos_leidos_escritos(self, ejecucion_smartctl):
        '''
        Devuelve el total de datos leídos y escritos del disco en base a la
        salida del comando smartctl en un tuple, donde el primer elemento es
        el total de datos leídos y el segundo elemento es el total de datos
        escritos.
        '''
        datos_leidos = None
        datos_escritos = None

        for linea in ejecucion_smartctl.splitlines():
            if 'Data Units Read' in linea:
                cadenas = linea.split()

                for cadena in cadenas:
                    valor = cadena.replace(',', '')

                    if valor.isdigit():
                        datos_leidos = int(valor)
                        break

            elif 'Data Units Written' in linea:
                cadenas = linea.split()

                for cadena in cadenas:
                    valor = cadena.replace(',', '')

                    if valor.isdigit():
                        datos_escritos = int(valor)
                        break

            # * Si ya se encontraron ambos valores, se sale del bucle.
            if datos_leidos is not None and datos_escritos is not None:
                break

        return (datos_leidos, datos_escritos)

    def obtener_temperatura(self, ejecucion_smartctl):
        '''
        Devuelve la temperatura del disco en base a la salida del comando
        smartctl.
        '''
        for linea in ejecucion_smartctl.splitlines():
            if 'Temperature' in linea:
                cadenas = linea.split()

                for cadena in cadenas:
                    if cadena.isdigit():
                        return int(cadena)

        return -1
    
    def obtener_uso_particion(self, particion):
        '''
        Devuelve el uso de cada partición del storage en un tuple, donde el
        primer elemento es el total, el segundo elemento es el espacio usado,
        el tercero elemento es el espacio libre y el cuarto elemento es el
        porcentaje de uso.
        '''
        uso_storage = psutil.disk_usage(particion)
        uso_storage = (
            uso_storage.total, uso_storage.used, uso_storage.free,
            uso_storage.percent
        )

        return uso_storage
