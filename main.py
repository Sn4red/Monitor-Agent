import os
import sys

# * Libre Hardware Monitor.
import utils.libre_hardware_monitor as lhm

# * Configuración.
import config

# * Métricas
import metrics.cpu as cpu
import metrics.storage as storage

# * GUI.
import utils.gui as gui

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

    cpu_metrics = cpu.Cpu()
    storage_metrics = storage.Storage()

    aplicacion = gui.GUI(cpu_metrics, storage_metrics, sistema_operativo)
    aplicacion.mainloop()

if __name__ == '__main__':
    main()
