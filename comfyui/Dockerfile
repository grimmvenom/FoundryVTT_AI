FROM python:3.13-slim

EXPOSE 8188

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    COMFYUI_HOME=/opt/ComfyUI \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"

# ---------------------------------------------------------------------------
# System dependencies
# ---------------------------------------------------------------------------

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    libsndfile1 \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Python virtual environment
# ---------------------------------------------------------------------------

RUN python -m venv "${VIRTUAL_ENV}" \
    && pip install --upgrade pip setuptools wheel


# ---------------------------------------------------------------------------
# PyTorch
#
# Install the CUDA 13.0 wheels explicitly. NVIDIA GPU access is provided
# by the NVIDIA Container Toolkit on the host.
# ---------------------------------------------------------------------------

RUN pip install \
    --extra-index-url https://download.pytorch.org/whl/cu130 \
    torch torchvision torchaudio torchsde

# ---------------------------------------------------------------------------
# ComfyUI
# ---------------------------------------------------------------------------

RUN git clone --depth 1 \
    https://github.com/Comfy-Org/ComfyUI.git \
    "${COMFYUI_HOME}"

WORKDIR "${COMFYUI_HOME}"

# ---------------------------------------------------------------------------
# ComfyUI dependencies
#
# Install the dependencies defined by the version of ComfyUI we cloned.
# This keeps ComfyUI's dependency requirements synchronized with upstream.
# ---------------------------------------------------------------------------

RUN pip install -r requirements.txt

# ---------------------------------------------------------------------------
# Project / custom-node dependencies
# ---------------------------------------------------------------------------

COPY requirements.txt /tmp/project-requirements.txt

RUN pip install -r /tmp/project-requirements.txt


# ---------------------------------------------------------------------------
# ComfyUI Manager
# ---------------------------------------------------------------------------

RUN git clone --depth 1 \
    https://github.com/Comfy-Org/ComfyUI-Manager.git \
    "${COMFYUI_HOME}/custom_nodes/ComfyUI-Manager"

# ---------------------------------------------------------------------------
# Qwen3-TTS
# ---------------------------------------------------------------------------

RUN git clone --depth 1 \
    https://github.com/ai-joe-git/ComfyUI-Qwen3-TTS.git \
    "${COMFYUI_HOME}/custom_nodes/ComfyUI-Qwen3-TTS"

# ---------------------------------------------------------------------------
# Persistent data directories
# ---------------------------------------------------------------------------

RUN mkdir -p \
    /data/input \
    /data/output \
    /data/user \
    /data/models

COPY scripts/extra_model_paths.yaml "${COMFYUI_HOME}/extra_model_paths.yaml"


COPY scripts/download_flux2_models.sh /usr/local/bin/download_flux2_models.sh
RUN chmod +x /usr/local/bin/download_flux2_models.sh

COPY scripts/entrypoint.sh /usr/local/bin/comfyui-entrypoint
RUN chmod +x /usr/local/bin/comfyui-entrypoint




ENTRYPOINT ["/bin/bash", "/usr/local/bin/comfyui-entrypoint"]