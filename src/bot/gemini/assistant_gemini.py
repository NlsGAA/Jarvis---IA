# assistant_gemini.py
import google.generativeai as genai
import threading
from queue import Queue
import base64
from PIL import Image
import io

class AssistantGemini:
    def __init__(self, api_key="AIzaSyBJzBHgzyt9zvT-QWxevOxysdMBLr_h96k"):
        """
        Inicializa assistente com Gemini

        Args:
            api_key (str): Chave da API do Google
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')
        self.chat = None
        self.historico_conversa = []
        self.ultima_imagem = None
        self.lock = threading.Lock()

        print("✅ Assistente Gemini inicializado")

    def set_screenshot(self, img_base64):
        """Define screenshot atual"""
        with self.lock:
            # Converte base64 para PIL Image
            img_data = base64.b64decode(img_base64)
            self.ultima_imagem = Image.open(io.BytesIO(img_data))

    def talk_stream_generator(self, user_message, incluir_visao=True):
        """
        Conversa com streaming

        Args:
            user_message (str): Mensagem do usuário
            incluir_visao (bool): Incluir screenshot

        Yields:
            str: Chunks da resposta
        """
        print("🤖 Gerando resposta", end='')

        with self.lock:
            usar_imagem = incluir_visao and self.ultima_imagem is not None
            imagem_atual = self.ultima_imagem if usar_imagem else None

        if usar_imagem:
            print(" (com visão)...\n")
        else:
            print("...\n")

        try:
            # Prepara prompt
            if usar_imagem:
                # Com imagem
                response = self.model.generate_content(
                    [user_message, imagem_atual],
                    stream=True
                )
            else:
                # Sem imagem
                response = self.model.generate_content(
                    user_message,
                    stream=True
                )

            print("💬 Resposta: ", end='', flush=True)
            resposta_completa = ""

            for chunk in response:
                if chunk.text:
                    resposta_completa += chunk.text
                    print(chunk.text, end='', flush=True)
                    yield chunk.text

            print("\n")

        except Exception as e:
            print(f"\n❌ Erro: {e}")
            yield ""

    def talk(self, user_message, incluir_visao=True):
        """Conversa (versão completa)"""
        resposta = ""
        for chunk in self.talk_stream_generator(user_message, incluir_visao):
            resposta += chunk
        return resposta

    def limpar_historico(self):
        """Limpa histórico"""
        self.historico_conversa = []
        self.chat = None
        print("🗑️ Histórico limpo")