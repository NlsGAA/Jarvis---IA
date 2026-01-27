import re
import whisper
import edge_tts
import numpy as np
from scipy.io.wavfile import read

class SpeechConverter:
    # Aumenta 20% a velocidade (pode ajustar: +10%, +30%, etc)
    voice_speed = "+20%"

    # pt-BR-AntonioNeural - male
    # pt-BR-FranciscaNeural - female
    # pt-BR-ThalitaNeural - female
    voice_sample = "pt-BR-AntonioNeural"

    @staticmethod
    def transcribe_audio(audio_recorded="temp_audio.wav", modelo="base"):
        """Transcreve o áudio usando Whisper"""
        print("🔄 Transcrevendo...")
        model = whisper.load_model(modelo)

        sample_rate, audio = read(audio_recorded)
        audio = audio.astype(np.float32) / 32768.0

        resultado = model.transcribe(audio, language="pt", fp16=False)
        return resultado["text"]

    @staticmethod
    def limpar_texto_para_fala(texto):
        """Remove emojis, markdown e outros caracteres que não devem ser falados"""

        texto = re.sub(r'[😀-🙏🌀-🗿🚀-🛿🇀-🇿✀-➿]+', '', texto)
        texto = re.sub(r'\*+', '', texto)
        texto = re.sub(r'_+', '', texto)
        texto = re.sub(r'#+', '', texto)
        texto = re.sub(r'https?://\S+', '', texto)
        texto = re.sub(r'\[\s*\]|\(\s*\)', '', texto)
        texto = re.sub(r'\s+', ' ', texto)
        texto = re.sub(r'\n+', '. ', texto)

        return texto.strip()

    @staticmethod
    async def text_to_speech(texto, arquivo_saida):
        """Converte texto em áudio usando Edge TTS"""
        print(f"🔊 Gerando áudio da resposta... Na pasta {arquivo_saida}")

        texto_limpo = SpeechConverter.limpar_texto_para_fala(texto)

        communicate = edge_tts.Communicate(
            texto_limpo,
            SpeechConverter.voice_sample,
            rate=SpeechConverter.voice_speed
        )

        await communicate.save(arquivo_saida)