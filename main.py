import subprocess
import os
import psutil
import sys
import time

# * Libre Hardware Monitor.
import utils.libre_hardware_monitor as lhm

# * Smartmontools.
import utils.smartmontools as smartmontools

# * Configuración.
import config

# * Métricas
import metrics.cpu as cpu
import metrics.storage as storage

import xml.etree.ElementTree as ET

from datetime import datetime

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
        almacenamiento = storage_metrics.obtener_almacenamiento_linux()

    instancia_smartmontools = smartmontools.Smartmontools()

    for disco in almacenamiento:
        print(f'Modelo: {disco['modelo']}')

        if sistema_operativo == 'nt':
            # * La primera partición en el tuple de particiones va a servir
            # * como partición representante del disco, y de esta manera de
            # * obtendrán las métricas del disco.
            particion_representante = disco['particiones'][0]['particion']

            resultado_smartctl = (
                instancia_smartmontools.ejecutar_smartmontools(
                    particion_representante
                )
            )

        if sistema_operativo == 'posix':
            # * En Linux, se obtiene el nombre del disco directamente del
            # * dictionary del disco, que se usará para obtener las métricas.
            nombre_disco = disco['nombre']

            resultado_smartctl = (
                instancia_smartmontools.ejecutar_smartmontools(nombre_disco)
            )

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

        print(f'Temperatura: {temperatura_disco}°C\n')

        for particion in disco['particiones']:
            print(f'Partición: {particion['particion']}')
            print(f'Sistema de Archivos: {particion['sistema_archivos']}')
            
            # * Se obtiene el uso por partición en Windows.
            uso_particion = (
                storage_metrics.obtener_uso_particion(particion['particion'])
            )

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
        instancia_lhm = lhm.LibreHardwareMonitor()
        instancia_lhm.iniciar_libre_hardware_monitor()

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
