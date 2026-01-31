# bot/abstract/abstract_assistant.py
from abc import ABC, abstractmethod
from typing import Generator, Optional

class AbstractAssistant(ABC):
    """Interface para diferentes provedores de IA (Strategy Pattern)"""

    @abstractmethod
    def talk_stream_generator(
        self,
        user_message: str,
        system_prompt: str,
        historico: list,
        imagem_base64: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Gera resposta em streaming

        Args:
            user_message: Mensagem do usuário
            system_prompt: Prompt do sistema
            historico: Histórico de conversas
            imagem_base64: Screenshot em base64 (opcional)

        Yields:
            str: Chunks da resposta
        """
        pass