"""
Character Manager

Coordinates:

- SpeechToText
- Qwen3Engine
- CharacterStorage

Contains business logic only.
"""

from pathlib import Path

from app.core.characters.models import (
    CharacterMetadata,
    CreateCharacterResult,
)

from app.core.characters.storage import (
    CharacterStorage,
)

from app.core.speech_to_text import (
    SpeechToText,
)

from app.core.qwen3_engine import (
    Qwen3Engine,
)


class CharacterManager:

    SUPPORTED_FORMATS = {
        ".wav",
        ".mp3",
        ".m4a",
        ".flac",
        ".ogg",
    }

    def __init__(
        self,
        storage=None,
        speech_to_text=None,
        engine=None,
    ):

        self.storage = (
            storage
            or CharacterStorage()
        )

        self.stt = (
            speech_to_text
            or SpeechToText()
        )

        self.engine = (
            engine
            or Qwen3Engine()
        )

    #
    # Validation
    #

    def validate_audio(
        self,
        audio_path,
    ):

        audio_path = Path(audio_path)

        if not audio_path.exists():

            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        if not audio_path.is_file():

            raise ValueError(
                f"Path is not a file: {audio_path}"
            )

        if (
            audio_path.suffix.lower()
            not in self.SUPPORTED_FORMATS
        ):

            raise ValueError(
                f"Unsupported audio format: {audio_path.suffix}"
            )

    #
    # Create Character
    #

    def create_character(
        self,
        *,
        name: str,
        audio_path,
        instructions=None,
    ):

        audio_path = Path(audio_path)

        self.validate_audio(
            audio_path
        )

        transcript = self.stt.transcribe(
            audio_path
        )

        if not transcript.strip():

            raise ValueError(
                "Transcript cannot be empty."
            )

        self.engine.load()

        character = self.storage.create(
            name
        )

        self.engine.create_character(
            audio_path=audio_path,
            transcript=transcript,
            output_path=character.voice_path,
            instructions=instructions,
        )

        metadata = CharacterMetadata(
            name=name,
            source_audio=str(audio_path),
            instructions=instructions,
        )

        self.storage.save_transcript(
            character,
            transcript,
        )

        self.storage.save_metadata(
            character,
            metadata,
        )

        return CreateCharacterResult(
            character=character,
            transcript=transcript,
        )

    #
    # Convenience helpers
    #

    def exists(
        self,
        name: str,
    ):

        return self.storage.exists(
            name
        )

    def delete(
        self,
        name: str,
    ):

        self.storage.delete(
            name
        )