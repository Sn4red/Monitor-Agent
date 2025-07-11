import tkinter as tk
import config
import threading

# * Smartmontools.
import utils.smartmontools as smartmontools

from tkinter import ttk
from datetime import datetime

class GUI(tk.Tk):
    def __init__(self, cpu_metrics, storage_metrics, sistema_operativo):
        super().__init__()
        self.title('Monitor Agent')
        self.geometry("800x900")
        self.cpu_metrics = cpu_metrics
        self.storage_metrics = storage_metrics
        self.sistema_operativo = sistema_operativo

        self.horas_encendido_var = {}
        self.disco_temperatura_var = {}
        self.particiones_text = {}
        self.disk_rw_var = {}

        # Scrollable frame
        container = ttk.Frame(self)
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        container.pack(fill="both", expand=True)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Sections
        self.create_cpu_section()
        self.create_storage_section(storage_metrics)
        self.create_log_section()

        self._actualizar_aplicacion()

    def create_cpu_section(self):
        cpu_frame = ttk.LabelFrame(self.scrollable_frame, text="CPU")
        cpu_frame.pack(fill="x", padx=10, pady=5)

        # Modelo
        ttk.Label(cpu_frame, text="Modelo:").grid(row=0, column=0, sticky="w")
        self.cpu_model_var = tk.StringVar(value="Desconocido")
        ttk.Label(cpu_frame, textvariable=self.cpu_model_var).grid(row=0, column=1, sticky="w")

        # Núcleos
        ttk.Label(cpu_frame, text="Núcleos físicos:").grid(row=1, column=0, sticky="w")
        self.cpu_physical_var = tk.StringVar(value="0")
        ttk.Label(cpu_frame, textvariable=self.cpu_physical_var).grid(row=1, column=1, sticky="w")

        ttk.Label(cpu_frame, text="Núcleos lógicos:").grid(row=2, column=0, sticky="w")
        self.cpu_logical_var = tk.StringVar(value="0")
        ttk.Label(cpu_frame, textvariable=self.cpu_logical_var).grid(row=2, column=1, sticky="w")

        # Uso total
        ttk.Label(cpu_frame, text="Uso total:").grid(row=3, column=0, sticky="w")
        self.cpu_total_usage_var = tk.StringVar(value="0%")
        ttk.Label(cpu_frame, textvariable=self.cpu_total_usage_var).grid(row=3, column=1, sticky="w")

        # Uso por núcleo (lista)
        ttk.Label(cpu_frame, text="Uso por núcleo:").grid(row=4, column=0, sticky="nw")
        self.cpu_core_usages_text = tk.Text(cpu_frame, height=5, width=50)
        self.cpu_core_usages_text.grid(row=4, column=1, sticky="w")

        # Temperatura total
        ttk.Label(cpu_frame, text="Temperatura General:").grid(row=5, column=0, sticky="w")
        self.cpu_temp_total_var = tk.StringVar(value="Desconocido")
        ttk.Label(cpu_frame, textvariable=self.cpu_temp_total_var).grid(row=5, column=1, sticky="w")

        # Temperatura de paquete
        ttk.Label(cpu_frame, text="Temperatura de paquete:").grid(row=6, column=0, sticky="w")
        self.cpu_temp_package_var = tk.StringVar(value="Desconocido")
        ttk.Label(cpu_frame, textvariable=self.cpu_temp_package_var).grid(row=6, column=1, sticky="w")

        # Temperaturas detalladas (por núcleo, etc.)
        ttk.Label(cpu_frame, text="Temperaturas por núcleo:").grid(row=7, column=0, sticky="nw")
        self.cpu_temp_text = tk.Text(cpu_frame, height=5, width=50)
        self.cpu_temp_text.grid(row=7, column=1, sticky="w")

    def create_storage_section(self, storage_metrics):
        storage_frame = ttk.LabelFrame(self.scrollable_frame, text="Almacenamiento")
        storage_frame.pack(fill="x", padx=10, pady=5)

        if self.sistema_operativo == 'nt':
            # * Se obtiene la información del almacenamiento en Windows.
            almacenamiento = storage_metrics.obtener_almacenamiento_windows()
        if self.sistema_operativo == 'posix':
            # * Se obtiene la información del almacenamiento en Linux.
            almacenamiento = storage_metrics.obtener_almacenamiento_linux()

        for i, disco in enumerate(almacenamiento):
            # Subframe para un disco
            disco_frame = ttk.LabelFrame(storage_frame, text=disco['modelo'])
            disco_frame.pack(fill="x", padx=5, pady=5)

            # Horas de encendido
            ttk.Label(disco_frame, text="Horas de encendido:").grid(row=1, column=0, sticky="w")
            self.horas_encendido_var[i] = tk.StringVar(value="Desconocido")
            ttk.Label(disco_frame, textvariable=self.horas_encendido_var[i]).grid(row=1, column=1, sticky="w")

            # Temperatura del disco
            ttk.Label(disco_frame, text="Temperatura del disco:").grid(row=2, column=0, sticky="w")
            self.disco_temperatura_var[i] = tk.StringVar(value="Desconocido")
            ttk.Label(disco_frame, textvariable=self.disco_temperatura_var[i]).grid(row=2, column=1, sticky="w")

            # Reads/Writes
            ttk.Label(disco_frame, text="Datos leídos/escritos:").grid(row=3, column=0, sticky="w")
            self.disk_rw_var[i] = tk.StringVar(value=disco['modelo'])
            ttk.Label(disco_frame, textvariable=self.disk_rw_var[i]).grid(row=3, column=1, sticky="w")

            # Particiones
            ttk.Label(disco_frame, text="Particiones:").grid(row=4, column=0, sticky="nw")
            self.particiones_text[i] = tk.Text(disco_frame, height=5, width=60)
            self.particiones_text[i].grid(row=4, column=1, sticky="w")

    def create_log_section(self):
        """Crea una sección con un área de texto grande para logs o información adicional"""
        log_frame = ttk.LabelFrame(self.scrollable_frame, text="Registro de Alertas")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Área de texto grande con scrollbar
        text_container = ttk.Frame(log_frame)
        text_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(text_container, height=8, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(text_container, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")

    def _actualizar_metricas(
        self,
        configuracion_metricas_cpu,
        configuracion_metricas_storage,
        umbrales_cpu_uso,
        umbrales_cpu_temperatura_paquete,
        umbrales_storage_temperatura,
        umbrales_storage_espacio_libre

    ):
        # * CPU.
        if configuracion_metricas_cpu:
            # * Se obtiene el modelo de la CPU.
            if self.cpu_metrics.modelo is None:
                self.cpu_metrics.obtener_modelo_cpu()

            self.cpu_model_var.set(self.cpu_metrics.modelo)

            # * Se obtienen los núcleos físicos y lógicos de la CPU.
            self.cpu_physical_var.set(f'{self.cpu_metrics.obtener_nucleos_fisicos()}')
            self.cpu_logical_var.set(f'{self.cpu_metrics.obtener_nucleos_logicos()}')

            # * Se obtiene el uso de la CPU en un hilo separado.
            def obtener_uso_cpu_async():
                uso_cpu = self.cpu_metrics.obtener_uso_cpu()
                self.after(0, lambda: self._actualizar_uso_cpu(uso_cpu, umbrales_cpu_uso))

            threading.Thread(target=obtener_uso_cpu_async, daemon=True).start()

            # * Se obtiene la temperatura de la CPU en Windows.
            if self.sistema_operativo == 'nt':
                temperatura_cpu = self.cpu_metrics.obtener_temperatura_cpu_windows(self.cpu_metrics.modelo)

                self.cpu_temp_total_var.set(f'{temperatura_cpu[1]}°C')
                self.cpu_temp_package_var.set(f'{temperatura_cpu[2]}°C')

                if self.cpu_metrics.modelo.startswith('Intel'):
                    self.cpu_temp_text.delete("1.0", "end")
                    for nucleo, temperatura in enumerate(temperatura_cpu[0]):
                        self.cpu_temp_text.insert("end", f"Núcleo {nucleo}: {temperatura} °C\n")

            # * Se obtiene la temperatura de la CPU en Linux.
            if self.sistema_operativo == 'posix':
                temperatura_cpu = self.cpu_metrics.obtener_temperatura_cpu_linux()

                self.cpu_temp_total_var.set(f'{temperatura_cpu[1]}°C')
                self.cpu_temp_package_var.set(f'{temperatura_cpu[2]}°C')

                self.cpu_temp_text.delete("1.0", "end")

                for nucleo, temperatura in enumerate(temperatura_cpu[0]):
                    self.cpu_temp_text.insert("end", f"Núcleo {nucleo}: {temperatura} °C\n")

            if temperatura_cpu[2] >= umbrales_cpu_temperatura_paquete:
                mensaje = f'[{datetime.now().strftime("%H:%M:%S")}] Alerta: Temperatura de CPU alta: {temperatura_cpu[2]}°C\n'
                self.log_text.insert("end", mensaje)
                self.log_text.see("end")

        # * Almacenamiento.
        if configuracion_metricas_storage:
            instancia_smartmontools = smartmontools.Smartmontools()

            if self.sistema_operativo == 'nt':
                # * Se obtiene la información del almacenamiento en Windows.
                almacenamiento = self.storage_metrics.obtener_almacenamiento_windows()
            if self.sistema_operativo == 'posix':
                # * Se obtiene la información del almacenamiento en Linux.
                almacenamiento = self.storage_metrics.obtener_almacenamiento_linux()
                
            for i, disco in enumerate(almacenamiento):
                if self.sistema_operativo == 'nt':
                    # * La primera partición en el tuple de particiones va a servir
                    # * como partición representante del disco, y de esta manera de
                    # * obtendrán las métricas del disco.
                    particion_representante = disco['particiones'][0]['particion']

                    resultado_smartctl = (
                        instancia_smartmontools.ejecutar_smartmontools(
                            particion_representante
                        )
                    )

                if self.sistema_operativo == 'posix':
                    # * En Linux, se obtiene el nombre del disco directamente del
                    # * dictionary del disco, que se usará para obtener las métricas.
                    disco_nombre = disco['nombre']

                    resultado_smartctl = (
                        instancia_smartmontools.ejecutar_smartmontools(disco_nombre)
                    )

                # * Se obtienen las horas de encendido del disco en Windows.
                disco_horas_encendido = (
                    self.storage_metrics.obtener_horas_encendido(resultado_smartctl)
                )

                # * Se obtiene el total de datos leídos y escritos del disco en
                # * Windows.
                datos_leidos_escritos = (
                    self.storage_metrics.obtener_datos_leidos_escritos(resultado_smartctl)
                )

                # * Se obtiene la temperatura del disco en Windows.
                temperatura_disco = (
                    self.storage_metrics.obtener_temperatura(resultado_smartctl)
                )

                self.horas_encendido_var[i].set(f'{disco_horas_encendido} horas')
                self.disco_temperatura_var[i].set(f'{temperatura_disco} °C')
                self.disk_rw_var[i].set(f'Reads {datos_leidos_escritos[0]} bytes, Writes {datos_leidos_escritos[1]} bytes')

                self.particiones_text[i].delete("1.0", "end")

                if temperatura_disco >= umbrales_storage_temperatura:
                    mensaje = f'[{datetime.now().strftime("%H:%M:%S")}] Alerta: Temperatura de disco {disco['modelo']}: {temperatura_disco} °C\n'
                    self.log_text.insert("end", mensaje)
                    self.log_text.see("end")

                for part in disco['particiones']:
                    self.particiones_text[i].insert('end', f'Partición: {part['particion']}\n')
                    self.particiones_text[i].insert('end', f'Sistema de Archivos: {part['sistema_archivos']}\n')

                    # * Se obtiene el uso por partición en Windows.
                    uso_particion = (
                        self.storage_metrics.obtener_uso_particion(part['particion'])
                    )

                    self.particiones_text[i].insert('end', f'Espacio total (bytes): {uso_particion[0]}\n')
                    self.particiones_text[i].insert('end', f'Espacio usado (bytes): {uso_particion[1]}\n')
                    self.particiones_text[i].insert('end', f'Espacio libre (bytes): {uso_particion[2]}\n')
                    self.particiones_text[i].insert('end', f'Porcentaje usado: {uso_particion[3]}%\n\n')

                    if uso_particion[2] <= umbrales_storage_espacio_libre:
                        mensaje = (
                            f'[{datetime.now().strftime("%H:%M:%S")}] Alerta: '
                            f'Espacio libre bajo en {part['particion']}: '
                            f'{uso_particion[2]} bytes\n'
                        )
                        self.log_text.insert("end", mensaje)
                        self.log_text.see("end")

    def _actualizar_uso_cpu(self, uso_cpu, umbral_cpu_uso):
        self.cpu_total_usage_var.set(f'{uso_cpu[1]}%')

        self.cpu_core_usages_text.delete("1.0", "end")

        for nucleo, uso in enumerate(uso_cpu[0]):
            self.cpu_core_usages_text.insert("end", f"Núcleo {nucleo}: {uso}%\n")

        if uso_cpu[1] >= umbral_cpu_uso:
            mensaje = f'[{datetime.now().strftime("%H:%M:%S")}] Alerta: Uso de CPU alto: {uso_cpu[1]}%\n'
            self.log_text.insert("end", mensaje)
            self.log_text.see("end")

    def _actualizar_aplicacion(self):
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

        umbrales_cpu_uso = configuracion.get('umbrales').get('cpu').get('uso')
        umbrales_cpu_temperatura_paquete = configuracion.get('umbrales').get('cpu').get('temperatura_paquete')
        umbrales_storage_temperatura = configuracion.get('umbrales').get('storage').get('temperatura')
        umbrales_storage_espacio_libre = configuracion.get('umbrales').get('storage').get('espacio_libre')

        self._actualizar_metricas(
            configuracion_metricas_cpu, configuracion_metricas_storage,
            umbrales_cpu_uso, umbrales_cpu_temperatura_paquete,
            umbrales_storage_temperatura, umbrales_storage_espacio_libre
        )

        self.after(intervalo, self._actualizar_aplicacion)
