# =============================================================
#   INSTALAÇÃO DAS DEPENDÊNCIAS
# =============================================================
!pip install -q sentence-transformers transformers accelerate bitsandbytes

# =============================================================
#   IMPORTS
# =============================================================
import os
from sentence_transformers import SentenceTransformer
from tqdm.auto import tqdm
import numpy as np
from collections import defaultdict
from sentence_transformers.util import cos_sim

# =============================================================
#   DEFINIR O CAMINHO DO PROJETO SCREENPIPE
# =============================================================
BASE_DIR = "/content/screenpipe"   # <- ajuste aqui se necessário

# =============================================================
#   CARREGAR MODELO DE EMBEDDINGS BGE BASE
# =============================================================
embed_model_name = "BAAI/bge-base-en-v1.5"
embed_model = SentenceTransformer(embed_model_name, device="cuda")

print("Modelo de embeddings carregado:", embed_model_name)

# =============================================================
#   DEFINIÇÃO DE EXTENSÕES VÁLIDAS DO SCREENPIPE
# =============================================================
EXTENSOES_VALIDAS = (
    ".rs", ".ts", ".tsx", ".js", ".md",
    ".toml", ".yaml", ".yml"
)

# MÓDULOS DO SCREENPIPE – ISSO GARANTE QUE NÃO INDEXE ARQUIVOS DO COLAB
MODULOS_SCREENPIPE = [
    "screenpipe-core",
    "screenpipe-server",
    "screenpipe-db",
    "screenpipe-events",
    "screenpipe-audio",
    "screenpipe-vision",
    "screenpipe-app-tauri",
]

# =============================================================
#   COLETA DE ARQUIVOS COM CHUNKS
# =============================================================
docs = []

os.chdir(BASE_DIR)

for modulo in MODULOS_SCREENPIPE:
    modulo_path = os.path.join(BASE_DIR, modulo)

    if not os.path.exists(modulo_path):
        continue

    for root, dirs, files in os.walk(modulo_path):
        # ignorar diretórios ocultos
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for fname in files:
            if not fname.endswith(EXTENSOES_VALIDAS):
                continue

            path = os.path.join(root, fname)

            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except Exception:
                continue

            CHUNK_SIZE = 1000
            for i in range(0, len(text), CHUNK_SIZE):
                chunk = text[i:i+CHUNK_SIZE].strip()
                if chunk:
                    docs.append({
                        "texto": chunk,
                        "arquivo": path,
                        "modulo": modulo,
                        "offset": i,
                    })

print(f"Total de chunks coletados: {len(docs)}")
print("Exemplo:", docs[0]["arquivo"], "→", docs[0]["modulo"])

# =============================================================
#   GERAR EMBEDDINGS
# =============================================================
corpus_texts = [d["texto"] for d in docs]

embeddings = embed_model.encode(
    corpus_texts,
    batch_size=32,
    show_progress_bar=True,
    normalize_embeddings=True
)

print("Shape dos embeddings:", embeddings.shape)

# =============================================================
#   FUNÇÃO DE BUSCA POR TRECHOS
# =============================================================
def buscar_trechos(query, modulo=None, top_k=5):
    q_emb = embed_model.encode([query], normalize_embeddings=True)[0]

    scores = cos_sim(q_emb, embeddings)[0].cpu().numpy()

    indices_validos = list(range(len(docs)))
    if modulo:
        indices_validos = [
            i for i, d in enumerate(docs)
            if d["modulo"] == modulo
        ]

    scores_filtrados = np.array([scores[i] for i in indices_validos])
    top_idx_local = scores_filtrados.argsort()[::-1][:top_k]

    resultados = []
    for local_idx in top_idx_local:
        idx_global = indices_validos[local_idx]
        d = docs[idx_global]
        resultados.append({
            "score": float(scores[idx_global]),
            "arquivo": d["arquivo"],
            "modulo": d["modulo"],
            "offset": d["offset"],
            "texto": d["texto"],
        })

    return resultados

# =============================================================
#   FUNÇÃO: BUSCAR ARQUIVOS MAIS RELEVANTES
# =============================================================
def buscar_arquivos_relevantes(query, top_k_arquivos=10, top_k_chunks=200):
    trechos = buscar_trechos(query, modulo=None, top_k=top_k_chunks)

    melhor_por_arquivo = defaultdict(float)
    exemplo_por_arquivo = {}

    for t in trechos:
        arq = t["arquivo"]
        score = t["score"]

        if score > melhor_por_arquivo[arq]:
            melhor_por_arquivo[arq] = score
            exemplo_por_arquivo[arq] = t

    arquivos_ordenados = sorted(
        melhor_por_arquivo.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_k_arquivos]

    resultados = []
    for arq, score in arquivos_ordenados:
        t = exemplo_por_arquivo[arq]
        resultados.append({
            "arquivo": arq,
            "score": float(score),
            "modulo": t["modulo"],
            "offset": t["offset"],
            "preview": t["texto"][:400]
        })

    return resultados

# =============================================================
#   TESTE — BUSCA ARQUITETURA GERAL
# =============================================================
query = "arquitetura geral do sistema, componentes principais, organização do projeto, arquitetura de software"

top_arquivos = buscar_arquivos_relevantes(query, top_k_arquivos=10)

print("\n=== TOP ARQUIVOS MAIS RELEVANTES PARA ARQUITETURA ===\n")
for r in top_arquivos:
    print(f"{r['score']:.4f} | {r['arquivo']} | módulo: {r['modulo']}")
