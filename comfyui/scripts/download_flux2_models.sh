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
#       full_encoder_small_decoder.safetensors
#
# No Hugging Face CLI or authentication is required.
#
# COMFYUI_MODELS can be overridden:
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
# The official BFL repository is gated.
# This is a public mirror of the exact file.
#
FLUX2_URL="https://huggingface.co/VixenQuest/flux2/resolve/main/flux-2-klein-9b-fp8.safetensors?download=true"


#
# Qwen 3 8B FP8 mixed
#
# Public Comfy-Org repository.
#
QWEN_URL="https://huggingface.co/Comfy-Org/flux2-klein-9B/resolve/main/split_files/text_encoders/qwen_3_8b_fp8mixed.safetensors?download=true"


#
# FLUX.2 VAE
#
VAE_URL="https://huggingface.co/Comfy-Org/flux2-klein-9B/resolve/main/split_files/vae/flux2-vae.safetensors?download=true"


#
# FLUX.2 Small Decoder / Full Encoder
#
# Official Black Forest Labs repository.
#
# This is the VAE used by the current ComfyUI FLUX.2 workflows.
#
FULL_ENCODER_SMALL_DECODER_URL="https://huggingface.co/black-forest-labs/FLUX.2-small-decoder/resolve/main/full_encoder_small_decoder.safetensors?download=true"


###############################################################################
# SHA256 checksums
###############################################################################

#
# FLUX.2 Klein 9B FP8
#
# 9,433,061,528 bytes
#
FLUX2_SHA256="865ba09f5b4c3cbd3468a4bd3acb9fcb2f8740c54317482f0bcd4ed1d3655cee"


#
# FLUX.2 Small Decoder / Full Encoder
#
# 249,519,092 bytes
#
FULL_ENCODER_SMALL_DECODER_SHA256="ea4273f02d1fafbf8e1d1c2cf6018ed8748652eb0bf34f2dd91171f16f15ab62"


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
echo "Hugging Face authentication is NOT required."
echo


###############################################################################
# Create directories
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
    local expected_sha256="${3:-}"

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

        if [[ -n "${expected_sha256}" ]]; then

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

        else

            echo "No checksum supplied."
            echo "Skipping download."

            return 0

        fi

    fi


    ###########################################################################
    # Temporary file
    ###########################################################################

    local temporary_file

    temporary_file="${destination}.download"

    rm -f "${temporary_file}"


    ###########################################################################
    # Download
    ###########################################################################

    echo
    echo "Downloading:"
    echo "${url}"
    echo

    if ! curl \
        --fail \
        --location \
        --retry 5 \
        --retry-delay 5 \
        --retry-all-errors \
        --progress-bar \
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
    # Verify checksum
    ###########################################################################

    if [[ -n "${expected_sha256}" ]]; then

        echo
        echo "Download complete."
        echo "Verifying SHA256..."

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

    fi


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
# FLUX.2 Klein 9B FP8
###############################################################################

download_model \
    "${FLUX2_URL}" \
    "${DIFFUSION_DIR}/flux-2-klein-9b-fp8.safetensors" \
    "${FLUX2_SHA256}"


###############################################################################
# Qwen 3 8B FP8 mixed
###############################################################################

download_model \
    "${QWEN_URL}" \
    "${TEXT_ENCODER_DIR}/qwen_3_8b_fp8mixed.safetensors"


###############################################################################
# FLUX.2 VAE
###############################################################################

download_model \
    "${VAE_URL}" \
    "${VAE_DIR}/flux2-vae.safetensors"


###############################################################################
# FLUX.2 Small Decoder / Full Encoder
###############################################################################

download_model \
    "${FULL_ENCODER_SMALL_DECODER_URL}" \
    "${VAE_DIR}/full_encoder_small_decoder.safetensors" \
    "${FULL_ENCODER_SMALL_DECODER_SHA256}"


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
    "${VAE_DIR}/flux2-vae.safetensors" \
    "${VAE_DIR}/full_encoder_small_decoder.safetensors"

echo
echo "Model directories:"
echo
echo "  ${DIFFUSION_DIR}"
echo "  ${TEXT_ENCODER_DIR}"
echo "  ${VAE_DIR}"
echo

echo "Done."