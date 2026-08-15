from .character_utils import (
    character_from_library,
    list_characters,
    make_character_context,
)


class DNDPrepareCharacters:
    """
    Prepare one or more CHARACTER objects for the D&D image-generation
    workflow.

    Character sources:

        1. Direct `characters` input.
           Optional 1:many CHARACTER input from D&D Character Editor
           or another CHARACTER-producing node.

        2. Persistent character-library selectors.

    Both sources are merged into the same character collection.

    Library selectors can be empty. An empty selector contributes no
    character.

    This node does NOT perform FLUX.2 image preparation.
    """

    MAX_CHARACTERS = 10

    @classmethod
    def INPUT_TYPES(cls):

        # --------------------------------------------------------------
        # IMPORTANT:
        #
        # The empty string is a real selectable option.
        #
        # This allows a library selector to be cleared after a character
        # has previously been selected.
        # --------------------------------------------------------------

        library_choices = [
            "",
            *list_characters(),
        ]

        return {
            "required": {
            },

            "optional": {

                # ------------------------------------------------------
                # Optional 1:many CHARACTER input.
                # ------------------------------------------------------

                "characters": (
                    "CHARACTER",
                ),

                # ------------------------------------------------------
                # Persistent character-library selectors.
                #
                # "" means no character selected.
                # ------------------------------------------------------

                "library_character_0": (
                    library_choices,
                ),

                "library_character_1": (
                    library_choices,
                ),

                "library_character_2": (
                    library_choices,
                ),

                "library_character_3": (
                    library_choices,
                ),

                "library_character_4": (
                    library_choices,
                ),

                "library_character_5": (
                    library_choices,
                ),

                "library_character_6": (
                    library_choices,
                ),

                "library_character_7": (
                    library_choices,
                ),

                "library_character_8": (
                    library_choices,
                ),

                "library_character_9": (
                    library_choices,
                ),
            },
        }

    # ------------------------------------------------------------------
    # CHARACTER input accepts multiple connections.
    # ------------------------------------------------------------------

    INPUT_IS_LIST = True

    RETURN_TYPES = (
        "CHARACTER",
        "IMAGE",
        "STRING",
    )

    RETURN_NAMES = (
        "CHARACTERS",
        "CHARACTER IMAGE",
        "CHARACTER CONTEXT",
    )

    OUTPUT_IS_LIST = (
        True,
        True,
        False,
    )

    FUNCTION = "prepare_characters"

    CATEGORY = "D&D Images/Characters"

    # ==================================================================
    # Prepare characters
    # ==================================================================

    def prepare_characters(
        self,
        characters=None,
        library_character_0="",
        library_character_1="",
        library_character_2="",
        library_character_3="",
        library_character_4="",
        library_character_5="",
        library_character_6="",
        library_character_7="",
        library_character_8="",
        library_character_9="",
    ):

        # ==============================================================
        # Direct CHARACTER input
        # ==============================================================

        prepared_characters = []

        if characters is None:
            characters = []

        elif not isinstance(
            characters,
            list,
        ):
            characters = [
                characters
            ]

        for character in characters:

            if character is None:
                continue

            if not isinstance(
                character,
                dict,
            ):
                raise ValueError(
                    "Prepare Characters received "
                    "an invalid CHARACTER object."
                )

            prepared_characters.append(
                character
            )

        # ==============================================================
        # Library characters
        # ==============================================================

        library_ids = (
            library_character_0,
            library_character_1,
            library_character_2,
            library_character_3,
            library_character_4,
            library_character_5,
            library_character_6,
            library_character_7,
            library_character_8,
            library_character_9,
        )

        for character_id in library_ids:

            # ----------------------------------------------------------
            # INPUT_IS_LIST can cause optional values to arrive as lists.
            # Normalize them.
            # ----------------------------------------------------------

            if isinstance(
                character_id,
                list,
            ):

                if not character_id:
                    continue

                character_id = character_id[0]

            # ----------------------------------------------------------
            # Empty selector = no character.
            # ----------------------------------------------------------

            if (
                character_id is None
                or str(character_id).strip() == ""
            ):
                continue

            character, _ = (
                character_from_library(
                    character_id
                )
            )

            prepared_characters.append(
                character
            )

        # ==============================================================
        # Require at least one character
        # ==============================================================

        if not prepared_characters:
            raise ValueError(
                "Prepare Characters requires at least one character. "
                "Connect a CHARACTER input or select a character "
                "from the library."
            )

        # ==============================================================
        # Collect reference images
        # ==============================================================

        images = []

        for index, character in enumerate(
            prepared_characters,
            start=1,
        ):

            image = character.get(
                "image"
            )

            if image is None:

                name = character.get(
                    "name",
                    f"Character {index}",
                )

                raise ValueError(
                    f"Character '{name}' "
                    f"has no reference image."
                )

            try:
                image_empty = (
                    len(image) == 0
                )
            except TypeError:
                image_empty = False

            if image_empty:

                name = character.get(
                    "name",
                    f"Character {index}",
                )

                raise ValueError(
                    f"Character '{name}' "
                    f"has an empty reference image."
                )

            images.append(
                image
            )

        # ==============================================================
        # Build consolidated character context
        # ==============================================================

        contexts = []

        for character in prepared_characters:

            context = (
                make_character_context(
                    character
                )
            )

            if context:
                contexts.append(
                    context
                )

        character_context = (
            "\n\n".join(
                contexts
            )
        )

        # ==============================================================
        # Return
        # ==============================================================

        return (
            prepared_characters,
            images,
            character_context,
        )


# ==========================================================================
# Node registration
# ==========================================================================

NODE_CLASS_MAPPINGS = {
    "DNDPrepareCharacters":
        DNDPrepareCharacters,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DNDPrepareCharacters":
        "D&D Prepare Characters",
}