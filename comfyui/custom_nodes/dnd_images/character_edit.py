import os

import folder_paths

from .character_utils import (
    safe_id,
    split_lines,
    save_character_data,
    make_character,
    characters_root,
)


def make_character_context(character):
    """
    Build the textual context representation for a CHARACTER.
    """

    if not character:
        return ""

    name = (
        character.get("name")
        or character.get("id")
        or "Character"
    ).strip()

    description = (
        character.get("description")
        or ""
    ).strip()

    preserve = [
        str(value).strip()
        for value in (
            character.get("preserve")
            or []
        )
        if str(value).strip()
    ]

    avoid = [
        str(value).strip()
        for value in (
            character.get("avoid")
            or []
        )
        if str(value).strip()
    ]

    lines = [
        f"Character: {name}"
    ]

    if description:
        lines.append(
            f"Description: {description}"
        )

    if preserve:
        lines.append(
            "Preserve: "
            + ", ".join(preserve)
        )

    if avoid:
        lines.append(
            "Avoid: "
            + ", ".join(avoid)
        )

    return "\n".join(lines)


class DNDCharacterEditor:

    @classmethod
    def INPUT_TYPES(cls):

        input_dir = folder_paths.get_input_directory()

        files = [
            f
            for f in os.listdir(input_dir)
            if os.path.isfile(
                os.path.join(
                    input_dir,
                    f,
                )
            )
        ]

        files = folder_paths.filter_files_content_types(
            files,
            ["image"],
        )

        return {
            "required": {

                "character_name": (
                    "STRING",
                    {
                        "default": "New Character",
                    },
                ),

                "reference_image": (
                    sorted(files),
                    {
                        "image_upload": True,
                    },
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
        "CHARACTER",
        "IMAGE",
        "STRING",
    )

    RETURN_NAMES = (
        "CHARACTER",
        "CHARACTER IMAGE",
        "CHARACTER CONTEXT",
    )

    FUNCTION = "edit_character"

    CATEGORY = "D&D Images/Characters"

    def edit_character(
        self,
        character_name,
        reference_image,
        description,
        preserve,
        avoid,
        save_character,
    ):

        # ================================================================
        # Validate character name
        # ================================================================

        character_id = safe_id(
            character_name
        )

        if not character_id:
            raise ValueError(
                "Character name must contain a letter or number."
            )

        # ================================================================
        # Validate reference image selection
        # ================================================================

        if not reference_image:
            raise ValueError(
                "A reference image must be selected."
            )

        # ================================================================
        # Load image using native ComfyUI LoadImage
        # ================================================================

        from nodes import LoadImage

        image_result = LoadImage().load_image(
            reference_image
        )

        if not image_result:
            raise ValueError(
                "Unable to load the selected reference image."
            )

        image = image_result[0]

        if image is None:
            raise ValueError(
                "The selected reference image returned no IMAGE."
            )

        try:
            if len(image) == 0:
                raise ValueError(
                    "The selected reference image is empty."
                )
        except TypeError:
            pass

        # ================================================================
        # Persist character
        # ================================================================

        character_path = None

        if save_character:

            character_id, folder = (
                save_character_data(
                    name=character_name,
                    reference_image=image,
                    description=description,
                    preserve=preserve,
                    avoid=avoid,
                )
            )

            character_path = str(
                folder
            )

            # ------------------------------------------------------------
            # IMPORTANT:
            #
            # Verify that persistence actually happened.
            # ------------------------------------------------------------

            expected_folder = (
                characters_root()
                / character_id
            )

            expected_image = (
                expected_folder
                / "reference.png"
            )

            expected_metadata = (
                expected_folder
                / "character.json"
            )

            if not expected_folder.is_dir():
                raise RuntimeError(
                    "Character save failed: "
                    f"directory was not created:\n"
                    f"{expected_folder}"
                )

            if not expected_image.is_file():
                raise RuntimeError(
                    "Character save failed: "
                    f"reference image was not created:\n"
                    f"{expected_image}"
                )

            if not expected_metadata.is_file():
                raise RuntimeError(
                    "Character save failed: "
                    f"character metadata was not created:\n"
                    f"{expected_metadata}"
                )

        # ================================================================
        # Build CHARACTER object
        # ================================================================

        character = make_character(
            name=character_name,
            description=description,
            preserve=split_lines(
                preserve
            ),
            avoid=split_lines(
                avoid
            ),
            image=image,
            character_id=character_id,
            path=character_path,
        )

        # ================================================================
        # Build textual context
        # ================================================================

        character_context = (
            make_character_context(
                character
            )
        )

        # ================================================================
        # Return
        # ================================================================

        return (
            character,
            image,
            character_context,
        )


NODE_CLASS_MAPPINGS = {
    "DNDCharacterEditor":
        DNDCharacterEditor,
}


NODE_DISPLAY_NAME_MAPPINGS = {
    "DNDCharacterEditor":
        "D&D Character Editor",
}