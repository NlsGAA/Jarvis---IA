# bot/assistant.py
import threading
from typing import Optional
from bot.abstract.abstract_assistant import AbstractAssistant

class Assistant:
    """Facade para gerenciar assistentes de IA com Strategy Pattern"""

    def __init__(self, assistant: AbstractAssistant):
        """
        Args:
            assistant: Strategy de IA (OllamaAssistant, GeminiAssistant, etc)
        """
        self.assistant = assistant
        self.historico_conversa = []
        self.contexto_parcial = ""
        self.resposta_preparada = ""
        self.processando = False
        self.lock = threading.Lock()
        self.ultima_imagem = None

        self.system_prompt = """
            Você é um assistente de voz amigável e prestativo com capacidade de visão.
            Você pode ver a tela do usuário e ajudá-lo com o que está fazendo.
            Quando receber uma imagem da tela, verifique se o usuário solicitou algo e o ajude conforme necessário.
            Responda de forma natural, concisa e direta, como em uma conversa falada.
            Nunca utilize emojis, asteriscos, formatação markdown ou listas longas.
            Fale de forma clara e objetiva, sem repetições desnecessárias e textos longos.
        """

    def set_screenshot(self, img_base64: str) -> None:
        """Define screenshot atual"""
        with self.lock:
            self.ultima_imagem = img_base64

    def processar_contexto_parcial(self, texto_parcial: str) -> None:
        """Processa contexto parcial (pré-aquecimento)"""
        if not texto_parcial or not texto_parcial.strip():
            return

        with self.lock:
            self.contexto_parcial = texto_parcial

    def talk_stream_generator(self, user_message: str, incluir_visao: bool = True):
        """
        Conversa com streaming

        Args:
            user_message: Mensagem do usuário
            incluir_visao: Se True, inclui screenshot

        Yields:
            str: Chunks da resposta
        """

        with self.lock:
            self.processando = True
            imagem_atual = self.ultima_imagem if incluir_visao else None

        if imagem_atual:
            print(" (com visão)...\n")
        else:
            print("...\n")

        try:
            print("💬 Resposta: ", end='', flush=True)
            resposta_completa = ""

            for chunk in self.assistant.talk_stream_generator(
                user_message=user_message,
                system_prompt=self.system_prompt,
                historico=self.historico_conversa,
                imagem_base64=imagem_atual
            ):
                resposta_completa += chunk
                print(chunk, end='', flush=True)
                yield chunk

            print("\n")

            self.historico_conversa.append({
                'role': 'user',
                'content': user_message + (" [com imagem]" if imagem_atual else "")
            })
            self.historico_conversa.append({
                'role': 'assistant',
                'content': resposta_completa
            })

            with self.lock:
                self.resposta_preparada = resposta_completa

        except Exception as e:
            print(f"\n❌ Erro: {e}")
            yield ""

        finally:
            with self.lock:
                self.processando = False

    def talk(self, user_message: str, incluir_visao: bool = True) -> str:
        """Conversa (versão completa)"""
        resposta_completa = ""
        for chunk in self.talk_stream_generator(user_message, incluir_visao):
            resposta_completa += chunk
        return resposta_completa
