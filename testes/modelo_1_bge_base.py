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

# =============================================================
#   BUSCA: CORE / PIPELINE PRINCIPAL
#   Foca na lógica central do Screenpipe: captura de tela,
#   pipeline de processamento, integração com FFmpeg e
#   componentes fundamentais do sistema.
# =============================================================
query = "ffmpeg integration, screen capture pipeline, core logic"

top_arquivosCore = buscar_arquivos_relevantes(query, top_k_arquivos=5)

print("\n=== TOP ARQUIVOS — CORE / PIPELINE ===\n")
for r in top_arquivosCore:
    print(f"{r['score']:.4f} | {r['arquivo']} | módulo: {r['modulo']}")

# =============================================================
#   BUSCA: SERVER / API / BACKEND
#   Foca nos arquivos responsáveis pela camada de servidor:
#   HTTP API, WebSocket, endpoints, streaming e lógica backend.
# =============================================================
query = "http server, websocket backend, api routes, streaming endpoints"

top_arquivosServer = buscar_arquivos_relevantes(query, top_k_arquivos=5)

print("\n=== TOP ARQUIVOS — SERVER / API / BACKEND ===\n")
for r in top_arquivosServer:
    print(f"{r['score']:.4f} | {r['arquivo']} | módulo: {r['modulo']}")


# =============================================================
#   BUSCA: STORAGE / DATABASE / INDEXAÇÃO
#   Foca na camada de armazenamento do Screenpipe:
#   base de dados, indexação, persistência e consultas.
# =============================================================
query = "database module, storage layer, indexing system, persistence"

top_arquivosStorage = buscar_arquivos_relevantes(query, top_k_arquivos=5)

print("\n=== TOP ARQUIVOS — STORAGE / DATABASE ===\n")
for r in top_arquivosStorage:
    print(f"{r['score']:.4f} | {r['arquivo']} | módulo: {r['modulo']}")


# =============================================================
#   BUSCA: VISÃO COMPUTACIONAL / OCR
#   Foca nos arquivos relacionados à análise de imagens:
#   OCR, visão computacional, pipelines de screenshot.
# =============================================================
query = "ocr, computer vision, image processing, screenshot analysis"

top_arquivosVc = buscar_arquivos_relevantes(query, top_k_arquivos=5)

print("\n=== TOP ARQUIVOS — VISÃO COMPUTACIONAL / OCR ===\n")
for r in top_arquivosVc:
    print(f"{r['score']:.4f} | {r['arquivo']} | módulo: {r['modulo']}")


# =============================================================
#   BUSCA: ÁUDIO / CAPTAÇÃO / PIPELINE SONORO
#   Foca no subsistema de áudio: gravação do microfone,
#   processamento sonoro, integração com FFmpeg e pipeline.
# =============================================================
query = "audio recording, microphone capture, audio pipeline, ffmpeg audio"

top_arquivosAudio = buscar_arquivos_relevantes(query, top_k_arquivos=5)

print("\n=== TOP ARQUIVOS — ÁUDIO / PIPELINE ===\n")
for r in top_arquivosAudio:
    print(f"{r['score']:.4f} | {r['arquivo']} | módulo: {r['modulo']}")




