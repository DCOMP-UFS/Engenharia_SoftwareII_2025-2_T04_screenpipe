# -*- coding: utf-8 -*-
""" Modelo 4 Llama-3.1-8B.ipynb

Notebook para análise arquitetural utilizando o modelo Llama-3.1-8B.
"""

# Commented out IPython magic to ensure Python compatibility.
!apt-get install git -y  # Opcional, se o git não estiver instalado
!git clone https://github.com/mediar-ai/screenpipe.git
# %cd screenpipe

!pip install -q -U transformers accelerate
!pip install -q transformers sentencepiece

from huggingface_hub import login

# Execute esta célula. Uma caixa de diálogo irá aparecer pedindo seu token.
# Cole o token gerado no Passo 1 aqui.
login()

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from huggingface_hub import login # Certifique-se de executar login() ou configurar HF_TOKEN antes!

# 1. Defina o modelo Llama 3.1 (Substitua se estiver usando a versão 70B ou outra)
# Certifique-se de ter acesso liberado para este repositório no Hugging Face
model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"

# 2. Carregar o tokenizer e o modelo
# Mude o runtime do Colab para GPU T4 (ou A100, se disponível e necessário).
# torch_dtype=torch.bfloat16 é crucial para otimizar o uso da memória na GPU.
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# Crie o pipeline de geração de texto
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

# 3. Preparação do Prompt de Análise (Análise de QNFs para o Screenpipe)
contexto_do_projeto = """
Projeto: Screenpipe (Aplicação de Desktop para gravação e indexação de tela e áudio).
Padrão Arquitetural Dominante: Microkernel/Plugin (Core em Rust, Plugins/Pipes em Next.js/TypeScript).
QNFs Chave para Avaliação: Performance/Eficiência, Extensibilidade, Modularidade, Segurança/Privacidade.
Motivação da Arquitetura: Os componentes de alta performance (gravação/OCR) estão em Rust, enquanto a interface e extensões (Pipes) usam tecnologias web (Next.js) para rápida iteração e UI amigável.
"""

pergunta_analise = """
Como Engenheiro de Software Sênior, valide a adequação do padrão Microkernel/Plugin para as QNFs de Extensibilidade e Performance no contexto do Screenpipe.
1. Como a escolha do Rust contribui diretamente para a QNF de Performance neste contexto?
2. Como a estrutura de Pipes e a separação de tecnologias afetam a QNF de Extensibilidade?
3. Qual é a principal desvantagem arquitetural (trade-off) que a modularidade e as diferentes linguagens introduzem?
"""

messages = [
    {"role": "system", "content": "Você é um Engenheiro de Software Sênior especialista em padrões arquiteturais e Qualidades Não-Funcionais (QNFs). Forneça uma análise de engenharia de software baseada no contexto fornecido."},
    {"role": "user", "content": f"{contexto_do_projeto}\n\n{pergunta_analise}"}
]

# 4. Gerar a Resposta
input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt")
terminators = [
    tokenizer.eos_token_id,
    tokenizer.convert_tokens_to_ids("<|eot_id|>")
]
input_ids = input_ids.to(model.device)

print("\n--- RESPOSTA DO LLAMA 3.1 (Análise Arquitetural e de QNFs) ---")
output = model.generate(
    input_ids,
    max_new_tokens=1024,
    eos_token_id=terminators,
    do_sample=True,
    temperature=0.6,
    top_p=0.9
)

response = output[0][input_ids.shape[-1]:]
print(tokenizer.decode(response, skip_special_tokens=True))
print("\n-------------------------------------------------------------")
