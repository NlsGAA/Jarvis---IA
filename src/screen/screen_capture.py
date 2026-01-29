import mss
import mss.tools
from PIL import Image
import io
import base64
import threading
import time
from queue import Queue
import os

class ScreenCapture:
    def __init__(self, intervalo_captura=2.0, qualidade=50, resolucao_maxima=(800, 600)):
        """
        Inicializa o capturador de tela

        Args:
            intervalo_captura (float): Intervalo em segundos entre capturas
            qualidade (int): Qualidade da compressão JPEG (1-100)
            resolucao_maxima (tuple): Resolução máxima (largura, altura)
        """
        self.intervalo_captura = intervalo_captura
        self.qualidade = qualidade
        self.resolucao_maxima = resolucao_maxima
        self.capturando = False
        self.ultima_captura = None
        self.lock = threading.Lock()
        self.fila_processamento = Queue(maxsize=2)  # Limita fila para evitar acúmulo

        print(f"✅ Capturador de tela inicializado")
        print(f"   Intervalo: {intervalo_captura}s")
        print(f"   Qualidade: {qualidade}")
        print(f"   Resolução máxima: {resolucao_maxima}")

    def capturar_tela(self):
        """
        Captura a tela principal e retorna como base64 (OTIMIZADO)

        Returns:
            str: Imagem em base64 (JPEG)
        """
        with mss.mss() as sct:
            try:
                # Captura o monitor principal
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)

                # Converte para PIL Image
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

                # Redimensiona AGRESSIVAMENTE para melhor performance
                img.thumbnail(self.resolucao_maxima, Image.Resampling.BILINEAR)  # BILINEAR é mais rápido

                # Converte para JPEG com qualidade reduzida
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=self.qualidade, optimize=False)  # optimize=False é mais rápido

                # Converte para base64
                img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

                return img_base64

            except Exception as e:
                print(f"⚠️ Erro ao capturar tela: {e}")
                return None

    def iniciar_captura_continua(self, callback=None):
        """
        Inicia captura contínua em background

        Args:
            callback: Função chamada a cada captura com a imagem base64
        """
        if self.capturando:
            print("⚠️ Captura já está ativa")
            return

        self.capturando = True

        # Thread de captura
        thread_captura = threading.Thread(
            target=self._thread_captura_continua,
            args=(callback,)
        )
        thread_captura.daemon = True
        thread_captura.start()

        print("📸 Captura de tela contínua iniciada")

    def _thread_captura_continua(self, callback):
        """Thread que captura a tela continuamente (OTIMIZADO)"""
        ultimo_tempo = 0

        while self.capturando:
            tempo_atual = time.time()

            # Controle de taxa (rate limiting)
            if tempo_atual - ultimo_tempo < self.intervalo_captura:
                time.sleep(0.1)
                continue

            ultimo_tempo = tempo_atual

            # Captura em thread separada para não bloquear
            img_base64 = self.capturar_tela()

            if img_base64:
                with self.lock:
                    self.ultima_captura = img_base64

                # Chama callback de forma assíncrona
                if callback:
                    try:
                        # Não bloqueia se callback for lento
                        threading.Thread(target=callback, args=(img_base64,), daemon=True).start()
                    except Exception as e:
                        print(f"⚠️ Erro no callback de screenshot: {e}")

    def parar_captura(self):
        """Para a captura contínua"""
        self.capturando = False
        print("⏹️ Captura de tela parada")

    def get_ultima_captura(self):
        """Retorna a última captura armazenada"""
        with self.lock:
            return self.ultima_captura

    def salvar_captura(self, caminho="screenshot.jpg"):
        """
        Salva a tela atual em um arquivo

        Args:
            caminho (str): Caminho do arquivo
        """
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)

            # Converte e salva
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            img.save(caminho, "JPEG", quality=85)
            print(f"💾 Screenshot salvo em: {caminho}")

    def salvar_ultima_captura_debug(self, pasta="debug_screenshots"):
        """
        Salva a última captura para debug

        Args:
            pasta (str): Pasta onde salvar

        Returns:
            str: Caminho do arquivo salvo
        """
        import datetime

        if not os.path.exists(pasta):
            os.makedirs(pasta)

        with self.lock:
            if not self.ultima_captura:
                print("⚠️ Nenhuma captura disponível")
                return None

            # Decodifica base64 e salva
            img_data = base64.b64decode(self.ultima_captura)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            caminho = os.path.join(pasta, f"screenshot_{timestamp}.jpg")

            with open(caminho, 'wb') as f:
                f.write(img_data)

            print(f"💾 Screenshot debug salvo em: {caminho}")
            print(f"📊 Tamanho: {len(img_data)/1024:.1f}KB")
            return caminho

    def get_info_captura(self):
        """Retorna informações sobre a última captura"""
        with self.lock:
            if not self.ultima_captura:
                return None

            tamanho_kb = len(self.ultima_captura) / 1024
            return {
                'tamanho_base64_kb': tamanho_kb,
                'tamanho_bytes': len(self.ultima_captura)
            }

    def capturar_area(self, x, y, largura, altura):
        """
        Captura uma área específica da tela

        Args:
            x, y: Coordenadas do canto superior esquerdo
            largura, altura: Dimensões da área

        Returns:
            str: Imagem em base64
        """
        with mss.mss() as sct:
            try:
                monitor = {"top": y, "left": x, "width": largura, "height": altura}
                screenshot = sct.grab(monitor)

                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=self.qualidade)

                return base64.b64encode(buffer.getvalue()).decode('utf-8')

            except Exception as e:
                print(f"⚠️ Erro ao capturar área: {e}")
                return None