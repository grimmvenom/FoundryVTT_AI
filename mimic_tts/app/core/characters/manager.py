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


from pathlib import Path


from app.core.characters.models import (
    CharacterMetadata,
    CreateCharacterResult,
    RoleplayRequest,
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



    #
    # Character creation
    #

    def create_character(
        self,
        *,
        name: str,
        audio_path,
        instructions=None,
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

            name=name,

            source_audio=str(
                audio_path
            ),

            instructions=(
                instructions or ""
            ),

            personality="",

            description="",
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
    # Character helpers
    #

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
    ):

        if not self.exists(name):

            raise FileNotFoundError(
                f"Character not found: {name}"
            )


        return self.storage.load(
            name
        )



    #
    # Roleplay
    #

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