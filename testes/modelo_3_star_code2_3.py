# -*- coding: utf-8 -*-
"""Modelo 3 - StarCoder2-3B.ipynb

Notebook para análise arquitetural utilizando o modelo StarCoder2-3B.
"""

# ============================================================
# 1. Instalar dependências
# ============================================================
!pip install transformers accelerate bitsandbytes datasets
!pip install -q git+https://github.com/huggingface/peft.git

# ============================================================
# 2. Clonar o repositório ScreenPipe
# ============================================================
!git clone https://github.com/mediar-ai/screenpipe.git
!ls

# Comentado propositalmente para não trocar o diretório global
# %cd screenpipe

# ============================================================
# 3. Carregar o modelo StarCoder2-3B
# ============================================================
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "second-state/StarCoder2-3B-GGUF"

tokenizer = AutoTokenizer.from_pretrained("bigcode/starcoder2-3b")
model = AutoModelForCausalLM.from_pretrained(
    "bigcode/starcoder2-3b",
    device_map="auto",
    torch_dtype=torch.float16,
)

print("Modelo carregado:", model_name)

# ============================================================
# 4. Carregar arquivos do repositório
# ============================================================
import os

EXTENSOES_VALIDAS = (".rs", ".ts", ".tsx", ".js", ".md", ".toml", ".yaml", ".yml")

docs = []

for root, dirs, files in os.walk("./screenpipe"):
    for fname in files:
        if fname.endswith(EXTENSOES_VALIDAS):
            path = os.path.join(root, fname)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except:
                continue

            rel = path.replace("./screenpipe/", "")
            modulo = rel.split(os.sep)[0]

            # chunk 1000 chars
            CHUNK_SIZE = 1000
            for i in range(0, len(text), CHUNK_SIZE):
                chunk = text[i:i+CHUNK_SIZE]
                if chunk.strip():
                    docs.append({
                        "texto": chunk,
                        "arquivo": path,
                        "modulo": modulo,
                        "offset": i,
                    })

print("Chunks carregados:", len(docs))
print("Exemplo:", docs[0]["arquivo"], "| módulo:", docs[0]["modulo"])

# ============================================================
# 5. Função de análise arquitetural usando StarCoder2-3B
# ============================================================

def analisar_codigo(texto):
    """
    Gera uma análise arquitetural automática usando o StarCoder2-3B.
    """
    prompt = f"""
Você é um arquiteto de software experiente. Analise o código abaixo e responda:

1. Qual é a responsabilidade principal desse módulo?
2. Em que parte da arquitetura ele se encaixa (core/captura, server/API, pipes/plugins, storage/db)?
3. Com quais outros componentes ele provavelmente interage?
4. Ele gerencia recursos? Como?

Código analisado:
{texto}

Responda de forma clara e objetiva.
"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    output = model.generate(
        **inputs,
        max_new_tokens=350,
        do_sample=True,
        temperature=0.4,
        top_p=0.95,
    )

    resposta = tokenizer.decode(output[0], skip_special_tokens=True)
    return resposta[len(prompt):].strip()

# ============================================================
# 6. Buscar trechos por módulo (similar ao Modelo 1)
# ============================================================

def buscar_trechos(modulo=None, top_k=3):
    """
    Retorna os primeiros trechos de um módulo (simplificado para StarCoder).
    """
    filtrados = [d for d in docs if d["modulo"] == modulo] if modulo else docs
    return filtrados[:top_k]

# ============================================================
# 7. Teste no arquivo capture_loop.rs (como no relatório)
# ============================================================

resultados = buscar_trechos(modulo="screenpipe-core", top_k=1)

for r in resultados:
    print("="*80)
    print("Arquivo:", r["arquivo"])
    print("Offset:", r["offset"])
    print("Trecho:\n", r["texto"])

    print("\n### Análise do StarCoder2-3B ###")
    analise = analisar_codigo(r["texto"])
    print(analise)
    print("="*80)