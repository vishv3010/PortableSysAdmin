import os
import sys
import platform
import urllib.request
import zipfile
import tarfile
from urllib.error import URLError

def download_file(url, dest):
    print(f"Downloading from {url}...")
    try:
        urllib.request.urlretrieve(url, dest, reporthook=progress_hook)
        print("\nDownload complete.")
    except URLError as e:
        print(f"\n[ERROR] Failed to download {url}: {e}")
        sys.exit(1)

def progress_hook(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size)
    if percent > 100:
        percent = 100
    sys.stdout.write(f"\rProgress: {percent}%")
    sys.stdout.flush()

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bin_dir = os.path.join(project_root, "bin")
    models_dir = os.path.join(project_root, "models")
    
    os.makedirs(bin_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    
    sys_os = platform.system().lower()
    
    # 1. Download llama-server
    print("=== Step 1: Downloading Local AI Server (llama.cpp) ===")
    
    # Using a stable, known release version for compatibility
    LLAMA_CPP_VER = "b3600"
    
    if sys_os == "windows":
        server_url = f"https://github.com/ggerganov/llama.cpp/releases/download/{LLAMA_CPP_VER}/llama-{LLAMA_CPP_VER}-bin-win-avx2-x64.zip"
        zip_path = os.path.join(bin_dir, "llama.zip")
        download_file(server_url, zip_path)
        
        print("Extracting llama-server.exe...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if file.endswith("llama-server.exe"):
                    # Extract specifically the server binary
                    source = zip_ref.open(file)
                    target_path = os.path.join(bin_dir, "llama-server.exe")
                    with open(target_path, "wb") as target:
                        target.write(source.read())
        os.remove(zip_path)
        
    elif sys_os == "linux":
        server_url = f"https://github.com/ggerganov/llama.cpp/releases/download/{LLAMA_CPP_VER}/llama-{LLAMA_CPP_VER}-bin-ubuntu-x64.zip"
        zip_path = os.path.join(bin_dir, "llama.zip")
        download_file(server_url, zip_path)
        
        print("Extracting llama-server...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if file.endswith("llama-server"):
                    source = zip_ref.open(file)
                    target_path = os.path.join(bin_dir, "llama-server")
                    with open(target_path, "wb") as target:
                        target.write(source.read())
        os.remove(zip_path)
        os.chmod(os.path.join(bin_dir, "llama-server"), 0o755)
        
    else:
        print(f"[ERROR] Unsupported OS for automated setup: {sys_os}")
        sys.exit(1)

    # 2. Download AI Model
    print("\n=== Step 2: Downloading AI Model (Phi-3 Mini 4k Instruct) ===")
    print("Note: This is a ~2.4GB file. This may take a while depending on your internet connection.")
    model_url = "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
    model_path = os.path.join(models_dir, "model.gguf")
    
    if os.path.exists(model_path):
        print("Model already exists. Skipping download.")
    else:
        download_file(model_url, model_path)
        
    print("\n=== Setup Complete! ===")
    print("You can now start the AI server by running: ")
    if sys_os == "windows":
        print(f"   {os.path.join(bin_dir, 'llama-server.exe')} -m {model_path} --port 8080")
    else:
        print(f"   {os.path.join(bin_dir, 'llama-server')} -m {model_path} --port 8080")

if __name__ == "__main__":
    main()
