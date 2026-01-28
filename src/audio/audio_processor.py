import time
import threading
import numpy as np
from queue import Queue
import sounddevice as sd
from scipy.io.wavfile import write

class AudioProcessor:
    sample_rate = 16000
    temp_file = "temp_audio.wav"

    SILENCIO_LIMITE = 2.0        # Segundos de silêncio para parar
    MIC_RESTRICTION = 200        # Ajuste se necessário (200-1000)
    CHUNK_DURATION = 0.1         # Duração de cada chunk em segundos
    TRANSCRICAO_INTERVALO = 3.0  # Transcreve a cada 3 segundos

    def __init__(self):
        """Inicializa o processador de áudio"""
        self.frames = []
        self.esta_falando = False
        self.ultimo_som = time.time()
        self.ultima_transcricao = time.time()
        self.transcricao_parcial = ""
        self.callback_transcricao = None  # Callback para transcrição em tempo real

    @staticmethod
    def store_audio(recorded_audio):
        """Salva o áudio em arquivo WAV"""
        write(AudioProcessor.temp_file, AudioProcessor.sample_rate, recorded_audio)

    @staticmethod
    def calcular_energia(audio_chunk):
        """Calcula a energia (volume) do chunk de áudio"""
        return np.abs(audio_chunk).mean()

    def set_transcricao_callback(self, callback):
        """
        Define uma função callback que será chamada com os chunks de áudio para transcrição

        Args:
            callback: função que recebe numpy array de áudio
        """
        self.callback_transcricao = callback

    def set_ia_callback(self, ia_assistente):
        """
        Define o assistente de IA para receber contexto parcial

        Args:
            ia_assistente: Instância de IAAssistente
        """
        self.ia_assistente = ia_assistente

    def thread_transcricao_continua(self):
        """Thread que chama o callback de transcrição continuamente"""
        print("🔄 Sistema de transcrição em tempo real ativado\n")

        while self.esta_falando:
            tempo_desde_ultima = time.time() - self.ultima_transcricao

            # Transcreve a cada X segundos se houver áudio suficiente
            if tempo_desde_ultima >= self.TRANSCRICAO_INTERVALO and len(self.frames) > 0:
                # Pega os frames acumulados
                try:
                    frames_para_transcrever = np.concatenate(self.frames, axis=0)

                    # Chama o callback de transcrição se definido
                    if self.callback_transcricao:
                        texto_parcial = self.callback_transcricao(frames_para_transcrever)

                        # Envia contexto parcial para a IA se disponível
                        if hasattr(self, 'ia_assistente') and self.ia_assistente and texto_parcial:
                            self.ia_assistente.processar_contexto_parcial(texto_parcial)

                    self.ultima_transcricao = time.time()
                except Exception as e:
                    print(f"⚠️ Erro na thread de transcrição: {e}")

            time.sleep(0.5)

    def record_audio(self, streaming=False):
        """
        Grava áudio continuamente até detectar silêncio prolongado

        Args:
            streaming (bool): Se True, ativa transcrição em tempo real via callback

        Returns:
            numpy.ndarray: Áudio gravado ou None se erro
        """
        print("🎤 Pode falar! (a gravação para automaticamente quando você parar)")
        if streaming:
            print("📡 Transcrição em tempo real ativada")
        print("⏸️  Aguardando você começar a falar...\n")

        self.frames = []
        silencio_tempo = 0
        self.esta_falando = False
        self.ultimo_som = time.time()
        chunk_size = int(self.sample_rate * self.CHUNK_DURATION)

        # Inicia thread de transcrição se streaming ativo e callback definido
        thread_transcricao = None
        if streaming and self.callback_transcricao:
            thread_transcricao = threading.Thread(target=self.thread_transcricao_continua)
            thread_transcricao.daemon = True
            thread_transcricao.start()

        try:
            with sd.InputStream(samplerate=self.sample_rate,
                            channels=1,
                            dtype='int16',
                            blocksize=chunk_size) as stream:

                print("🎧 Sistema de áudio iniciado...")

                while True:
                    # Lê um chunk de áudio
                    audio_chunk, overflowed = stream.read(chunk_size)

                    # Calcula energia do chunk
                    energia = self.calcular_energia(audio_chunk)

                    # Detecta se há fala
                    if energia > self.MIC_RESTRICTION:
                        if not self.esta_falando:
                            print("🗣️  Detectado: Você está falando...")
                            self.esta_falando = True

                        self.frames.append(audio_chunk.copy())
                        self.ultimo_som = time.time()
                        silencio_tempo = 0

                    else:
                        # Se já estava falando, continua gravando o silêncio
                        if self.esta_falando:
                            self.frames.append(audio_chunk.copy())
                            silencio_tempo = time.time() - self.ultimo_som

                            # Para se silêncio prolongado
                            if silencio_tempo >= self.SILENCIO_LIMITE:
                                print(f"🔇 Silêncio detectado ({silencio_tempo:.1f}s). Finalizando gravação...")
                                self.esta_falando = False  # Para a thread de transcrição
                                break

                    # Timeout de segurança (60 segundos máximo)
                    if self.esta_falando and (time.time() - self.ultimo_som) > 60:
                        print("⏱️  Tempo máximo atingido. Finalizando...")
                        self.esta_falando = False
                        break

        except KeyboardInterrupt:
            print("\n⚠️  Gravação interrompida pelo usuário")
            self.esta_falando = False
            return None

        # Aguarda thread de transcrição finalizar
        if thread_transcricao and thread_transcricao.is_alive():
            thread_transcricao.join(timeout=2)

        if not self.frames:
            print("⚠️  Nenhum áudio detectado!")
            return None

        # Concatena todos os frames
        audio_completo = np.concatenate(self.frames, axis=0)
        duracao = len(audio_completo) / self.sample_rate
        print(f"✅ Gravação finalizada! ({duracao:.1f} segundos)")

        return audio_completo