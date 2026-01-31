import io
import base64
from PIL import Image
import google.generativeai as genai
from typing import Generator, Optional
from bot.abstract.abstract_assistant import AbstractAssistant

class AssistantGemini(AbstractAssistant):
    """Modelo de assistente usando Google Gemini"""

    def __init__(
        self,
        api_key: str = "",
        model_name: str = "gemini-flash-latest"
    ):
        """
        Args:
            api_key: Chave da API do Google
            model_name: Nome do modelo Gemini
        """
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model      = genai.GenerativeModel(model_name)

    def talk_stream_generator(
        self,
        user_message: str,
        system_prompt: str,
        historico: list,
        imagem_base64: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Gera resposta em streaming"""

        try:
            prompt_completo = f"{system_prompt}\n\n{user_message}"

            if imagem_base64:
                img_data = base64.b64decode(imagem_base64)
                imagem   = Image.open(io.BytesIO(img_data))
                content  = [prompt_completo, imagem]
            else:
                content = prompt_completo

            response = self.model.generate_content(
                content,
                stream=True,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                )
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            print(f"❌ Erro no Gemini: {e}")
            yield ""