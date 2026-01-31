# 🤖 Jarvis - Assistente de Voz Inteligente com Visão

Um assistente de voz avançado com capacidade de visão computacional, transcrição em tempo real e síntese de fala. Inspirado no assistente do Homem de Ferro, este projeto permite interagir com sua IA através de comandos de voz enquanto ela visualiza sua tela em tempo real.

## ✨ Características

- 🎤 **Reconhecimento de Voz em Tempo Real** - Transcrição automática usando Whisper
- 🗣️ **Síntese de Fala Natural** - Respostas em áudio com vozes brasileiras
- 👁️ **Visão Computacional** - Visualiza sua tela e ajuda com o que você está fazendo
- ⚡ **Streaming Inteligente** - Transcrição e respostas em tempo real
- 🔄 **Múltiplos Modelos de IA** - Suporte para Ollama (local) e Google Gemini (nuvem)
- 🎯 **Detecção Automática de Silêncio** - Para gravação quando você termina de falar
- 🧠 **Pré-processamento Contextual** - IA se prepara enquanto você fala
- 🎨 **Arquitetura Strategy** - Fácil adicionar novos provedores de IA

## 🎬 Demo
```
👤 Você: "O que você está vendo na minha tela?"
🤖 IA: "Vejo que você está no VS Code editando um arquivo Python..."

👤 Você: "Me ajuda a corrigir esse erro"
🤖 IA: [Analisa o código na tela e sugere correção]
```

## 📋 Pré-requisitos

- Python 3.10 ou superior
- Windows, Linux ou macOS
- 8GB RAM (mínimo) - 16GB recomendado
- Microfone funcional
- (Opcional) GPU NVIDIA para melhor performance

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/jarvis-ia.git
cd jarvis-ia
```

### 2. Crie e ative o ambiente virtual

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Instale o Ollama (para modelos locais)

**Windows:**
- Baixe em: https://ollama.com/download/windows
- Instale e execute

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Mac:**
```bash
brew install ollama
```

### 5. Baixe um modelo com visão
```bash
# Recomendado (balanced)
ollama pull llava:7b

# Alternativas:
# ollama pull moondream      # Mais leve
# ollama pull llava-llama3   # Melhor qualidade
```

### 6. Configure as variáveis de ambiente

Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

Edite o `.env` e adicione suas configurações:
```env
# Escolha o provedor de IA
USE_GEMINI=false              # true para Gemini, false para Ollama

# API Keys (apenas se usar Gemini)
GEMINI_API_KEY=sua-chave-aqui

# Configurações
OLLAMA_MODEL=llava:7b
WHISPER_MODEL=base
TTS_VOICE=pt-BR-AntonioNeural
TTS_SPEED=+20%
```

### 7. (Opcional) Configure o Gemini

Se preferir usar o Google Gemini (melhor qualidade, necessita internet):

1. Acesse: https://makersuite.google.com/app/apikey
2. Clique em "Create API Key"
3. Copie a chave e adicione no `.env`:
```env
   USE_GEMINI=true
   GEMINI_API_KEY=sua-chave-aqui
```

## 🎮 Como Usar

### Iniciar o assistente
```bash
cd src
python main.py
```

### Comandos de voz

O assistente responde a comandos naturais em português:

**Comandos de sistema:**
- "Sair" ou "Encerrar" - Fecha o assistente
- "Limpar histórico" - Apaga conversas anteriores
- "Ligar visão" - Ativa captura de tela
- "Desligar visão" - Desativa captura de tela

**Ativação automática de visão:**
Ao usar palavras-chave como "veja", "olha", "tela", "o que aparece", etc., a IA automaticamente usa a visão.

**Exemplos de uso:**
```
"Olha minha tela e me diz o que tem aqui"
"Me ajuda a corrigir esse erro"
"O que você está vendo?"
"Explica esse código para mim"
```

## 📁 Estrutura do Projeto
```
jarvis-ia/
├── .env                          # Configurações (não versionado)
├── .env.example                  # Exemplo de configurações
├── .gitignore                    # Arquivos ignorados pelo Git
├── requirements.txt              # Dependências Python
├── README.md                     # Este arquivo
└── src/
    ├── main.py                   # Ponto de entrada
    ├── audio_processor.py        # Captura e processamento de áudio
    ├── speech_converter.py       # STT e TTS
    ├── screen_capture.py         # Captura de tela
    └── bot/
        ├── assistant.py          # Facade principal
        ├── abstract/
        │   └── abstract_assistant.py  # Interface Strategy
        └── strategies/
            ├── ollama_assistant.py    # Strategy Ollama
            └── gemini_assistant.py    # Strategy Gemini
```

## ⚙️ Configurações Avançadas

### Calibrar sensibilidade do microfone

Se o assistente não detectar sua voz ou captar muito ruído:
```python
# No arquivo src/audio_processor.py, ajuste:
MIC_RESTRICTION = 300  # Aumente para ignorar mais ruído
                       # Diminua para ser mais sensível
```

### Trocar vozes do TTS

Edite no `.env`:
```env
# Vozes masculinas
TTS_VOICE=pt-BR-AntonioNeural

# Vozes femininas
TTS_VOICE=pt-BR-FranciscaNeural
TTS_VOICE=pt-BR-ThalitaNeural
```

### Ajustar velocidade da fala
```env
TTS_SPEED=+10%   # Mais devagar
TTS_SPEED=+20%   # Normal (padrão)
TTS_SPEED=+30%   # Mais rápido
```

### Otimizar captura de tela

Para melhorar performance:
```env
SCREEN_CAPTURE_INTERVAL=5.0  # Aumentar para capturar menos
SCREEN_CAPTURE_QUALITY=40    # Diminuir para comprimir mais
SCREEN_MAX_WIDTH=800         # Diminuir resolução
SCREEN_MAX_HEIGHT=600
```

## 🐛 Solução de Problemas

### "ModuleNotFoundError: No module named 'X'"
```bash
pip install -r requirements.txt
```

### "FileNotFoundError: ffmpeg"
Instale o FFmpeg:
- **Windows:** `choco install ffmpeg` ou `winget install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`
- **Mac:** `brew install ffmpeg`

### Microfone não detecta voz
1. Verifique se o microfone está funcionando no sistema
2. Execute o teste de calibração (no código)
3. Ajuste `MIC_RESTRICTION` no `audio_processor.py`

### IA não vê a tela corretamente
1. Certifique-se de usar um modelo com visão (`llava`, `moondream`, etc.)
2. Teste com: "salvar screenshot" e verifique a imagem
3. Use Gemini para melhor qualidade de visão

### Resposta muito lenta
**Soluções:**
- Use modelo menor: `ollama pull moondream`
- Ou use Gemini (muito mais rápido)
- Reduza qualidade/tamanho das capturas de tela
- Use GPU se disponível

### Erro "\_thread.\_local' object has no attribute 'srcdc'"
Já corrigido na versão atual. Atualize o `screen_capture.py`.

## 🎯 Roadmap

- [ ] Suporte a Claude (Anthropic)
- [ ] Suporte a Groq (ultra-rápido)
- [ ] Interface gráfica (GUI)
- [ ] Comandos personalizados
- [ ] Integração com automação (executar ações no PC)
- [ ] Multi-idiomas
- [ ] Wake word ("Hey Jarvis")
- [ ] Memória persistente entre sessões

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abrir um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🙏 Agradecimentos

- [OpenAI Whisper](https://github.com/openai/whisper) - Transcrição de voz
- [Ollama](https://ollama.ai/) - Modelos locais
- [Google Gemini](https://ai.google.dev/) - API de IA
- [Edge TTS](https://github.com/rany2/edge-tts) - Síntese de fala
- [MSS](https://github.com/BoboTiG/python-mss) - Captura de tela

## 👨‍💻 Autor

**Seu Nome**
- GitHub: [@seu-usuario](https://github.com/seu-usuario)
- Email: seu.email@exemplo.com

---

⭐ Se este projeto te ajudou, considere dar uma estrela!

💬 Dúvidas? Abra uma [issue](https://github.com/seu-usuario/jarvis-ia/issues)