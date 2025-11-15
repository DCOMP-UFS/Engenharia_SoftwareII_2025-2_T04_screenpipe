  
# 🖥️ Executando o Projeto Screenpipe Localmente

Este tutorial documenta como instalar, compilar e executar o Screenpipe — o sistema alvo analisado na nossa atividade de identificação de padrões arquiteturais.

Incluímos *scripts automatizados* para facilitar todo o processo.

---
## ✅ 1. Requisitos

Antes de executar o Screenpipe, instale:

- **Rust + Cargo**  

- **Git**

- **FFmpeg**

- **Linux, macOS ou Windows**

- (Opcional) GPU com suporte a aceleração

---
## 🚀 2. Baixar o Projeto Screenpipe


Clone o repositório oficial:

```bash
git clone https://github.com/mediar-ai/screenpipe.git

cd screenpipe
```

---
## 🛠️ 3. Compilar o Projeto

O Screenpipe é escrito em **Rust**. Para compilar:

```bash
cargo build --release
```

Este comando irá gerar os binários otimizados em:

```
target/release/
```
---
## ▶️ 4. Executar o Servidor principal do Screenpipe

O Screenpipe possui diversos binários, mas o principal para execução do backend é:

```bash
./target/release/screenpipe-server
```

Este comando inicializa:
- A API HTTP  
- O WebSocket para streaming de eventos  
- O pipeline central de captura  
- O módulo de indexação e consulta  

A saída no terminal exibirá logs confirmando os módulos inicializados.

---
## ⚙️ 5. Execução Automatizada via Script

Para facilitar, incluímos scripts no repositório:
```
scripts/run_screenpipe.py
```

Para rodar:
```bash

python scripts/run_screenpipe.py

```

Ambos os scripts realizam:
1. Verificação de Rust  
2. Instalação de dependências  
3. Compilação com Cargo  
4. Execução do servidor  

---
## 📌 7. Observações Gerais

- O Screenpipe depende de **FFmpeg** para manipulação de mídia.  

  Verifique se o comando `ffmpeg` funciona no terminal.

- A primeira compilação pode demorar por causa do download das crates do Rust.

- Se for usar a interface gráfica (Electron/Tauri), o processo de build é diferente.