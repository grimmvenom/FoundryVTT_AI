from .character_utils import (
    safe_id,
    split_lines,
    save_character_data,
    make_character,
    apply_character_reference,
)


class DNDCharacterEditor:
    """
    Create or edit a character from an arbitrary reference image.

    The character does NOT need to be saved.

    When save_character is false:
        The node still produces IMAGE, CHARACTER, and CONDITIONING.

    When save_character is true:
        The character definition is persisted to the character library.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "character_name": (
                    "STRING",
                    {
                        "default": "New Character",
                    },
                ),

                "reference_image": (
                    "IMAGE",
                ),

                "conditioning": (
                    "CONDITIONING",
                ),

                "vae": (
                    "VAE",
                ),

                "description": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "dynamicPrompts": False,
                    },
                ),

                "preserve": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "dynamicPrompts": False,
                    },
                ),

                "avoid": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "dynamicPrompts": False,
                    },
                ),

                "save_character": (
                    "BOOLEAN",
                    {
                        "default": False,
                    },
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

    FUNCTION = "edit_character"
    OUTPUT_NODE = True
    CATEGORY = "D&D Images/Characters"

    def edit_character(
        self,
        character_name,
        reference_image,
        conditioning,
        vae,
        description,
        preserve,
        avoid,
        save_character,
    ):
        character_id = safe_id(character_name)

        if not character_id:
            raise ValueError(
                "Character name must contain a letter or number."
            )

        # The image is always used for this execution,
        # regardless of whether the character is persisted.
        referenced_conditioning = apply_character_reference(
            image=reference_image,
            conditioning=conditioning,
            vae=vae,
        )

        character_path = None

        if save_character:
            _, folder = save_character_data(
                name=character_name,
                reference_image=reference_image,
                description=description,
                preserve=preserve,
                avoid=avoid,
            )

            character_path = str(folder)

        character = make_character(
            name=character_name,
            description=description,
            preserve=split_lines(preserve),
            avoid=split_lines(avoid),
            image=reference_image,
            character_id=character_id,
            path=character_path,
        )

        return (
            reference_image,
            character,
            referenced_conditioning,
        )


NODE_CLASS_MAPPINGS = {
    "DNDCharacterEditor": DNDCharacterEditor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DNDCharacterEditor": "D&D Character Editor",
}