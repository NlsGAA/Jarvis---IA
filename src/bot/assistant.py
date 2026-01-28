import ollama
import threading
from queue import Queue

class Assistant:
    model = "gemma2:2b"

    def __init__(self):
        """Inicializa o assistente com histórico e controle de threading"""
        self.historico_conversa = []
        self.contexto_parcial = ""
        self.resposta_preparada = ""
        self.processando = False
        self.lock = threading.Lock()

        self.system_prompt = """Você é um assistente de voz amigável e prestativo.
Você receberá partes de uma pergunta conforme o usuário fala.
Quando receber contexto parcial (marcado com [PARCIAL]), prepare internamente sua resposta mas NÃO a finalize.
Quando receber a pergunta completa (marcada com [COMPLETO]), forneça sua resposta final.
Responda de forma natural, concisa e direta, como em uma conversa falada.
Nunca utilize emojis, asteriscos, formatação markdown ou listas longas.
Fale de forma clara e objetiva, sem repetições desnecessárias."""

        print(f"✅ Assistente inicializado com modelo: {self.model}")

    def processar_contexto_parcial(self, texto_parcial):
        """
        Processa contexto parcial enquanto o usuário ainda está falando

        Args:
            texto_parcial (str): Transcrição parcial
        """
        if not texto_parcial or not texto_parcial.strip():
            return

        with self.lock:
            self.contexto_parcial = texto_parcial
            print(f"🧠 IA processando contexto parcial em background...")

        # Inicia thread para pré-processar
        thread = threading.Thread(target=self._pre_processar_contexto, args=(texto_parcial,))
        thread.daemon = True
        thread.start()

    def _pre_processar_contexto(self, contexto):
        """
        Pré-processa o contexto em background (prepara a IA)
        """
        try:
            # Prepara mensagem com contexto parcial
            mensagem_parcial = f"[CONTEXTO PARCIAL - Usuário ainda falando]\n{contexto}\n\nPrepare-se para responder, mas aguarde a pergunta completa."

            # Mensagens para aquecimento
            mensagens = [
                {'role': 'system', 'content': self.system_prompt}
            ] + self.historico_conversa + [
                {'role': 'user', 'content': mensagem_parcial}
            ]

            # Faz uma chamada rápida para "aquecer" a IA
            response = ollama.chat(
                model=self.model,
                messages=mensagens,
                stream=False,
                options={
                    'num_predict': 10  # Apenas algumas tokens para preparar
                }
            )

            print("💡 IA aquecida e pronta para resposta final")

        except Exception as e:
            print(f"⚠️ Erro no pré-processamento: {e}")

    def talk(self, user_message, stream=True):
        """
        Conversa com o assistente

        Args:
            user_message (str): Mensagem do usuário
            stream (bool): Se True, retorna resposta em streaming

        Returns:
            str: Resposta completa do assistente
        """
        if stream:
            return self._talk_stream(user_message)
        else:
            return self._talk_normal(user_message)

    def _talk_normal(self, user_message):
        """Modo sem streaming (resposta completa de uma vez)"""
        print("🤖 Pensando...")

        # Adiciona mensagem ao histórico
        self.historico_conversa.append({
            'role': 'user',
            'content': user_message
        })

        # Prepara mensagens
        mensagens = [
            {'role': 'system', 'content': self.system_prompt}
        ] + self.historico_conversa

        # Gera resposta
        response = ollama.chat(
            model=self.model,
            messages=mensagens
        )

        resposta = response['message']['content']

        # Adiciona resposta ao histórico
        self.historico_conversa.append({
            'role': 'assistant',
            'content': resposta
        })

        return resposta

    def _talk_stream(self, user_message):
        """Modo com streaming (resposta palavra por palavra)"""
        print("🤖 Gerando resposta...\n")

        with self.lock:
            self.processando = True

        try:
            # Adiciona mensagem ao histórico
            self.historico_conversa.append({
                'role': 'user',
                'content': user_message
            })

            # Prepara mensagens
            mensagens = [
                {'role': 'system', 'content': self.system_prompt}
            ] + self.historico_conversa

            # Stream da resposta
            resposta_completa = ""
            print("💬 Resposta: ", end='', flush=True)

            stream = ollama.chat(
                model=self.model,
                messages=mensagens,
                stream=True
            )

            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    conteudo = chunk['message']['content']
                    resposta_completa += conteudo
                    print(conteudo, end='', flush=True)

            print("\n")

            # Adiciona resposta ao histórico
            self.historico_conversa.append({
                'role': 'assistant',
                'content': resposta_completa
            })

            with self.lock:
                self.resposta_preparada = resposta_completa

            return resposta_completa

        except Exception as e:
            print(f"\n❌ Erro ao gerar resposta: {e}")
            return ""

        finally:
            with self.lock:
                self.processando = False

    def limpar_historico(self):
        """Limpa o histórico de conversas"""
        with self.lock:
            self.historico_conversa = []
            self.contexto_parcial = ""
            self.resposta_preparada = ""
        print("🗑️ Histórico de conversa limpo")

    def get_historico(self):
        """Retorna o histórico de conversas"""
        with self.lock:
            return self.historico_conversa.copy()

    def mostrar_historico(self):
        """Exibe o histórico de conversas formatado"""
        print("\n📜 Histórico de Conversa:")
        print("─" * 60)
        for msg in self.historico_conversa:
            role = "👤 Você" if msg['role'] == 'user' else "🤖 Assistente"
            print(f"{role}: {msg['content']}")
            print("─" * 60)

    @staticmethod
    def listar_modelos():
        """Lista modelos disponíveis no Ollama"""
        try:
            models = ollama.list()
            print("\n📋 Modelos disponíveis:")
            for model in models['models']:
                print(f"  - {model['name']}")
        except Exception as e:
            print(f"❌ Erro ao listar modelos: {e}")

    def trocar_modelo(self, novo_modelo):
        """
        Troca o modelo sendo usado

        Args:
            novo_modelo (str): Nome do novo modelo
        """
        self.model = novo_modelo
        print(f"✅ Modelo alterado para: {novo_modelo}")

    # Adicione este método na classe Assistant

    def talk_stream_generator(self, user_message):
        """
        Conversa com streaming retornando um generator

        Args:
            user_message (str): Mensagem do usuário

        Yields:
            str: Chunks da resposta
        """
        print("🤖 Gerando resposta...\n")

        with self.lock:
            self.processando = True

        try:
            # Adiciona mensagem ao histórico
            self.historico_conversa.append({
                'role': 'user',
                'content': user_message
            })

            # Prepara mensagens
            mensagens = [
                {'role': 'system', 'content': self.system_prompt}
            ] + self.historico_conversa

            # Stream da resposta
            resposta_completa = ""
            print("💬 Resposta: ", end='', flush=True)

            stream = ollama.chat(
                model=self.model,
                messages=mensagens,
                stream=True
            )

            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    conteudo = chunk['message']['content']
                    resposta_completa += conteudo
                    print(conteudo, end='', flush=True)
                    yield conteudo  # Retorna chunk por chunk

            print("\n")

            # Adiciona resposta ao histórico
            self.historico_conversa.append({
                'role': 'assistant',
                'content': resposta_completa
            })

            with self.lock:
                self.resposta_preparada = resposta_completa

        except Exception as e:
            print(f"\n❌ Erro ao gerar resposta: {e}")
            yield ""

        finally:
            with self.lock:
                self.processando = False