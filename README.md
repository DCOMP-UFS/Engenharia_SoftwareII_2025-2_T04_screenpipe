# Análise Arquitetural do Projeto *screenpipe* utilizando Modelos do Hugging Face

Repositório dedicado à documentação e reprodução do processo de identificação de padrões arquiteturais no software Screenpipe, contendo o tutorial completo, código e artefatos necessários para a execução da atividade.

## Configuração do Ambiente
```bash
# 1. Instalar as bibliotecas necessárias
!pip install transformers accelerate bitsandbytes sentence-transformers Pillow datasets
!pip install -q git+https://github.com/huggingface/peft.git  # PEFT é útil para modelos grandes

# 2. Clonar o repositório ScreenPipe
!git clone https://github.com/mediar-ai/screenpipe.git
%cd screenpipe
!ls # Verifique os diretórios clonados
```

## O que é o Screenpipe?

O Screenpipe é uma plataforma open-source que transforma todo o histórico do seu desktop em uma fonte de contexto contínuo para aplicações de Inteligência Artificial.
Ele captura, processa, indexa e disponibiliza (localmente) tudo o que acontece na tela e no microfone, permitindo que agentes de IA entendam o que o usuário está fazendo e construam automações sobre isso.

### Saída gerada automaticamente pelo Summarizer do HuggingFace
> *“AI app store powered by 24/7 desktop history open source.  
> 100% local, uses 10% CPU, 4 GB ram, 15 gb/m.  
> Plugin system called ‘pipe’ which lets you create desktop apps in Next.js in a sandboxed environment within Rust.  
> 24/7 screen and mic recording — recording reality, one pixel at a time.  
> Store includes Stripe integration enabling devs to monetize their apps.”*


## Modelo 1 — BGE Base (BAAI/bge-base-en-v1.5)

Task: `Feature Extraction`

### Motivação:

### Objetivo:
Modelo de embeddings, ótimo para descoberta de arquivos relevantes, não para explicação de código.

### Resultado resumido da identificação
BGE Base identificou os arquivos mais relevantes do projeto para compreender a arquitetura do servidor:
```bash 
screenpipe-server/src/server.rs
screenpipe-server/src/server.rs (rotas de streaming)
screenpipe-server/tests/tags_test.rs
screenpipe-server/tests/endpoint_test.rs
screenpipe-server/src/bin/screenpipe-server.rs
```

### Conclusão:

## Modelo 2 - DeepSeek Coder (deepseek-ai/deepseek-coder-6.7b-instruct)

Task: `Text Generation`

### Motivação:
Depois que o modelo **BGE Base** identificou os arquivos mais relevantes do repositório (principalmente em `screenpipe-server` e `screenpipe-core`), o próximo passo foi **entender arquiteturalmente o papel de cada módulo**.

Para isso, usamos o DeepSeek Coder como um “arquiteto de software virtual”, pedindo que ele respondesse sempre às mesmas perguntas para cada trecho de código selecionado.  
O objetivo era obter respostas padronizadas, fáceis de comparar entre módulos.

O prompt utilizado foi:

> Você é um arquiteto de software experiente. Analise o código/trecho abaixo
> do projeto Screenpipe e responda:
>
> 1. Qual é a responsabilidade principal desse módulo?  
> 2. Em que parte da arquitetura ele se encaixa (core/captura, server/API, pipes/plugins, storage/db)?  
> 3. Com quais outros componentes ele provavelmente interage?  
> 4. Explique como o módulo gerencia pipes/plugins, incluindo download, execução, logs e watchdog.

Esse conjunto de perguntas força o modelo a responder **sempre em termos arquiteturais** (responsabilidade, camada, interações e, quando aplicável, gerenciamento de plugins/pipes).

### Objetivo:
Usar o DeepSeek Coder para:

- Descrever a **responsabilidade principal** de cada módulo analisado  
- Classificar cada módulo dentro de uma **camada da arquitetura** (core, captura, server/API, pipes/plugins, storage/db)  
- Identificar os **principais componentes com os quais ele interage**  
- No caso específico dos módulos de pipes/plugins, **explicar o ciclo de vida completo dos pipes**:
  - download
  - instalação
  - execução (processos externos)
  - monitoramento via logs
  - watchdog e limpeza de processos

### 📂 Arquivo: `screenpipe-server/src/server.rs`

1. **Responsabilidade principal**  
   O módulo gerencia a camada de API REST do Screenpipe, incluindo:
   - operações de busca  
   - streaming de conteúdo capturado  
   - gerenciamento da cache de quadros  
   - controle dos pipes (PipeManager)  
   - gerenciamento de áudio  
   - conexão WebSocket para streaming em tempo real  

2. **Camada arquitetural**  
   ➝ **server/API**  

3. **Componentes relacionados**
   - `screenpipe_core` – captura de conteúdo e controle de pipes  
   - `screenpipe_db` – persistência e busca  
   - `screenpipe_audio` – gerenciamento sonoro  
   - `screenpipe_vision` – OCR e visão computacional  
   - `screenpipe_events` – eventos do sistema  
   - `screenpipe_video_cache` – cache de quadros  
   - `screenpipe_embeddings` – geração de embeddings  

4. **Gestão de streaming/pipes/plugins**  
   - endpoints de WebSocket (`ws::WebSocketUpgrade`)  
   - endpoints de streaming de frames  
   - mecanismos de busca (`SearchQuery`)  
   - interação com cache, vídeo e eventos em tempo real  

---

### 📂 Arquivo: `screenpipe-core/src/ffmpeg.rs`

1. **Responsabilidade principal**  
   Localizar o executável **FFmpeg** no sistema e retornar seu caminho.

2. **Camada arquitetural**  
   ➝ **core / infraestrutura (captura)**  

3. **Componentes relacionados**
   - módulos que precisam de FFmpeg para captura e processamento  
   - libs externas:  
     - `ffmpeg_sidecar`  
     - `log`  
     - `once_cell::sync`  
     - `which`  
     - `std::env` / `std::path::PathBuf`

4. **Processo identificado**  
   O módulo procura o FFmpeg:
   - no diretório do executável (Linux)  
   - em diretórios de bibliotecas do próprio projeto  
   - no PATH do sistema  
   - no `$HOME/.local/bin` (macOS)  
   - no diretório atual  

   **Não instala** FFmpeg caso não encontre → funciona apenas como “localizador”, não instalador.

---

### 🧠 Conclusão do DeepSeek

O modelo forneceu respostas:

- coerentes  
- contextualizadas  
- com clara identificação de camadas  
- com entendimento real das dependências internas  
- e descrevendo corretamente como o Screenpipe usa FFmpeg e como estrutura seu servidor  

Foi o modelo que gerou **as respostas mais ricas para fins arquiteturais**.

Modelo 3 — StarCoder2-3B (second-state/StarCoder2-3B-GGUF)

Task: Text Generation / Code Understanding

Motivação

Depois de usar:

BGE Base → para localizar os arquivos mais relevantes no repositório

DeepSeek Coder 6.7B → para análises profundas com foco na arquitetura

o próximo passo foi utilizar o StarCoder2-3B como um modelo menor, barato e rápido, ideal para:

validar interpretações

gerar explicações “suficientemente boas”

analisar módulos menores

confirmar se o entendimento arquitetural já está consistente entre modelos

O foco deste teste era observar se um modelo de 3B parâmetros consegue fornecer alguma utilidade arquitetural, mesmo com limitações.

Objetivo

O objetivo do uso do StarCoder2-3B foi:

analisar trechos individuais do screenpipe-core

verificar se ele identifica responsabilidades básicas do módulo

checar se ele entende dependências externas (ex: FFmpeg)

confirmar se ele consegue explicar o ciclo de execução de captura de tela

Esse modelo não foi usado para análise arquitetural profunda, mas para validar o pipeline e testar consistência das respostas.

📂 Arquivo analisado: screenpipe-core/src/capture_loop.rs

🔍 Resultado produzido automaticamente pelo StarCoder2-3B (resumido)

O modelo identificou:

1. Responsabilidade principal

O StarCoder2-3B explicou corretamente que:

A função inicia a captura de tela

Configura um comando FFmpeg

Define FPS, dispositivo, codec e arquivo de saída

Atualiza estado de gravação com set_status(true/false)

Embora repetitivo, o modelo acertou a descrição da função operacional do código.

2. Camada arquitetural

Apesar de não usar os termos do seu framework (“core, server, pipes”), a descrição deixa claro:

Trata-se de funcionalidade de captura

Usa FFmpeg como mecanismo de captura

Portanto → core / captura

3. Componentes relacionados

O modelo identifica implicitamente:

dependência de FFmpeg

uso da API do sistema via std::process::Command

função get_ffmpeg_path()

função de estado set_status()

Mesmo não mencionando explicitamente o módulo, ele entendeu o fluxo externo.

4. Gestão de recursos

O modelo percebe que:

FFmpeg é chamado como processo externo

Há verificação de falha

A função só liga/desliga o estado, sem watchdog

Aqui ele acertou: o módulo realmente não monitora FFmpeg — apenas executa e reporta.


