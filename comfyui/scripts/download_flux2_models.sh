#!/usr/bin/env bash

set -euo pipefail

###############################################################################
# FLUX.2 Klein 9B FP8 model installer for ComfyUI
#
# Installs:
#
#   diffusion_models/
#       flux-2-klein-9b-fp8.safetensors
#
#   text_encoders/
#       qwen_3_8b_fp8mixed.safetensors
#
#   vae/
#       flux2-vae.safetensors
#
# No Hugging Face authentication is required.
#
# The FLUX.2 Klein 9B FP8 diffusion model is downloaded from a public
# Hugging Face mirror because the official BFL repository is gated.
#
# The Qwen encoder and VAE are downloaded from the public Comfy-Org
# repositories.
#
# Override the model directory with:
#
#   COMFYUI_MODELS=/some/path ./download_flux2_models.sh
#
###############################################################################

COMFYUI_MODELS="${COMFYUI_MODELS:-/data/models}"

DIFFUSION_DIR="${COMFYUI_MODELS}/diffusion_models"
TEXT_ENCODER_DIR="${COMFYUI_MODELS}/text_encoders"
VAE_DIR="${COMFYUI_MODELS}/vae"


###############################################################################
# Public download URLs
###############################################################################

#
# FLUX.2 Klein 9B FP8
#
# Official BFL repository:
#
#   black-forest-labs/FLUX.2-klein-9b-fp8
#
# is gated.
#
# VixenQuest's public mirror contains the same file/Xet hash.
#
# File size:
#
#   ~9.43 GB
#
FLUX2_URL="https://huggingface.co/VixenQuest/flux2/resolve/main/flux-2-klein-9b-fp8.safetensors?download=true"

#
# Comfy-Org Qwen 3 8B FP8 mixed text encoder
#
QWEN_URL="https://huggingface.co/Comfy-Org/vae-text-encorder-for-flux-klein-9b/resolve/main/split_files/text_encoders/qwen_3_8b_fp8mixed.safetensors?download=true"

#
# Comfy-Org FLUX.2 VAE
#
VAE_URL="https://huggingface.co/Comfy-Org/vae-text-encorder-for-flux-klein-9b/resolve/main/split_files/vae/flux2-vae.safetensors?download=true"


###############################################################################
# Expected SHA256 values
###############################################################################

#
# FLUX.2 Klein 9B FP8
#
# Verified against the public VixenQuest mirror.
#
FLUX2_SHA256="865ba09f5b4c3cbd3468a4bd3acb9fcb2f8740c54317482f0bcd4ed1d3655cee"

#
# Qwen 3 8B FP8 mixed
#
QWEN_SHA256="abad16806e0cbabc54e0325d6565847443fe396d5f0be38bb3cd3fe75a1201d6"

#
# FLUX.2 VAE
#
VAE_SHA256="868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3"


###############################################################################
# Requirements
###############################################################################

if ! command -v sha256sum >/dev/null 2>&1; then
    echo "ERROR: sha256sum is required."
    exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
    echo "ERROR: curl is required."
    exit 1
fi


###############################################################################
# Header
###############################################################################

echo
echo "============================================================"
echo " FLUX.2 Klein 9B FP8 model installer"
echo "============================================================"
echo
echo "ComfyUI models:"
echo "  ${COMFYUI_MODELS}"
echo
echo "No Hugging Face authentication is required."
echo


###############################################################################
# Directory setup
###############################################################################

mkdir -p \
    "${DIFFUSION_DIR}" \
    "${TEXT_ENCODER_DIR}" \
    "${VAE_DIR}"


###############################################################################
# Download helper
###############################################################################

download_model() {

    local url="$1"
    local destination="$2"
    local expected_sha256="$3"

    local filename
    filename="$(basename "${destination}")"

    echo
    echo "------------------------------------------------------------"
    echo "Model: ${filename}"
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
    # Temporary file
    ###########################################################################

    local temporary_file

    temporary_file="$(
        mktemp "${destination}.download.XXXXXX"
    )

    echo
    echo "Downloading..."
    echo
    echo "${url}"
    echo


    ###########################################################################
    # Download
    ###########################################################################

    if ! curl \
        --fail \
        --location \
        --retry 5 \
        --retry-delay 5 \
        --retry-all-errors \
        --continue-attempts \
        --output "${temporary_file}" \
        "${url}"
    then

        echo
        echo "ERROR: Download failed."
        echo
        echo "URL:"
        echo "  ${url}"
        echo

        rm -f "${temporary_file}"

        exit 1
    fi


    ###########################################################################
    # SHA256 verification
    ###########################################################################

    echo
    echo "Download complete."
    echo "Verifying SHA256..."
    echo

    local actual_sha256

    actual_sha256="$(
        sha256sum "${temporary_file}" |
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
        echo "The downloaded file will NOT be installed."
        echo

        rm -f "${temporary_file}"

        exit 1
    fi


    echo "SHA256 OK."


    ###########################################################################
    # Install
    ###########################################################################

    mv \
        "${temporary_file}" \
        "${destination}"

    echo
    echo "Installed:"
    echo "  ${destination}"
}


###############################################################################
# FLUX.2 Klein 9B FP8 diffusion model
###############################################################################

download_model \
    "${FLUX2_URL}" \
    "${DIFFUSION_DIR}/flux-2-klein-9b-fp8.safetensors" \
    "${FLUX2_SHA256}"


###############################################################################
# Qwen 3 8B FP8 mixed text encoder
###############################################################################

download_model \
    "${QWEN_URL}" \
    "${TEXT_ENCODER_DIR}/qwen_3_8b_fp8mixed.safetensors" \
    "${QWEN_SHA256}"


###############################################################################
# FLUX.2 VAE
###############################################################################

download_model \
    "${VAE_URL}" \
    "${VAE_DIR}/flux2-vae.safetensors" \
    "${VAE_SHA256}"


###############################################################################
# Final verification
###############################################################################

echo
echo "============================================================"
echo " FLUX.2 Klein 9B installation complete"
echo "============================================================"
echo

echo "Installed models:"
echo

ls -lh \
    "${DIFFUSION_DIR}/flux-2-klein-9b-fp8.safetensors" \
    "${TEXT_ENCODER_DIR}/qwen_3_8b_fp8mixed.safetensors" \
    "${VAE_DIR}/flux2-vae.safetensors"

echo
echo "Model directories:"
echo
echo "  ${DIFFUSION_DIR}"
echo "  ${TEXT_ENCODER_DIR}"
echo "  ${VAE_DIR}"
echo

echo "Done."