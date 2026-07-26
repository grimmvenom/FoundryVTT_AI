"""
Mimic-TTS FastAPI API.

Provides:

    GET  /
    GET  /health

    GET  /v1/models
    GET  /models

    GET  /v1/voices
    GET  /v1/audio/voices
    GET  /voices

    POST /v1/audio/speech
    POST /tts/speech

    POST /tts/roleplay

The primary TTS endpoint follows the OpenAI-compatible
audio speech API used by Open WebUI and other clients.

Example:

    POST /v1/audio/speech

    {
        "model": "mimic-tts",
        "voice": "jester",
        "input": "Hello there!"
    }

Mimic-TTS-specific optional fields:

    {
        "instructions": "Speak cheerfully",
        "emotion": "happy"
    }
"""

from __future__ import annotations


import io
import json
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import Optional


import torch


from fastapi import (
    FastAPI,
    HTTPException,
)

from fastapi.responses import Response

from pydantic import (
    BaseModel,
    Field,
)

import soundfile as sf


from ..core.characters.manager import (
    CharacterManager,
)

from ..core.characters.models import (
    RoleplayRequest,
)

from ..core.qwen3_engine import (
    engine,
)



############################################################
#
# Application
#
############################################################


app = FastAPI(

    title="Mimic TTS",

    description=(
        "OpenAI-compatible Qwen3-TTS "
        "voice cloning API"
    ),
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "*",
    ],

    allow_credentials=False,

    allow_methods=[
        "*",
    ],

    allow_headers=[
        "*",
    ],
)


############################################################
#
# Shared Services
#
############################################################


# The Qwen engine is a module-level singleton.
#
# This prevents every HTTP request from creating
# a new Qwen3Engine instance.
#
# The model itself is loaded during application startup.

manager = CharacterManager(

    engine=engine,

)



############################################################
#
# Configuration
#
############################################################


VOICES_CONFIG_PATH = (

    Path(__file__).parent.parent.parent

    / "config"

    / "voices.json"

)


VOICES_CONFIG = {}


if VOICES_CONFIG_PATH.exists():

    with open(
        VOICES_CONFIG_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        VOICES_CONFIG = json.load(
            file
        )



############################################################
#
# Request Models
#
############################################################


class SpeechRequest(
    BaseModel
):
    """
    OpenAI-compatible speech request.

    Required fields:

        input:
            Text to synthesize.

        model:
            TTS model identifier.

        voice:
            Character voice identifier.

    Optional Mimic-TTS extensions:

        instructions:
            Temporary voice direction.

        emotion:
            Emotional delivery direction.

        response_format:
            Output format.

    Example:

        {
            "model": "mimic-tts",
            "voice": "jester",
            "input": "Hello there!",
            "instructions": "Speak quickly",
            "emotion": "happy"
        }
    """

    model: str = Field(

        default="mimic-tts",

        description=(
            "TTS model identifier"
        ),

    )


    voice: str = Field(

        ...,

        description=(
            "Character voice name"
        ),

    )


    input: str = Field(

        ...,

        description=(
            "Text to synthesize"
        ),

    )


    response_format: str = Field(

        default="wav",

        description=(
            "Audio response format. "
            "Only wav is currently supported."
        ),

    )


    instructions: Optional[str] = Field(

        default=None,

        description=(
            "Temporary voice performance "
            "instructions."
        ),

    )


    emotion: Optional[str] = Field(

        default="neutral",

        description=(
            "Emotion for voice delivery."
        ),

    )



############################################################
#
# Startup
#
############################################################


@app.on_event(
    "startup"
)
async def startup():

    print()

    print(
        "=" * 60
    )

    print(
        "Starting Mimic-TTS API"
    )

    print(
        "=" * 60
    )

    print()

    print(
        "Loading Qwen3-TTS..."
    )


    engine.load()


    print()

    print(
        "Mimic-TTS API ready"
    )

    print()



############################################################
#
# Root / Health
#
############################################################


@app.get(
    "/"
)
def root():

    return {

        "service": "mimic-tts",

        "status": "running",

        "model": "mimic-tts",

        "model_loaded": (
            engine.is_loaded()
        ),

        "cuda": (
            torch.cuda.is_available()
        ),

        "gpu": (

            torch.cuda.get_device_name(0)

            if torch.cuda.is_available()

            else None

        ),

    }



@app.get(
    "/health"
)
def health():

    return {

        "status": "ok",

        "model_loaded": (
            engine.is_loaded()
        ),

    }



############################################################
#
# Models
#
############################################################


@app.get(
    "/v1/models"
)
@app.get(
    "/models"
)
def list_models():

    return {

        "object": "list",

        "data": [

            {

                "id": "mimic-tts",

                "object": "model",

                "owned_by": "mimic-tts",

            }

        ],

    }



############################################################
#
# Voices
#
############################################################


@app.get(
    "/v1/voices"
)
@app.get(
    "/v1/audio/voices"
)
@app.get(
    "/voices"
)
def list_voices():

    characters = (
        manager.list()
    )


    voices = []


    for character in characters:

        voice_config = (

            VOICES_CONFIG

            .get(
                "voices",
                {}
            )

            .get(
                character.name,
                {}
            )

        )


        voices.append(

            {

                "id": character.name,

                "name": (

                    voice_config.get(

                        "name",

                        character.name.capitalize(),

                    )

                ),

                "object": "voice",

                "description": (

                    voice_config.get(

                        "description",

                        f"{character.name} character voice",

                    )

                ),

                "language": (

                    voice_config.get(

                        "language",

                        "en-US",

                    )

                ),

                "gender": (

                    voice_config.get(

                        "gender",

                        "unknown",

                    )

                ),

            }

        )


    return {

        "object": "list",

        "data": voices,

    }



############################################################
#
# OpenAI-Compatible TTS
#
############################################################


@app.post(
    "/v1/audio/speech"
)
@app.post(
    "/tts/speech"
)
def synthesize_speech(
    request: SpeechRequest,
):

    #
    # Validate model
    #

    if request.model != "mimic-tts":

        raise HTTPException(

            status_code=400,

            detail=(

                f"Unsupported model: "
                f"{request.model}. "
                f"Expected: mimic-tts."

            ),

        )


    #
    # Validate text
    #

    text = (
        request.input.strip()
    )


    if not text:

        raise HTTPException(

            status_code=400,

            detail=(
                "Input text is required."
            ),

        )


    #
    # Validate format
    #

    response_format = (

        request.response_format

        or "wav"

    ).lower()


    if response_format not in {

        "wav",

        "wave",

    }:

        raise HTTPException(

            status_code=400,

            detail=(

                "Only WAV output "
                "is currently supported."

            ),

        )


    #
    # Generate audio
    #

    audio, sample_rate = (

        _generate_character_audio(

            voice=request.voice,

            text=text,

            instructions=(

                request.instructions

                or ""

            ),

            emotion=(

                request.emotion

                or "neutral"

            ),

        )

    )


    #
    # Encode WAV
    #

    audio_bytes = (
        _encode_wav(
            audio,
            sample_rate,
        )
    )


    #
    # Return audio
    #

    return Response(

        content=audio_bytes,

        media_type="audio/wav",

        headers={

            "Cache-Control": (
                "no-store"
            ),

        },

    )



############################################################
#
# Roleplay Convenience Endpoint
#
############################################################


@app.post(
    "/tts/roleplay"
)
def roleplay(
    request: SpeechRequest,
):

    return synthesize_speech(
        request
    )



############################################################
#
# Character Generation
#
############################################################


def _generate_character_audio(
    *,
    voice: str,
    text: str,
    instructions: str,
    emotion: str,
):

    voice_name = (
        voice.strip()
    )


    if not voice_name:

        raise HTTPException(

            status_code=400,

            detail=(
                "Voice is required."
            ),

        )


    #
    # Load stored character
    #

    try:

        character = manager.get(

            voice_name

        )

    except FileNotFoundError:

        raise HTTPException(

            status_code=404,

            detail=(

                f"Voice not found: "
                f"{voice_name}"

            ),

        )


    #
    # Build roleplay request
    #

    request = RoleplayRequest(

        character=character,

        text=text,

        instructions=instructions,

        emotion=emotion,

        output=None,

    )


    #
    # Generate through the existing
    # CharacterManager workflow.
    #

    try:

        return manager.generate_roleplay(

            request

        )

    except Exception as exc:

        print()

        print(
            "TTS generation failed:"
        )

        print(
            repr(exc)
        )

        print()


        raise HTTPException(

            status_code=500,

            detail=(

                "TTS generation failed: "

                f"{exc}"

            ),

        ) from exc



############################################################
#
# Audio Encoding
#
############################################################


def _encode_wav(
    audio,
    sample_rate: int,
) -> bytes:

    buffer = io.BytesIO()


    sf.write(

        buffer,

        audio,

        sample_rate,

        format="WAV",

    )


    buffer.seek(
        0
    )


    return buffer.getvalue()