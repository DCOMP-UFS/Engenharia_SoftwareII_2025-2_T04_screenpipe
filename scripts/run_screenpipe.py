import os
import subprocess
import sys
import platform

print("=== Screenpipe - Setup e Execução ===")

# Verifica OS
if platform.system() != "Windows":
    print("Use run_screenpipe.sh para Linux/Mac.")
    sys.exit()

# 1. Verificar Rust
try:
    subprocess.run(["cargo", "--version"], check=True)
    print("Rust e Cargo encontrados!")
except:
    print("Rust não encontrado. Instale manualmente via https://rustup.rs/")
    sys.exit()

# 2. Compilar projeto
os.chdir("screenpipe")
subprocess.run(["cargo", "build", "--release"], check=True)

# 3. Rodar server
subprocess.run(["target\\release\\screenpipe-server"])