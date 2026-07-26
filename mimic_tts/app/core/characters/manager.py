"""
Character Manager

Responsibilities:

- Validate source audio
- Generate transcripts
- Create Qwen VoiceClonePrompt cache
- Save character metadata
- Coordinate roleplay generation

This class does NOT contain:
- Qwen model logic
- Whisper logic
- filesystem details
"""

from __future__ import annotations

from pathlib import Path

from app.core.characters.models import (
    Character,
    CharacterMetadata,
    CreateCharacterResult,
    RoleplayRequest,
)

from app.core.characters.storage import (
    CharacterStorage,
)


class CharacterManager:
    """
    Coordinates character workflows.
    """

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

        #
        # Lazy dependencies
        #
        # These are intentionally not created
        # during manager initialization.
        #

        self._stt = speech_to_text

        self._engine = engine



    ############################################################
    #
    # Lazy Services
    #
    ############################################################


    @property
    def stt(self):

        if self._stt is None:

            from app.core.speech_to_text import (
                SpeechToText,
            )

            self._stt = SpeechToText()

        return self._stt



    @property
    def engine(self):

        if self._engine is None:

            from app.core.qwen3_engine import (
                Qwen3Engine,
            )

            self._engine = Qwen3Engine()

        return self._engine



    ############################################################
    #
    # Validation
    #
    ############################################################


    def validate_audio(
        self,
        audio_path,
    ) -> None:

        audio_path = Path(audio_path)

        if not audio_path.exists():

            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )


        if not audio_path.is_file():

            raise ValueError(
                f"Path is not a file: {audio_path}"
            )


        if audio_path.suffix.lower() not in self.SUPPORTED_FORMATS:

            raise ValueError(
                f"Unsupported audio format: {audio_path.suffix}"
            )



    ############################################################
    #
    # Character Creation
    #
    ############################################################


    def create_character(
        self,
        *,
        name: str,
        audio_path,
        instructions=None,
        personality=None,
        description=None,
        overwrite=False,
    ) -> CreateCharacterResult:


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


        character = self.storage.create(
            name,
            overwrite=overwrite,
        )


        self.engine.load()


        voice_prompt = (
            self.engine.create_voice_clone_prompt(
                audio_path=audio_path,
                transcript=transcript,
            )
        )


        self.storage.save_voice_prompt(
            character,
            voice_prompt,
        )


        self.storage.save_transcript(
            character,
            transcript,
        )


        metadata = CharacterMetadata(

            schema_version=1,

            name=name,

            source_audio=str(
                audio_path.resolve()
            ),

            instructions=(
                instructions or ""
            ),

            personality=(
                personality or ""
            ),

            description=(
                description or ""
            ),
        )
        
        self.storage.save_metadata(
            character,
            metadata,
        )


        return CreateCharacterResult(
            character=character,
            transcript=transcript,
        )



    ############################################################
    #
    # Character Listing
    #
    ############################################################


    def list(self) -> list[Character]:
        """
        Return all stored characters.
        """

        return self.storage.list()



    ############################################################
    #
    # Character Helpers
    #
    ############################################################


    def exists(
        self,
        name: str,
    ) -> bool:

        return self.storage.exists(
            name
        )


    def delete(
        self,
        name: str,
    ) -> None:

        self.storage.delete(
            name
        )


    def get(
        self,
        name: str,
    ) -> Character:

        if not self.exists(name):

            raise FileNotFoundError(
                f"Character not found: {name}"
            )


        return self.storage.load(
            name
        )



    ############################################################
    #
    # Roleplay
    #
    ############################################################


    def generate_roleplay(
        self,
        request: RoleplayRequest,
    ):

        metadata, prompt = (
            self.storage.load_assets(
                request.character
            )
        )


        return self.engine.generate_roleplay(

            text=request.text,

            prompt=prompt,

            metadata=metadata,

            instructions=request.instructions,

            emotion=request.emotion,
        )