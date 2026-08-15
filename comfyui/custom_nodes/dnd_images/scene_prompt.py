from nodes import CLIPTextEncode


class DNDScenePrompt:
    """
    Build the textual conditioning for a D&D scene.

    Character identity is supplied automatically through CHARACTER_CONTEXT.

    This version deliberately structures character information so that
    each character has a distinct identity block. The goal is to reduce
    attribute migration between characters when multiple character
    references are supplied to FLUX.2.

    Character reference images are handled downstream by the FLUX.2
    reference workflow.
    """

    # ------------------------------------------------------------------
    # Character identity instruction
    #
    # Keep this concise and explicit. We do not want a huge collection
    # of negative instructions competing with the actual character
    # descriptions.
    # ------------------------------------------------------------------

    CHARACTER_IDENTITY_INSTRUCTION = (
        "IMPORTANT CHARACTER IDENTITY RULES: "
        "Each character is a separate individual. "
        "Match each character to their own reference image and description. "
        "Keep physical features, clothing, accessories, hair, ears, "
        "body traits, colors, and other identifying attributes attached "
        "to the correct character. "
        "Do not transfer attributes from one character to another. "
        "Do not merge characters. "
        "Do not duplicate characters. "
        "Do not replace one character with another."
    )

    @classmethod
    def INPUT_TYPES(cls):

        return {
            "required": {

                # ==========================================================
                # CLIP
                # ==========================================================

                "clip": (
                    "CLIP",
                ),

                # ==========================================================
                # Character textual context
                # ==========================================================

                "character_context": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "dynamicPrompts": False,
                    },
                ),

                # ==========================================================
                # Scene
                # ==========================================================

                "scene": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "dynamicPrompts": False,
                    },
                ),

                # ==========================================================
                # Global Avoid
                # ==========================================================

                "global_avoid": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "dynamicPrompts": False,
                    },
                ),
            }
        }

    RETURN_TYPES = (
        "CONDITIONING",
    )

    RETURN_NAMES = (
        "CONDITIONING",
    )

    FUNCTION = "build_scene_prompt"

    CATEGORY = "D&D Images/Prompts"

    # ======================================================================
    # Build conditioning
    # ======================================================================

    def build_scene_prompt(
        self,
        clip,
        character_context,
        scene,
        global_avoid,
    ):

        character_context = (
            character_context or ""
        ).strip()

        scene = (
            scene or ""
        ).strip()

        global_avoid = (
            global_avoid or ""
        ).strip()

        sections = []

        # ------------------------------------------------------------------
        # Characters
        #
        # The character context comes directly from DNDPrepareCharacters.
        #
        # We explicitly frame these as separate individuals before the
        # actual character descriptions.
        # ------------------------------------------------------------------

        if character_context:

            sections.append(
                "CHARACTER REFERENCES\n"
                "The image contains the following distinct characters. "
                "Each character corresponds to their own reference image. "
                "Treat every character description as belonging only to "
                "that character.\n\n"
                + character_context
                + "\n\n"
                + self.CHARACTER_IDENTITY_INSTRUCTION
            )

        # ------------------------------------------------------------------
        # Scene
        #
        # The scene should describe actions, environment, composition,
        # relationships, and positioning without redefining character
        # identity.
        # ------------------------------------------------------------------

        if scene:

            sections.append(
                "SCENE\n"
                + scene
            )

        # ------------------------------------------------------------------
        # Global Avoid
        #
        # These restrictions apply to the entire generated image.
        # ------------------------------------------------------------------

        if global_avoid:

            sections.append(
                "GLOBAL AVOID\n"
                + global_avoid
            )

        # ------------------------------------------------------------------
        # Final prompt
        # ------------------------------------------------------------------

        prompt = "\n\n".join(
            sections
        )

        # ------------------------------------------------------------------
        # Encode using native ComfyUI CLIPTextEncode
        # ------------------------------------------------------------------

        conditioning = (
            CLIPTextEncode()
            .encode(
                clip=clip,
                text=prompt,
            )[0]
        )

        return (
            conditioning,
        )


# ==========================================================================
# Node Registration
# ==========================================================================

NODE_CLASS_MAPPINGS = {
    "DNDScenePrompt":
        DNDScenePrompt,
}


NODE_DISPLAY_NAME_MAPPINGS = {
    "DNDScenePrompt":
        "D&D Scene Prompt",
}