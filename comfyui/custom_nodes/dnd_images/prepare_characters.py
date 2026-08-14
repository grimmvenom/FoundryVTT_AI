from comfy_api.latest import io

from .character_utils import (
    list_characters,
    character_from_library,
)


# ============================================================================
# Custom Types
# ============================================================================

Character = io.Custom("CHARACTER")
CharacterReferences = io.Custom("CHARACTER_REFERENCES")


# ============================================================================
# Constants
# ============================================================================

MAX_LIBRARY_CHARACTERS = 10


# ============================================================================
# Helpers
# ============================================================================

def _clean_list(value):
    """Normalize Preserve/Avoid data into a clean list of strings."""

    if value is None:
        return []

    if isinstance(value, str):
        value = [value]

    if not isinstance(value, (list, tuple)):
        return []

    return [
        str(item).strip()
        for item in value
        if str(item).strip()
    ]


def _character_to_section(character):
    """
    Convert one CHARACTER dictionary into scene-prompt context text.

    The image itself is NOT represented here. Images are carried separately
    through CHARACTER_REFERENCES.
    """

    if not isinstance(character, dict):
        return None

    name = str(
        character.get("name", "")
    ).strip()

    description = str(
        character.get("description", "")
    ).strip()

    preserve = _clean_list(
        character.get("preserve", [])
    )

    avoid = _clean_list(
        character.get("avoid", [])
    )

    if not name:
        name = "Unnamed Character"

    lines = [
        f"CHARACTER: {name}",
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


def _character_name(character):
    """Return a normalized character name."""

    if not isinstance(character, dict):
        return ""

    return str(
        character.get("name", "")
    ).strip()


def _add_character(
    sections,
    references,
    seen_names,
    character,
    image=None,
):
    """
    Add one CHARACTER object.

    `sections` contains the textual prompt context.

    `references` contains the actual reference image together with the
    character name.

    Duplicate names are ignored.
    """

    if not isinstance(character, dict):
        return

    section = _character_to_section(character)

    if not section:
        return

    name = _character_name(character)

    normalized_name = name.lower()

    if not normalized_name:
        normalized_name = section.lower()

    if normalized_name in seen_names:
        return

    seen_names.add(normalized_name)

    sections.append(section)

    # Only add an image reference when an actual image exists.
    if image is not None:
        references.append(
            {
                "name": name,
                "image": image,
            }
        )


# ============================================================================
# D&D Prepare Characters
# ============================================================================

class DNDPrepareCharacters(io.ComfyNode):
    """
    Combine connected CHARACTER objects and persistent library characters.

    Outputs:

        CHARACTER_CONTEXT
            Textual character descriptions, Preserve instructions, and
            Avoid instructions.

        CHARACTER_REFERENCES
            The actual reference images associated with the characters.

    Library selectors are fixed in the Python schema. The JavaScript
    extension only controls how many of those selectors are visible.

    There is intentionally NO autogrow behavior.
    """

    @classmethod
    def define_schema(cls):

        library_characters = list_characters()

        # ComfyUI combo validation requires selected values to exist in
        # this list.
        library_options = [""]

        for name in library_characters:

            if (
                name
                and name not in library_options
            ):
                library_options.append(name)

        return io.Schema(
            node_id="DNDPrepareCharacters",

            display_name="D&D Prepare Characters",

            category="D&D Images/Characters",

            description=(
                "Combine CHARACTER inputs and persistent library "
                "characters into character context and reference images."
            ),

            inputs=[

                # ============================================================
                # ONE CHARACTER input
                # ============================================================

                Character.Input(
                    "characters",
                    optional=True,
                    lazy=False,
                    tooltip=(
                        "Connect CHARACTER outputs here."
                    ),
                ),

                # ============================================================
                # Persistent library selectors
                # ============================================================

                io.Combo.Input(
                    "library_character_1",
                    options=library_options,
                    default="",
                ),

                io.Combo.Input(
                    "library_character_2",
                    options=library_options,
                    default="",
                ),

                io.Combo.Input(
                    "library_character_3",
                    options=library_options,
                    default="",
                ),

                io.Combo.Input(
                    "library_character_4",
                    options=library_options,
                    default="",
                ),

                io.Combo.Input(
                    "library_character_5",
                    options=library_options,
                    default="",
                ),

                io.Combo.Input(
                    "library_character_6",
                    options=library_options,
                    default="",
                ),

                io.Combo.Input(
                    "library_character_7",
                    options=library_options,
                    default="",
                ),

                io.Combo.Input(
                    "library_character_8",
                    options=library_options,
                    default="",
                ),

                io.Combo.Input(
                    "library_character_9",
                    options=library_options,
                    default="",
                ),

                io.Combo.Input(
                    "library_character_10",
                    options=library_options,
                    default="",
                ),
            ],

            outputs=[

                # ============================================================
                # Text context
                # ============================================================

                io.String.Output(
                    "character_context",
                    display_name="CHARACTER_CONTEXT",
                ),

                # ============================================================
                # Actual reference images
                # ============================================================

                CharacterReferences.Output(
                    "character_references",
                    display_name="CHARACTER_REFERENCES",
                ),
            ],
        )

    @classmethod
    def execute(
        cls,
        characters=None,
        library_character_1="",
        library_character_2="",
        library_character_3="",
        library_character_4="",
        library_character_5="",
        library_character_6="",
        library_character_7="",
        library_character_8="",
        library_character_9="",
        library_character_10="",
    ):
        sections = []

        references = []

        seen_names = set()

        # ====================================================================
        # Connected CHARACTER input
        # ====================================================================

        if characters is not None:

            if isinstance(
                characters,
                dict,
            ):
                character_values = [
                    characters
                ]

            elif isinstance(
                characters,
                (list, tuple),
            ):
                character_values = characters

            else:
                character_values = []

            for character in character_values:

                if character is None:
                    continue

                _add_character(
                    sections=sections,
                    references=references,
                    seen_names=seen_names,
                    character=character,
                    image=None,
                )

        # ====================================================================
        # Library selections
        # ====================================================================

        library_selections = [
            library_character_1,
            library_character_2,
            library_character_3,
            library_character_4,
            library_character_5,
            library_character_6,
            library_character_7,
            library_character_8,
            library_character_9,
            library_character_10,
        ]

        for character_name in library_selections:

            if not character_name:
                continue

            character_name = str(
                character_name
            ).strip()

            if not character_name:
                continue

            # character_from_library() returns:
            #
            #     character_data, image
            #
            # The previous implementation discarded `image`.
            #
            character_data, image = (
                character_from_library(
                    character_name
                )
            )

            _add_character(
                sections=sections,
                references=references,
                seen_names=seen_names,
                character=character_data,
                image=image,
            )

        # ====================================================================
        # Final textual context
        # ====================================================================

        character_context = (
            "\n\n".join(sections)
        )

        # ====================================================================
        # Final image reference context
        # ====================================================================

        character_references = references

        # V3 NodeOutput values are positional.
        return io.NodeOutput(
            character_context,
            character_references,
        )


# ============================================================================
# Registration
# ============================================================================

NODE_CLASS_MAPPINGS = {
    "DNDPrepareCharacters": DNDPrepareCharacters,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DNDPrepareCharacters": "D&D Prepare Characters",
}