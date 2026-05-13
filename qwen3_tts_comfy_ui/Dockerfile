FROM nvidia/cuda:12.1.1-base-ubuntu22.04

EXPOSE 8188

RUN apt-get update && apt-get install -y \
    python3-pip git ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git .

# Install Core ComfyUI requirements
RUN pip install --no-cache-dir -r requirements.txt

# Clone DarioFT's Node
RUN git clone https://github.com/DarioFT/ComfyUI-Qwen3-TTS.git ./custom_nodes/ComfyUI-Qwen3-TTS

# Install Node requirements (pointing to the specific path)
RUN pip install --no-cache-dir -r ./custom_nodes/ComfyUI-Qwen3-TTS/requirements.txt


CMD ["python3", "main.py", "--listen", "0.0.0.0"]