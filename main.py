import os
import wave
from dotenv import load_dotenv
import groq

# Cargar las variables de entorno
load_dotenv()
api_key = os.getenv("API_KEY")

# Verificar que la API Key esté configurada
if not api_key:
    raise ValueError("API_KEY no encontrada en el entorno. Verifica tu archivo .env.")

# Inicializar cliente Groq
client = groq.Groq(api_key=api_key)

# Directorio donde están los audios
AUDIO_DIR = "audio"
LOG_FILE = "log.txt"
CHUNK_DIR = os.path.join(AUDIO_DIR, "chunks")

# Crear directorio de chunks si no existe
os.makedirs(CHUNK_DIR, exist_ok=True)


def transcribir_audio_groq(file_path):
    """Transcribe un archivo de audio usando Groq Whisper."""
    try:
        with open(file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                response_format="json",
                language="es",
                temperature=0.0
            )
        return response.text
    except Exception as e:
        print(f"Error en la transcripción de {file_path}: {e}")
        return ""


def volcar_log(file_path, transcripcion):
    """Guarda la transcripción en el log."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\nArchivo: {file_path}\n")
            f.write(f"{transcripcion}\n")
        print(f"Transcripción guardada en {LOG_FILE}.")
    except Exception as e:
        print(f"Error al escribir en el log: {e}")


def dividir_audio(file_path, duracion_chunk_segundos=60):
    """Divide un archivo de audio en segmentos si es mayor a 25MB."""
    try:
        with wave.open(file_path, 'rb') as wav:
            frame_rate = wav.getframerate()
            n_frames = wav.getnframes()
            n_channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            total_segundos = n_frames / frame_rate
            
            num_chunks = int(total_segundos / duracion_chunk_segundos)
            chunk_frame_count = frame_rate * duracion_chunk_segundos
            
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            chunk_paths = []
            
            for i in range(num_chunks + 1):
                start_frame = i * chunk_frame_count
                end_frame = min((i + 1) * chunk_frame_count, n_frames)

                wav.setpos(start_frame)
                chunk_data = wav.readframes(end_frame - start_frame)
                
                chunk_file_path = os.path.join(CHUNK_DIR, f"{base_name}_part_{i}.wav")
                with wave.open(chunk_file_path, 'wb') as chunk_wav:
                    chunk_wav.setnchannels(n_channels)
                    chunk_wav.setsampwidth(sample_width)
                    chunk_wav.setframerate(frame_rate)
                    chunk_wav.writeframes(chunk_data)
                
                chunk_paths.append(chunk_file_path)

            return chunk_paths
    except Exception as e:
        print(f"Error al dividir el audio {file_path}: {e}")
        return []


def procesar_archivo_audio(file_path, duracion_chunk_segundos=60):
    """Procesa un archivo de audio, dividiéndolo si es necesario y transcribiéndolo."""
    try:
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # Convertir a MB
        transcripcion_completa = ""

        if file_size_mb > 25:
            print(f"El archivo {file_path} supera los 25MB. Dividiendo en trozos...")
            chunk_paths = dividir_audio(file_path, duracion_chunk_segundos)

            for chunk_path in chunk_paths:
                transcripcion = transcribir_audio_groq(chunk_path)
                transcripcion_completa += transcripcion.replace(".", ".\n").replace("!", "!\n").replace("?", "?\n")
                os.remove(chunk_path)  # Borrar chunk tras procesarlo
        else:
            print(f"Transcribiendo directamente {file_path}...")
            transcripcion_completa = transcribir_audio_groq(file_path)
            transcripcion_completa = transcripcion_completa.replace(".", ".\n").replace("!", "!\n").replace("?", "?\n")

        volcar_log(file_path, transcripcion_completa)
    except Exception as e:
        print(f"Error al procesar {file_path}: {e}")


def main():
    """Función principal para procesar todos los archivos de audio en el directorio."""
    try:
        audio_files = [
            os.path.join(AUDIO_DIR, f) for f in os.listdir(AUDIO_DIR)
            if os.path.isfile(os.path.join(AUDIO_DIR, f)) and f.lower().endswith((".wav", ".mp3", ".ogg"))
        ]

        if not audio_files:
            print("No se encontraron archivos de audio en la carpeta.")
            return

        for file_path in audio_files:
            procesar_archivo_audio(file_path)

        print("Proceso completado. Revisa el archivo log.txt.")
    except Exception as e:
        print(f"Error en la ejecución principal: {e}")


if __name__ == "__main__":
    main()

