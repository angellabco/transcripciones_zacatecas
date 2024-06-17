import sys
import os
import asyncio
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QTextEdit, QFileDialog, QVBoxLayout, QWidget, QProgressBar, QHBoxLayout, QSlider, QProgressDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor, QIcon
from moviepy.editor import VideoFileClip
from pydub import AudioSegment, effects
import whisper
from docx import Document

def ms_to_time(ms):
    seconds = ms // 1000
    minutes = seconds // 60
    hours = minutes // 60
    return f"{hours:02}:{minutes % 60:02}:{seconds % 60:02}"

def ms_to_time_string(ms):
    seconds = ms // 1000
    minutes = seconds // 60
    hours = minutes // 60
    return f"{hours}h{minutes % 60}m{seconds % 60}s"

class TranscriptionWorker(QThread):
    transcription_complete = pyqtSignal(str)

    def __init__(self, model, audio_path):
        super().__init__()
        self.model = model
        self.audio_path = audio_path

    def run(self):
        result = self.model.transcribe(self.audio_path)
        transcription = result["text"]
        self.transcription_complete.emit(transcription)

class AudioExtractor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.model = whisper.load_model("medium")
        self.audio_path = ''
        self.cut_audio_path = ''
        self.loading_dialog = None
        self.worker = None

    def initUI(self):
        self.setWindowTitle('Herramienta de transcripción')
        self.setGeometry(100, 100, 1200, 900)

        # Configurar el icono de la ventana
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, 'logo_nuevo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Logo not found at {icon_path}")

        # Configurar el color de fondo
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#FAF9F6"))
        self.setPalette(palette)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Layout para el logo
        self.logo_layout = QHBoxLayout()
        self.layout.addLayout(self.logo_layout)

        # Configuración del logo
        self.logo_label = QLabel(self)
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            self.logo_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))
        else:
            self.logo_label.setText("Logo no encontrado")
        self.logo_layout.addWidget(self.logo_label, alignment=Qt.AlignLeft)

        # Etiqueta de instrucción
        self.label = QLabel('Carga tu archivo de video o audio', self)
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

        # Layout para los botones de carga de video y audio
        self.upload_layout = QHBoxLayout()
        self.layout.addLayout(self.upload_layout)

        # Botón para subir archivos de video
        self.upload_video_button = QPushButton('Subir Video', self)
        self.upload_video_button.setFont(QFont('Helvetica', 12))
        self.upload_video_button.setStyleSheet(button_style)
        self.upload_video_button.clicked.connect(self.load_video)
        self.upload_layout.addWidget(self.upload_video_button)

        # Botón para subir archivos de audio
        self.upload_audio_button = QPushButton('Subir Audio', self)
        self.upload_audio_button.setFont(QFont('Helvetica', 12))
        self.upload_audio_button.setStyleSheet(button_style)
        self.upload_audio_button.clicked.connect(self.load_audio)
        self.upload_layout.addWidget(self.upload_audio_button)

        # Botón para extraer audio del video
        self.extract_button = QPushButton('Extraer Audio del Video', self)
        self.extract_button.setFont(QFont('Helvetica', 12))
        self.extract_button.setStyleSheet(button_style)
        self.extract_button.clicked.connect(self.extract_audio)
        self.layout.addWidget(self.extract_button)
        self.extract_button.setEnabled(False)

        # Etiqueta para mostrar la ruta del archivo cargado
        self.file_label = QLabel('', self)
        self.file_label.setFont(QFont('Helvetica', 12))
        self.layout.addWidget(self.file_label)

        self.slider_layout = QVBoxLayout()

        self.start_slider_layout = QHBoxLayout()
        self.start_slider_label = QLabel('Inicio: 00:00:00')
        self.start_slider = QSlider(Qt.Horizontal)
        self.start_slider.setRange(0, 100)
        self.start_slider.setValue(0)
        self.start_slider.setTickInterval(1)
        self.start_slider.setTickPosition(QSlider.TicksBelow)
        self.start_slider.valueChanged.connect(self.update_start_label)
        self.start_slider_layout.addWidget(QLabel("Inicio"))
        self.start_slider_layout.addWidget(self.start_slider)
        self.start_slider_layout.addWidget(self.start_slider_label)

        self.end_slider_layout = QHBoxLayout()
        self.end_slider_label = QLabel('Fin: 00:00:00')
        self.end_slider = QSlider(Qt.Horizontal)
        self.end_slider.setRange(0, 100)
        self.end_slider.setValue(100)
        self.end_slider.setTickInterval(1)
        self.end_slider.setTickPosition(QSlider.TicksBelow)
        self.end_slider.valueChanged.connect(self.update_end_label)
        self.end_slider_layout.addWidget(QLabel("Fin"))
        self.end_slider_layout.addWidget(self.end_slider)
        self.end_slider_layout.addWidget(self.end_slider_label)

        self.layout.addLayout(self.start_slider_layout)
        self.layout.addLayout(self.end_slider_layout)

        self.cut_button = QPushButton('Cortar Audio')
        self.cut_button.setFont(QFont('Helvetica', 12))
        self.cut_button.setStyleSheet(button_style)
        self.cut_button.clicked.connect(self.cut_audio)
        self.layout.addWidget(self.cut_button)
        self.cut_button.setEnabled(False)

        self.transcribe_button = QPushButton('Transcribir Audio')
        self.transcribe_button.setFont(QFont('Helvetica', 12))
        self.transcribe_button.setStyleSheet(button_style)
        self.transcribe_button.clicked.connect(self.start_transcription)
        self.layout.addWidget(self.transcribe_button)
        self.transcribe_button.setEnabled(False)

        self.transcription_area = QTextEdit(self)
        self.transcription_area.setFont(QFont('Helvetica', 12))
        self.transcription_area.setReadOnly(True)
        self.transcription_area.setStyleSheet("border: 1px solid #6e6e6e; border-radius: 10px; padding: 10px 16px;")
        self.layout.addWidget(self.transcription_area)

        self.download_button = QPushButton('Descargar Transcripción', self)
        self.download_button.setFont(QFont('Helvetica', 12))
        self.download_button.setStyleSheet(button_style)
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self.download_transcription)
        self.layout.addWidget(self.download_button)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.layout.addWidget(self.progress_bar)

        self.clear_button = QPushButton('Limpiar', self)
        self.clear_button.setFont(QFont('Helvetica', 12))
        self.clear_button.setStyleSheet(button_style)
        self.clear_button.clicked.connect(self.clear_all)
        self.layout.addWidget(self.clear_button)

        self.video_path = ''
        self.audio_path = ''
        self.cut_audio_path = ''
        self.audio_duration = 0

    def load_video(self):
        self.video_path, _ = QFileDialog.getOpenFileName(self, 'Abrir Archivo de Video', '', 'Archivos de Video (*.mp4)')
        if self.video_path:
            self.label.setText(f'Video cargado: {self.video_path}')
            self.extract_button.setEnabled(True)
            self.cut_button.setEnabled(False)
            self.transcribe_button.setEnabled(False)

    def load_audio(self):
        self.audio_path, _ = QFileDialog.getOpenFileName(self, 'Abrir Archivo de Audio', '', 'Archivos de Audio (*.wav *.mp3 *.m4a)')
        if self.audio_path:
            self.label.setText(f'Audio cargado: {self.audio_path}')
            self.extract_button.setEnabled(False)
            self.cut_button.setEnabled(True)
            self.transcribe_button.setEnabled(True)
            self.audio_duration = int(AudioSegment.from_file(self.audio_path).duration_seconds * 1000)
            self.start_slider.setRange(0, self.audio_duration)
            self.end_slider.setRange(0, self.audio_duration)
            self.start_slider.setValue(0)
            self.end_slider.setValue(self.audio_duration)
            self.update_start_label(0)
            self.update_end_label(self.audio_duration)

    def extract_audio(self):
        if self.video_path:
            video = VideoFileClip(self.video_path)
            audio = video.audio
            self.audio_path = self.video_path.replace('.mp4', '.wav')
            audio.write_audiofile(self.audio_path, codec='pcm_s16le')  # Exportar con codec PCM para mejor calidad
            self.label.setText(f'Audio extraído a: {self.audio_path}')

            self.audio_duration = int(audio.duration * 1000)
            self.start_slider.setRange(0, self.audio_duration)
            self.end_slider.setRange(0, self.audio_duration)
            self.start_slider.setValue(0)
            self.end_slider.setValue(self.audio_duration)
            self.update_start_label(0)
            self.update_end_label(self.audio_duration)
            self.cut_button.setEnabled(True)
            self.transcribe_button.setEnabled(True)

    def update_start_label(self, value):
        self.start_slider_label.setText(f'Inicio: {ms_to_time(value)}')

    def update_end_label(self, value):
        self.end_slider_label.setText(f'Fin: {ms_to_time(value)}')

    def cut_audio(self):
        if self.audio_path:
            audio = AudioSegment.from_file(self.audio_path)

            start_time = self.start_slider.value()
            end_time = self.end_slider.value()

            if start_time < end_time:
                cut_audio = audio[start_time:end_time]
                cut_audio = effects.normalize(cut_audio)  # Normalizar el audio
                start_time_str = ms_to_time_string(start_time)
                end_time_str = ms_to_time_string(end_time)
                self.cut_audio_path = self.audio_path.replace('.wav', f'_corte_{start_time_str}_a_{end_time_str}.wav')
                cut_audio.export(self.cut_audio_path, format="wav")
                self.label.setText(f'Audio cortado y guardado en: {self.cut_audio_path}')
                self.transcribe_button.setEnabled(True)
            else:
                self.label.setText('El tiempo de fin debe ser mayor que el tiempo de inicio')

    def start_transcription(self):
        if self.cut_audio_path:
            audio_to_transcribe = self.cut_audio_path
        else:
            audio_to_transcribe = self.audio_path

        self.loading_dialog = QProgressDialog("Transcribiendo audio...", None, 0, 0, self)
        self.loading_dialog.setWindowTitle("Por favor, espera")
        self.loading_dialog.setWindowModality(Qt.ApplicationModal)
        self.loading_dialog.setMinimumDuration(0)
        self.loading_dialog.show()

        self.worker = TranscriptionWorker(self.model, audio_to_transcribe)
        self.worker.transcription_complete.connect(self.on_transcription_complete)
        self.worker.start()

    def on_transcription_complete(self, transcription):
        self.transcription = transcription
        self.transcription_area.setPlainText(transcription)
        self.download_button.setEnabled(True)
        self.progress_bar.setValue(100)
        self.transcribe_button.setText("Transcribir Audio")
        self.transcribe_button.setEnabled(True)
        if self.loading_dialog:
            self.loading_dialog.close()

    def download_transcription(self):
        if self.transcription:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Guardar Transcripción", "transcripcion.docx", "Archivos Word (*.docx)", options=options)
            if file_name:
                doc = Document()
                doc.add_paragraph(self.transcription)
                doc.save(file_name)

    def clear_all(self):
        self.video_path = ''
        self.audio_path = ''
        self.cut_audio_path = ''
        self.transcription = ''
        self.label.setText('Carga tu archivo de video o audio')
        self.file_label.setText('')
        self.transcription_area.clear()
        self.download_button.setEnabled(False)
        self.transcribe_button.setEnabled(False)
        self.cut_button.setEnabled(False)
        self.extract_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.start_slider.setValue(0)
        self.end_slider.setValue(100)
        self.update_start_label(0)
        self.update_end_label(0)

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        extractor = AudioExtractor()
        extractor.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred: {e}")
