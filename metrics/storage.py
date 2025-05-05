import psutil

class Storage:
    '''Clase para obtener las métricas del storage.'''

    def obtener_particiones(self):
        '''
        Devuelve las particiones del storage, donde el primer elemento es un tuple conteniendo
        el dispositivo de cada particion, el segundo elemento
        '''
        particiones = psutil.disk_partitions()

        dispositivo = []
        punto_montaje = []
        tipo_sistema_archivos = []

        for particion in particiones:
            dispositivo.append(particion.device)
            punto_montaje.append(particion.mountpoint)
            tipo_sistema_archivos.append(particion.fstype)

        dispositivo = tuple(dispositivo)
        punto_montaje = tuple(punto_montaje)
        tipo_sistema_archivos = tuple(tipo_sistema_archivos)

        particiones = (dispositivo, punto_montaje, tipo_sistema_archivos)

        return particiones
    
    def obtener_uso_particion(self, particion):
        '''
        Devuelve el uso de cada partición del storage en un tuple, donde el primer elemento es el total,
        el segundo elemento es el espacio usado, el tercero elemento es el espacio libre y el cuarto
        elemento es el porcentaje de uso.
        '''
        uso_storage = psutil.disk_usage(particion)
        uso_storage = (uso_storage.total, uso_storage.used, uso_storage.free, uso_storage.percent)

        return uso_storage
    
    def obtener_uso_storage_io(self):
        '''
        Devuelve el uso de I/O por disco en un tuple, donde el primer elemento es un tuple conteniendo
        el número de bytes leídos por cada disco y el segundo elemento es un tuple conteniendo el número
        de bytes escritos por cada disco.
        '''
        uso_storage_io = psutil.disk_io_counters(perdisk=True)

        lectura = []
        escritura = []

        for _, uso in uso_storage_io.items():
            lectura.append(uso.read_bytes)
            escritura.append(uso.write_bytes)
        
        lectura = tuple(lectura)
        escritura = tuple(escritura)

        io = (lectura, escritura)

        return io
