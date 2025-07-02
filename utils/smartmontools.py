import subprocess
import os
import sys

from datetime import datetime

class Smartmontools:
    '''
    Clase para interactuar con Smartmontools.
    '''

    def ejecutar_smartmontools(self, almacenamiento):
        '''
        Ejecuta Smartmontools para obtener las métricas del almacenamiento.
        '''
        try:
            sistema_operativo = os.name

            if sistema_operativo != 'nt':
                # * Para Windows, se obtiene la ruta relativa del ejecutable, y
                # * se convierte a ruta absoluta para mayor claridad en la
                # * depuración.
                ruta = os.path.abspath(
                    os.path.join(
                        'externals/smartctl', 'smartctl.exe'
                    )
                )

                comando = [ruta, '-A', almacenamiento, '--device=auto']

            if sistema_operativo == 'nt':
                # * Para Linux, se asume que smartctl está
                # * instalado y se ejecuta directamente.
                comando = ['smartctl', '-A', almacenamiento, '--device=auto']

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
