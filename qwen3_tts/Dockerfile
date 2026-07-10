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

# Whisper dependencies
RUN pip install \
    faster-whisper \
    ctranslate2 \
    sentencepiece \
    av

RUN pip install openai-whisper


WORKDIR /app

# Clone ComfyUI into the pristine /app directory FIRST
RUN git clone https://github.com/comfyanonymous/ComfyUI.git .

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Overwrite with our stable CUDA 12.4 PyTorch stack
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Inject core ML dependencies stripped out by the installer
RUN pip install torchsde einops transformers>=4.28.1 safetensors>=0.4.2

# Fix optree warning & bridge the gap between ComfyUI and OpenCV using NumPy 1.25+
RUN pip install "optree>=0.13.0" "numpy>=1.25.0,<2.0.0"

# Clean and install remaining ComfyUI dependencies (safeguarding torch & numpy)
RUN sed -i '/torch/d' requirements.txt && \
    sed -i '/numpy/d' requirements.txt && \
    pip install -r requirements.txt

# Inject ComfyUI-Manager
RUN git clone https://github.com/ltdrdata/ComfyUI-Manager.git ./custom_nodes/ComfyUI-Manager && \
    sed -i '/torch/d' ./custom_nodes/ComfyUI-Manager/requirements.txt && \
    sed -i '/numpy/d' ./custom_nodes/ComfyUI-Manager/requirements.txt && \
    pip install -r ./custom_nodes/ComfyUI-Manager/requirements.txt

# Inject the flybirdxx Qwen-TTS custom node
RUN git clone https://github.com/flybirdxx/ComfyUI-Qwen-TTS.git ./custom_nodes/ComfyUI-Qwen-TTS

# Clean and install flybirdxx custom node dependencies
RUN if [ -f ./custom_nodes/ComfyUI-Qwen-TTS/requirements.txt ]; then \
        sed -i '/torch/d' ./custom_nodes/ComfyUI-Qwen-TTS/requirements.txt && \
        sed -i '/numpy/d' ./custom_nodes/ComfyUI-Qwen-TTS/requirements.txt && \
        pip install -r ./custom_nodes/ComfyUI-Qwen-TTS/requirements.txt; \
    fi


# Install ComfyUI-Whisper
RUN git clone https://github.com/yuvraj108c/ComfyUI-Whisper.git \
    ./custom_nodes/ComfyUI-Whisper

# Install Whisper node dependencies
RUN if [ -f ./custom_nodes/ComfyUI-Whisper/requirements.txt ]; then \
        pip install -r ./custom_nodes/ComfyUI-Whisper/requirements.txt; \
    fi

# Rebuild FlashAttention 2 targeting the local container layout
RUN pip install flash-attn --no-build-isolation --extra-index-url https://flashattentions.blob.core.windows.net/wheel

# Fix the pre-installed OpenCV breaking type-hint loop via native shell patch
RUN OPENCV_PATH=$(python3 -c "import cv2, os; print(os.path.dirname(cv2.__file__))") && \
    if [ -f "$OPENCV_PATH/typing/__init__.py" ]; then \
        sed -i 's/LayerId = cv2.dnn.DictValue/# LayerId = cv2.dnn.DictValue/g' "$OPENCV_PATH/typing/__init__.py"; \
    fi



CMD ["python3", "main.py", "--listen", "0.0.0.0"]