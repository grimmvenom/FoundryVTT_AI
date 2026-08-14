from .character_utils import (
    list_characters,
    character_from_library,
    apply_character_reference,
    characters_root,
)


class DNDCharacterReference:
    """
    Apply one persistent character from the character library.

    Outputs:

        IMAGE
        CHARACTER
        CONDITIONING

    CONDITIONING is compatible with D&D Character Editor and another
    D&D Character Reference node, allowing multiple character references
    to be chained before FluxKontextMultiReferenceLatentMethod.
    """

    @classmethod
    def INPUT_TYPES(cls):
        characters = list_characters()

        if not characters:
            characters = ["<no characters found>"]

        return {
            "required": {
                "character": (
                    characters,
                ),

                "conditioning": (
                    "CONDITIONING",
                ),

                "vae": (
                    "VAE",
                ),
            }
        }

    RETURN_TYPES = (
        "IMAGE",
        "CHARACTER",
        "CONDITIONING",
    )

    RETURN_NAMES = (
        "IMAGE",
        "CHARACTER",
        "CONDITIONING",
    )

    FUNCTION = "apply_reference"
    CATEGORY = "D&D Images/Characters"

    def apply_reference(
        self,
        character,
        conditioning,
        vae,
    ):
        if character.startswith("<"):
            raise ValueError(
                f"No characters found in {characters_root()}."
            )

        character_data, image = character_from_library(
            character
        )

        referenced_conditioning = apply_character_reference(
            image=image,
            conditioning=conditioning,
            vae=vae,
        )

        return (
            image,
            character_data,
            referenced_conditioning,
        )


NODE_CLASS_MAPPINGS = {
    "DNDCharacterReference": DNDCharacterReference,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DNDCharacterReference": "D&D Character Reference",
}