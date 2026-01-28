import asyncio
from audio.audio_processor import AudioProcessor
from speech_converter.speech_converter import SpeechConverter
from bot.assistant import Assistant

async def main_async():
    print("=== Assistente de Voz Inteligente com Streaming Completo ===\n")

    # Inicializa componentes
    audio_processor = AudioProcessor()
    speech_converter = SpeechConverter(modelo_whisper="base")
    assistant = Assistant()

    # Conecta callbacks
    audio_processor.set_transcricao_callback(
        speech_converter.transcribe_audio_array
    )
    audio_processor.set_ia_callback(assistant)

    print("✅ Sistema pronto! Todos os componentes conectados.\n")

    while True:
        print("─" * 60)

        # Grava com streaming ativo
        audio = audio_processor.record_audio(streaming=True)

        if audio is None:
            print("Encerrando...")
            break

        # Salva áudio
        audio_processor.store_audio(audio)

        # Transcrição final
        transcricao = speech_converter.transcribe_final(audio)

        if not transcricao or not transcricao.strip():
            print("⚠️ Transcrição vazia. Tente novamente.\n")
            continue

        print(f"\n📝 Você disse: {transcricao}\n")

        # Verifica comandos especiais
        if "sair" in transcricao.lower() or "encerrar" in transcricao.lower():
            print("👋 Até logo!")
            break

        if "limpar histórico" in transcricao.lower():
            assistant.limpar_historico()
            continue

        # Gera resposta com streaming E reproduz em tempo real
        texto_generator = assistant.talk_stream_generator(transcricao)

        # Converte e reproduz em streaming (IA fala conforme pensa!)
        await speech_converter.text_to_speech_stream(texto_generator)

        print()

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n\n⚠️ Programa interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")

if __name__ == "__main__":
    main()