"""
Qwen3-TTS Engine Wrapper

Responsibilities:
- Load Qwen3-TTS model
- Create character voice profiles
- Generate voice cloned speech
- Provide roleplay generation interface

This class intentionally hides the Qwen3 API
so the rest of the application does not depend
directly on qwen_tts internals.
"""


from pathlib import Path
import json

import torch
from qwen_tts import Qwen3TTSModel

from app.config import settings



class Qwen3Engine:


    def __init__(self):

        self.model = None
        self.loaded = False



    ############################################################
    #
    # Model Loading
    #
    ############################################################


    def load(self):

        if self.loaded:
            return


        print()
        print("=" * 60)
        print("Loading Qwen3-TTS")
        print("=" * 60)


        model_path = settings.get(
            "model",
            "path"
        )


        device = settings.get(
            "runtime",
            "device"
        )


        dtype_name = settings.get(
            "runtime",
            "dtype"
        )



        if dtype_name == "bfloat16":

            dtype = torch.bfloat16

        elif dtype_name == "float16":

            dtype = torch.float16

        else:

            dtype = torch.float32



        self.model = Qwen3TTSModel.from_pretrained(

            model_path,

            device_map=device,

            dtype=dtype,
        )


        self.loaded = True


        print(
            "Qwen3-TTS loaded successfully"
        )



    ############################################################
    #
    # Character Creation
    #
    ############################################################


    def create_character(
        self,
        audio_path: Path,
        transcript: str,
        output_path: Path,
        instructions: str | None = None,
    ):
        """
        Create reusable character voice data.

        Currently stores metadata as .qvp.

        Future:
        Replace with native Qwen voice prompt generation
        if/when exposed by qwen_tts.
        """


        if not self.loaded:

            self.load()



        audio_path = Path(
            audio_path
        )

        output_path = Path(
            output_path
        )



        character = {

            "audio_source":
                str(audio_path),

            "transcript":
                transcript,

            "instructions":
                instructions,

            "engine":
                "Qwen3-TTS",

        }



        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )



        with open(
            output_path,
            "w"
        ) as f:

            json.dump(
                character,
                f,
                indent=4
            )



        print()
        print(
            "Character profile created:"
        )

        print(
            output_path
        )


        return output_path



    ############################################################
    #
    # Voice Clone Generation
    #
    ############################################################


    def clone_voice(
        self,
        text: str,
        audio_path: Path,
        transcript: str,
        instructions: str | None = None,
    ):

        """
        Generate speech using a reference voice.
        """


        if not self.loaded:

            self.load()



        print()
        print(
            "Generating voice clone..."
        )



        wavs, sample_rate = (

            self.model.generate_voice_clone(

                text=text,

                language="English",

                ref_audio=str(
                    audio_path
                ),

                ref_text=transcript,

                # Future:
                # Add instructions when
                # Qwen API supports it.

            )

        )



        return (
            wavs[0],
            sample_rate
        )



    ############################################################
    #
    # Roleplay Generation
    #
    ############################################################


    def generate_roleplay(
        self,
        character,
        text,
        emotion=None,
    ):
        """
        Future roleplay interface.

        Example:

        character:
            louise.qvp

        text:
            "Welcome to my dungeon"

        emotion:
            mischievous
        """


        raise NotImplementedError(
            "Roleplay generation not implemented yet"
        )



    ############################################################
    #
    # Helper / Introspection
    #
    ############################################################


    def is_loaded(self):

        return self.loaded