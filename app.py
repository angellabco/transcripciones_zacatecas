import streamlit as st
import whisper
from io import BytesIO

# Cargar el modelo de Whisper
model = whisper.load_model("medium")

# Título de la aplicación
st.title("Transcripción de Audio con Whisper")

# Carga de archivo de audio
uploaded_file = st.file_uploader("Sube un archivo de audio", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    # Guardar el archivo de audio en memoria
    audio_bytes = uploaded_file.read()
    
    # Crear un archivo temporal para que Whisper lo procese
    with open("temp_audio.mp3", "wb") as f:
        f.write(audio_bytes)

    # Transcribir el audio
    st.write("Transcribiendo el audio, por favor espera...")
    result = model.transcribe("temp_audio.mp3")

    # Mostrar la transcripción
    transcription = result["text"]
    st.text_area("Transcripción", transcription, height=200)

    # Descargar la transcripción como archivo de texto
    st.download_button(
        label="Descargar Transcripción",
        data=transcription,
        file_name="transcription.txt",
        mime="text/plain"
    )
