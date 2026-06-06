FROM nvcr.io/nvidia/pytorch:24.07-py3

EXPOSE 8188

ENV PIP_NO_CACHE_DIR=1
ENV PIP_ROOT_USER_ACTION=ignore

# Core system dependencies
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    libsndfile1 \
    sox \
    libsox-fmt-all \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Clone ComfyUI into the pristine /app directory FIRST
RUN git clone https://github.com/comfyanonymous/ComfyUI.git .

# 2. Upgrade pip
RUN python3 -m pip install --upgrade pip

# 3. Overwrite with our stable CUDA 12.4 PyTorch stack
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 4. Inject core ML dependencies stripped out by the installer
RUN pip install torchsde einops transformers>=4.28.1 safetensors>=0.4.2

# 5. Clean and install remaining ComfyUI dependencies (safeguarding torch)
RUN sed -i '/torch/d' requirements.txt && \
    pip install -r requirements.txt

# 6. Inject ComfyUI-Manager
RUN git clone https://github.com/ltdrdata/ComfyUI-Manager.git ./custom_nodes/ComfyUI-Manager && \
    sed -i '/torch/d' ./custom_nodes/ComfyUI-Manager/requirements.txt && \
    pip install -r ./custom_nodes/ComfyUI-Manager/requirements.txt

# 7. Inject the advanced Qwen3-TTS custom node (wanaigc fork with Script Processor & SenseVoice ASR)
RUN git clone https://github.com/wanaigc/ComfyUI-Qwen3-TTS.git ./custom_nodes/ComfyUI-Qwen3-TTS

# 8. Clean and install custom node dependencies
RUN sed -i '/torch/d' ./custom_nodes/ComfyUI-Qwen3-TTS/requirements.txt && \
    pip install -r ./custom_nodes/ComfyUI-Qwen3-TTS/requirements.txt

# 9. Rebuild FlashAttention 2 targeting the local container layout
RUN pip install flash-attn --no-build-isolation --extra-index-url https://flashattentions.blob.core.windows.net/wheel

# 10. Fix the pre-installed OpenCV breaking type-hint loop via native shell patch
RUN OPENCV_PATH=$(python3 -c "import cv2, os; print(os.path.dirname(cv2.__file__))") && \
    if [ -f "$OPENCV_PATH/typing/__init__.py" ]; then \
        sed -i 's/LayerId = cv2.dnn.DictValue/# LayerId = cv2.dnn.DictValue/g' "$OPENCV_PATH/typing/__init__.py"; \
    fi

CMD ["python3", "main.py", "--listen", "0.0.0.0"]