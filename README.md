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

## Modelo 3 — StarCoder2-3B (second-state/StarCoder2-3B-GGUF)

Task: `Text Generation / Code Understanding`

### Motivação

Após utilizar:

BGE Base → para identificar os arquivos mais relevantes no repositório

DeepSeek Coder 6.7B → para análises profundas e respostas arquiteturais completas

- o próximo passo foi testar o StarCoder2-3B, um modelo menor e mais leve, com o objetivo de verificar:
- consistência das interpretações
- rapidez na análise de módulos simples
- capacidade de compreender responsabilidades básicas do código

- O foco não era obter uma análise arquitetural profunda, mas sim validar o pipeline e medir até onde um modelo pequeno pode ajudar no entendimento geral.

### Objetivo
Usar o StarCoder2-3B para:

- Analisar trechos menores do screenpipe-core
- Identificar a responsabilidade principal de funções isoladas
- Compreender dependências externas (ex: FFmpeg)
- Verificar se o modelo entende o fluxo de captura de tela
- Validar a coerência com as respostas dos modelos anteriores

O modelo foi usado como um validador leve, e não como fonte primária de arquitetura.

### 📂 Arquivo analisado: screenpipe-core/src/capture_loop.rs
Resultado resumido da identificação

O StarCoder2-3B analisou corretamente o módulo e descreveu:

1. **Responsabilidade principal**
O modelo explicou que o objetivo da função é:

- iniciar o processo de captura de tela
- montar o comando FFmpeg
- definir parâmetros como FPS, codec e dispositivo
- iniciar a gravação chamando o processo externo
- atualizar o estado global (set_status(true/false))
- 
A descrição, embora simples, está alinhada funcionalmente com o papel do arquivo.

2. **Camada arquitetural**

Mesmo sem usar a nomenclatura formal (“core / server / pipes”), o modelo identificou que o código:

- faz parte da lógica de captura
- utiliza FFmpeg diretamente
- pertence claramente ao core do sistema

## → Conclusão: core / captura

3. **Componentes relacionados**

O modelo identificou implicitamente que o módulo depende de:

- FFmpeg (via Command)
- função get_ffmpeg_path()
- sistema operacional (processos externos)
- função de estado set_status()

Mesmo sem nomear os módulos explicitamente, reconheceu corretamente o fluxo de dependências.

4. **Gestão de recursos**

O modelo entendeu que:

- FFmpeg é executado como processo externo
- há detecção básica de falhas
- o módulo não faz gerenciamento avançado (watchdog, restart, logs)
- apenas inicia ou finaliza a captura e atualiza o estado

Essa leitura está correta: este arquivo realmente não gerencia lifecycle completo, apenas a invocação.

### 🧠 Conclusão do StarCoder2-3B

O modelo, mesmo sendo pequeno (3B), conseguiu:

- identificar a responsabilidade operacional
- entender dependências externas
- categorizar a camada arquitetural
- reconhecer corretamente as limitações do módulo

Embora não forneça análises profundas como o DeepSeek, ele é útil como:

- validador rápido
- analisador de módulos menores
- reforço para consistência das interpretações
