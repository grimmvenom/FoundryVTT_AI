import torch
import node_helpers

from nodes import VAEEncode

import comfy.utils


class DNDPrepareCharacterReferences:
    """
    Prepare multiple D&D character reference images and attach them to
    Flux 2 conditioning as independent reference latents.

    Architecture:

        CHARACTER IMAGES
              |
              +--> Character 1 --> resize --> VAE encode --> reference latent 1
              |
              +--> Character 2 --> resize --> VAE encode --> reference latent 2
              |
              +--> Character 3 --> resize --> VAE encode --> reference latent 3
              |
              +--> Character N --> resize --> VAE encode --> reference latent N
              |
              v
        Scene CONDITIONING
              |
              +--> reference_latents[0]
              +--> reference_latents[1]
              +--> reference_latents[2]
              +--> ...
              |
              v
        CONDITIONING

    Each character reference is encoded independently.

    Character reference latents are deliberately NOT concatenated into a
    single LATENT batch. Each latent is registered independently through
    conditioning_set_values(..., append=True).

    This is intended to preserve separation between character identities
    and character-specific attributes when multiple characters are present.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # ----------------------------------------------------------
                # One or more character reference images.
                #
                # DNDPrepareCharacters produces IMAGE values for the
                # selected characters. Because this node uses
                # INPUT_IS_LIST = True, ComfyUI supplies the connected
                # values as a Python list.
                # ----------------------------------------------------------
                "character_images": (
                    "IMAGE",
                ),

                # ----------------------------------------------------------
                # Scene conditioning produced by DNDScenePrompt.
                # ----------------------------------------------------------
                "conditioning": (
                    "CONDITIONING",
                ),

                # ----------------------------------------------------------
                # Flux 2 VAE.
                # ----------------------------------------------------------
                "vae": (
                    "VAE",
                ),
            }
        }

    # ----------------------------------------------------------------------
    # Allow character_images to contain multiple values.
    #
    # NOTE:
    #
    # ComfyUI may also provide single-value inputs as lists when
    # INPUT_IS_LIST is enabled. We normalize those below.
    # ----------------------------------------------------------------------

    INPUT_IS_LIST = True

    RETURN_TYPES = (
        "CONDITIONING",
    )

    RETURN_NAMES = (
        "CONDITIONING",
    )

    FUNCTION = "prepare_references"

    CATEGORY = "D&D Images/Characters"

    # ======================================================================
    # Helpers
    # ======================================================================

    @staticmethod
    def _unwrap_single(value, name):
        """
        INPUT_IS_LIST=True causes non-list inputs to potentially arrive
        wrapped in a list.

        CONDITIONING and VAE are single logical values, so unwrap them.

        We intentionally do NOT use this for character_images because that
        input is genuinely 1:many.
        """

        if isinstance(value, list):

            if not value:
                raise ValueError(
                    f"Prepare Character References received no {name}."
                )

            return value[0]

        return value

    @staticmethod
    def _validate_image(image, index):
        """
        Validate a single IMAGE tensor.
        """

        if image is None:
            return None

        if not isinstance(image, torch.Tensor):
            raise ValueError(
                f"Character reference {index} is not a valid IMAGE tensor."
            )

        if image.ndim != 4:
            raise ValueError(
                f"Character reference {index} has invalid dimensions: "
                f"{tuple(image.shape)}"
            )

        if image.shape[0] <= 0:
            return None

        if image.shape[-1] != 3:
            raise ValueError(
                f"Character reference {index} does not appear to be an RGB "
                f"IMAGE tensor. Received shape: {tuple(image.shape)}"
            )

        return image

    @staticmethod
    def _split_image_batch(image):
        """
        Split an IMAGE tensor into individual images.

        ComfyUI IMAGE tensors normally have shape:

            [batch, height, width, channels]

        DNDPrepareCharacters may provide multiple character images through
        the list input mechanism, but a single connected IMAGE value can
        itself potentially contain a batch.

        We split the batch here so that each character gets its own
        independently encoded latent.

        Returns:

            [
                image_0,  # shape [1, H, W, C]
                image_1,  # shape [1, H, W, C]
                ...
            ]
        """

        if image.shape[0] == 1:
            return [image]

        return [
            image[index:index + 1]
            for index in range(image.shape[0])
        ]

    @staticmethod
    def _calculate_target_size(image):
        """
        Determine a suitable target size for a character reference.

        We preserve the image aspect ratio rather than forcing every
        reference into a 768x768 square.

        The longest dimension is capped at 768 pixels and the shortest
        dimension is rounded to a practical multiple of 16.

        This keeps the reference images reasonably sized for VAE encoding
        while avoiding unnecessary distortion.

        Returns:

            target_width,
            target_height
        """

        height = int(image.shape[1])
        width = int(image.shape[2])

        if width <= 0 or height <= 0:
            raise ValueError(
                f"Character reference has invalid dimensions: "
                f"{width}x{height}"
            )

        max_dimension = 768

        scale = min(
            1.0,
            max_dimension / max(width, height),
        )

        scaled_width = max(
            16,
            int(round(width * scale)),
        )

        scaled_height = max(
            16,
            int(round(height * scale)),
        )

        # --------------------------------------------------------------
        # Round dimensions to multiples of 16.
        # --------------------------------------------------------------

        target_width = max(
            16,
            (scaled_width // 16) * 16,
        )

        target_height = max(
            16,
            (scaled_height // 16) * 16,
        )

        return target_width, target_height

    @staticmethod
    def _resize_image(image):
        """
        Resize one character reference while preserving its aspect ratio.
        """

        target_width, target_height = (
            DNDPrepareCharacterReferences._calculate_target_size(image)
        )

        resized = comfy.utils.common_upscale(
            image.movedim(-1, 1),
            target_width,
            target_height,
            "lanczos",
            "center",
        ).movedim(
            1,
            -1,
        )

        return resized

    @staticmethod
    def _encode_image(vae, image, index):
        """
        VAE encode exactly one character reference.

        Returns only the latent samples tensor.

        The important property here is that this method is called
        independently for every character.
        """

        encoded_result = VAEEncode().encode(
            vae=vae,
            pixels=image,
        )

        if not encoded_result:
            raise ValueError(
                f"Unable to VAE encode character reference {index}."
            )

        latent = encoded_result[0]

        if latent is None:
            raise ValueError(
                f"VAE encoding produced no latent for "
                f"character reference {index}."
            )

        if not isinstance(latent, dict):
            raise ValueError(
                f"VAE encoding returned an unexpected value for "
                f"character reference {index}: "
                f"{type(latent).__name__}"
            )

        if "samples" not in latent:
            raise ValueError(
                f"VAE encoding produced no 'samples' tensor for "
                f"character reference {index}."
            )

        samples = latent["samples"]

        if not isinstance(samples, torch.Tensor):
            raise ValueError(
                f"VAE encoding produced an invalid 'samples' value for "
                f"character reference {index}."
            )

        if samples.ndim != 4:
            raise ValueError(
                f"VAE encoding produced an invalid latent shape for "
                f"character reference {index}: "
                f"{tuple(samples.shape)}"
            )

        return samples

    # ======================================================================
    # Main processing
    # ======================================================================

    def prepare_references(
        self,
        character_images,
        conditioning,
        vae,
    ):
        """
        Encode every character independently and append each latent to the
        scene conditioning.
        """

        # ==================================================================
        # Normalize character images
        # ==================================================================

        if character_images is None:
            raise ValueError(
                "Prepare Character References received no character images."
            )

        if not isinstance(character_images, list):
            character_images = [
                character_images
            ]

        # ==================================================================
        # Normalize single-value inputs.
        # ==================================================================

        conditioning = self._unwrap_single(
            conditioning,
            "conditioning",
        )

        vae = self._unwrap_single(
            vae,
            "VAE",
        )

        # ==================================================================
        # Validate conditioning
        # ==================================================================

        if conditioning is None:
            raise ValueError(
                "Prepare Character References received no conditioning."
            )

        if not isinstance(conditioning, list):
            raise ValueError(
                "Prepare Character References expected CONDITIONING "
                "to be a list."
            )

        # ==================================================================
        # Validate VAE
        # ==================================================================

        if vae is None:
            raise ValueError(
                "Prepare Character References received no VAE."
            )

        # ==================================================================
        # Expand IMAGE batches into individual character images.
        #
        # This is important:
        #
        # We never VAE encode a multi-character batch as one reference.
        #
        # Every resulting image is processed independently.
        # ==================================================================

        images = []

        character_number = 0

        for input_index, image in enumerate(
            character_images,
            start=1,
        ):

            validated = self._validate_image(
                image,
                input_index,
            )

            if validated is None:
                continue

            individual_images = self._split_image_batch(
                validated
            )

            for individual_image in individual_images:

                character_number += 1

                images.append(
                    individual_image
                )

        if not images:
            raise ValueError(
                "Prepare Character References received no valid "
                "character images."
            )

        # ==================================================================
        # Start with the original scene conditioning.
        #
        # We do not modify the original object in-place.
        # ==================================================================

        prepared_conditioning = conditioning

        # ==================================================================
        # Encode each character independently.
        # ==================================================================

        reference_count = 0

        for index, image in enumerate(
            images,
            start=1,
        ):

            # --------------------------------------------------------------
            # Resize only THIS character.
            # --------------------------------------------------------------

            resized = self._resize_image(
                image
            )

            # --------------------------------------------------------------
            # VAE encode only THIS character.
            # --------------------------------------------------------------

            samples = self._encode_image(
                vae,
                resized,
                index,
            )

            # --------------------------------------------------------------
            # Add THIS character as its own reference latent.
            #
            # IMPORTANT:
            #
            # We deliberately do NOT do:
            #
            #     torch.cat(...)
            #
            # and we do NOT create one large latent batch.
            #
            # Instead, every call appends one independent reference latent
            # to the conditioning.
            # --------------------------------------------------------------

            prepared_conditioning = (
                node_helpers.conditioning_set_values(
                    prepared_conditioning,
                    {
                        "reference_latents": [
                            samples
                        ]
                    },
                    append=True,
                )
            )

            reference_count += 1

        # ==================================================================
        # Safety check.
        # ==================================================================

        if reference_count == 0:
            raise ValueError(
                "Prepare Character References did not create any "
                "reference latents."
            )

        # ==================================================================
        # Return CONDITIONING.
        #
        # This output MUST connect directly to the positive conditioning
        # input of CFGGuider.
        #
        # It must NOT connect to ReferenceLatent.
        # ==================================================================

        return (
            prepared_conditioning,
        )


# ==========================================================================
# Node Registration
# ==========================================================================

NODE_CLASS_MAPPINGS = {
    "DNDPrepareCharacterReferences":
        DNDPrepareCharacterReferences,
}


NODE_DISPLAY_NAME_MAPPINGS = {
    "DNDPrepareCharacterReferences":
        "D&D Prepare Character References",
}