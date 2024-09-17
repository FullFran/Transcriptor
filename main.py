from dotenv import load_dotenv
import os


load_dotenv()
api_key = os.getenv("API_KEY")
file_paths = "audio"

import wave
import groq

client = groq.Groq(api_key=api_key)

# Transcribimos el audio
def transcribir_audio_groq(file_path):
    with open(file_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3",
            response_format="json",
            language="es",
            temperature=0.0
        )
        return response.text

# Volcamos la transcripción al archivo log
def volcar_log(file_path, transcripcion):
    log_file = "log.txt"
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("Log de Transcripciones\n")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\nArchivo: {file_path}\n")
        f.write(f"{transcripcion}\n")

# Dividimos el audio en trozos de duración especificada en segundos si supera los 25MB
def dividir_audio(file_path, duracion_chunk_segundos):
    with wave.open(file_path, 'rb') as wav:
        frame_rate = wav.getframerate()
        n_frames = wav.getnframes()
        n_channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        total_segundos = n_frames / frame_rate
        
        num_chunks = int(total_segundos / duracion_chunk_segundos)
        chunk_frame_count = frame_rate * duracion_chunk_segundos
        
        output_dir = os.path.join(os.path.dirname(file_path), "chunks")
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        
        chunks_paths = []
        for i in range(num_chunks + 1):
            start_frame = i * chunk_frame_count
            # Calculamos cuántos frames leer para evitar leer más allá del final del archivo
            end_frame = min((i + 1) * chunk_frame_count, n_frames)
            wav.setpos(start_frame)
            chunk_data = wav.readframes(end_frame - start_frame)
            chunk_file_path = os.path.join(output_dir, f"{base_name}_part_{i}.wav")
            
            with wave.open(chunk_file_path, 'wb') as chunk_wav:
                chunk_wav.setnchannels(n_channels)
                chunk_wav.setsampwidth(sample_width)
                chunk_wav.setframerate(frame_rate)
                chunk_wav.writeframes(chunk_data)
            chunks_paths.append(chunk_file_path)
        
        return chunks_paths

# Flujo principal para procesar el archivo de audio
def procesar_archivo_audio(file_path, duracion_chunk_segundos=60):
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # Tamaño en MB
    transcripcion_completa = ""

    if file_size_mb > 25:
        print(f"El archivo {file_path} supera los 25MB. Dividiendo en trozos...")
        chunk_paths = dividir_audio(file_path, duracion_chunk_segundos)

        for chunk_path in chunk_paths:
            transcripcion = transcribir_audio_groq(chunk_path)
            transcripcion = transcripcion.replace(".", ".\n").replace("!", "!\n").replace("?", "?\n")
            transcripcion_completa += transcripcion

            os.remove(chunk_path)
    else:
        print(f"El archivo {file_path} es menor a 25MB. Transcribiendo directamente...")
        transcripcion_completa = transcribir_audio_groq(file_path)
        transcripcion_completa = transcripcion_completa.replace(".", ".\n").replace("!", "!\n").replace("?", "?\n")

    volcar_log(file_path, transcripcion_completa)



if __name__ == "__main__":
    file_paths = "G:\\Mi unidad\\PKM\\002 - Profesional\\002-1 Racks Academy\\Aula Triple A\\Audios"
    for file_name in os.listdir(file_paths):
        file_path = os.path.join(file_paths, file_name)
        procesar_archivo_audio(file_path)

    print("Proceso completado. Revisa el archivo log.txt.")
