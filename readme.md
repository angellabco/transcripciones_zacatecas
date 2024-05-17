# Herramienta de Transcripción de Audio

## Descripción

Esta es una aplicación de escritorio desarrollada en Python que permite transcribir archivos de audio utilizando el modelo de transcripción Whisper de OpenAI. La interfaz gráfica está construida con PyQt5 y permite cargar archivos de audio, transcribirlos y guardar las transcripciones en archivos Word.

## Requisitos

- Python 3.7 o superior
- `PyQt5` para la interfaz gráfica
- `whisper` de OpenAI para la transcripción
- `python-docx` para la manipulación de archivos Word
- `ffmpeg` para la manipulación de archivos multimedia

## Instalación

1. **Clonar el repositorio**

    ```sh
    git clone https://github.com/tuusuario/nombre_del_repositorio.git
    cd nombre_del_repositorio
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

    Asegúrate de que `requirements.txt` contenga las siguientes líneas:

    ```plaintext
    PyQt5
    openai-whisper
    python-docx
    ```

4. **Instalar `ffmpeg`**

    - **En Windows**:
        - Descarga `ffmpeg` desde [FFmpeg Releases](https://ffmpeg.org/download.html).
        - Extrae los archivos y agrega la carpeta `bin` de `ffmpeg` al `PATH` del sistema.

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
    python main.py
    ```

    Asegúrate de que el archivo principal se llama `main.py`.

2. **Interfaz de usuario**

    - **Subir Archivos**: Haz clic en el botón "Subir Archivos" y selecciona los archivos de audio que deseas transcribir.
    - **Comenzar Transcripción**: Una vez cargados los archivos, haz clic en "Comenzar Transcripción" para iniciar el proceso.
    - **Descargar Transcripción**: Después de la transcripción, utiliza el botón "Descargar Transcripción" para guardar cada transcripción como un archivo Word.
    - **Limpiar**: El botón "Limpiar" restablece la aplicación, permitiéndote cargar nuevos archivos.

## Notas

- Asegúrate de tener una conexión a Internet activa cuando utilices el modelo Whisper, ya que puede requerir acceso a recursos en línea.
- El rendimiento de la transcripción puede variar según la longitud y calidad de los archivos de audio.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, sigue los pasos a continuación para contribuir:

1. **Fork** el repositorio.
2. **Crea** una rama para tu característica (`git checkout -b feature/nueva-caracteristica`).
3. **Commit** tus cambios (`git commit -am 'Agrega nueva característica'`).
4. **Push** a la rama (`git push origin feature/nueva-caracteristica`).
5. **Abre** un Pull Request.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo `LICENSE` para obtener más información.
