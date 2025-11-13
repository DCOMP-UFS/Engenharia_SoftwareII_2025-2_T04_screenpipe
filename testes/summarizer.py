import os
from transformers import pipeline

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
    tokenizer="facebook/bart-large-cnn",
    truncation=True,
    device=0  # usa GPU (CUDA)
)

def chunk_text(text, max_words=1000):
    sentences = text.split(". ")
    chunks, current = [], ""
    for sentence in sentences:
        if len((current + sentence).split()) > max_words:
            chunks.append(current.strip())
            current = sentence
        else:
            current += ". " + sentence
    if current:
        chunks.append(current.strip())
    return chunks

def summarize_text(text):
    chunks = chunk_text(text)
    results = []

    for chunk in chunks:
        try:
            summary = summarizer(
                chunk,
                max_length=250,     # aumenta comprimento final (resumo mais detalhado)
                min_length=80,      # mantém densidade de informação
                do_sample=True,     # sampling dá mais variedade e riqueza lexical
                temperature=0.8,    # controla criatividade
                top_p=0.95,         # nucleus sampling
                repetition_penalty=1.1,  # evita repetições
                length_penalty=1.5, # favorece resumos mais longos
                truncation=True
            )
            results.append(summary[0]["summary_text"])
        except Exception as e:
            print("Erro ao resumir chunk:", e)

    return "\n".join(results)

def summarize_folder(input_folder="parsed", output_folder="results"):
    os.makedirs(output_folder, exist_ok=True)
    for filename in os.listdir(input_folder):
        if not filename.endswith(".txt"):
            continue

        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, f"summary_{filename}")

        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        print(f"📄 Resumindo: {filename}")
        summary = summarize_text(text)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"✅ Salvo em: {output_path}\n")

if __name__ == "__main__":
    summarize_folder("parsed", "results")
