import ollama

class Assistant:
    model = "gemma2:2b"

    @staticmethod
    def talk(user_message):
        """Envia mensagem para o Gemma 2 e retorna resposta"""
        print("🤖 Pensando...")

        system_prompt = """
            Você é um assistente de voz amigável e prestativo.
            Responda de forma natural, concisa e direta, como em uma conversa falada.
            Nunca utilize emojis, asteriscos, formatação markdown ou listas longas.
            Fale de forma clara e objetiva, sem repetições desnecessárias.
        """

        response = ollama.chat(model=Assistant.model, messages=[
            {
                'role': 'system',
                'content': system_prompt,
            },
            {
                'role': 'user',
                'content': user_message,
            },
        ])

        return response['message']['content']