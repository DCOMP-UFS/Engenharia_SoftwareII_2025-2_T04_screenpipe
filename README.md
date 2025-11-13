# Análise Arquitetural do Projeto *screenpipe* utilizando Modelos do Hugging Face

Repositório dedicado à documentação e reprodução do processo de identificação de padrões arquiteturais no software Screenpipe, contendo o tutorial completo, código e artefatos necessários para a execução da atividade.

Este repositório documenta o processo de identificação de padrões arquiteturais no software **Screenpipe**, utilizando três modelos do Hugging Face:

- **BAAI/bge-base-en-v1.5**  
- **mistralai/Mistral-7B-Instruct-v0.3**  
- **second-state/StarCoder2-3B-GGUF**

## O que é o Screenpipe?

O Screenpipe é uma plataforma open-source que transforma todo o histórico do seu desktop em uma fonte de contexto contínuo para aplicações de Inteligência Artificial.
Ele captura, processa, indexa e disponibiliza (localmente) tudo o que acontece na tela e no microfone, permitindo que agentes de IA entendam o que o usuário está fazendo e construam automações sobre isso.

### Saída gerada automaticamente pelo Summarizer do HuggingFace
> *“AI app store powered by 24/7 desktop history open source.  
> 100% local, uses 10% CPU, 4 GB ram, 15 gb/m.  
> Plugin system called ‘pipe’ which lets you create desktop apps in Next.js in a sandboxed environment within Rust.  
> 24/7 screen and mic recording — recording reality, one pixel at a time.  
> Store includes Stripe integration enabling devs to monetize their apps.”*

## Configuração do Ambiente

Esta seção explica como preparar o ambiente para executar os modelos e reproduzir a análise arquitetural.

```bash
# 1. Instalar as bibliotecas necessárias
!pip install transformers accelerate bitsandbytes sentence-transformers Pillow datasets
!pip install -q git+https://github.com/huggingface/peft.git  # PEFT é útil para modelos grandes

# 2. Clonar o repositório ScreenPipe
!git clone https://github.com/mediar-ai/screenpipe.git
%cd screenpipe
!ls # Verifique os diretórios clonados
```

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

## Modelo 2 - Mistralai (mistralai/Mistral-7B-Instruct-v0.3)

Task: `Text Generation / Code Understanding`

### Motivação:
Após o modelo BGE Base identificar os arquivos mais relevantes do repositório (especialmente em screenpipe-server, screenpipe-core e screenpipe-db), era necessário analisar arquiteturalmente cada módulo encontrado.

Para isso utilizamos o Mistral-7B-Instruct, um modelo treinado para seguir instruções e interpretar código.
Ele foi usado como um “arquiteto de software virtual”, capaz de explicar responsabilidades, papéis e interações de cada módulo.

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
Usar o **Mistral-7B-Instruct** para:

- Descrever a **responsabilidade principal** de cada módulo analisado  
- Classificá-lo dentro de uma **camada da arquitetura** (core, captura, server/API, pipes/plugins, storage/db)  
- Identificar os **componentes com os quais o módulo interage**  
- Identificar ou inferir **endpoints** (busca, streaming, WebSocket) quando aplicável  

Essa etapa complementa o BGE Base, que identifica “onde olhar”, enquanto o Mistral explica “o que o módulo faz”.

### 📂 Resultados da Análise com Mistral

📌 Arquivo: `screenpipe-server/src/server.rs`

1. **Responsabilidade principal**  
   O módulo implementa a camada de **API REST e streaming** do Screenpipe, incluindo:
   - endpoints de busca  
   - streaming de conteúdo capturado  
   - gerência de caches de frames  
   - comunicação com o `PipeManager`  
   - integração com áudio (`AudioManager`)  
   - suporte a WebSocket para transmissão em tempo real  

2. **Camada arquitetural**  
   ➝ **server/API**

3. **Componentes relacionados**
   - `screenpipe_core` — captura de tela, UI e pipes  
   - `screenpipe_db` — banco de dados e busca  
   - `screenpipe_audio` — gerenciamento de áudio  
   - `screenpipe_vision` — OCR e visão computacional  
   - `screenpipe_events` — subsistema de eventos  
   - `screenpipe_video_cache` — cache de quadros  
   - `embedding_endpoint` — geração de embeddings  

4. **Streaming e busca identificados**
   - `WebSocketUpgrade` → endpoints de streaming de eventos e frames  
   - `SearchQuery` → endpoints de busca com paginação e múltiplos filtros  

---

📌 Arquivo: `screenpipe-core/src/ffmpeg.rs`

1. **Responsabilidade principal**  
   Localizar o executável **FFmpeg** no sistema e retornar seu caminho para uso pelos módulos de captura.

2. **Camada arquitetural**  
   ➝ **core / infraestrutura de captura**

3. **Componentes relacionados**
   - módulos que dependem de FFmpeg para captura e processamento  
   - bibliotecas auxiliares:  
     - `ffmpeg_sidecar`  
     - `which`  
     - `once_cell::sync`  
     - `log`  

4. **Processo identificado**
   O módulo busca o FFmpeg em:
   - diretórios locais (caminho do executável)  
   - caminhos internos do projeto  
   - variáveis de ambiente (`PATH`)  
   - `$HOME/.local/bin` no macOS  
   - diretório atual  

   Observação: **o módulo apenas localiza o binário**, não realiza instalação.

---

## 🧠 Conclusão do Mistral

O modelo Mistral apresentou:

- respostas **coerentes e consistentes**  
- identificação correta de **camadas arquiteturais**  
- compreensão adequada de **responsabilidades** e **dependências**  
- inferências corretas sobre **endpoints de busca e streaming**

Ele se mostrou eficaz para transformar trechos de código em conhecimento arquitetural claro, fornecendo insights diretamente utilizáveis na documentação do projeto.

---


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

## 📊 Comparação entre os Modelos Utilizados

| Modelo                             | Task HF / Tipo                     | Onde foi usado no projeto                          | Pontos fortes                                                                 | Limitações                                                                   | Papel na atividade                                          |
|------------------------------------|------------------------------------|----------------------------------------------------|-------------------------------------------------------------------------------|-------------------------------------------------------------------------------|-------------------------------------------------------------|
| **BAAI/bge-base-en-v1.5**          | Feature Extraction / Text Embedding | Repositório completo (`screenpipe-*`)              | Excelente para encontrar arquivos relevantes via similaridade semântica.      | Não explica código; não interpreta arquitetura.                              | Descoberta de contexto: ajuda a identificar **onde olhar**. |
| **Mistral-7B-Instruct-v0.3**       | Text Generation / Code Understanding | `screenpipe-server`, `screenpipe-core`, `ffmpeg.rs` | Análise profunda; entende responsabilidades, camadas e interações arquiteturais. | Modelo pesado; depende de prompts bem escritos.                               | “**Arquiteto virtual**”: descreve camadas, módulos e padrões. |
| **StarCoder2-3B-GGUF**             | Text Generation focado em código    | Funções específicas (`capture_loop.rs`, core)       | Leve e rápido; ótimo para explicar funções e dependências simples.            | Menos contexto; análise arquitetural menos completa.                          | Validador leve das análises do Mistral.                     |

