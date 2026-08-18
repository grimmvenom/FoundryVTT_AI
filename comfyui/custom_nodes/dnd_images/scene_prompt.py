from nodes import CLIPTextEncode


class DNDScenePrompt:
    """
    Build textual conditioning for a D&D scene.

    Character identity is supplied automatically through CHARACTER_CONTEXT.

    This version deliberately uses strong per-character identity boundaries
    so that multiple referenced characters remain distinct and their
    attributes are not merged between characters.
    """

    CHARACTER_IDENTITY_INSTRUCTION = (
        "IMPORTANT CHARACTER IDENTITY RULES:\n"
        "There are multiple distinct characters in this scene.\n"
        "Treat EVERY character listed below as *separate* individuals.\n"
        "Each character MUST keep ONLY their *own original appearance* and attributes.\n"
        "Do NOT transfer attributes from one character to aNOTher.\n"
        "Do NOT merge character identities.\n"
        "Do NOT duplicate characters.\n"
        "Do NOT replace one character with another.\n"
        "Every listed character MUST appear exactly once.\n"
        "Preserve each character's hair, face, skin color, clothing, "
        "body features, accessories, markings, ears, horns, tattoos, "
        "and other identifying traits according to that character's "
        "reference and description."
    )

    @classmethod
    def INPUT_TYPES(cls):

        return {
            "required": {

                "clip": (
                    "CLIP",
                ),

                "character_context": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "dynamicPrompts": False,
                    },
                ),

                "scene": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "dynamicPrompts": False,
                    },
                ),

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
        # Character identity
        # ------------------------------------------------------------------

        if character_context:

            sections.append(
                "CHARACTER REFERENCES:\n"
                + character_context
            )

            sections.append(
                self.CHARACTER_IDENTITY_INSTRUCTION
            )

        # ------------------------------------------------------------------
        # Scene
        # ------------------------------------------------------------------

        if scene:

            sections.append(
                "SCENE:\n"
                + scene
            )

        # ------------------------------------------------------------------
        # Global restrictions
        # ------------------------------------------------------------------

        if global_avoid:

            sections.append(
                "GLOBAL AVOID:\n"
                + global_avoid
            )

        # ------------------------------------------------------------------
        # Final prompt
        # ------------------------------------------------------------------

        prompt = "\n\n".join(
            sections
        )

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