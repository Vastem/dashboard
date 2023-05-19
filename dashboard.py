import customtkinter
import requests
import time
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import pytz
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("System")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("dark-blue")


class App(customtkinter.CTk):
    data = []
    ejecutar = True
    password = "ea"
    estado_actual = "DESOCUPADO"

    def get_data(self):
        self.data.clear()
        self.textbox.delete(1.0, customtkinter.END)
        response = requests.get(
            'https://lock-system-production.up.railway.app/datos')
        if response.status_code == 200:
            datos_obtenidos = response.json()
            for i, registro in enumerate(datos_obtenidos):
                estado = registro["estado"]
                fecha_utc = datetime.datetime.utcfromtimestamp(
                    registro["fecha"])
                self.data.append(
                    {"id": i+1, "estado": estado, "fecha": fecha_utc})
            self.set_grafica_dia(datetime.datetime.now())
        else:
            print("Error al obtener los datos:", response.status_code)
        self.textbox.insert(customtkinter.END, text=self.data)

    def __init__(self):
        super().__init__()
        # configure window
        self.title("Inicio")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # Establecer las dimensiones de la ventana
        width = 1300
        height = 760
        # Calcular las coordenadas del centro de la pantalla
        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)

        self.geometry(f'{width}x{height}+{x}+{y}')
        self.resizable(False, False)

        # configure grid layout (4x4)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(
            self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Dashboard", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.btn_grafico_all = customtkinter.CTkButton(
            self.sidebar_frame, command=self.set_grafica, text="Gráfico cambio de estados")
        self.btn_grafico_all.grid(
            row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.btn_grafico_dia = customtkinter.CTkButton(
            self.sidebar_frame, command=self.filtrar_dia_evt, text="Gráfico de barrar p/día")
        self.btn_grafico_dia.grid(
            row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.btn_grafico_intervalo = customtkinter.CTkButton(
            self.sidebar_frame, command=self.grafica_intervalo, text="Gráfico de intervalos")
        self.btn_grafico_intervalo.grid(
            row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.btn_grafico_pstl = customtkinter.CTkButton(
            self.sidebar_frame, command=self.set_grafica_pastel, text="Gráfico circular")
        self.btn_grafico_pstl.grid(
            row=4, column=0, padx=20, pady=10, sticky="nsew")

        self.label_pass = customtkinter.CTkLabel(
            self.sidebar_frame, text=f'Contrasena actual: {self.password}', font=customtkinter.CTkFont(size=14, weight="bold"))
        self.label_pass.grid(row=6, column=0, pady=(10, 0), sticky="nsew")

        self.btn_password = customtkinter.CTkButton(
            self.sidebar_frame, command=self.set_contrasena_evt, text="Cambiar contrasena acceso")
        self.btn_password.grid(row=7, column=0, padx=20,
                               pady=(0, 10), sticky="nsew")

        self.label_state = customtkinter.CTkLabel(
            self.sidebar_frame, text="Estado: ", font=customtkinter.CTkFont(size=14, weight="bold"))
        self.label_state.grid(row=8, column=0, pady=(10, 0), sticky="nsew")

        self.estados_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=[
            "DESOCUPADO", "OCUPADO"], command=self.update_state)
        self.estados_menu.grid(
            row=9, column=0, padx=20, pady=(0, 30), sticky="nsew")

        # create textbox (Frame)
        self.frameImage = customtkinter.CTkFrame(self, width=250)
        self.frameImage.grid(row=0, column=1, padx=(
            20, 0), pady=(20, 0), sticky="nsew")

        # create right view
        self.rightView = customtkinter.CTkFrame(
            self, width=140, corner_radius=0)
        self.rightView.grid(row=0, column=2, padx=(20, 0),
                            pady=(0, 0), sticky="nsew")
        self.rightView.grid_rowconfigure(8, weight=2)
        self.rightView.grid_columnconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(self.rightView, width=10, text="Datos recopilados de hoy: ",
                                            anchor="w", font=customtkinter.CTkFont(size=14, weight="bold"))
        self.label.grid(row=0, column=0, padx=20, pady=(20, 0))

        self.txtPersonas = customtkinter.CTkLabel(
            self.rightView, width=10, text=f'2 veces ocupado', anchor="w", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.txtPersonas.grid(row=1, column=0, padx=20, pady=(10, 0))

        self.entrando = customtkinter.CTkLabel(self.rightView, width=10, text="Gente que entro estando ocupado: ",
                                               anchor="w", font=customtkinter.CTkFont(size=14, weight="bold"))
        self.entrando.grid(row=2, column=0, padx=20, pady=(30, 0))

        self.txt_entrando = customtkinter.CTkLabel(
            self.rightView, width=10, text=f'', anchor="w", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.txt_entrando.grid(row=3, column=0, padx=20, pady=(10, 0))

        # create textbox
        self.textbox = customtkinter.CTkTextbox(
            self.rightView, corner_radius=10, width=350, height=250)
        self.textbox.grid(row=6, column=0, padx=(0, 0), pady=(80, 0))

        self.btn_get = customtkinter.CTkButton(self.rightView, text="Recopilar datos", font=customtkinter.CTkFont(
            size=14, weight="normal"), command=self.get_data)
        self.btn_get.grid(row=7, column=0, padx=(0, 0), pady=(28, 0))

        self.hora = customtkinter.CTkLabel(
            self.rightView, font=customtkinter.CTkFont(size=22, weight="bold"))
        self.hora.grid(row=9, column=0, padx=20, pady=(20, 10))

        self.get_data()

        self.intervalo_ocupado()
        self.contar_ocupado()
        self.contar_entrando()
        self.show_time()
        self.protocol("WM_DELETE_WINDOW", self.close_window)

    def close_window(self):
        # Realizar limpieza y cerrar la ventana principal
        self.ejecutar = False
        self.destroy()

    def set_estado_actual(self):
        response = requests.get(f'http://192.168.0.3/estado')
        print()

    def set_contrasena_actual(self):
        print()

    def show_time(self):
        self.time = time.strftime("%H:%M:%S")
        self.date = time.strftime('%Y/%m/%d')
        set_text = f"  {self.time} \n {self.date}"
        self.hora.configure(text=set_text, font=("", 22, "bold"))
        self.hora.after(100, self.show_time)

    def set_grafica_dia(self, fecha_seleccionada):
        if self.ejecutar:
            for widget in self.frameImage.winfo_children():
                widget.destroy()

            # Convertir los datos en un DataFrame de Pandas
            df = pd.DataFrame(self.data)
            # Obtener la zona horaria local
            timezone = pytz.timezone('America/Hermosillo')

            # Convertir las fechas en el DataFrame a la zona horaria local
            df['fecha'] = pd.to_datetime(df['fecha'], unit='s').dt.tz_localize(
                'UTC').dt.tz_convert(timezone)

            # Filtrar el DataFrame por la fecha seleccionada en la zona horaria local
            df_filtrado = df[df['fecha'].dt.date == fecha_seleccionada.date()]

            print(df_filtrado)
            # Verificar si hay datos disponibles
            if df_filtrado.empty:
                fig = plt.Figure()

                # Agregar un objeto Text a la figura
                texto = "No hay datos en este día"
                fig.text(0.5, 0.5, texto, ha='center',
                         va='center', fontsize=12)

                # Crear el lienzo de la figura con TkAgg
                canvas = FigureCanvasTkAgg(fig, master=self.frameImage)
                canvas.draw()
                canvas.get_tk_widget().pack(side="left", padx=20, pady=20)
            else:
                cuenta_ocupado = df_filtrado[df_filtrado['estado']
                                             == 'OCUPADO'].shape[0]
                cuenta_desocupado = df_filtrado[df_filtrado['estado']
                                                == 'DESOCUPADO'].shape[0]

                # Crear gráfico de barras
                fig, ax = plt.subplots()

                estados = ['OCUPADO', 'DESOCUPADO']
                cantidades = [cuenta_ocupado, cuenta_desocupado]

                ax.bar(estados, cantidades)

                ax.set_title(f'Estado por día ({fecha_seleccionada})')
                ax.set_xlabel('Estado')
                ax.set_ylabel('Cantidad')

                # Crear objeto FigureCanvasTkAgg
                canvas = FigureCanvasTkAgg(fig, master=self.frameImage)
                canvas.draw()
                canvas.get_tk_widget().pack(side="left", padx=20, pady=20)

    def set_grafica(self):
        if self.ejecutar:
            for widget in self.frameImage.winfo_children():
                widget.destroy()

            # Convertir los datos en un DataFrame de Pandas
            df = pd.DataFrame(self.data)

            # Obtener la zona horaria local de Sonora, México
            timezone = pytz.timezone('America/Hermosillo')

            # Convertir las fechas en el DataFrame a la zona horaria local
            df['fecha'] = pd.to_datetime(df['fecha'], unit='s').dt.tz_localize(
                'UTC').dt.tz_convert(timezone)

            print(df)

            # Contar la cantidad de veces que ocurrió cada estado por día
            cuenta_estados = df.groupby(
                [df['fecha'].dt.date, 'estado']).size().unstack()

            # Verificar si faltan estados y llenar con ceros
            cuenta_estados = cuenta_estados.fillna(0)

            # Calcular el total de ocurrencias por día
            cuenta_estados['total'] = cuenta_estados.sum(axis=1)

            # Calcular el porcentaje de tiempo en cada estado por día
            cuenta_estados['porcentaje_ocupado'] = cuenta_estados['OCUPADO'] / \
                cuenta_estados['total']
            cuenta_estados['porcentaje_desocupado'] = cuenta_estados['DESOCUPADO'] / \
                cuenta_estados['total']

            # Crear gráfico de línea con área sombreada
            fig, ax = plt.subplots()

            ax.plot(cuenta_estados.index,
                    cuenta_estados['porcentaje_ocupado'], label='OCUPADO')
            ax.plot(cuenta_estados.index,
                    cuenta_estados['porcentaje_desocupado'], label='DESOCUPADO')

            ax.fill_between(cuenta_estados.index, cuenta_estados['porcentaje_ocupado'], cuenta_estados['porcentaje_desocupado'],
                            where=cuenta_estados['porcentaje_ocupado'] >= cuenta_estados['porcentaje_desocupado'],
                            facecolor='green', alpha=0.3)
            ax.fill_between(cuenta_estados.index, cuenta_estados['porcentaje_ocupado'], cuenta_estados['porcentaje_desocupado'],
                            where=cuenta_estados['porcentaje_ocupado'] < cuenta_estados['porcentaje_desocupado'],
                            facecolor='red', alpha=0.3)

            ax.set_title('Cambio de estado a lo largo del tiempo')
            ax.set_xlabel('Fecha')
            ax.set_ylabel('Porcentaje')
            ax.legend()

            # Rotar las etiquetas del eje x para mejorar la legibilidad
            plt.xticks(rotation=45, ha='right')

            # Crear objeto FigureCanvasTkAgg
            canvas = FigureCanvasTkAgg(fig, master=self.frameImage)
            canvas.draw()
            canvas.get_tk_widget().pack(side="left", padx=20, pady=20)

    def intervalo_ocupado(self):
        df = pd.DataFrame(self.data)

        # Convertir la columna 'fecha' en tipo datetime
        df['fecha'] = pd.to_datetime(df['fecha'], unit='s')

        # Obtener la zona horaria local de Sonora, México
        timezone = pytz.timezone('America/Hermosillo')

        # Convertir las fechas en el DataFrame a la zona horaria local
        df['fecha'] = df['fecha'].dt.tz_localize('UTC').dt.tz_convert(timezone)

        # Filtrar los datos por estado 'OCUPADO'
        df_ocupado = df[df['estado'] == 'OCUPADO'].copy()

        # Calcular la duración de cada intervalo 'OCUPADO'
        df_ocupado['duracion'] = df_ocupado['fecha'].diff()

        # Eliminar el primer registro ya que no hay un intervalo previo
        df_ocupado = df_ocupado.dropna()

        # Mostrar los resultados
        print(df_ocupado[['fecha', 'duracion']])

    def grafica_intervalo(self):
        for widget in self.frameImage.winfo_children():
            widget.destroy()
        # Convertir los datos en un DataFrame de Pandas
        df = pd.DataFrame(self.data)

        # Obtener la zona horaria local de Sonora, México
        timezone = pytz.timezone('America/Hermosillo')

        # Convertir las fechas en el DataFrame a la zona horaria local
        df['fecha'] = df['fecha'].dt.tz_localize('UTC').dt.tz_convert(timezone)

        # Calcular la duración de cada intervalo 'OCUPADO'
        df_ocupado = df[df['estado'] == 'OCUPADO'].copy()
        df_ocupado['duracion'] = df_ocupado['fecha'].diff()
        df_ocupado = df_ocupado.dropna()

        # Crear gráfico de línea
        fig, ax = plt.subplots()
        ax.plot(df_ocupado['fecha'],
                df_ocupado['duracion'].dt.total_seconds(), marker='o')

        ax.set_title('Duración de los intervalos "OCUPADO"')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Duración (segundos)')

        plt.xticks(rotation=45)
        plt.tight_layout()
        # Crear objeto FigureCanvasTkAgg
        canvas = FigureCanvasTkAgg(fig, master=self.frameImage)
        canvas.draw()
        canvas.get_tk_widget().pack(side="left", padx=20, pady=20)

    def set_grafica_pastel(self):
        if self.ejecutar:
            # Convertir los datos en un DataFrame de Pandas
            df = pd.DataFrame(self.data)

            for widget in self.frameImage.winfo_children():
                widget.destroy()

            # Calcular la cantidad de elementos por categoría
            cuenta_por_categoria = df['estado'].value_counts()

            # Crear gráfico de pastel
            fig, ax = plt.subplots()
            ax.pie(cuenta_por_categoria,
                   labels=cuenta_por_categoria.index, autopct='%1.1f%%')
            ax.set_title('Distribución por Categoría')

            # Mostrar leyenda
            ax.legend()

            # Crear objeto FigureCanvasTkAgg
            canvas = FigureCanvasTkAgg(fig, master=self.frameImage)
            canvas.draw()
            canvas.get_tk_widget().pack(side="left", padx=20, pady=20)

    def contar_ocupado(self):
        # Convertir los datos en un DataFrame de Pandas
        df = pd.DataFrame(self.data)

        # Obtener la zona horaria local de Sonora, México
        timezone = pytz.timezone('America/Hermosillo')

        # Convertir las fechas en el DataFrame a la zona horaria local
        df['fecha'] = pd.to_datetime(df['fecha']).dt.tz_localize(
            'UTC').dt.tz_convert(timezone)

        # Filtrar los registros de 'OCUPADO' en la fecha actual
        fecha_seleccionada = pd.to_datetime(
            datetime.datetime.now()).tz_localize(timezone).normalize()
        df_ocupado = df[(df['estado'] == 'OCUPADO') & (
            df['fecha'].dt.date == fecha_seleccionada.date())]

        # Obtener el contador de registros
        contador = len(df_ocupado)

        set_text = f"{contador} veces ocupado hoy"
        print(contador)
        self.txtPersonas.configure(text=set_text)

    def contar_entrando(self):
        # Convertir los datos en un DataFrame de Pandas
        df = pd.DataFrame(self.data)

        # Obtener la zona horaria local de Sonora, México
        timezone = pytz.timezone('America/Hermosillo')

        # Convertir las fechas en el DataFrame a la zona horaria local
        df['fecha'] = pd.to_datetime(df['fecha']).dt.tz_localize(
            'UTC').dt.tz_convert(timezone)

        # Filtrar los registros de 'OCUPADO' y 'ENTRANDING' en la fecha actual
        fecha_seleccionada = pd.to_datetime(
            datetime.datetime.now()).tz_localize(timezone).normalize()
        df_ocupado = df[(df['estado'].isin(['OCUPADO', 'ENTRANDING'])) & (
            df['fecha'].dt.date == fecha_seleccionada.date())]

        # Obtener el contador de registros
        contador = len(df_ocupado)

        set_text = f"{contador} persona(s)"
        print(contador)
        self.txt_entrando.configure(text=set_text)

    def filtrar_dia_evt(self):
        dialog = customtkinter.CTkInputDialog(
            title="Filtrar por dia", text="Ingresar fecha (DD/MM/AAAA)")
        window_width = dialog.winfo_reqwidth()
        window_height = dialog.winfo_reqheight()
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        dialog.geometry(f"+{x}+{y}")

        try:
            fecha = datetime.datetime.strptime(dialog.get_input(), "%d/%m/%Y")
            self.set_grafica_dia(fecha)
        except Exception as e:
            print(e)

    def set_contrasena_evt(self):
        dialog = customtkinter.CTkInputDialog(
            title="Cambiar contrasena", text="Ingresar nueva contrasena:")
        window_width = dialog.winfo_reqwidth()
        window_height = dialog.winfo_reqheight()
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        dialog.geometry(f"+{x}+{y}")
        """ response = requests.get(
            f'http://192.168.0.3/contrasena?{dialog.get_input()}')
        if response.status_code == 200:
            self.label_pass.configure(
                text=f'Contrasena actual: {dialog.get_input()}') """

    def update_state(self, estado):
        # response = requests.get(
        #   f'http://192.168.0.3/estado?{estado}')
        print()


if __name__ == "__main__":
    app = App()
    app.mainloop()
