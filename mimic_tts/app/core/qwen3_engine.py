"""
Qwen3-TTS Engine Wrapper

Responsibilities:

- Load the correct Qwen3 model
- Create voice clone profiles
- Create reusable voice clone prompts
- Generate cloned character speech
- Generate CustomVoice speech
- Provide a stable interface for the application

This class intentionally hides qwen_tts internals.

The rest of the application should NOT directly
depend on Qwen3 APIs.
"""

from __future__ import annotations

from pathlib import Path
import json

import torch

from qwen_tts import Qwen3TTSModel

from app.config import settings



class Qwen3Engine:
    """
    Application wrapper around Qwen3-TTS.
    """

    def __init__(self):

        self.model = None

        self.loaded = False

        self.mode = settings.default_model



    ############################################################
    #
    # Model Loading
    #
    ############################################################

    def load(self):
        """
        Load configured Qwen3 model.
        """

        if self.loaded:
            return


        print()
        print("=" * 60)
        print("Loading Qwen3-TTS")
        print("=" * 60)


        model_path = self._get_model_path()


        device = settings.get(
            "runtime",
            "device",
        )


        dtype_name = settings.get(
            "runtime",
            "dtype",
        )


        dtype = self._resolve_dtype(
            dtype_name
        )


        print(
            f"Mode: {self.mode}"
        )


        self.model = Qwen3TTSModel.from_pretrained(
            model_path,
            device_map=device,
            dtype=dtype,
        )


        self.loaded = True


        print(
            "Qwen3-TTS loaded successfully"
        )



    def _get_model_path(self):

        if self.mode == "clone":

            return settings.clone_model_path


        if self.mode == "custom":

            return settings.custom_model_path


        if self.mode == "design":

            return settings.design_model_path


        raise ValueError(
            f"Unknown Qwen model mode: {self.mode}"
        )



    def _resolve_dtype(
        self,
        name: str,
    ):

        if name == "bfloat16":

            return torch.bfloat16


        if name == "float16":

            return torch.float16


        return torch.float32



    ############################################################
    #
    # Character Voice Profile
    #
    ############################################################

    def create_voice_profile(
        self,
        audio_path: Path,
        transcript: str,
        output_path: Path,
        instructions: str = "",
    ):
        """
        Store reusable voice metadata.

        The actual Qwen tensors are stored separately
        in voice_prompt.pt.
        """

        audio_path = Path(audio_path)

        output_path = Path(output_path)


        profile = {

            "audio_source":
                str(audio_path),

            "transcript":
                transcript,

            "instructions":
                instructions,

            "engine":
                "Qwen3-TTS",

            "mode":
                "clone",
        }


        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )


        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                profile,
                file,
                indent=4,
            )


        print()
        print(
            "Voice profile created:"
        )

        print(
            output_path
        )


        return output_path



    ############################################################
    #
    # Qwen Voice Clone Prompt
    #
    ############################################################

    def create_voice_clone_prompt(
        self,
        audio_path: Path,
        transcript: str,
    ):
        """
        Create native Qwen VoiceClonePrompt data.
        """

        if not self.loaded:

            self.load()


        print()
        print("=" * 60)
        print("Creating Voice Clone Prompt")
        print("=" * 60)


        prompt = (
            self.model.create_voice_clone_prompt(
                ref_audio=str(audio_path),
                ref_text=transcript,
            )
        )


        print(
            "Voice clone prompt created"
        )


        return prompt



    ############################################################
    #
    # Voice Clone Generation
    #
    ############################################################

    def generate_voice_clone(
        self,
        text: str,
        prompt,
        instructions: str = "",
    ):
        """
        Generate speech from cached voice prompt.
        """

        if not self.loaded:

            self.load()


        kwargs = {}


        if instructions:

            kwargs["instruct"] = instructions



        wavs, sample_rate = (
            self.model.generate_voice_clone(
                text=text,
                language="English",
                voice_clone_prompt=prompt,
                **kwargs,
            )
        )


        return (
            wavs[0],
            sample_rate,
        )



    ############################################################
    #
    # Roleplay Generation
    #
    ############################################################

    def generate_roleplay(
        self,
        text: str,
        prompt,
        metadata=None,
        instructions: str = "",
        emotion: str = "neutral",
    ):
        """
        Generate character dialogue.

        The engine receives:

        - text
        - voice prompt
        - character metadata
        - performance instructions

        It does NOT load files.
        """

        if not self.loaded:

            self.load()



        performance = []


        #
        # Support dataclass metadata
        #

        if metadata:

            if hasattr(
                metadata,
                "instructions",
            ):

                default_instruction = (
                    metadata.instructions
                )

            elif isinstance(
                metadata,
                dict,
            ):

                default_instruction = (
                    metadata.get(
                        "instructions",
                        "",
                    )
                )

            else:

                default_instruction = ""


            if default_instruction:

                performance.append(
                    default_instruction
                )



        if instructions:

            performance.append(
                instructions
            )


        if emotion:

            performance.append(
                f"Emotion: {emotion}"
            )


        instruction_text = "\n".join(
            performance
        )


        return self.generate_voice_clone(
            text=text,
            prompt=prompt,
            instructions=instruction_text,
        )



    ############################################################
    #
    # Custom Voice
    #
    ############################################################

    def generate_custom_voice(
        self,
        text: str,
        speaker: str,
        instructions: str = "",
    ):
        """
        Generate speech using Qwen CustomVoice.
        """

        if not self.loaded:

            self.load()



        wavs, sample_rate = (
            self.model.generate_custom_voice(
                text=text,
                speaker=speaker,
                language="English",
                instruct=instructions,
            )
        )


        return (
            wavs[0],
            sample_rate,
        )



    ############################################################
    #
    # Status
    #
    ############################################################

    def is_loaded(self):

        return self.loaded