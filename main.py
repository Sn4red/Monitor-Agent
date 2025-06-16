import subprocess
import os
import psutil
import sys
import time

# * Configuración.
import config

# * Métricas
import metrics.cpu as cpu
import metrics.storage as storage

import xml.etree.ElementTree as ET

from datetime import datetime

def esta_libre_hardware_monitor_activo():
    '''
    Verifica si Libre Hardware Monitor ya está en ejecución, y si es una
    instancia externa al proyecto.
    '''
    # * Se obtiene la ruta relativa del ejecutable, y se convierte a ruta
    # * absoluta para compararla con la ruta del ejecutable en ejecución.
    ruta_local = os.path.abspath(
        os.path.join(
            'externals/librehardwaremonitor', 'LibreHardwareMonitor.exe'
        )
    )

    esta_activo = False
    hay_instancias_externas = []

    # * Se itera sobre los procesos en ejecución.
    for proceso in psutil.process_iter(['name', 'exe']):
        try:
            # * Se verifica si el nombre del proceso es
            # * 'LibreHardwareMonitor.exe'.
            if proceso.info['name'] == 'LibreHardwareMonitor.exe':
                esta_activo = True

                ruta_ejecucion = os.path.abspath(proceso.info['exe'])

                # * Se compara la ruta del ejecutable en ejecución con la ruta
                # * del ejecutable local. Si son diferentes, se agrega True al
                # * list.
                if ruta_ejecucion != ruta_local:
                    hay_instancias_externas.append(True)
                else:
                    hay_instancias_externas.append(False)
        except psutil.AccessDenied as error:
            print(
                f'{datetime.now()} >>> *** Error. No se tienen permisos '
                'suficientes para verificar si Libre Hardware Monitor está '
                'activo ***'
            )
            print(
                f'{datetime.now()} >>> *** La ejecución del agente se '
                'finalizará. Verificar privilegios ***'
            )
            print(error)

            # * Si se tienen permisos insuficientes para verificar el proceso,
            # * se finaliza el agente.
            sys.exit(1)
        except Exception as error:
            print(
                f'{datetime.now()} >>> *** Error al verificar si Libre '
                'Hardware Monitor está activo ***'
            )
            print(error)

            esta_activo = False
            hay_instancias_externas.append(False)

    return {
        'esta_activo': esta_activo,
        'hay_instancias_externas': hay_instancias_externas
    }

def configurar_libre_hardware_monitor():
    '''
    Configura Libre Hardware Monitor para que se inicie con los siguientes
    ajustes:

    - Iniciar el Web Server.
    - Iniciar en segundo plano.
    - Configurar el puerto del Web Server a 8085.
    '''
    # * Se obtiene el directorio de trabajo actual como una ruta absoluta para
    # * buscar el archivo de configuración.
    ruta_configuracion = os.path.join(
        os.getcwd(), 'externals/librehardwaremonitor',
        'LibreHardwareMonitor.config'
    )

    try:
        tree = ET.parse(ruta_configuracion)
        root = tree.getroot()

        # * Se itera sobre los ajustes de configuración que están en el XML,
        # * ahora convertidos a un objeto de tipo ElementTree.
        for ajuste in root.findall('.//add'):
            # * Iniciar el Web Server.
            if ajuste.attrib.get('key') == 'runWebServerMenuItem':
                ajuste.set('value', 'true')
            # * Iniciar en segundo plano.
            if ajuste.attrib.get('key') == 'startMinMenuItem':
                ajuste.set('value', 'true')
            # * Configurar el puerto del Web Server a 8085.
            if ajuste.attrib.get('key') == 'listenerPort':
                ajuste.set('value', '8085')

        # * Se sobreescribe el archivo de configuración con los nuevos ajustes.
        tree.write(ruta_configuracion)
        print(
            f'{datetime.now()} >>> *** Libre Hardware Monitor configurado '
            'correctamente ***'
        )
    except Exception as error:
        print(
            f'{datetime.now()} >>> *** Error al configurar Libre Hardware '
            'Monitor ***'
        )
        print(error)

def iniciar_libre_hardware_monitor():
    '''
    Inicia Libre Hardware Monitor con privilegios de administrador.
    '''
    # * Se obtiene la ruta relativa del ejecutable, y se convierte a ruta
    # * absoluta para mayor claridad en la depuración.
    ruta = os.path.abspath(
        os.path.join(
            'externals/librehardwaremonitor', 'LibreHardwareMonitor.exe'
        )
    )

    try:
        inspeccion_instancia = esta_libre_hardware_monitor_activo()

        # * Se verifica si Libre Hardware Monitor ya está en ejecución. Si ya
        # * lo está, no se vuelve a iniciar.
        if inspeccion_instancia['esta_activo']:
            print(
                f'{datetime.now()} >>> *** Libre Hardware Monitor ya está en '
                'ejecución ***'
            )

            # * Si la instancia ejecutada es externa al proyecto, verificando
            # * si hay un valor True en el list, se notifica al usuario.
            if True in inspeccion_instancia['hay_instancias_externas']:
                print(
                    f'{datetime.now()} >>> *** Libre Hardware Monitor está en '
                    'ejecución como una instancia externa al proyecto ***'
                )
                print(
                    f'{datetime.now()} >>> *** Se recomienda cerrar la '
                    'instancia externa para evitar conflictos ***'
                )
        else:
            # * Se ejecuta el comando de PowerShell para iniciar Libre Hardware
            # * Monitor con privilegios de administrador.
            subprocess.run(
                ['powershell', 'Start-Process', ruta, '-Verb', 'runAs'],
                check=True
            )
            print(
                f'{datetime.now()} >>> *** Libre Hardware Monitor iniciado '
                'correctamente ***'
            )

            # * Se configura Libre Hardware Monitor para que se inicie con los
            # * ajustes deseados.
            configurar_libre_hardware_monitor()
    except Exception as error:
        print(
            f'{datetime.now()} >>> *** Error al iniciar Libre Hardware '
            'Monitor ***'
        )
        print(error)

        # * Si no se puede iniciar Libre Hardware Monitor, se finaliza el
        # * agente.
        sys.exit(1)

def ejecutar_smartmontools(almacenamiento):
    '''
    Ejecuta Smartmontools para obtener las métricas del almacenamiento.
    '''
    try:
        # * Se obtiene la ruta relativa del ejecutable, y se convierte a ruta
        # * absoluta para mayor claridad en la depuración.
        ruta = os.path.abspath(
            os.path.join(
                'externals/smartctl', 'smartctl.exe'
            )
        )

        comando = [ruta, '-A', almacenamiento, '--device=auto']
        resultado = subprocess.run(
            comando, capture_output=True, text=True, check=True
        )

        return resultado.stdout
    except Exception as error:
        print(
            f'{datetime.now()} >>> *** Error al ejecutar Smartmontools ***'
        )
        print(error)

        # * Si no se puede ejecutar Smartmontools, se finaliza el agente.
        sys.exit(1)

def obtener_alertas_cpu(uso_cpu, temperatura_cpu, temperatura_paquete_cpu,
                        umbrales_uso, umbrales_temperatura,
                        umbrales_temperatura_paquete):
    '''
    Muestra las alertas de la CPU según los umbrales definidos en la
    configuración.
    '''
    # * Alerta para el uso de CPU alto.
    if uso_cpu >= umbrales_uso:
        print(f'\nAlerta: uso de CPU alto - {uso_cpu[1]}%')

    # * Alerta para la temperatura de CPU alta.
    if temperatura_cpu >= umbrales_temperatura:
        print(f'\nAlerta: temperatura de CPU alta - {temperatura_cpu[1]}°C')

    # * Alerta para la temperatura de paquete de CPU alta.
    if temperatura_paquete_cpu >= umbrales_temperatura_paquete:
        print(
            '\nAlerta: temperatura de paquete de CPU alta - '
            f'{temperatura_cpu[2]}°C'
        )

def obtener_metricas_cpu(sistema_operativo, umbrales_uso, umbrales_temperatura,
                         umbrales_temperatura_paquete):
    '''
    Obtiene las métricas de la CPU.
    '''
    cpu_metrics = cpu.Cpu()

    print(f'\n{datetime.now()} >>> *** Métricas de la CPU ***\n')

    # * Se obtiene el uso general de la CPU.
    uso_cpu = cpu_metrics.obtener_uso_cpu()

    print(f'Uso CPU General: {uso_cpu[1]}%\n')

    # * Se obtiene el uso de cada núcleo de la CPU.
    for nucleo, uso in enumerate(uso_cpu[0]):
        print(f'Uso CPU Núcleo {nucleo}: {uso}%')

    # * Se obtienen los núcleos físicos y lógicos de la CPU.
    print(f'\nNúcleos físicos: {cpu_metrics.obtener_nucleos_fisicos()}')
    print(f'Núcleos lógicos: {cpu_metrics.obtener_nucleos_logicos()}')

    # * Se obtiene la temperatura de la CPU.
    if sistema_operativo == 'nt':
        temperatura_cpu = cpu_metrics.obtener_temperatura_cpu_windows()
    if sistema_operativo == 'posix':
        temperatura_cpu = cpu_metrics.obtener_temperatura_cpu_linux()

    print(f'\nTemperatura CPU General: {temperatura_cpu[1]}°C\n')

    # * Se obtiene la temperatura de cada núcleo de la CPU.
    for nucleo, temperatura in enumerate(temperatura_cpu[0]):
        print(f'Temperatura CPU Núcleo {nucleo}: {temperatura}°C')

    # * Se obtiene la temperatura del paquete de la CPU.
    print(f'\nTemperatura Paquete CPU: {temperatura_cpu[2]}°C')

    obtener_alertas_cpu(
        uso_cpu[1], temperatura_cpu[1], temperatura_cpu[2], umbrales_uso,
        umbrales_temperatura, umbrales_temperatura_paquete
    )

def obtener_metricas_storage(sistema_operativo):
    '''
    Obtiene las métricas del almacenamiento.
    '''
    storage_metrics = storage.Storage()

    print(f'\n{datetime.now()} >>> *** Métricas del Almacenamiento ***\n')

    if sistema_operativo == 'nt':
        # * Se obtiene la información del almacenamiento en Windows.
        almacenamiento = storage_metrics.obtener_almacenamiento_windows()
    if sistema_operativo == 'posix':
        pass

    for modelo, particion, sistema_archivos in zip(*almacenamiento):
        print(f'Modelo: {modelo}')
        print(f'Partición: {particion}')
        print(f'Sistema de Archivos: {sistema_archivos}')

        resultado_smartctl = ejecutar_smartmontools(particion)

        # * Se obtienen las horas de encendido del disco en Windows.
        horas_encendido = (
            storage_metrics.obtener_horas_encendido(resultado_smartctl)
        )

        print(f'Horas de Encendido: {horas_encendido}')

        # * Se obtiene el total de datos leídos y escritos del disco en
        # * Windows.
        datos_leidos_escritos = (
            storage_metrics.obtener_datos_leidos_escritos(resultado_smartctl)
        )

        print(f'Total Leído (bytes): {datos_leidos_escritos[0]}')
        print(f'Total Escrito (bytes): {datos_leidos_escritos[1]}')

        # * Se obtiene la temperatura del disco en Windows.
        temperatura_disco = (
            storage_metrics.obtener_temperatura(resultado_smartctl)
        )

        print(f'Temperatura: {temperatura_disco}°C')

        # * Se obtiene el uso por disco en Windows.
        uso_particion = storage_metrics.obtener_uso_particion(particion)

        print(f'Espacio total (bytes): {uso_particion[0]}')
        print(f'Espacio usado (bytes): {uso_particion[1]}')
        print(f'Espacio libre (bytes): {uso_particion[2]}')
        print(f'Porcentaje usado: {uso_particion[3]}%\n')

def main():
    '''
    Punto de entrada del programa.
    '''
    sistema_operativo = os.name
    print(f'{datetime.now()} >>> *** Sistema Operativo: {sys.platform} ***')

    # * Se verifica el operating system que está ejecutando el agente. Si es
    # * Windows, se inicia Libre Hardware Monitor.
    if sistema_operativo == 'nt':
        iniciar_libre_hardware_monitor()

    # * El agente se ejecuta indefinidamente.
    while True:
        # * Se cargan los parámetros de configuración, comenzando por el
        # * intervalo de tiempo entre cada iteración. En el caso de la métrica
        # * del uso de la CPU, este demora 5 segundos, por lo que el mínimo
        # * valor del intervalo debe ser 5 segundos.
        configuracion = config.Config().parametros
        intervalo = configuracion.get('intervalo')

        configuracion_metricas_cpu = configuracion.get('metricas').get('cpu')
        configuracion_metricas_storage = (
            configuracion.get('metricas').get('storage')
        )

        umbrales_cpu_uso = (
            configuracion.get('umbrales').get('cpu').get('uso')
        )
        umbrales_cpu_temperatura = (
            configuracion.get('umbrales').get('cpu').get('temperatura')
        )
        umbrales_cpu_temperatura_paquete = (
            configuracion.get('umbrales').get('cpu').get('temperatura_paquete')
        )

        # * Si está definido en la configuración, se obtienen las métricas de
        # * la CPU.
        if configuracion_metricas_cpu:
            # * Se descuentan 5 segundos al intervalo para compensar el tiempo
            # * que demora la métrica del uso de la CPU.
            intervalo -= 5

            obtener_metricas_cpu(
                sistema_operativo, umbrales_cpu_uso, umbrales_cpu_temperatura,
                umbrales_cpu_temperatura_paquete
            )

        # * Si está definido en la configuración, se obtienen las métricas del
        # * almacenamiento.
        if configuracion_metricas_storage:
            obtener_metricas_storage(sistema_operativo)

        time.sleep(intervalo)

if __name__ == '__main__':
    main()
