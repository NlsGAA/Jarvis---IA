import whisper
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write, read
import os

SAMPLE_RATE = 16000
DURACAO = 5
ARQUIVO_AUDIO = "assets/temp/audios/temp_audio.wav"

def gravar_audio(duracao, sample_rate):
    """Grava áudio do microfone"""
    print(f"🎤 Gravando por {duracao} segundos... Fale agora!")
    audio = sd.rec(int(duracao * sample_rate),
                   samplerate=sample_rate,
                   channels=1,
                   dtype='int16')
    sd.wait()
    print("Gravação finalizada!")
    return audio

def salvar_audio(audio, arquivo, sample_rate):
    """Salva o áudio em arquivo WAV"""
    write(arquivo, sample_rate, audio)

def transcrever_audio(arquivo, modelo="base"):
    """Transcreve o áudio usando Whisper"""
    print("Transcrevendo...")
    model = whisper.load_model(modelo)

    sample_rate, audio = read(arquivo)

    audio = audio.astype(np.float32) / 32768.0


    if sample_rate != 16000:
        print(f"Sample rate é {sample_rate}, convertendo para 16000...")

    resultado = model.transcribe(audio, language="pt", fp16=False)
    return resultado["text"]

def main():
    audio = gravar_audio(DURACAO, SAMPLE_RATE)

    salvar_audio(audio, ARQUIVO_AUDIO, SAMPLE_RATE)

    # Modelos: tiny, base, small, medium, large
    transcricao = transcrever_audio(ARQUIVO_AUDIO, modelo="tiny")

    print("\nTranscrição:")
    print(transcricao)

    if os.path.exists(ARQUIVO_AUDIO):
        os.remove(ARQUIVO_AUDIO)

if __name__ == "__main__":
    main()