import asyncio
from audio.audio_processor import AudioProcessor
from speech_converter.speech_converter import SpeechConverter
from bot.assistant import Assistant
from screen.screen_capture import ScreenCapture
from bot.gemini.assistant_gemini import AssistantGemini
import os

async def main_async():
    print("=== Assistente de Voz com Visão em Tempo Real ===\n")

    # Inicializa componentes
    audio_processor = AudioProcessor()
    speech_converter = SpeechConverter(modelo_whisper="base")
    assistant = AssistantGemini()
    screen_capture = ScreenCapture(
        intervalo_captura=5.0,
        qualidade=60,
        resolucao_maxima=(1200, 800)
    )  # Aumentei intervalo

    # Conecta callbacks
    audio_processor.set_transcricao_callback(
        speech_converter.transcribe_audio_array
    )
    audio_processor.set_ia_callback(assistant)

    # Callback para captura de tela
    def on_screenshot(img_base64):
        if img_base64:
            assistant.set_screenshot(img_base64)
            # print("📸 Screenshot atualizada")  # Removi para menos poluição

    # Inicia captura contínua de tela
    screen_capture.iniciar_captura_continua(callback=on_screenshot)

    print("✅ Sistema pronto! Todos os componentes conectados.")
    print("👁️ Visão da tela ATIVA - A IA pode ver o que você está fazendo!\n")

    try:
        while True:
            print("─" * 60)

            # Grava com streaming ativo
            audio = audio_processor.record_audio(streaming=True)

            if audio is None:
                break

            # Salva áudio
            audio_processor.store_audio(audio)

            # Transcrição final
            transcricao = speech_converter.transcribe_final(audio)

            if not transcricao or not transcricao.strip():
                print("⚠️ Transcrição vazia. Tente novamente.\n")
                continue

            print(f"\n📝 Você disse: {transcricao}\n")

            # Comandos especiais
            if "sair" in transcricao.lower() or "encerrar" in transcricao.lower():
                print("👋 Até logo!")
                break

            if "limpar histórico" in transcricao.lower():
                assistant.limpar_historico()
                continue

            if "desligar visão" in transcricao.lower():
                screen_capture.parar_captura()
                print("👁️ Visão desativada")
                continue

            if "ligar visão" in transcricao.lower():
                screen_capture.iniciar_captura_continua(callback=on_screenshot)
                print("👁️ Visão ativada")
                continue

            if "salvar screenshot" in transcricao.lower() or "debug screenshot" in transcricao.lower():
                screen_capture.salvar_ultima_captura_debug()
                continue

            # Detecta se usuário quer contexto visual
            palavras_chave_visao = [
                "veja", "olha", "olhe", "tela", "vendo",
                "o que tem", "que aparece", "me ajuda com",
                "isso aqui", "este", "essa janela", "essa página",
                "na tela", "tô fazendo"
            ]

            usar_visao = any(palavra in transcricao.lower() for palavra in palavras_chave_visao)

            # Gera resposta com streaming (com ou sem visão)
            texto_generator = assistant.talk_stream_generator(transcricao, incluir_visao=usar_visao)

            # Converte e reproduz em streaming
            await speech_converter.text_to_speech_stream(texto_generator)

            print()

    finally:
        # Cleanup
        screen_capture.parar_captura()
        print("\n🛑 Sistema encerrado")

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n\n⚠️ Programa interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()