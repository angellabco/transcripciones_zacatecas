import sys
import asyncio
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QTextEdit, QFileDialog, QVBoxLayout, QWidget, QProgressBar, QHBoxLayout
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QObject, QEventLoop
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor, QIcon
import whisper
from docx import Document

# Definición de una clase para las señales de transcripción
class TranscriptionSignals(QObject):
    transcription_complete = pyqtSignal(str, int)  # Señal que se emite cuando una transcripción se completa

# Clase que representa la tarea de transcripción
class TranscriptionTask(QObject):
    def __init__(self, model, audio_path, index, signals):
        super().__init__()
        self.model = model  # El modelo de transcripción Whisper
        self.audio_path = audio_path  # Ruta del archivo de audio a transcribir
        self.index = index  # Índice de la tarea
        self.signals = signals  # Señales para comunicar resultados

    async def transcribe_audio(self):
        try:
            result = self.model.transcribe(self.audio_path)  # Realizar la transcripción usando el modelo Whisper
            transcription = result["text"]  # Obtener el texto de la transcripción
            self.signals.transcription_complete.emit(transcription, self.index)  # Emitir señal indicando que la transcripción se completó
        except Exception as e:
            print(f"Error in transcription task {self.index}: {e}")

# Clase principal de la aplicación de transcripción de audio
class AudioTranscriptionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()  # Inicializar la interfaz de usuario
        self.signals = TranscriptionSignals()  # Crear señales de transcripción
        self.signals.transcription_complete.connect(self.on_transcription_complete)  # Conectar la señal a un slot
        self.model = whisper.load_model("medium")  # Cargar el modelo Whisper
        self.audio_paths = []  # Lista para almacenar las rutas de los archivos de audio
        self.transcriptions = []  # Lista para almacenar las transcripciones
        self.progress_bars = []  # Lista para almacenar las barras de progreso
        self.transcription_areas = []  # Lista para almacenar las áreas de texto de las transcripciones
        self.download_buttons = []  # Lista para almacenar los botones de descarga
        self.tasks = []  # Lista para almacenar las tareas de transcripción
        self.completed_tasks = 0  # Contador de tareas completadas

    # Configuración inicial de la interfaz de usuario
    def initUI(self):
        self.setWindowTitle('Herramienta de transcripción')  # Título de la ventana
        self.setGeometry(100, 100, 1200, 900)  # Dimensiones de la ventana

        # Configurar el icono de la ventana
        self.setWindowIcon(QIcon("C:/Users/AngelSerrano/Downloads/aplicacion_tribunal/logo_nuevo.png"))

        # Configurar el color de fondo
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#FAF9F6"))
        self.setPalette(palette)

        self.central_widget = QWidget()  # Widget central
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)  # Layout vertical principal

        # Layout para el logo
        self.logo_layout = QHBoxLayout()
        self.layout.addLayout(self.logo_layout)

        # Configuración del logo
        self.logo_label = QLabel(self)
        pixmap = QPixmap("C:/Users/AngelSerrano/Downloads/aplicacion_tribunal/logo_nuevo.png")
        self.logo_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))
        self.logo_layout.addWidget(self.logo_label, alignment=Qt.AlignLeft)

        # Etiqueta de instrucción
        self.label = QLabel('Carga tus archivos de audio', self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont('Helvetica', 14, QFont.Bold))
        self.layout.addWidget(self.label)

        # Estilo para los botones
        button_style = """
        QPushButton {
            background-color: #d3d3d3; 
            border: none; 
            border-radius: 10px; 
            padding: 10px 16px;
        }
        QPushButton:pressed {
            background-color: #c0c0c0;
        }
        """

        # Botón para subir archivos
        self.upload_button = QPushButton('Subir Archivos', self)
        self.upload_button.setFont(QFont('Helvetica', 12))
        self.upload_button.setStyleSheet(button_style)
        self.upload_button.clicked.connect(self.upload_files)
        self.layout.addWidget(self.upload_button)

        # Etiqueta para mostrar la cantidad de archivos cargados
        self.file_label = QLabel('', self)
        self.file_label.setFont(QFont('Helvetica', 12))
        self.layout.addWidget(self.file_label)

        # Botón para iniciar la transcripción
        self.transcribe_button = QPushButton('Comenzar Transcripción', self)
        self.transcribe_button.setFont(QFont('Helvetica', 12))
        self.transcribe_button.setStyleSheet(button_style)
        self.transcribe_button.clicked.connect(self.start_transcription)
        self.transcribe_button.setEnabled(False)  # Deshabilitado inicialmente
        self.layout.addWidget(self.transcribe_button)

        # Barra de progreso general
        self.overall_progress_bar = QProgressBar(self)
        self.overall_progress_bar.setRange(0, 100)
        self.layout.addWidget(self.overall_progress_bar)

        # Botón para limpiar la interfaz
        self.clear_button = QPushButton('Limpiar', self)
        self.clear_button.setFont(QFont('Helvetica', 14))
        self.clear_button.setStyleSheet(button_style)
        self.clear_button.clicked.connect(self.clear_all)
        self.layout.addWidget(self.clear_button)

    # Crear widgets para cada transcripción individual
    def create_transcription_widgets(self, index):
        # Barra de progreso individual
        progress_bar = QProgressBar(self)
        self.layout.addWidget(progress_bar)
        self.progress_bars.append(progress_bar)

        # Área de texto para mostrar la transcripción
        transcription_area = QTextEdit(self)
        transcription_area.setFont(QFont('Helvetica', 12))
        transcription_area.setReadOnly(True)
        transcription_area.setStyleSheet("border: 1px solid #6e6e6e; border-radius: 10px; padding: 10px 16px;")
        self.layout.addWidget(transcription_area)
        self.transcription_areas.append(transcription_area)

        # Botón para descargar la transcripción
        download_button = QPushButton(f'Descargar Transcripción {index + 1}', self)
        download_button.setFont(QFont('Helvetica', 12))
        download_button.setStyleSheet("""
        QPushButton {
            background-color: #d3d3d3; 
            border: none; 
            border-radius: 10px; 
            padding: 10px 16px;
        }
        QPushButton:pressed {
            background-color: #c0c0c0;
        }
        """)
        download_button.clicked.connect(self.get_download_function(index))
        download_button.setEnabled(False)  # Deshabilitado hasta que la transcripción esté lista
        self.layout.addWidget(download_button)
        self.download_buttons.append(download_button)

    # Función para obtener la función de descarga correspondiente a un índice
    def get_download_function(self, index):
        def download():
            try:
                self.download_transcription(index)
            except Exception as e:
                print(f"Error in download function {index}: {e}")
        return download

    # Subir archivos de audio
    def upload_files(self):
        try:
            options = QFileDialog.Options()
            file_names, _ = QFileDialog.getOpenFileNames(self, "Sube archivos de audio", "", "Audio Files (*.mp3 *.wav *.m4a)", options=options)
            if file_names:
                self.audio_paths = file_names  # Guardar rutas de archivos
                self.file_label.setText(f'{len(file_names)} archivos cargados')  # Mostrar cantidad de archivos cargados
                self.transcribe_button.setEnabled(True)  # Habilitar botón de transcripción

                # Limpiar widgets previos
                for progress_bar in self.progress_bars:
                    self.layout.removeWidget(progress_bar)
                    progress_bar.deleteLater()
                self.progress_bars.clear()

                for transcription_area in self.transcription_areas:
                    self.layout.removeWidget(transcription_area)
                    transcription_area.deleteLater()
                self.transcription_areas.clear()

                for download_button in self.download_buttons:
                    self.layout.removeWidget(download_button)
                    download_button.deleteLater()
                self.download_buttons.clear()

                self.transcriptions = [None] * len(file_names)  # Inicializar lista de transcripciones

                # Crear nuevos widgets para cada archivo
                for i in range(len(file_names)):
                    self.create_transcription_widgets(i)
        except Exception as e:
            print(f"Error in upload_files: {e}")

    # Iniciar transcripción de los archivos subidos
    def start_transcription(self):
        self.tasks = []  # Lista de tareas de transcripción
        self.completed_tasks = 0  # Reiniciar contador de tareas completadas
        loop = asyncio.new_event_loop()  # Crear un nuevo bucle de eventos
        asyncio.set_event_loop(loop)
        self.transcribe_button.setEnabled(False)  # Deshabilitar botón de transcripción mientras se ejecuta
        self.transcribe_button.setText("Transcripción en curso...")

        # Crear y agregar tareas de transcripción
        for i, audio_path in enumerate(self.audio_paths):
            self.progress_bars[i].setVisible(True)
            self.progress_bars[i].setRange(0, 0)  # Barra de progreso indeterminada
            task = TranscriptionTask(self.model, audio_path, i, self.signals)
            self.tasks.append(task.transcribe_audio())
        
        # Ejecutar las tareas de transcripción
        loop.run_until_complete(asyncio.gather(*self.tasks))
        loop.close()
        self.transcribe_button.setEnabled(True)  # Rehabilitar botón de transcripción
        self.transcribe_button.setText("Comenzar Transcripción")

    # Slot para manejar la señal de transcripción completa
    def on_transcription_complete(self, transcription, index):
        try:
            self.transcriptions[index] = transcription  # Guardar transcripción
            self.transcription_areas[index].setPlainText(transcription)  # Mostrar transcripción
            self.download_buttons[index].setEnabled(True)  # Habilitar botón de descarga
            self.progress_bars[index].setVisible(False)  # Ocultar barra de progreso

            self.completed_tasks += 1  # Incrementar contador de tareas completadas
            total_tasks = len(self.audio_paths)
            progress_percentage = int((self.completed_tasks / total_tasks) * 100)  # Calcular progreso general
            self.overall_progress_bar.setValue(progress_percentage)  # Actualizar barra de progreso general

            if self.completed_tasks == total_tasks:
                self.label.setText("Todas las transcripciones completadas")  # Mensaje cuando todas las transcripciones estén completas
        except Exception as e:
            print(f"Error in on_transcription_complete {index}: {e}")

    # Descargar transcripción
    def download_transcription(self, index):
        try:
            if self.transcriptions[index]:
                options = QFileDialog.Options()
                file_name, _ = QFileDialog.getSaveFileName(self, f"Guardar Transcripción {index + 1}", f"transcription_{index + 1}.docx", "Word Files (*.docx)", options=options)
                if file_name:
                    doc = Document()
                    doc.add_paragraph(self.transcriptions[index])  # Agregar transcripción al documento
                    doc.save(file_name)  # Guardar documento
        except Exception as e:
            print(f"Error in download_transcription {index}: {e}")

    # Limpiar todos los datos y widgets
    def clear_all(self):
        self.audio_paths = []  # Limpiar lista de rutas de archivos de audio
        self.transcriptions = []  # Limpiar lista de transcripciones
        self.file_label.setText('')  # Limpiar etiqueta de archivos cargados
        self.transcribe_button.setEnabled(False)  # Deshabilitar botón de transcripción

        # Eliminar barras de progreso
        for progress_bar in self.progress_bars:
            self.layout.removeWidget(progress_bar)
            progress_bar.deleteLater()
        self.progress_bars.clear()

        # Eliminar áreas de transcripción
        for transcription_area in self.transcription_areas:
            self.layout.removeWidget(transcription_area)
            transcription_area.deleteLater()
        self.transcription_areas.clear()

        # Eliminar botones de descarga
        for download_button in self.download_buttons:
            self.layout.removeWidget(download_button)
            download_button.deleteLater()
        self.download_buttons.clear()

        self.overall_progress_bar.setValue(0)  # Reiniciar barra de progreso general
        self.label.setText('Carga tus archivos de audio')  # Restablecer etiqueta de instrucción

# Código principal para ejecutar la aplicación
if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)  # Crear aplicación PyQt
        ex = AudioTrnscriptionApp()  # Crear instancia de la aplicación de transcripción
        ex.show()  # Mostrar la interfaz de usuario
        sys.exit(app.exec_())  # Ejecutar el bucle de eventos de la aplicación
    except Exception as e:
        print(f"An error occurred: {e}")
