import subprocess
import os
import psutil
import sys

import xml.etree.ElementTree as ET

from datetime import datetime

def iniciar_libre_hardware_monitor():
    '''
    Inicia Libre Hardware Monitor con privilegios de administrador.
    '''
    # Se obtiene la ruta relativa del ejecutable, y se convierte a ruta absoluta para
    # mayor claridad en la depuración.
    ruta = os.path.abspath(os.path.join('librehardwaremonitor', 'LibreHardwareMonitor.exe'))

    try:
        inspeccion_instancia = esta_libre_hardware_monitor_activo()

        # Se verifica si Libre Hardware Monitor ya está en ejecución. Si ya lo está, no se vuelve a iniciar.
        if inspeccion_instancia['esta_activo']:
            print(f'{datetime.now()} >>> *** Libre Hardware Monitor ya está en ejecución ***')

            # Si la instancia ejecutada es externa al proyecto, se notifica al usuario.
            if inspeccion_instancia['es_instancia_externa']:
                print('*** Libre Hardware Monitor está en ejecución como una instancia externa al proyecto ***')
                print('*** Se recomienda cerrar la instancia externa para evitar conflictos ***')
        else:
            # Se ejecuta el comando de PowerShell para iniciar Libre Hardware Monitor con privilegios de administrador.
            subprocess.run(['powershell', 'Start-Process', ruta, '-Verb', 'runAs'], check=True)
            print(f'{datetime.now()} >>>*** Libre Hardware Monitor iniciado correctamente ***')

            # Se configura Libre Hardware Monitor para que se inicie con los ajustes deseados.
            configurar_libre_hardware_monitor()
    except Exception as error:
        print(f'{datetime.now()} >>> *** Error al iniciar Libre Hardware Monitor ***')
        print(error)

def esta_libre_hardware_monitor_activo():
    '''
    Verifica si Libre Hardware Monitor ya está en ejecución, y si es una instancia externa al proyecto.
    '''
    # Se obtiene la ruta relativa del ejecutable, y se convierte a ruta absoluta para
    # compararla con la ruta del ejecutable en ejecución.
    ruta_local = os.path.abspath(os.path.join('librehardwaremonitor', 'LibreHardwareMonitor.exe'))

    esta_activo = None
    es_instancia_externa = None

    # Se iteran sobre los procesos en ejecución.
    for proceso in psutil.process_iter(['name', 'exe']):
        try:
            # Se verifica si el nombre del proceso es 'LibreHardwareMonitor.exe'.
            if proceso.info['name'] == 'LibreHardwareMonitor.exe':
                esta_activo = True

                ruta_ejecucion = os.path.abspath(proceso.info['exe'])

                # Se compara la ruta del ejecutable en ejecución con la ruta del ejecutable local.
                if ruta_ejecucion != ruta_local:
                    es_instancia_externa = True
                else:
                    es_instancia_externa = False
            
                return {
                    'esta_activo': esta_activo,
                    'es_instancia_externa': es_instancia_externa
                }
        except psutil.AccessDenied as error:
            print(f'{datetime.now()} >>> *** Error. No se tienen permisos suficientes para verificar si Libre Hardware Monitor está activo ***')
            print('*** La ejecución del agente se finalizará. Verificar privilegios ***')
            print(error)

            # Si se tienen permisos insuficientes para verificar el proceso, se finaliza el agente.
            sys.exit(1)
        except Exception as error:
            print(f'{datetime.now()} >>> *** Error al verificar si Libre Hardware Monitor está activo ***')
            print(error)

            esta_activo = False
            es_instancia_externa = False
                    
    esta_activo = False
    es_instancia_externa = False

    return {
        'esta_activo': esta_activo,
        'es_instancia_externa': es_instancia_externa
    }

def configurar_libre_hardware_monitor():
    '''
    Configura Libre Hardware Monitor para que se inicie con los siguientes ajustes:

    - Iniciar el Web Server.
    - Iniciar en segundo plano.
    - Configurar el puerto del Web Server a 8085.
    '''

    ruta_configuracion = os.path.join(os.getcwd(), 'librehardwaremonitor', 'LibreHardwareMonitor.config')

    try:
        tree = ET.parse(ruta_configuracion)
        root = tree.getroot()

        # Se itera sobre los ajustes de configuración que están en el XML, ahora convertidos a un objeto de tipo ElementTree.
        for ajuste in root.findall('.//add'):
            # Iniciar el Web Server.
            if ajuste.attrib.get('key') == 'runWebServerMenuItem':
                ajuste.set('value', 'true')
            # Iniciar en segundo plano.
            if ajuste.attrib.get('key') == 'startMinMenuItem':
                ajuste.set('value', 'true')
            # Configurar el puerto del Web Server a 8085.
            if ajuste.attrib.get('key') == 'listenerPort':
                ajuste.set('value', '8085')

        tree.write(ruta_configuracion)
        print(f'{datetime.now()} >>> *** Libre Hardware Monitor configurado correctamente ***')
    except Exception as error:
        print(f'{datetime.now()} >>> *** Error al configurar Libre Hardware Monitor ***')
        print(error)

iniciar_libre_hardware_monitor()
