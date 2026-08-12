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

POST /v1/roleplay
POST /roleplay
POST /tts/roleplay

POST /v1/characters
POST /characters

PUT  /v1/characters/{name}
PUT  /characters/{name}

The character creation endpoint accepts an audio upload,
transcribes it using Whisper, creates the Qwen voice clone
prompt, and stores the resulting character.

The character update endpoint can optionally accept new
reference audio. If audio is supplied, the voice clone
prompt and transcript are regenerated.

Character layout:

    /data/characters/<name>/
        metadata.json
        transcript.txt
        voice_prompt.pt
"""

from __future__ import annotations

import io
import json
import tempfile

from pathlib import Path
from typing import Optional

import soundfile as sf
import torch

from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from pydantic import BaseModel, Field

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

class SpeechRequest(BaseModel):
    """
    OpenAI-compatible speech request.
    """

    model: str = Field(
        default="mimic-tts",
        description="TTS model identifier",
    )

    voice: str = Field(
        ...,
        description="Character voice name",
    )

    input: str = Field(
        ...,
        description="Text to synthesize",
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


class RoleplayAPIRequest(BaseModel):
    """
    Mimic-TTS roleplay generation request.

    Unlike the OpenAI-compatible speech endpoint,
    this endpoint uses explicit character terminology.
    """

    character: str = Field(
        ...,
        description="Character name",
    )

    text: str = Field(
        ...,
        description="Dialogue to speak",
    )

    instructions: Optional[str] = Field(
        default=None,
        description=(
            "Temporary performance instructions."
        ),
    )

    emotion: Optional[str] = Field(
        default="neutral",
        description=(
            "Emotion for voice delivery."
        ),
    )

    response_format: str = Field(
        default="wav",
        description=(
            "Audio response format. "
            "Only wav is currently supported."
        ),
    )


############################################################
#
# Startup
#
############################################################

@app.on_event("startup")
async def startup():

    print()
    print("=" * 60)
    print("Starting Mimic-TTS API")
    print("=" * 60)
    print()

    print(
        "Loading Qwen3-TTS..."
    )

    engine.load()

    print()
    print("Mimic-TTS API ready")
    print()


############################################################
#
# Root / Health
#
############################################################

@app.get("/")
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


@app.get("/health")
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

@app.get("/v1/models")
@app.get("/models")
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

@app.get("/v1/voices")
@app.get("/v1/audio/voices")
@app.get("/voices")
def list_voices():

    characters = manager.list()

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
# Character Creation
#
############################################################

@app.post(
    "/v1/characters",
    status_code=201,
)
@app.post(
    "/characters",
    status_code=201,
)
async def create_character(
    name: str = Form(...),
    audio: UploadFile = File(...),
    instructions: Optional[str] = Form(
        default=None
    ),
    personality: Optional[str] = Form(
        default=None
    ),
    description: Optional[str] = Form(
        default=None
    ),
    overwrite: bool = Form(
        default=False
    ),
):

    name = name.strip()

    if not name:

        raise HTTPException(
            status_code=400,
            detail=(
                "Character name is required."
            ),
        )

    if audio is None:

        raise HTTPException(
            status_code=400,
            detail=(
                "Audio file is required."
            ),
        )

    filename = (
        audio.filename
        or "reference_audio.wav"
    )

    suffix = (
        Path(filename)
        .suffix
        .lower()
    )

    if suffix not in manager.SUPPORTED_FORMATS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported audio format: "
                f"{suffix or 'unknown'}. "
                "Supported formats: "
                + ", ".join(
                    sorted(
                        manager.SUPPORTED_FORMATS
                    )
                )
            ),
        )

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temp_file:

            temp_path = Path(
                temp_file.name
            )

            while True:

                chunk = await audio.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                temp_file.write(
                    chunk
                )

        result = manager.create_character(
            name=name,
            audio_path=temp_path,
            instructions=instructions,
            personality=personality,
            description=description,
            overwrite=overwrite,
        )

    except FileExistsError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    except (
        FileNotFoundError,
        ValueError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        print()
        print(
            "Character creation failed:"
        )
        print(
            repr(exc)
        )
        print()

        raise HTTPException(
            status_code=500,
            detail=(
                "Character creation failed: "
                f"{exc}"
            ),
        ) from exc

    finally:

        if temp_path is not None:

            try:

                temp_path.unlink(
                    missing_ok=True
                )

            except Exception:
                pass

        await audio.close()

    return {
        "success": True,

        "character": {
            "name": result.character.name,
        },

        "transcript": result.transcript,

        "files": {
            "metadata": str(
                result.character.metadata_path
            ),
            "transcript": str(
                result.character.transcript_path
            ),
            "voice_prompt": str(
                result.character.prompt_path
            ),
        },
    }


############################################################
#
# Character Update
#
############################################################

@app.put(
    "/v1/characters/{name}",
)
@app.put(
    "/characters/{name}",
)
async def update_character(
    name: str,
    audio: Optional[UploadFile] = File(
        default=None
    ),
    instructions: Optional[str] = Form(
        default=None
    ),
    personality: Optional[str] = Form(
        default=None
    ),
    description: Optional[str] = Form(
        default=None
    ),
):

    name = name.strip()

    if not name:

        raise HTTPException(
            status_code=400,
            detail=(
                "Character name is required."
            ),
        )

    try:

        manager.get(name)

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    temp_path = None

    try:

        if audio is not None:

            filename = (
                audio.filename
                or "reference_audio.wav"
            )

            suffix = (
                Path(filename)
                .suffix
                .lower()
            )

            if (
                suffix
                not in manager.SUPPORTED_FORMATS
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Unsupported audio format: "
                        f"{suffix or 'unknown'}. "
                        "Supported formats: "
                        + ", ".join(
                            sorted(
                                manager.SUPPORTED_FORMATS
                            )
                        )
                    ),
                )

            with tempfile.NamedTemporaryFile(
                suffix=suffix,
                delete=False,
            ) as temp_file:

                temp_path = Path(
                    temp_file.name
                )

                while True:

                    chunk = await audio.read(
                        1024 * 1024
                    )

                    if not chunk:
                        break

                    temp_file.write(
                        chunk
                    )

        result = manager.update_character(
            name=name,
            audio_path=temp_path,
            instructions=instructions,
            personality=personality,
            description=description,
        )

    except HTTPException:

        raise

    except (
        FileNotFoundError,
        ValueError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        print()
        print(
            "Character update failed:"
        )
        print(
            repr(exc)
        )
        print()

        raise HTTPException(
            status_code=500,
            detail=(
                "Character update failed: "
                f"{exc}"
            ),
        ) from exc

    finally:

        if temp_path is not None:

            try:

                temp_path.unlink(
                    missing_ok=True
                )

            except Exception:
                pass

        if audio is not None:

            await audio.close()

    return {
        "success": True,

        "character": {
            "name": result.character.name,
        },

        "audio_updated": (
            result.audio_updated
        ),

        "transcript": (
            result.transcript
        ),

        "files": {
            "metadata": str(
                result.character.metadata_path
            ),
            "transcript": str(
                result.character.transcript_path
            ),
            "voice_prompt": str(
                result.character.prompt_path
            ),
        },
    }


############################################################
#
# OpenAI-Compatible TTS
#
############################################################

@app.post("/v1/audio/speech")
@app.post("/tts/speech")
def synthesize_speech(
    request: SpeechRequest,
):

    if request.model != "mimic-tts":

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported model: "
                f"{request.model}. "
                "Expected: mimic-tts."
            ),
        )

    text = request.input.strip()

    if not text:

        raise HTTPException(
            status_code=400,
            detail=(
                "Input text is required."
            ),
        )

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

    audio_bytes = _encode_wav(
        audio,
        sample_rate,
    )

    return Response(
        content=audio_bytes,
        media_type="audio/wav",
        headers={
            "Cache-Control": "no-store",
        },
    )


############################################################
#
# Roleplay API
#
############################################################

@app.post("/v1/roleplay")
@app.post("/roleplay")
@app.post("/tts/roleplay")
def roleplay(
    request: RoleplayAPIRequest,
):

    """
    Generate character dialogue.

    This is the explicit Mimic-TTS roleplay API.

    Request JSON:

        {
            "character": "eira",
            "text": "Hello there.",
            "instructions": "Speak warmly.",
            "emotion": "happy",
            "response_format": "wav"
        }

    The character's stored metadata and voice clone
    prompt are loaded automatically.

    Temporary instructions and emotion are passed
    to CharacterManager.generate_roleplay().
    """

    character_name = (
        request.character.strip()
    )

    if not character_name:

        raise HTTPException(
            status_code=400,
            detail=(
                "Character is required."
            ),
        )

    text = request.text.strip()

    if not text:

        raise HTTPException(
            status_code=400,
            detail=(
                "Text is required."
            ),
        )

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

    audio, sample_rate = (
        _generate_roleplay_audio(
            character=character_name,
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

    audio_bytes = _encode_wav(
        audio,
        sample_rate,
    )

    return Response(
        content=audio_bytes,
        media_type="audio/wav",
        headers={
            "Cache-Control": "no-store",
        },
    )


############################################################
#
# Roleplay Generation
#
############################################################

def _generate_roleplay_audio(
    *,
    character: str,
    text: str,
    instructions: str,
    emotion: str,
):

    character_name = character.strip()

    if not character_name:

        raise HTTPException(
            status_code=400,
            detail=(
                "Character is required."
            ),
        )

    try:

        character_object = manager.get(
            character_name
        )

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Character not found: "
                f"{character_name}"
            ),
        )

    roleplay_request = RoleplayRequest(
        character=character_object,
        text=text,
        instructions=instructions,
        emotion=emotion,
        output=None,
    )

    try:

        return manager.generate_roleplay(
            roleplay_request
        )

    except Exception as exc:

        print()
        print(
            "Roleplay generation failed:"
        )
        print(
            repr(exc)
        )
        print()

        raise HTTPException(
            status_code=500,
            detail=(
                "Roleplay generation failed: "
                f"{exc}"
            ),
        ) from exc


############################################################
#
# OpenAI-Compatible Character Generation
#
############################################################

def _generate_character_audio(
    *,
    voice: str,
    text: str,
    instructions: str,
    emotion: str,
):

    voice_name = voice.strip()

    if not voice_name:

        raise HTTPException(
            status_code=400,
            detail=(
                "Voice is required."
            ),
        )

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

    request = RoleplayRequest(
        character=character,
        text=text,
        instructions=instructions,
        emotion=emotion,
        output=None,
    )

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

    buffer.seek(0)

    return buffer.getvalue()