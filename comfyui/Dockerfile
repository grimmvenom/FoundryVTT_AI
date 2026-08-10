FROM python:3.13-slim

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
# ComfyUI
# ---------------------------------------------------------------------------

RUN git clone --depth 1 \
        https://github.com/Comfy-Org/ComfyUI.git \
        "${COMFYUI_HOME}"

WORKDIR "${COMFYUI_HOME}"

# ---------------------------------------------------------------------------
# Python dependencies
# ---------------------------------------------------------------------------

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

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
        /data/models \
        /data/custom_nodes \
        /data/input \
        /data/output \
        /data/user \
        /data/workflows

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

COPY entrypoint.sh /usr/local/bin/comfyui-entrypoint

RUN chmod +x /usr/local/bin/comfyui-entrypoint

EXPOSE 8188

ENTRYPOINT ["/usr/local/bin/comfyui-entrypoint"]
