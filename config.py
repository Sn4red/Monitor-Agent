import json

from pathlib import Path
from datetime import datetime

class Config:
    '''Clase para gestionar la configuración de Monitor Agent.'''

    def __init__(self):
        self.parametros = self.__cargar_configuracion()

    def __cargar_configuracion(self):
        '''Carga la configuración desde el archivo JSON.'''
        ruta_configuracion = Path('config.json')

        if ruta_configuracion.exists():
            try:
                contenido = ruta_configuracion.read_text(encoding='utf-8')
                parametros = json.loads(contenido)

                return parametros
            except json.JSONDecodeError as error:
                print(
                    f'{datetime.now()} >> *** Error de formato en config.json '
                    '***'
                )
                print(error)
        else:
            print(
                f'{datetime.now()} >> *** Error. Archivo de configuración '
                'config.json no encontrado ***'
            )

        return {}
