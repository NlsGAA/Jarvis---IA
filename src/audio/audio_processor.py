import time
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

class AudioProcessor:
    duraction = 5
    sample_rate = 16000
    temp_file = "temp_audio.wav"

    SILENCIO_LIMITE = 2.0 # Segundos de silêncio para parar
    MIC_SENSIBILITY = 300  # Ajuste se necessário (200-1000)
    CHUNK_DURATION = 0.1  # Duração de cada chunk em segundos

    @staticmethod
    def store_audio(recorded_audio):
        """Salva o áudio em arquivo WAV"""
        write(AudioProcessor.temp_file, AudioProcessor.sample_rate, recorded_audio)

    def record_audio():
        """Grava áudio continuamente até detectar silêncio prolongado"""
        print("🎤 Pode falar! (a gravação para automaticamente quando você parar)")
        print("⏸️  Aguardando você começar a falar...\n")

        frames = []
        silencio_tempo = 0
        esta_falando = False
        ultimo_som = time.time()
        chunk_size = int(AudioProcessor.sample_rate * AudioProcessor.CHUNK_DURATION)

        def calcular_energia(audio_chunk):
            """Calcula a energia (volume) do chunk de áudio"""
            return np.abs(audio_chunk).mean()

        try:
            with sd.InputStream(samplerate=AudioProcessor.sample_rate,
                            channels=1,
                            dtype='int16',
                            blocksize=chunk_size) as stream:

                print("🎧 Sistema de áudio iniciado...")

                while True:
                    # Lê um chunk de áudio
                    audio_chunk, overflowed = stream.read(chunk_size)

                    # Calcula energia do chunk
                    energia = calcular_energia(audio_chunk)

                    # Detecta se há fala
                    if energia > AudioProcessor.MIC_SENSIBILITY:
                        if not esta_falando:
                            print("🗣️  Detectado: Você está falando...")
                            esta_falando = True

                        frames.append(audio_chunk.copy())
                        ultimo_som = time.time()
                        silencio_tempo = 0

                    else:
                        # Se já estava falando, continua gravando o silêncio
                        if esta_falando:
                            frames.append(audio_chunk.copy())
                            silencio_tempo = time.time() - ultimo_som

                            # Para se silêncio prolongado
                            if silencio_tempo >= AudioProcessor.SILENCIO_LIMITE:
                                print(f"🔇 Silêncio detectado ({silencio_tempo:.1f}s). Finalizando gravação...")
                                break

                    # Timeout de segurança (60 segundos máximo)
                    if esta_falando and (time.time() - ultimo_som) > 60:
                        print("⏱️  Tempo máximo atingido. Finalizando...")
                        break

        except KeyboardInterrupt:
            print("\n⚠️  Gravação interrompida pelo usuário")
            return None

        if not frames:
            print("⚠️  Nenhum áudio detectado!")
            return None

        # Concatena todos os frames
        audio_completo = np.concatenate(frames, axis=0)
        duracao = len(audio_completo) / AudioProcessor.sample_rate
        print(f"✅ Gravação finalizada! ({duracao:.1f} segundos)")

        return audio_completo