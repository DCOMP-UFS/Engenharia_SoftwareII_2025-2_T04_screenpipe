import os
import re
from bs4 import BeautifulSoup
from tqdm import tqdm

def clean_html(text):
    soup = BeautifulSoup(text, "html.parser")
    clean_text = soup.get_text(" ", strip=True)
    clean_text = re.sub(r"http\S+", "", clean_text)
    clean_text = re.sub(r"\s+", " ", clean_text)
    clean_text = re.sub(r"[^\x00-\x7F]+", "", clean_text)
    return clean_text.strip()

def clean_folder(input_folder="raw", output_folder="parsed"):
    os.makedirs(output_folder, exist_ok=True)
    files = [f for f in os.listdir(input_folder) if f.endswith(".txt")]

    for filename in tqdm(files, desc="Limpando HTML"):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        with open(input_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        clean_text = clean_html(html_content)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(clean_text)

if __name__ == "__main__":
    clean_folder("raw", "parsed")
