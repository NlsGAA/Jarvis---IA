import os
import asyncio
from playsound import playsound
from bot.assistant import Assistant
from audio.audio_processor import AudioProcessor
from speech_converter.speech_converter import SpeechConverter

RESPONSE_FILE = "resposta_audio.mp3"

def reproduzir_audio(arquivo):
    """Reproduz o arquivo de áudio"""
    print("▶️ Reproduzindo resposta...")
    playsound(arquivo)
    print("✅ Reprodução finalizada!")

def main():
    audio_recorded = AudioProcessor.record_audio()

    if audio_recorded is None:
        print("Nenhum audio detectado, encerrando...")
        return

    AudioProcessor.store_audio(audio_recorded)

    transcribed_audio = SpeechConverter.transcribe_audio()
    print(f"\n📝 Você disse: {transcribed_audio}")

    response = Assistant.talk(transcribed_audio)
    print(f"\n🤖 IA respondeu:\n{response}\n")

    # Converte resposta em áudio
    asyncio.run(SpeechConverter.text_to_speech(response, RESPONSE_FILE))

    # Reproduz o áudio
    reproduzir_audio(RESPONSE_FILE)

    # Limpa arquivos temporários
    if os.path.exists("temp_audio.wav"):
        os.remove("temp_audio.wav")
    if os.path.exists(RESPONSE_FILE):
        os.remove(RESPONSE_FILE)

if __name__ == "__main__":
    main()