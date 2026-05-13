FROM nvcr.io/nvidia/pytorch:24.03-py3

# Example for RTX 3090/4090 (compute 8.6 or 8.9)
# ENV MAX_JOBS=4 
# ENV FLASH_ATTENTION_FORCE_BUILD=TRUE

EXPOSE 50051

# Install / update system tools
RUN apt-get update && apt-get install -y \
    git ffmpeg libsndfile1 sox \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# install FLashAttention 2 to reduce GPU memory usage:
RUN pip install flash-attn --no-build-isolation --extra-index-url https://flashattentions.blob.core.windows.net/wheel
# RUN MAX_JOBS=4 TORCH_CUDA_ARCH_LIST="8.6;8.9" pip install flash-attn --no-build-isolation

# Clone the repo directly into /app
RUN git clone https://github.com/QwenLM/Qwen3-TTS.git .

# RUN pip install -r requirements.txt
RUN pip install -e .

CMD ["python3", "server.py", "--host", "0.0.0.0", "--port", "50051"]
# CMD ["tail", "-f", "/dev/null"]