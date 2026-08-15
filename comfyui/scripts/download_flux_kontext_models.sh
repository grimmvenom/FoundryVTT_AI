#!/usr/bin/env bash
# Deprecated: Use download_flux2_models.sh instead. This script will be removed in a future release.

set -euo pipefail

###############################################################################
# FLUX.1 Kontext Dev model installer for ComfyUI
#
# Installs the ComfyUI-compatible FLUX Kontext components into /data/models
#
# diffusion_models/
#   flux1-dev-kontext_fp8_scaled.safetensors
#
# text_encoders/
#   clip_l.safetensors
#   t5xxl_fp8_e4m3fn_scaled.safetensors
#
# vae/
#   ae.safetensors
#
# All downloads are from public Hugging Face repositories.
#
# No Hugging Face authentication/token is required.
#
# The model directory can be overridden with:
#
#   COMFYUI_MODELS=/some/path ./download_flux_kontext_models.sh
#
###############################################################################

COMFYUI_MODELS="${COMFYUI_MODELS:-/data/models}"

DIFFUSION_DIR="${COMFYUI_MODELS}/diffusion_models"
TEXT_ENCODER_DIR="${COMFYUI_MODELS}/text_encoders"
VAE_DIR="${COMFYUI_MODELS}/vae"

###############################################################################
# Hugging Face repositories
###############################################################################

KONTEXT_REPO="Comfy-Org/flux1-kontext-dev_ComfyUI"
KONTEXT_FILE="split_files/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors"

CLIP_REPO="comfyanonymous/flux_text_encoders"
CLIP_FILE="clip_l.safetensors"

T5_REPO="comfyanonymous/flux_text_encoders"
T5_FILE="t5xxl_fp8_e4m3fn_scaled.safetensors"

#
# IMPORTANT:
#
# Do NOT use:
#
#   black-forest-labs/FLUX.1-dev
#
# That repository is gated and requires Hugging Face approval.
#
# Comfy-Org/z_image contains the same ae.safetensors VAE with the
# exact same SHA256.
#
VAE_REPO="Comfy-Org/z_image"
VAE_FILE="split_files/vae/ae.safetensors"

###############################################################################
# Expected SHA256 values
###############################################################################

KONTEXT_SHA256="630ba795ec64283b4230ea23cf79406c2c68b7c578229ed139f30043eadb30a2"

CLIP_SHA256="660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c0c8576cd796491d9a6cdd"

T5_SHA256="a498f0485dc9536735258018417c3fd7758dc3bccc0a645feaa472b34955557a"

VAE_SHA256="afc8e28272cd15db3919bacdb6918ce9c1ed22e96cb12c4d5ed0fba823529e38"

###############################################################################
# Requirements
###############################################################################

if ! command -v sha256sum >/dev/null 2>&1; then
    echo "ERROR: sha256sum is required."
    exit 1
fi

if ! command -v hf >/dev/null 2>&1; then
    echo "ERROR: Hugging Face CLI (hf) is required."
    echo
    echo "Install it with:"
    echo
    echo "    pip install -U huggingface_hub"
    echo
    exit 1
fi

###############################################################################
# Directory setup
###############################################################################

echo
echo "============================================================"
echo " FLUX.1 Kontext Dev model installer"
echo "============================================================"
echo
echo "ComfyUI models:"
echo "  ${COMFYUI_MODELS}"
echo

mkdir -p \
    "${DIFFUSION_DIR}" \
    "${TEXT_ENCODER_DIR}" \
    "${VAE_DIR}"

###############################################################################
# Download helper
###############################################################################

download_model() {

    local repo="$1"
    local repo_file="$2"
    local destination="$3"
    local expected_sha256="$4"

    local filename
    filename="$(basename "${destination}")"

    echo
    echo "------------------------------------------------------------"
    echo "Model: ${filename}"
    echo "Repository: ${repo}"
    echo "File: ${repo_file}"
    echo "Destination: ${destination}"
    echo "------------------------------------------------------------"

    ###########################################################################
    # Existing file
    ###########################################################################

    if [[ -f "${destination}" ]]; then

        echo "File already exists."
        echo "Verifying SHA256..."

        local actual_sha256

        actual_sha256="$(
            sha256sum "${destination}" |
            awk '{print $1}'
        )"

        if [[ "${actual_sha256}" == "${expected_sha256}" ]]; then

            echo "SHA256 OK."
            echo "Skipping download."

            return 0
        fi

        echo
        echo "WARNING: Existing file failed SHA256 verification."
        echo
        echo "Expected:"
        echo "  ${expected_sha256}"
        echo
        echo "Actual:"
        echo "  ${actual_sha256}"
        echo
        echo "Removing invalid file."

        rm -f "${destination}"

    fi

    ###########################################################################
    # Temporary download directory
    ###########################################################################

    local temporary_dir

    temporary_dir="$(mktemp -d)"

    echo
    echo "Downloading..."
    echo

    if ! hf download \
        "${repo}" \
        "${repo_file}" \
        --local-dir "${temporary_dir}"
    then

        echo
        echo "ERROR: Hugging Face download failed."
        echo
        echo "Repository:"
        echo "  ${repo}"
        echo
        echo "File:"
        echo "  ${repo_file}"
        echo

        rm -rf "${temporary_dir}"

        exit 1
    fi

    ###########################################################################
    # Locate downloaded file
    ###########################################################################

    local downloaded_file="${temporary_dir}/${repo_file}"

    if [[ ! -f "${downloaded_file}" ]]; then

        echo
        echo "ERROR: Download completed but expected file was not found:"
        echo
        echo "  ${downloaded_file}"
        echo

        echo "Files downloaded:"
        find "${temporary_dir}" \
            -type f \
            -maxdepth 10 \
            -print \
            2>/dev/null || true

        rm -rf "${temporary_dir}"

        exit 1
    fi

    ###########################################################################
    # SHA256 verification
    ###########################################################################

    echo
    echo "Download complete."
    echo "Verifying SHA256..."

    local actual_sha256

    actual_sha256="$(
        sha256sum "${downloaded_file}" |
        awk '{print $1}'
    )"

    if [[ "${actual_sha256}" != "${expected_sha256}" ]]; then

        echo
        echo "ERROR: SHA256 verification failed."
        echo
        echo "File:"
        echo "  ${filename}"
        echo
        echo "Expected:"
        echo "  ${expected_sha256}"
        echo
        echo "Actual:"
        echo "  ${actual_sha256}"
        echo

        rm -rf "${temporary_dir}"

        exit 1
    fi

    echo "SHA256 OK."

    ###########################################################################
    # Install
    ###########################################################################

    mkdir -p "$(dirname "${destination}")"

    cp \
        "${downloaded_file}" \
        "${destination}"

    rm -rf "${temporary_dir}"

    echo
    echo "Installed:"
    echo "  ${destination}"
}

###############################################################################
# Kontext diffusion model
###############################################################################

download_model \
    "${KONTEXT_REPO}" \
    "${KONTEXT_FILE}" \
    "${DIFFUSION_DIR}/flux1-dev-kontext_fp8_scaled.safetensors" \
    "${KONTEXT_SHA256}"

###############################################################################
# CLIP-L
###############################################################################

download_model \
    "${CLIP_REPO}" \
    "${CLIP_FILE}" \
    "${TEXT_ENCODER_DIR}/clip_l.safetensors" \
    "${CLIP_SHA256}"

###############################################################################
# T5-XXL FP8 scaled
###############################################################################

download_model \
    "${T5_REPO}" \
    "${T5_FILE}" \
    "${TEXT_ENCODER_DIR}/t5xxl_fp8_e4m3fn_scaled.safetensors" \
    "${T5_SHA256}"

###############################################################################
# FLUX VAE
#
# This is ae.safetensors.
#
# The file is sourced from the public Comfy-Org/z_image repository because
# the official FLUX.1-dev repository is gated.
#
# SHA256:
#
#   afc8e28272cd15db3919bacdb6918ce9c1ed22e96cb12c4d5ed0fba823529e38
#
###############################################################################

download_model \
    "${VAE_REPO}" \
    "${VAE_FILE}" \
    "${VAE_DIR}/ae.safetensors" \
    "${VAE_SHA256}"

###############################################################################
# Final verification
###############################################################################

echo
echo "============================================================"
echo " FLUX.1 Kontext installation complete"
echo "============================================================"
echo

echo "Installed models:"
echo

ls -lh \
    "${DIFFUSION_DIR}/flux1-dev-kontext_fp8_scaled.safetensors" \
    "${TEXT_ENCODER_DIR}/clip_l.safetensors" \
    "${TEXT_ENCODER_DIR}/t5xxl_fp8_e4m3fn_scaled.safetensors" \
    "${VAE_DIR}/ae.safetensors"

echo
echo "Model directories:"
echo
echo "  ${DIFFUSION_DIR}"
echo "  ${TEXT_ENCODER_DIR}"
echo "  ${VAE_DIR}"
echo

echo "Done."