import re
import whisper
import edge_tts
import numpy as np
from scipy.io.wavfile import read
import asyncio
import os
from playsound import playsound
import threading
from queue import Queue

class SpeechConverter:
    # Aumenta 20% a velocidade (pode ajustar: +10%, +30%, etc)
    voice_speed = "+20%"

    # pt-BR-AntonioNeural - male
    # pt-BR-FranciscaNeural - female
    # pt-BR-ThalitaNeural - female
    voice_sample = "pt-BR-AntonioNeural"

    # Configurações de segurança
    MAX_AUDIO_DURATION = 120  # Máximo 2 minutos
    SAMPLE_RATE = 16000

    def __init__(self, modelo_whisper="base"):
        """
        Inicializa o conversor de fala com modelo Whisper carregado

        Args:
            modelo_whisper (str): Nome do modelo ('tiny', 'base', 'small', 'medium', 'large')
        """
        print(f"🔄 Carregando modelo Whisper '{modelo_whisper}'...")
        self.model = whisper.load_model(modelo_whisper)
        print(f"✅ Modelo Whisper '{modelo_whisper}' carregado!")

        # Controle para TTS streaming
        self.fila_audio = Queue()
        self.esta_reproduzindo = False

    # ... (mantenha todos os outros métodos de transcrição) ...

    @staticmethod
    def saniteze_ia_response(texto):
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
        print(f"🔊 Gerando áudio da resposta...")

        texto_limpo = SpeechConverter.saniteze_ia_response(texto)

        communicate = edge_tts.Communicate(
            texto_limpo,
            SpeechConverter.voice_sample,
            rate=SpeechConverter.voice_speed
        )

        await communicate.save(arquivo_saida)
        print(f"✅ Áudio salvo em: {arquivo_saida}")

    async def text_to_speech_stream(self, texto_stream_generator, pasta_temp="temp_audio_chunks"):
        """
        Converte texto para fala em streaming (gera e reproduz em tempo real)

        Args:
            texto_stream_generator: Generator que produz chunks de texto
            pasta_temp (str): Pasta temporária para chunks de áudio
        """
        print("🔊 Iniciando síntese de voz em streaming...")

        # Cria pasta temporária se não existir
        if not os.path.exists(pasta_temp):
            os.makedirs(pasta_temp)

        buffer_texto = ""
        chunk_count = 0
        arquivos_audio = []

        # Inicia thread de reprodução
        thread_reproducao = threading.Thread(target=self._reproduzir_chunks_continuo, args=(arquivos_audio,))
        thread_reproducao.daemon = True
        thread_reproducao.start()

        try:
            # Processa chunks de texto conforme chegam
            for chunk_texto in texto_stream_generator:
                buffer_texto += chunk_texto

                # Quando completar uma frase ou tiver texto suficiente
                if self._deve_gerar_audio(buffer_texto):
                    # Limpa o texto
                    texto_limpo = self.saniteze_ia_response(buffer_texto)

                    if texto_limpo:
                        # Gera arquivo de áudio
                        arquivo_chunk = os.path.join(pasta_temp, f"chunk_{chunk_count}.mp3")

                        # Cria áudio
                        communicate = edge_tts.Communicate(
                            texto_limpo,
                            self.voice_sample,
                            rate=self.voice_speed
                        )
                        await communicate.save(arquivo_chunk)

                        # Adiciona à fila de reprodução
                        arquivos_audio.append(arquivo_chunk)
                        print(f"🎵 Chunk {chunk_count} gerado e enfileirado")

                        chunk_count += 1
                        buffer_texto = ""

            # Processa texto restante
            if buffer_texto.strip():
                texto_limpo = self.saniteze_ia_response(buffer_texto)
                if texto_limpo:
                    arquivo_chunk = os.path.join(pasta_temp, f"chunk_{chunk_count}.mp3")
                    communicate = edge_tts.Communicate(
                        texto_limpo,
                        self.voice_sample,
                        rate=self.voice_speed
                    )
                    await communicate.save(arquivo_chunk)
                    arquivos_audio.append(arquivo_chunk)
                    print(f"🎵 Chunk final {chunk_count} gerado")

            # Aguarda todas as reproduções terminarem
            while len(arquivos_audio) > 0:
                await asyncio.sleep(0.1)

            print("✅ Síntese e reprodução em streaming finalizada!")

        finally:
            # Limpa arquivos temporários
            await asyncio.sleep(0.5)  # Aguarda reprodução final
            self._limpar_pasta_temp(pasta_temp)

    def _deve_gerar_audio(self, texto):
        """
        Decide se deve gerar áudio para o chunk atual

        Args:
            texto (str): Texto acumulado no buffer

        Returns:
            bool: True se deve gerar áudio
        """
        # Gera áudio quando:
        # 1. Completou uma frase (. ! ?)
        # 2. Tem pelo menos 100 caracteres
        # 3. Completou uma vírgula e tem pelo menos 50 caracteres

        if not texto.strip():
            return False

        # Fim de frase
        if texto.rstrip().endswith(('.', '!', '?')):
            return True

        # Texto longo o suficiente
        if len(texto) >= 100:
            return True

        # Vírgula com texto razoável
        if ',' in texto and len(texto) >= 50:
            # Pega até a última vírgula
            return True

        return False

    def _reproduzir_chunks_continuo(self, arquivos_audio):
        """
        Thread que reproduz chunks de áudio conforme ficam disponíveis

        Args:
            arquivos_audio (list): Lista compartilhada de arquivos de áudio
        """
        self.esta_reproduzindo = True
        indice_atual = 0

        while self.esta_reproduzindo or indice_atual < len(arquivos_audio):
            # Se há novo arquivo disponível
            if indice_atual < len(arquivos_audio):
                arquivo = arquivos_audio[indice_atual]

                # Aguarda o arquivo estar pronto
                while not os.path.exists(arquivo):
                    threading.Event().wait(0.1)

                # Reproduz
                print(f"▶️ Reproduzindo chunk {indice_atual}...")
                try:
                    playsound(arquivo)
                    # Remove da lista após reproduzir
                    arquivos_audio.pop(0)
                except Exception as e:
                    print(f"⚠️ Erro ao reproduzir chunk {indice_atual}: {e}")
                    indice_atual += 1
            else:
                # Aguarda novos chunks
                threading.Event().wait(0.1)

        self.esta_reproduzindo = False

    def transcribe_audio_array(self, audio_array):
        """
        Transcreve áudio a partir de numpy array (para streaming)

        Args:
            audio_array (numpy.ndarray): Array de áudio (int16)

        Returns:
            str: Texto transcrito
        """
        try:
            # Valida
            audio_array = self._validar_audio(audio_array)

            # Converte para float32
            audio_float = self._converter_para_float32(audio_array)

            # Verifica tamanho mínimo (0.1 segundo)
            if len(audio_float) < self.SAMPLE_RATE * 0.1:
                return ""

            # Transcreve
            resultado = self.model.transcribe(
                audio_float,
                language="pt",
                fp16=False,
                verbose=False  # Não mostra progresso
            )

            texto = resultado["text"].strip()
            if texto:
                print(f"📝 Transcrevendo: {texto}")

            return texto
        except Exception as e:
            print(f"⚠️ Erro na transcrição do chunk: {e}")
            return ""

    def _validar_audio(self, audio_array):
        """
        Valida e limita o tamanho do áudio

        Args:
            audio_array (numpy.ndarray): Array de áudio

        Returns:
            numpy.ndarray: Array validado e potencialmente truncado
        """
        # Verifica se o array está vazio
        if audio_array is None or len(audio_array) == 0:
            raise ValueError("Array de áudio vazio")

        # Calcula duração
        duracao = len(audio_array) / self.SAMPLE_RATE

        # Limita duração máxima
        if duracao > self.MAX_AUDIO_DURATION:
            print(f"⚠️ Áudio muito longo ({duracao:.1f}s). Truncando para {self.MAX_AUDIO_DURATION}s")
            max_samples = int(self.MAX_AUDIO_DURATION * self.SAMPLE_RATE)
            audio_array = audio_array[:max_samples]

        # Verifica se é 1D (mono)
        if len(audio_array.shape) > 1:
            # Se for stereo, pega apenas um canal
            audio_array = audio_array[:, 0]

        return audio_array

    def _converter_para_float32(self, audio_array):
        """
        Converte array de áudio para float32 normalizado

        Args:
            audio_array (numpy.ndarray): Array de áudio (int16 ou float)

        Returns:
            numpy.ndarray: Array em float32 normalizado
        """
        # Se já for float, retorna
        if audio_array.dtype == np.float32:
            return audio_array

        # Converte int16 para float32
        if audio_array.dtype == np.int16:
            return audio_array.astype(np.float32) / 32768.0

        # Outros tipos, tenta converter
        return audio_array.astype(np.float32)

    def transcribe_audio(self, audio_recorded="temp_audio.wav"):
        """
        Transcreve o áudio usando Whisper (arquivo)

        Args:
            audio_recorded (str): Caminho do arquivo de áudio

        Returns:
            str: Texto transcrito
        """
        print("🔄 Transcrevendo arquivo de áudio...")

        sample_rate, audio = read(audio_recorded)

        # Valida e converte
        audio = self._validar_audio(audio)
        audio = self._converter_para_float32(audio)

        resultado = self.model.transcribe(audio, language="pt", fp16=False)
        return resultado["text"]

    def transcribe_final(self, audio_array):
        """
        Transcrição final completa (mais precisa)

        Args:
            audio_array (numpy.ndarray): Array de áudio completo

        Returns:
            str: Texto transcrito
        """
        print("\n🔄 Fazendo transcrição final completa...")

        try:
            # Valida e limita
            audio_array = self._validar_audio(audio_array)

            # Mostra informações de debug
            duracao = len(audio_array) / self.SAMPLE_RATE
            print(f"📊 Duração do áudio: {duracao:.1f}s")
            print(f"📊 Tamanho do array: {len(audio_array)} samples")
            print(f"📊 Tipo de dados: {audio_array.dtype}")

            # Converte para float32
            audio_float = self._converter_para_float32(audio_array)

            # Libera memória do array original
            del audio_array

            # Transcreve
            resultado = self.model.transcribe(
                audio_float,
                language="pt",
                fp16=False,
                verbose=True  # Mostra progresso
            )

            transcricao = resultado["text"].strip()
            print(f"✅ Transcrição finalizada!")

            return transcricao

        except Exception as e:
            print(f"❌ Erro na transcrição final: {e}")
            print(f"📊 Informações do erro:")
            print(f"   - Tamanho do array: {len(audio_array) if audio_array is not None else 'None'}")
            print(f"   - Tipo: {audio_array.dtype if audio_array is not None else 'None'}")
            return ""

    def _limpar_pasta_temp(self, pasta):
        """
        Remove pasta temporária e seus arquivos

        Args:
            pasta (str): Caminho da pasta
        """
        try:
            if os.path.exists(pasta):
                for arquivo in os.listdir(pasta):
                    caminho = os.path.join(pasta, arquivo)
                    if os.path.isfile(caminho):
                        os.remove(caminho)
                os.rmdir(pasta)
                print("🗑️ Arquivos temporários limpos")
        except Exception as e:
            print(f"⚠️ Erro ao limpar pasta temporária: {e}")