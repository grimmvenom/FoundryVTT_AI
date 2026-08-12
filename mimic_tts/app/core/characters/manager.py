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
    UpdateCharacterResult,
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
                f"Unsupported audio format: "
                f"{audio_path.suffix}"
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

        name = name.strip()

        if not name:

            raise ValueError(
                "Character name cannot be empty."
            )

        audio_path = Path(audio_path)

        #
        # Validate source audio before modifying
        # the character filesystem.
        #

        self.validate_audio(
            audio_path
        )

        #
        # Whisper transcription
        #

        transcript = self.stt.transcribe(
            audio_path
        )

        if not transcript or not transcript.strip():

            raise ValueError(
                "Transcript cannot be empty."
            )

        transcript = transcript.strip()

        #
        # Create character directory.
        #

        character = self.storage.create(
            name,
            overwrite=overwrite,
        )

        #
        # Ensure Qwen is loaded.
        #

        self.engine.load()

        #
        # Generate the cached voice-clone prompt.
        #
        # This is the character's only persistent
        # voice asset.
        #

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

        #
        # Save Whisper transcript.
        #

        self.storage.save_transcript(
            character,
            transcript,
        )

        #
        # Save metadata.
        #

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
    # Update Character
    #
    ############################################################
    def update_character(
        self,
        *,
        name: str,
        audio_path=None,
        instructions=None,
        personality=None,
        description=None,
    ) -> UpdateCharacterResult:
        """
        Update an existing character.

        Audio is optional.

        If audio_path is supplied:
            - transcribe new audio
            - regenerate voice clone prompt
            - replace transcript
            - update source_audio

        If audio_path is omitted:
            - preserve existing voice prompt
            - preserve existing transcript
            - update metadata only
        """

        character = self.get(name)

        #
        # Load existing metadata.
        #
        metadata = self.storage.load_metadata(
            character
        )

        transcript = None
        
        #
        # New audio supplied?
        #
        if audio_path is not None:

            audio_path = Path(audio_path)

            self.validate_audio(
                audio_path
            )

            #
            # Do the expensive work BEFORE modifying
            # the existing character.
            #

            transcript = self.stt.transcribe(
                audio_path
            )

            if not transcript or not transcript.strip():
                raise ValueError(
                    "Transcript cannot be empty."
                )

            transcript = transcript.strip()

            #
            # Ensure Qwen is loaded.
            #
            self.engine.load()

            #
            # Generate the replacement voice prompt.
            #
            voice_prompt = (
                self.engine.create_voice_clone_prompt(
                    audio_path=audio_path,
                    transcript=transcript,
                )
            )

            #
            # Only modify the character after all
            # expensive operations succeeded.
            #

            self.storage.save_voice_prompt(
                character,
                voice_prompt,
            )

            self.storage.save_transcript(
                character,
                transcript,
            )

            metadata.source_audio = str(
                audio_path.resolve()
            )

        #
        # Update metadata fields only when supplied.
        #
        if instructions is not None:
            metadata.instructions = instructions

        if personality is not None:
            metadata.personality = personality

        if description is not None:
            metadata.description = description

        self.storage.save_metadata(
            character,
            metadata,
        )

        return UpdateCharacterResult(
            character=character,
            transcript=transcript if audio_path is not None else None,
            audio_updated=audio_path is not None,
        )

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