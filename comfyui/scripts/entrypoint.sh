#!/bin/bash
set -euo pipefail

COMFYUI_HOME="${COMFYUI_HOME:-/opt/ComfyUI}"
DATA_DIR="/data"

echo "========================================"
echo " Starting ComfyUI"
echo "========================================"
echo "ComfyUI: ${COMFYUI_HOME}"
echo "Data:    ${DATA_DIR}"
echo

# ---------------------------------------------------------------------------
# Persistent directories
# ---------------------------------------------------------------------------

mkdir -p \
    "${DATA_DIR}/models" \
    "${DATA_DIR}/input" \
    "${DATA_DIR}/output" \
    "${DATA_DIR}/user" \

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

if [ -e "${COMFYUI_HOME}/models" ] && [ ! -L "${COMFYUI_HOME}/models" ]; then
    rm -rf "${COMFYUI_HOME}/models"
fi

if [ ! -L "${COMFYUI_HOME}/models" ]; then
    ln -s "${DATA_DIR}/models" "${COMFYUI_HOME}/models"
fi

# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

if [ -e "${COMFYUI_HOME}/input" ] && [ ! -L "${COMFYUI_HOME}/input" ]; then
    rm -rf "${COMFYUI_HOME}/input"
fi

if [ ! -L "${COMFYUI_HOME}/input" ]; then
    ln -s "${DATA_DIR}/input" "${COMFYUI_HOME}/input"
fi

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

if [ -e "${COMFYUI_HOME}/output" ] && [ ! -L "${COMFYUI_HOME}/output" ]; then
    rm -rf "${COMFYUI_HOME}/output"
fi

if [ ! -L "${COMFYUI_HOME}/output" ]; then
    ln -s "${DATA_DIR}/output" "${COMFYUI_HOME}/output"
fi

# ---------------------------------------------------------------------------
# User data
# ---------------------------------------------------------------------------

if [ -e "${COMFYUI_HOME}/user" ] && [ ! -L "${COMFYUI_HOME}/user" ]; then
    rm -rf "${COMFYUI_HOME}/user"
fi

if [ ! -L "${COMFYUI_HOME}/user" ]; then
    ln -s "${DATA_DIR}/user" "${COMFYUI_HOME}/user"
fi

# ---------------------------------------------------------------------------
# Persistent custom nodes
#
# Custom nodes installed by the image remain in:
#
#   /opt/ComfyUI/custom_nodes/
#
# Additional nodes can be placed in:
#
#   /data/custom_nodes/
#
# They are linked into ComfyUI at startup.
# ---------------------------------------------------------------------------

for node in "${DATA_DIR}/custom_nodes/"*; do
    if [ -d "${node}" ]; then
        name="$(basename "${node}")"
        target="${COMFYUI_HOME}/custom_nodes/${name}"

        if [ ! -e "${target}" ]; then
            ln -s "${node}" "${target}"
        fi
    fi
done

# ---------------------------------------------------------------------------
# Display useful runtime information
# ---------------------------------------------------------------------------

echo
echo "Persistent data:"
echo "  Models:        ${DATA_DIR}/models"
echo "  Input:         ${DATA_DIR}/input"
echo "  Output:        ${DATA_DIR}/output"
echo "  User:          ${DATA_DIR}/user"
echo

# ---------------------------------------------------------------------------
# Start ComfyUI
# ---------------------------------------------------------------------------

cd "${COMFYUI_HOME}"

exec python main.py \
    --listen 0.0.0.0 \
    --port 8188 \
    --extra-model-paths-config /opt/ComfyUI/extra_model_paths.yaml \
    --enable-manager

