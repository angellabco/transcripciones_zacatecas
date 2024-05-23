# Herramienta de Transcripción de Audio

## Descripción

Esta es una aplicación de escritorio desarrollada en Python que permite transcribir archivos de audio utilizando el modelo de transcripción Whisper de OpenAI. La interfaz gráfica está construida con PyQt5 y permite cargar archivos de audio, transcribirlos y guardar las transcripciones en archivos Word.

## Requisitos

- Python 3.9 o superior
- `PyQt5` para la interfaz gráfica
- `openai-whisper` de OpenAI para la transcripción
- `python-docx` para la manipulación de archivos Word
- `pydub` para el procesamiento de audio
- `moviepy` para la manipulación de archivos de video
- `ffmpeg` para la manipulación de archivos multimedia

## Instalación

1. **Clonar el repositorio**

    ```sh
    git clone https://github.com/angellabco/transcripciones_zacatecas
    cd transcripciones_zacatecas
    ```

2. **Crear y activar un entorno virtual**

    ```sh
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3. **Instalar las dependencias**

    ```sh
    pip install -r requirements.txt
    ```

4. **Instalar `ffmpeg`**

    - **En Windows**:
        - Descarga `ffmpeg` desde [FFmpeg Releases](https://ffmpeg.org/download.html).
        - Extrae los archivos y agrega la carpeta `bin` de `ffmpeg` al `PATH` del sistema.
        - Usando Chocolatey (https://chocolatey.org/):
          ```sh
          choco install ffmpeg
          ```
        - Usando Scoop (https://scoop.sh/):
          ```sh
          scoop install ffmpeg
          ```

    - **En macOS**:
        ```sh
        brew install ffmpeg
        ```

    - **En Ubuntu/Debian**:
        ```sh
        sudo apt update
        sudo apt install ffmpeg
        ```

## Uso

1. **Ejecutar la aplicación**

    ```sh
    python gui_app.py
    ```

    Asegúrate de que el archivo principal se llama `gui_app.py`.

2. **Interfaz de usuario**

    - **Subir Archivos**: Haz clic en el botón "Subir Archivos" y selecciona los archivos de audio que deseas transcribir.
    - **Comenzar Transcripción**: Una vez cargados los archivos, haz clic en "Comenzar Transcripción" para iniciar el proceso.
    - **Descargar Transcripción**: Después de la transcripción, utiliza el botón "Descargar Transcripción" para guardar cada transcripción como un archivo Word.
    - **Limpiar**: El botón "Limpiar" restablece la aplicación, permitiéndote cargar nuevos archivos.

## Notas

- Asegúrate de tener una conexión a Internet activa cuando utilices por primera vez el modelo Whisper, ya que requerirá acceso a internet.
- El rendimiento de la transcripción puede variar según la longitud y calidad de los archivos de audio.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo `LICENSE` para obtener más información.
