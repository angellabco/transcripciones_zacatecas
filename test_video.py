import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget, QLabel, QSlider, QHBoxLayout
from PyQt5.QtCore import Qt
from moviepy.editor import VideoFileClip
from pydub import AudioSegment

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

class AudioExtractor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Audio Extractor')
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        
        self.load_button = QPushButton('Load Video')
        self.load_button.clicked.connect(self.load_video)
        self.layout.addWidget(self.load_button)
        
        self.extract_button = QPushButton('Extract Audio')
        self.extract_button.clicked.connect(self.extract_audio)
        self.layout.addWidget(self.extract_button)
        
        self.label = QLabel('')
        self.layout.addWidget(self.label)
        
        self.slider_layout = QVBoxLayout()
        
        self.start_slider_layout = QHBoxLayout()
        self.start_slider_label = QLabel('Start: 00:00:00')
        self.start_slider = QSlider(Qt.Horizontal)
        self.start_slider.setRange(0, 100)
        self.start_slider.setValue(0)
        self.start_slider.setTickInterval(1)
        self.start_slider.setTickPosition(QSlider.TicksBelow)
        self.start_slider.valueChanged.connect(self.update_start_label)
        self.start_slider_layout.addWidget(QLabel("Start"))
        self.start_slider_layout.addWidget(self.start_slider)
        self.start_slider_layout.addWidget(self.start_slider_label)
        
        self.end_slider_layout = QHBoxLayout()
        self.end_slider_label = QLabel('End: 00:00:00')
        self.end_slider = QSlider(Qt.Horizontal)
        self.end_slider.setRange(0, 100)
        self.end_slider.setValue(100)
        self.end_slider.setTickInterval(1)
        self.end_slider.setTickPosition(QSlider.TicksBelow)
        self.end_slider.valueChanged.connect(self.update_end_label)
        self.end_slider_layout.addWidget(QLabel("End"))
        self.end_slider_layout.addWidget(self.end_slider)
        self.end_slider_layout.addWidget(self.end_slider_label)
        
        self.layout.addLayout(self.start_slider_layout)
        self.layout.addLayout(self.end_slider_layout)
        
        self.cut_button = QPushButton('Cut Audio')
        self.cut_button.clicked.connect(self.cut_audio)
        self.layout.addWidget(self.cut_button)
        
        self.central_widget.setLayout(self.layout)
        
        self.video_path = ''
        self.audio_path = ''
        self.audio_duration = 0
    
    def load_video(self):
        self.video_path, _ = QFileDialog.getOpenFileName(self, 'Open Video File', '', 'Video Files (*.mp4)')
        if self.video_path:
            self.label.setText(f'Loaded video: {self.video_path}')
    
    def extract_audio(self):
        if self.video_path:
            video = VideoFileClip(self.video_path)
            audio = video.audio
            self.audio_path = self.video_path.replace('.mp4', '.wav')
            audio.write_audiofile(self.audio_path)
            self.label.setText(f'Audio extracted to: {self.audio_path}')
            
            # Set sliders according to audio duration
            self.audio_duration = int(audio.duration * 1000)  # duration in milliseconds as integer
            self.start_slider.setRange(0, self.audio_duration)
            self.end_slider.setRange(0, self.audio_duration)
            self.start_slider.setValue(0)
            self.end_slider.setValue(self.audio_duration)
            self.update_start_label(0)
            self.update_end_label(self.audio_duration)
    
    def update_start_label(self, value):
        self.start_slider_label.setText(f'Start: {ms_to_time(value)}')
    
    def update_end_label(self, value):
        self.end_slider_label.setText(f'End: {ms_to_time(value)}')
    
    def cut_audio(self):
        if self.audio_path:
            audio = AudioSegment.from_wav(self.audio_path)
            
            start_time = self.start_slider.value()
            end_time = self.end_slider.value()
            
            if start_time < end_time:  # Ensure the end time is greater than the start time
                cut_audio = audio[start_time:end_time]
                start_time_str = ms_to_time_string(start_time)
                end_time_str = ms_to_time_string(end_time)
                cut_audio_path = self.audio_path.replace('.wav', f'_cut_{start_time_str}_to_{end_time_str}.wav')
                cut_audio.export(cut_audio_path, format="wav")
                self.label.setText(f'Audio cut and saved to: {cut_audio_path}')
            else:
                self.label.setText('End time must be greater than start time')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    extractor = AudioExtractor()
    extractor.show()
    sys.exit(app.exec_())
